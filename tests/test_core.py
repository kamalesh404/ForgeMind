"""Tests for approvals, traces, and runs."""

from src.core.approvals import ApprovalGate
from src.core.run import AgentRun
from src.core.trace import Tracer


def test_approval_modes():
    assert not ApprovalGate("auto").needs_approval("write_file")
    gate = ApprovalGate("confirm_tools")
    assert gate.needs_approval("write_file")
    assert not gate.needs_approval("calculator")
    assert ApprovalGate("confirm_all").needs_approval("calculator")


def test_approval_decide():
    gate = ApprovalGate("confirm_all")
    gate.request("r1", 0, "write_file", {"path": "x"})
    assert len(gate.outstanding("r1")) == 1
    assert gate.decide("r1", "write_file", True)
    assert gate.outstanding("r1") == []


def test_run_lifecycle():
    run = AgentRun(goal="test")
    assert run.status == "running"
    step = run.add_step("thinking")
    assert step.index == 0
    run.finish("answer")
    assert run.status == "done"
    assert run.summary()["steps"] == 1


def test_tracer_roundtrip(tmp_path):
    tracer = Tracer(str(tmp_path))
    run = AgentRun(goal="hello")
    run.add_step("t")
    run.finish("world")
    path = tracer.save(run)
    assert path.endswith(".json")
    loaded = tracer.load(run.run_id)
    assert loaded["answer"] == "world"
    assert run.run_id in tracer.list_runs()
