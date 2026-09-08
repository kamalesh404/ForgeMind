"""Executor agent — runs approved tool calls and summarizes observations."""

from __future__ import annotations

import time
from typing import Any, Dict

from src.agents.base import BaseAgent
from src.core.errors import ApprovalDeniedError, ToolExecutionError
from src.core.run import RunStep, ToolCall


class ExecutorAgent(BaseAgent):
    """Executes tool calls through the registry with approvals enforced."""

    role = "executor"
    system_prompt = (
        "You are an executor in a multi-agent system. You run tools exactly as "
        "planned and summarize their outputs as short observations."
    )

    def __init__(self, llm: Any, registry: Any, approvals: Any) -> None:
        super().__init__(llm)
        self.registry = registry
        self.approvals = approvals

    def run(self, step: RunStep, plan: Dict[str, Any], run_id: str) -> str:
        """Execute each planned tool call; return the combined observation."""
        observations = []
        for call in plan.get("tool_calls", []):
            name = call.get("name", "")
            args = call.get("arguments", {}) or {}
            tool_call = ToolCall(name=name, arguments=args)
            step.tool_calls.append(tool_call)
            if self.approvals.needs_approval(name):
                self.approvals.request(run_id, step.index, name, args)
                tool_call.approved = False
                raise ApprovalDeniedError(
                    f"Tool '{name}' needs human approval (mode={self.approvals.mode})."
                )
            started = time.time()
            try:
                tool_call.result = self.registry.execute(name, args)
            except Exception as e:  # noqa: BLE001 — surfaced as observation
                raise ToolExecutionError(name, str(e)) from e
            tool_call.duration_ms = round((time.time() - started) * 1000, 1)
            observations.append(f"[{name}] {tool_call.result[:1500]}")
        observation = "\n".join(observations) if observations else "(no tools called)"
        step.observation = observation
        return observation
