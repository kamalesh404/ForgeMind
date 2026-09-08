"""Tool registry — the single source of truth for callable tools."""

from __future__ import annotations

import inspect
import json
import os
from typing import Any, Callable, Dict, List

from src.core.errors import ToolExecutionError, ToolNotFoundError
from src.mcp import protocol


class ToolDefinition:
    """A registered tool with its schema and implementation."""

    def __init__(self, name: str, description: str, func: Callable[..., str],
                 parameters: Dict[str, Any] | None = None, risky: bool = False) -> None:
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or {"type": "object", "properties": {}}
        self.risky = risky

    def to_mcp(self) -> Dict[str, Any]:
        """Render as an MCP tool definition."""
        props = self.parameters.get("properties", {})
        required = self.parameters.get("required", [])
        return protocol.tool_schema(self.name, self.description, props, required)


class ToolRegistry:
    """Registers, describes, persists, and executes tools."""

    def __init__(self, path: str | None = None) -> None:
        self.tools: Dict[str, ToolDefinition] = {}
        self.path = path

    def register(self, name: str, description: str, risky: bool = False,
                 parameters: Dict[str, Any] | None = None):
        """Decorator to register a function as a tool."""
        def decorator(func: Callable[..., str]) -> Callable[..., str]:
            params = parameters or self._infer_parameters(func)
            self.tools[name] = ToolDefinition(name, description, func, params, risky)
            return func
        return decorator

    @staticmethod
    def _infer_parameters(func: Callable) -> Dict[str, Any]:
        """Build a basic object schema from a function's signature."""
        props: Dict[str, Any] = {}
        required: List[str] = []
        for pname, param in inspect.signature(func).parameters.items():
            props[pname] = {"type": "string", "description": f"Argument '{pname}'"}
            if param.default is inspect.Parameter.empty:
                required.append(pname)
        return {"type": "object", "properties": props, "required": required}

    def describe(self) -> str:
        """Human-readable tool list for planner prompts."""
        lines = []
        for t in self.tools.values():
            flag = " [RISKY]" if t.risky else ""
            lines.append(f"- {t.name}{flag}: {t.description}")
        return "\n".join(lines) or "(no tools registered)"

    def list_mcp_tools(self) -> List[Dict[str, Any]]:
        """All tools in MCP tools/list format."""
        return [t.to_mcp() for t in self.tools.values()]

    def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        """Run a tool by name. Raises ToolNotFoundError / ToolExecutionError."""
        tool = self.tools.get(name)
        if tool is None:
            raise ToolNotFoundError(f"Unknown tool: {name}")
        try:
            result = tool.func(**(arguments or {}))
        except ToolNotFoundError:
            raise
        except Exception as e:  # noqa: BLE001 — wrapped for the agent loop
            raise ToolExecutionError(name, str(e)) from e
        return str(result)

    def save(self) -> None:
        """Persist the tool catalogue (names + schemas, not code)."""
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        catalogue = [
            {"name": t.name, "description": t.description,
             "risky": t.risky, "parameters": t.parameters}
            for t in self.tools.values()
        ]
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(catalogue, fh, indent=2)
