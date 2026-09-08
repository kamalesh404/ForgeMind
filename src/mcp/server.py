"""MCP server — exposes the registry over JSON-RPC (stdio + HTTP)."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from src.mcp import protocol


class MCPServer:
    """Serves initialize, tools/list, and tools/call for the registry."""

    def __init__(self, registry: Any, name: str = "forgemind", version: str = "0.1.0") -> None:
        self.registry = registry
        self.name = name
        self.version = version

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any] | None:
        """Handle one JSON-RPC message; returns a response or None."""
        msg_id = message.get("id", 0)
        method = message.get("method", "")
        params = message.get("params", {}) or {}

        if method == "initialize":
            return protocol.response(msg_id, {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": self.name, "version": self.version},
                "capabilities": {"tools": {"listChanged": True}},
            })
        if method == "tools/list":
            return protocol.response(msg_id, {"tools": self.registry.list_mcp_tools()})
        if method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {}) or {}
            try:
                content = self.registry.execute(tool_name, arguments)
            except Exception as e:  # noqa: BLE001 — returned as MCP error
                return protocol.error(msg_id, protocol.INTERNAL_ERROR, str(e))
            return protocol.response(msg_id, {
                "content": [{"type": "text", "text": content}],
            })
        if method.startswith("notifications/"):
            return None
        return protocol.error(msg_id, protocol.METHOD_NOT_FOUND, f"Unknown method: {method}")

    def serve_stdio(self) -> None:
        """Serve newline-delimited JSON-RPC on stdin/stdout (MCP stdio mode)."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                sys.stdout.write(json.dumps(protocol.error(0, protocol.PARSE_ERROR, "bad json")) + "\n")
                sys.stdout.flush()
                continue
            reply = self.handle(message)
            if reply is not None:
                sys.stdout.write(json.dumps(reply) + "\n")
                sys.stdout.flush()
