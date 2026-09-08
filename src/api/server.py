"""FastAPI server: runs, tools, approvals, traces + WebSocket live stream."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, List, Tuple

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.agents.coordinator import Coordinator
from src.api import schemas
from src.core.approvals import ApprovalGate
from src.core.config import Config
from src.core.run import AgentRun
from src.core.trace import Tracer
from src.llm.base import create_backend
from src.mcp.registry import ToolRegistry
from src.mcp.server import MCPServer
from src.tools import builtin, risky


def build_app(config: Config | None = None) -> FastAPI:
    """Assemble the app with registry, coordinator factory, and routes."""
    config = config or Config.from_env()
    app = FastAPI(title="ForgeMind", version="0.1.0")

    registry = ToolRegistry(config.registry_path)
    builtin.register_builtin(registry)
    risky.register_risky(registry)
    mcp_server = MCPServer(registry)
    tracer = Tracer(config.trace_dir)
    # run_id -> (AgentRun, Coordinator) so approvals stay decidable
    active: Dict[str, Tuple[AgentRun | None, Coordinator]] = {}
    subscribers: List[WebSocket] = []

    def make_coordinator(events: List[Dict[str, Any]] | None = None,
                         approval_mode: str | None = None,
                         max_steps: int | None = None) -> Coordinator:
        llm = create_backend(config.backend)
        if config.backend == "ollama":
            llm.load(config.model)
        elif config.api_key:
            llm.load(config.model, api_key=config.api_key)

        def on_event(kind: str, payload: Dict[str, Any]) -> None:
            frame = schemas.event_frame(kind, payload)
            if events is not None:
                events.append(frame)

        return Coordinator(
            llm, registry,
            approvals=ApprovalGate(approval_mode or config.approval_mode),
            tracer=tracer,
            max_steps=max_steps or config.max_steps,
            on_event=on_event,
        )

    async def broadcast(frame: Dict[str, Any]) -> None:
        dead = []
        for ws in subscribers:
            try:
                await ws.send_text(json.dumps(frame))
            except Exception:  # noqa: BLE001 — drop dead sockets
                dead.append(ws)
        for ws in dead:
            subscribers.remove(ws)

    dashboard_dir = os.path.join(os.path.dirname(__file__), "..", "dashboard")
    if os.path.isdir(dashboard_dir):
        app.mount("/dashboard", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "healthy", "version": "0.1.0"}

    @app.get("/v1/tools")
    def list_tools() -> Dict[str, Any]:
        return {"tools": registry.list_mcp_tools()}

    @app.post("/v1/mcp")
    async def mcp_endpoint(message: Dict[str, Any]) -> Any:
        reply = mcp_server.handle(message)
        if reply is None:
            return JSONResponse({"status": "notification received"})
        return reply

    @app.post("/v1/runs")
    async def start_run(body: Dict[str, Any]) -> Any:
        try:
            req = schemas.run_request(body)
        except (ValueError, TypeError) as e:
            return JSONResponse({"error": str(e)}, status_code=400)
        events: List[Dict[str, Any]] = []
        coordinator = make_coordinator(
            events, approval_mode=req["approval_mode"], max_steps=req["max_steps"]
        )
        loop = asyncio.get_event_loop()
        run = await loop.run_in_executor(None, coordinator.execute_goal, req["goal"])
        active[run.run_id] = (run, coordinator)
        for frame in events:
            await broadcast(frame)
        await broadcast(schemas.event_frame("run_finished", run.summary()))
        return schemas.run_summary(run)

    @app.get("/v1/runs/{run_id}")
    def get_run(run_id: str) -> Any:
        if run_id in active:
            run, _ = active[run_id]
            return schemas.run_summary(run)
        try:
            return tracer.load(run_id)
        except FileNotFoundError:
            return JSONResponse({"error": "run not found"}, status_code=404)

    @app.get("/v1/traces")
    def list_traces() -> Dict[str, Any]:
        return {"runs": tracer.list_runs()}

    @app.get("/v1/approvals/{run_id}")
    def list_approvals(run_id: str) -> Any:
        if run_id not in active:
            return JSONResponse({"error": "run not found"}, status_code=404)
        _, coordinator = active[run_id]
        outstanding = coordinator.approvals.outstanding(run_id)
        return {"pending": [
            {"tool_name": r.tool_name, "arguments": r.arguments, "reason": r.reason}
            for r in outstanding
        ]}

    @app.post("/v1/approvals/{run_id}")
    def decide_approval(run_id: str, body: Dict[str, Any]) -> Any:
        if run_id not in active:
            return JSONResponse({"error": "run not found"}, status_code=404)
        _, coordinator = active[run_id]
        tool_name = str(body.get("tool_name", ""))
        approved = bool(body.get("approved", False))
        found = coordinator.approvals.decide(run_id, tool_name, approved)
        if not found:
            return JSONResponse({"error": "no pending request for that tool"}, status_code=404)
        return {"run_id": run_id, "tool_name": tool_name, "approved": approved}

    @app.websocket("/v1/stream")
    async def stream(ws: WebSocket) -> None:
        await ws.accept()
        subscribers.append(ws)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            if ws in subscribers:
                subscribers.remove(ws)

    return app


def main() -> None:
    """Run the server with uvicorn."""
    import uvicorn

    config = Config.from_env()
    uvicorn.run(build_app(config), host=config.host, port=config.port)


if __name__ == "__main__":
    main()
