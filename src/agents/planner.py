"""Planner agent — decomposes a goal into tool-using steps."""

from __future__ import annotations

from typing import Any, Dict

from src.agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    """Produces the next thought + tool calls for a run."""

    role = "planner"
    system_prompt = (
        "You are a planner in a multi-agent system. Given the goal, the tools "
        "available, and the history so far, decide the next step. Respond with "
        "STRICT JSON: {'thought': str, 'tool_calls': [{'name': str, 'arguments': dict}], "
        "'done': bool, 'final_answer': str}. Set done=true only when the goal is "
        "fully achieved. Prefer finishing in few steps."
    )

    def run(self, goal: str, tool_descriptions: str, history_summary: str) -> Dict[str, Any]:
        """Return the next plan as a structured dict."""
        raw = self.chat(
            f"GOAL: {goal}\n\nTOOLS:\n{tool_descriptions}\n\n"
            f"PROGRESS SO FAR:\n{history_summary}\n\nNext step as JSON:",
            temperature=0.2,
            max_tokens=1024,
        )
        plan = self.parse_json_object(raw)
        plan.setdefault("thought", raw.strip())
        plan.setdefault("tool_calls", [])
        plan.setdefault("done", False)
        plan.setdefault("final_answer", "")
        return plan
