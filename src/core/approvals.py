"""Human-in-the-loop approvals for tool calls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ApprovalRequest:
    """A pending tool call awaiting a human decision."""

    run_id: str
    step_index: int
    tool_name: str
    arguments: Dict[str, Any]
    reason: str = ""
    decided: bool = False
    approved: bool = False


class ApprovalGate:
    """Decides which tool calls need human confirmation.

    Modes:
      - auto: approve everything (default, best for trusted tools)
      - confirm_tools: ask for tools marked risky (write, shell, network)
      - confirm_all: ask for every tool call
    """

    RISKY_TOOLS = {"write_file", "run_shell", "http_request"}

    def __init__(self, mode: str = "auto") -> None:
        if mode not in ("auto", "confirm_tools", "confirm_all"):
            raise ValueError(f"Unknown approval mode: {mode}")
        self.mode = mode
        self.pending: List[ApprovalRequest] = []

    def needs_approval(self, tool_name: str) -> bool:
        """Return True if this tool call must wait for a human."""
        if self.mode == "confirm_all":
            return True
        if self.mode == "confirm_tools" and tool_name in self.RISKY_TOOLS:
            return True
        return False

    def request(self, run_id: str, step_index: int, tool_name: str,
                arguments: Dict[str, Any], reason: str = "") -> ApprovalRequest:
        """Register a pending approval and return it."""
        req = ApprovalRequest(
            run_id=run_id, step_index=step_index,
            tool_name=tool_name, arguments=arguments, reason=reason,
        )
        self.pending.append(req)
        return req

    def decide(self, run_id: str, tool_name: str, approved: bool) -> bool:
        """Resolve the oldest matching pending request. Returns True if found."""
        for req in self.pending:
            if req.run_id == run_id and req.tool_name == tool_name and not req.decided:
                req.decided = True
                req.approved = approved
                return True
        return False

    def outstanding(self, run_id: str) -> List[ApprovalRequest]:
        """List undecided requests for a run."""
        return [r for r in self.pending if r.run_id == run_id and not r.decided]
