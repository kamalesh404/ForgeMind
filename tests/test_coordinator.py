"""Tests for the coordinator loop with a scripted LLM."""

from src.agents.coordinator import Coordinator
from src.core.approvals import ApprovalGate
from src.mcp.registry import ToolRegistry
from src.tools import builtin
from tests.conftest import FakeLLM


def _coordinator(replies, approval_mode="auto", use_critic=False):
    reg = ToolRegistry()
    builtin.register_builtin(reg)
    return Coordinator(
        FakeLLM(replies), reg,
        approvals=ApprovalGate(approval_mode),
        tracer=None, max_steps=6, use_critic=use_critic,
    )


def test_immediate_done():
    coord = _coordinator([
        '{"thought": "nothing to do", "tool_calls": [], "done": true, "final_answer": "42"}'
    ])
    run = coord.execute_goal("answer 42")
    assert run.status == "done"
    assert run.answer == "42"


def test_tool_then_done():
    coord = _coordinator([
        '{"thought": "compute", "tool_calls": [{"name": "calculator", "arguments": {"expression": "2+2"}}], "done": false, "final_answer": ""}',
        '{"thought": "done", "tool_calls": [], "done": true, "final_answer": "4"}',
    ])
    run = coord.execute_goal("compute 2+2")
    assert run.status == "done"
    assert run.answer == "4"
    assert sum(len(s.tool_calls) for s in run.steps) == 1


def test_approval_blocks_run():
    coord = _coordinator([
        '{"thought": "write", "tool_calls": [{"name": "calculator", "arguments": {"expression": "1+1"}}], "done": false, "final_answer": ""}',
    ], approval_mode="confirm_all")
    run = coord.execute_goal("compute")
    assert run.status == "waiting_approval"


def test_critic_reject_retries():
    coord = _coordinator([
        '{"thought": "draft", "tool_calls": [], "done": true, "final_answer": "wrong"}',
        '{"accepted": false, "feedback": "not right"}',
        '{"thought": "fixed", "tool_calls": [], "done": true, "final_answer": "right"}',
        '{"accepted": true, "feedback": ""}',
    ], use_critic=True)
    run = coord.execute_goal("goal")
    assert run.status == "done"
    assert run.answer == "right"
