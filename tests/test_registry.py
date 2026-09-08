"""Tests for the tool registry."""

import pytest

from src.core.errors import ToolExecutionError, ToolNotFoundError
from src.mcp.registry import ToolRegistry
from src.tools import builtin


def _registry():
    reg = ToolRegistry()
    builtin.register_builtin(reg)
    return reg


def test_builtin_tools_registered():
    reg = _registry()
    for name in ("calculator", "current_time", "echo", "word_count"):
        assert name in reg.tools


def test_calculator():
    reg = _registry()
    assert reg.execute("calculator", {"expression": "(12 + 8) * 3"}) == "60"


def test_calculator_rejects_names():
    reg = _registry()
    with pytest.raises(ToolExecutionError):
        reg.execute("calculator", {"expression": "__import__('os').system('x')"})


def test_unknown_tool():
    reg = _registry()
    with pytest.raises(ToolNotFoundError):
        reg.execute("nope", {})


def test_mcp_schema_shape():
    reg = _registry()
    tools = reg.list_mcp_tools()
    calc = next(t for t in tools if t["name"] == "calculator")
    assert calc["inputSchema"]["type"] == "object"
    assert "expression" in calc["inputSchema"]["properties"]


def test_describe_lists_tools():
    reg = _registry()
    text = reg.describe()
    assert "calculator" in text
