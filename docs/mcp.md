# MCP Guide

ForgeMind speaks [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) in both directions.

## Exposing tools (server side)

Every registered tool is automatically an MCP tool. Methods:

- `initialize` → server info + capabilities
- `tools/list` → `[{name, description, inputSchema}]`
- `tools/call` → `{content: [{type: "text", text}]}`

Over HTTP:

```bash
curl -X POST localhost:8080/v1/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

Over stdio (for MCP hosts like Claude Desktop):

```python
from src.mcp.server import MCPServer
from src.mcp.registry import ToolRegistry
from src.tools import builtin

reg = ToolRegistry()
builtin.register_builtin(reg)
MCPServer(reg).serve_stdio()
```

## Adding a tool

```python
@registry.register(
    "reverse",
    "Reverse a string.",
    parameters={"type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]},
)
def reverse(text: str) -> str:
    return text[::-1]
```

Mark world-changing tools `risky=True` so `confirm_tools` mode gates them.

## Consuming external MCP servers (client side)

```python
from src.mcp.client import MCPClient

client = MCPClient("http://localhost:9000/mcp")
client.initialize()
print(client.list_tools())
print(client.call_tool("search", {"query": "MCP spec"}))
```
