"""HTTP + WebSocket API schemas."""

from __future__ import annotations

from typing import Any, Dict


def run_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a run request body."""
    goal = str(data.get("goal", "")).strip()
    if not goal:
        raise ValueError("Field 'goal' is required.")
    return {
        "goal": goal,
        "max_steps": int(data.get("max_steps", 12)),
        "approval_mode": str(data.get("approval_mode", "auto")),
        "use_critic": bool(data.get("use_critic", True)),
    }


def run_summary(run) -> Dict[str, Any]:
    """Serialize an AgentRun for HTTP responses."""
    return {
        **run.summary(),
        "answer": run.answer,
        "error": run.error,
        "steps": [
            {
                "index": s.index,
                "thought": s.thought,
                "observation": s.observation,
                "tool_calls": [
                    {"name": t.name, "arguments": t.arguments,
                     "result": t.result[:2000], "approved": t.approved}
                    for t in s.tool_calls
                ],
            }
            for s in run.steps
        ],
    }


def event_frame(kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap a coordinator event for WebSocket streaming."""
    return {"event": kind, "data": payload}
