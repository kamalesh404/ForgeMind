# API Reference

## HTTP

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness |
| GET | `/v1/tools` | MCP tool catalogue |
| POST | `/v1/mcp` | Raw MCP JSON-RPC (`initialize`, `tools/list`, `tools/call`) |
| POST | `/v1/runs` | Start a run: `{goal, max_steps?, approval_mode?, use_critic?}` |
| GET | `/v1/runs/{id}` | Run detail (live) or stored trace |
| GET | `/v1/traces` | Stored run ids, newest first |
| GET | `/v1/approvals/{run_id}` | Outstanding approval requests |
| POST | `/v1/approvals/{run_id}` | Decide: `{tool_name, approved}` |
| WS | `/v1/stream` | Live `run_started / step_planned / run_finished` frames |
| GET | `/dashboard` | Static web UI |

## CLI

```bash
forgemind run "<goal>" [--backend --model --max-steps --approvals --no-critic]
forgemind serve [--host --port]
forgemind evaluate [--backend --model]
forgemind tools
forgemind trace <run_id>
```

## Python

```python
from src.agents.coordinator import Coordinator
from src.core.approvals import ApprovalGate
from src.core.config import Config
from src.core.trace import Tracer
from src.llm.base import create_backend
from src.mcp.registry import ToolRegistry
from src.tools import builtin

config = Config.from_env()
registry = ToolRegistry()
builtin.register_builtin(registry)
llm = create_backend(config.backend)
llm.load(config.model)
coord = Coordinator(llm, registry, approvals=ApprovalGate("auto"),
                    tracer=Tracer(), max_steps=12)
run = coord.execute_goal("What is 7*6? Reply with just the number.")
print(run.status, run.answer)
```
