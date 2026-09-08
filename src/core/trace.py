"""Execution tracing — every run leaves a replayable JSON trace."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

from src.core.run import AgentRun


class Tracer:
    """Persists run traces to disk for debugging, evals, and the dashboard."""

    def __init__(self, trace_dir: str = ".forgemind/traces") -> None:
        self.trace_dir = trace_dir
        os.makedirs(self.trace_dir, exist_ok=True)

    def _path(self, run_id: str) -> str:
        return os.path.join(self.trace_dir, f"{run_id}.json")

    def save(self, run: AgentRun) -> str:
        """Serialize a run to its trace file. Returns the file path."""
        payload: Dict[str, Any] = {
            "run_id": run.run_id,
            "goal": run.goal,
            "status": run.status,
            "answer": run.answer,
            "error": run.error,
            "duration_s": run.duration_s,
            "steps": [
                {
                    "index": s.index,
                    "thought": s.thought,
                    "observation": s.observation,
                    "tool_calls": [
                        {
                            "name": t.name,
                            "arguments": t.arguments,
                            "result": t.result[:4000],
                            "approved": t.approved,
                            "duration_ms": t.duration_ms,
                        }
                        for t in s.tool_calls
                    ],
                }
                for s in run.steps
            ],
        }
        path = self._path(run.run_id)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        return path

    def load(self, run_id: str) -> Dict[str, Any]:
        """Load a stored trace by run id."""
        with open(self._path(run_id), "r", encoding="utf-8") as fh:
            return json.load(fh)

    def list_runs(self) -> list[str]:
        """Return stored run ids, newest first."""
        files = [f for f in os.listdir(self.trace_dir) if f.endswith(".json")]
        files.sort(
            key=lambda f: os.path.getmtime(os.path.join(self.trace_dir, f)),
            reverse=True,
        )
        return [f[:-5] for f in files]
