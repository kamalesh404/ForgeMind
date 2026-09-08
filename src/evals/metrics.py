"""Eval metrics — pass/fail plus efficiency signals."""

from __future__ import annotations

from typing import Any, Dict

from src.core.run import AgentRun


def score(case: Dict[str, Any], run: AgentRun) -> Dict[str, Any]:
    """Score one run against one case."""
    answer = run.answer or ""
    required = case.get("must_contain", [])
    hits = [s for s in required if s in answer]
    passed = bool(required) and len(hits) == len(required)
    steps = len(run.steps)
    tool_calls = sum(len(s.tool_calls) for s in run.steps)
    return {
        "case": case.get("id"),
        "passed": passed and run.status == "done",
        "status": run.status,
        "matched": hits,
        "missing": [s for s in required if s not in answer],
        "steps": steps,
        "tool_calls": tool_calls,
        "duration_s": run.duration_s,
    }


def aggregate(results: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize a list of per-case scores."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_steps = round(sum(r["steps"] for r in results) / total, 1) if total else 0
    return {
        "total": total,
        "passed": passed,
        "pass_rate": round(passed / total, 2) if total else 0,
        "avg_steps": avg_steps,
        "results": results,
    }
