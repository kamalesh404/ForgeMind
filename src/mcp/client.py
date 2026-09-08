"""MCP client — calls tools on external MCP servers over HTTP."""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List

from src.mcp import protocol


class MCPClient:
    """Minimal HTTP MCP client (tools/list + tools/call)."""

    def __init__(self, base_url: str, timeout_s: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self._msg_id = 0

    def _send(self, method: str, params: Dict[str, Any] | None = None) -> Any:
        self._msg_id += 1
        body = json.dumps(protocol.request(self._msg_id, method, params)).encode()
        req = urllib.request.Request(
            self.base_url, data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            data = json.loads(resp.read().decode())
        if "error" in data:
            raise RuntimeError(f"MCP error: {data['error']}")
        return data.get("result")

    def initialize(self) -> Dict[str, Any]:
        """Handshake with the server."""
        return self._send("initialize", {"clientInfo": {"name": "forgemind", "version": "0.1.0"}})

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return the server's tool catalogue."""
        result = self._send("tools/list")
        return result.get("tools", [])

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call a remote tool and return its text content."""
        result = self._send("tools/call", {"name": name, "arguments": arguments})
        parts = [c.get("text", "") for c in result.get("content", [])]
        return "\n".join(parts)
