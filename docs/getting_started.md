# Getting Started

## Install

```bash
git clone https://github.com/kamalesh404/ForgeMind.git
cd ForgeMind
pip install -e ".[dev]"
```

## Connect a model

| Backend | Setup |
|---|---|
| Ollama (recommended, free) | Install from ollama.com, then `ollama pull qwen2.5-coder:7b` |
| llama.cpp | `pip install -e ".[local]"`, point `FORGEMIND_MODEL` at a `.gguf` file |
| OpenAI-compatible | Set `FORGEMIND_BACKEND=openai_compat`, `FORGEMIND_API_KEY`, `FORGEMIND_MODEL` |

## Your first run

```bash
forgemind run "What is (12 + 8) * 3? Reply with just the number."
```

Then try the dashboard:

```bash
forgemind serve
# open http://127.0.0.1:8080/dashboard
```

## Next steps

- `docs/architecture.md` — how the ReAct loop works
- `docs/mcp.md` — the MCP surface and how to add tools
- `docs/api_reference.md` — every endpoint and CLI command
