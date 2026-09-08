"""Critic agent — checks the final answer before delivery."""

from __future__ import annotations

from typing import Any, Dict

from src.agents.base import BaseAgent


class CriticAgent(BaseAgent):
    """Scores a draft answer for correctness and completeness."""

    role = "critic"
    system_prompt = (
        "You are a critic. Given the goal and a draft answer, judge whether the "
        "answer actually achieves the goal. Respond STRICT JSON: "
        "{'accepted': bool, 'feedback': str}."
    )

    def run(self, goal: str, draft_answer: str) -> Dict[str, Any]:
        """Return {'accepted', 'feedback'} for a draft answer."""
        raw = self.chat(
            f"GOAL: {goal}\n\nDRAFT ANSWER:\n{draft_answer}\n\nVerdict as JSON:",
            temperature=0.1,
            max_tokens=512,
        )
        verdict = self.parse_json_object(raw)
        verdict.setdefault("accepted", True)
        verdict.setdefault("feedback", "")
        return verdict
