"""Eval harness — runs the suite through a coordinator factory."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from src.evals import cases, metrics


class EvalHarness:
    """Runs eval cases and aggregates scores."""

    def __init__(self, make_coordinator: Callable[[], Any],
                 eval_cases: List[Dict[str, Any]] | None = None) -> None:
        self.make_coordinator = make_coordinator
        self.eval_cases = eval_cases or cases.default_cases()

    def run_all(self) -> Dict[str, Any]:
        """Execute every case and return the aggregate report."""
        results = []
        for case in self.eval_cases:
            coordinator = self.make_coordinator()
            run = coordinator.execute_goal(case["goal"])
            results.append(metrics.score(case, run))
        return metrics.aggregate(results)

    def report_markdown(self, report: Dict[str, Any]) -> str:
        """Render an aggregate report as Markdown."""
        lines = [
            "# ForgeMind Eval Report",
            "",
            f"Pass rate: {report['passed']}/{report['total']} ({report['pass_rate']})",
            f"Avg steps: {report['avg_steps']}",
            "",
            "| Case | Passed | Steps | Tools | Duration |",
            "| ---- | ------ | ----- | ----- | -------- |",
        ]
        for r in report["results"]:
            lines.append(
                f"| {r['case']} | {'PASS' if r['passed'] else 'FAIL'} | "
                f"{r['steps']} | {r['tool_calls']} | {r['duration_s']}s |"
            )
        return "\n".join(lines)
