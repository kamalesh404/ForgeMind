"""Shared error types."""

from __future__ import annotations


class ForgeMindError(Exception):
    """Base error for all ForgeMind failures."""


class ToolNotFoundError(ForgeMindError):
    """Raised when a run references an unregistered tool."""


class ToolExecutionError(ForgeMindError):
    """Raised when a registered tool fails at runtime."""

    def __init__(self, tool_name: str, message: str) -> None:
        super().__init__(f"[{tool_name}] {message}")
        self.tool_name = tool_name


class ApprovalDeniedError(ForgeMindError):
    """Raised when a human rejects a tool call."""


class MaxStepsExceededError(ForgeMindError):
    """Raised when a run exceeds its step budget."""
