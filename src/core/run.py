"""Agent run lifecycle model."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ToolCall:
    """A single tool invocation inside a run."""

    name: str
    arguments: Dict[str, Any]
    result: str = ""
    approved: bool = True
    duration_ms: float = 0.0


@dataclass
class RunStep:
    """One planner/executor iteration."""

    index: int
    thought: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    observation: str = ""


@dataclass
class AgentRun:
    """Tracks a full agent execution from goal to final answer."""

    goal: str
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: str = "running"  # running | waiting_approval | done | failed
    steps: List[RunStep] = field(default_factory=list)
    answer: str = ""
    error: str = ""
    started_at: float = field(default_factory=time.time)
    ended_at: float = 0.0

    def add_step(self, thought: str) -> RunStep:
        step = RunStep(index=len(self.steps), thought=thought)
        self.steps.append(step)
        return step

    def finish(self, answer: str) -> None:
        self.answer = answer
        self.status = "done"
        self.ended_at = time.time()

    def fail(self, error: str) -> None:
        self.error = error
        self.status = "failed"
        self.ended_at = time.time()

    @property
    def duration_s(self) -> float:
        end = self.ended_at or time.time()
        return round(end - self.started_at, 2)

    def summary(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "goal": self.goal,
            "status": self.status,
            "steps": len(self.steps),
            "tool_calls": sum(len(s.tool_calls) for s in self.steps),
            "duration_s": self.duration_s,
        }
