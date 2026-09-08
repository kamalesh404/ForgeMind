"""Tests for MCP protocol handling and eval scoring."""

from src.core.run import AgentRun
from src.evals import metrics
from src.mcp import protocol
from src.mcp.registry import ToolRegistry
from src.mcp.server import MCPServer
from src.tools import builtin


def _server():
    reg = ToolRegistry()
    builtin.register_builtin(reg)
    return MCPServer(reg)


def test_initialize():
    reply = _server().handle(protocol.request(1, "initialize"))
    assert reply["result"]["serverInfo"]["name"] == "forgemind"


def test_tools_list():
    reply = _server().handle(protocol.request(2, "tools/list"))
    names = [t["name"] for t in reply["result"]["tools"]]
    assert "calculator" in names


def test_tools_call():
    msg = protocol.request(3, "tools/call", {
        "name": "calculator", "arguments": {"expression": "3*7"}})
    reply = _server().handle(msg)
    assert reply["result"]["content"][0]["text"] == "21"


def test_unknown_method():
    reply = _server().handle(protocol.request(4, "nope/method"))
    assert "error" in reply


def test_eval_scoring_pass():
    run = AgentRun(goal="g")
    run.finish("the answer is 60")
    result = metrics.score({"id": "x", "must_contain": ["60"]}, run)
    assert result["passed"] is True


def test_eval_scoring_fail():
    run = AgentRun(goal="g")
    run.finish("the answer is 7")
    result = metrics.score({"id": "x", "must_contain": ["60"]}, run)
    assert result["passed"] is False
    assert result["missing"] == ["60"]


def test_aggregate():
    report = metrics.aggregate([
        {"case": "a", "passed": True, "steps": 2, "tool_calls": 1, "duration_s": 1.0},
        {"case": "b", "passed": False, "steps": 4, "tool_calls": 2, "duration_s": 2.0},
    ])
    assert report["total"] == 2
    assert report["passed"] == 1
    assert report["pass_rate"] == 0.5
    assert report["avg_steps"] == 3.0
