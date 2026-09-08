"""Smoke tests for the HTTP API (no LLM needed)."""

from fastapi.testclient import TestClient

from src.api.server import build_app
from src.core.config import Config


def _client():
    config = Config(backend="ollama", model="test-model")
    return TestClient(build_app(config))


def test_health():
    r = _client().get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_list_tools():
    r = _client().get("/v1/tools")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()["tools"]]
    assert "calculator" in names


def test_mcp_tools_call():
    r = _client().post("/v1/mcp", json={
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "echo", "arguments": {"text": "hi"}},
    })
    assert r.status_code == 200
    assert r.json()["result"]["content"][0]["text"] == "hi"


def test_run_requires_goal():
    r = _client().post("/v1/runs", json={})
    assert r.status_code == 400


def test_unknown_run_404():
    r = _client().get("/v1/runs/does-not-exist")
    assert r.status_code == 404
