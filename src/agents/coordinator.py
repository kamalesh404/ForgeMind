"""Coordinator — runs planner/executor/critic loop with approvals and traces."""

from __future__ import annotations

from typing import Any, Callable, Dict

from src.agents.critic import CriticAgent
from src.agents.executor import ExecutorAgent
from src.agents.planner import PlannerAgent
from src.core.approvals import ApprovalGate
from src.core.errors import ApprovalDeniedError, MaxStepsExceededError, ToolExecutionError
from src.core.run import AgentRun
from src.core.trace import Tracer


class Coordinator:
    """Owns the full ReAct loop: plan -> approve -> execute -> observe -> repeat."""

    def __init__(
        self,
        llm: Any,
        registry: Any,
        approvals: ApprovalGate | None = None,
        tracer: Tracer | None = None,
        max_steps: int = 12,
        use_critic: bool = True,
        on_event: Callable[[str, Dict[str, Any]], None] | None = None,
    ) -> None:
        self.llm = llm
        self.registry = registry
        self.approvals = approvals or ApprovalGate()
        self.tracer = tracer
        self.max_steps = max_steps
        self.use_critic = use_critic
        self.on_event = on_event
        self.planner = PlannerAgent(llm)
        self.executor = ExecutorAgent(llm, registry, self.approvals)
        self.critic = CriticAgent(llm)

    def _emit(self, kind: str, payload: Dict[str, Any]) -> None:
        if self.on_event:
            self.on_event(kind, payload)

    def _history_summary(self, run: AgentRun) -> str:
        lines = []
        for s in run.steps[-5:]:
            lines.append(f"Step {s.index}: thought={s.thought}")
            if s.observation:
                lines.append(f"  observation: {s.observation[:500]}")
        return "\n".join(lines) or "(no steps yet)"

    def execute_goal(self, goal: str) -> AgentRun:
        """Run the loop until done, approval-needed, failed, or out of steps."""
        run = AgentRun(goal=goal)
        self._emit("run_started", run.summary())
        try:
            for _ in range(self.max_steps):
                plan = self.planner.run(
                    goal, self.registry.describe(), self._history_summary(run)
                )
                step = run.add_step(plan.get("thought", ""))
                self._emit("step_planned", {"run_id": run.run_id, "step": step.index})
                if plan.get("done"):
                    draft = plan.get("final_answer", "")
                    if self.use_critic:
                        verdict = self.critic.run(goal, draft)
                        if not verdict.get("accepted"):
                            step.observation = f"critic rejected: {verdict.get('feedback')}"
                            continue
                    run.finish(draft)
                    break
                try:
                    self.executor.run(step, plan, run.run_id)
                except ApprovalDeniedError as e:
                    run.status = "waiting_approval"
                    run.error = str(e)
                    break
                except ToolExecutionError as e:
                    step.observation = f"tool error: {e}"
            else:
                raise MaxStepsExceededError(f"Exceeded {self.max_steps} steps.")
        except MaxStepsExceededError as e:
            run.fail(str(e))
        if self.tracer:
            self.tracer.save(run)
        self._emit("run_finished", run.summary())
        return run
