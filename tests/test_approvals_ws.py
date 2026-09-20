"""Tests for approval gate edge cases and WebSocket lifecycle."""

from fastapi.testclient import TestClient

from src.api.server import build_app
from src.core.approvals import ApprovalGate
from src.core.config import Config


def _client():
    return TestClient(build_app(Config(backend="ollama", model="test-model")))


def test_approval_gate_unknown_mode_raises():
    try:
        ApprovalGate("invalid")
        assert False, "should raise"
    except ValueError as e:
        assert "Unknown approval mode" in str(e)


def test_approval_gate_outstanding_empty():
    gate = ApprovalGate("auto")
    assert gate.outstanding("no-run") == []


def test_approval_decide_missing_returns_false():
    gate = ApprovalGate("confirm_all")
    assert not gate.decide("r1", "write_file", True)


def test_health_has_version():
    r = _client().get("/health")
    assert r.json()["version"] == "0.1.0"


def test_traces_empty_initially(tmp_path):
    # Uses isolated tmp dir via Config override
    config = Config(backend="ollama", model="test-model", trace_dir=str(tmp_path))
    client = TestClient(build_app(config))
    r = client.get("/v1/traces")
    assert r.status_code == 200
    assert r.json()["runs"] == []


def test_websocket_connect_and_disconnect():
    client = _client()
    with client.websocket_connect("/v1/stream") as ws:
        ws.send_text("ping")
        # No assertion needed — just verify connect/send/close doesn't error
