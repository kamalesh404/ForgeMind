"""Minimal MCP (Model Context Protocol) JSON-RPC types.

Implements the subset of MCP needed to expose ForgeMind tools to any
MCP-compatible client and to talk to external MCP servers: initialize,
tools/list, tools/call, and notifications.
"""

from __future__ import annotations

from typing import Any, Dict, List


def request(msg_id: int | str, method: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Build a JSON-RPC 2.0 request object."""
    payload: Dict[str, Any] = {"jsonrpc": "2.0", "id": msg_id, "method": method}
    if params is not None:
        payload["params"] = params
    return payload


def response(msg_id: int | str, result: Any) -> Dict[str, Any]:
    """Build a JSON-RPC 2.0 success response."""
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def error(msg_id: int | str, code: int, message: str) -> Dict[str, Any]:
    """Build a JSON-RPC 2.0 error response."""
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def tool_schema(name: str, description: str, properties: Dict[str, Any],
                required: List[str] | None = None) -> Dict[str, Any]:
    """Build an MCP tool definition with a JSON-Schema input."""
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required or [],
        },
    }


# Standard JSON-RPC error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
