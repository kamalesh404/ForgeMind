"""ForgeMind CLI — run goals, serve the API, run evals, manage tools."""

from __future__ import annotations

import json

import click

from src.agents.coordinator import Coordinator
from src.core.approvals import ApprovalGate
from src.core.config import Config
from src.core.trace import Tracer
from src.evals.harness import EvalHarness
from src.llm.base import create_backend
from src.mcp.registry import ToolRegistry
from src.tools import builtin, risky


def _build_stack(config: Config) -> tuple[ToolRegistry, Tracer]:
    registry = ToolRegistry(config.registry_path)
    builtin.register_builtin(registry)
    risky.register_risky(registry)
    return registry, Tracer(config.trace_dir)


def _make_llm(config: Config):
    llm = create_backend(config.backend)
    if config.backend == "ollama":
        llm.load(config.model)
    elif config.api_key:
        llm.load(config.model, api_key=config.api_key)
    else:
        llm.load(config.model)
    return llm


@click.group()
def cli() -> None:
    """ForgeMind — MCP-native multi-agent platform."""


@cli.command()
@click.argument("goal")
@click.option("--backend", default=None, help="LLM backend (ollama, llama_cpp, openai).")
@click.option("--model", default=None, help="Model name or path.")
@click.option("--max-steps", default=12, help="Max planner iterations.")
@click.option("--approvals", default="auto",
              type=click.Choice(["auto", "confirm_tools", "confirm_all"]))
@click.option("--no-critic", is_flag=True, help="Skip the critic check.")
def run(goal: str, backend: str | None, model: str | None,
        max_steps: int, approvals: str, no_critic: bool) -> None:
    """Execute one agent goal end to end."""
    config = Config.from_env()
    if backend:
        config.backend = backend
    if model:
        config.model = model
    registry, tracer = _build_stack(config)
    coordinator = Coordinator(
        _make_llm(config), registry,
        approvals=ApprovalGate(approvals), tracer=tracer,
        max_steps=max_steps, use_critic=not no_critic,
    )
    result = coordinator.execute_goal(goal)
    click.echo(f"[{result.status}] ({result.duration_s}s, {len(result.steps)} steps)")
    if result.answer:
        click.echo(result.answer)
    if result.error:
        click.echo(click.style(f"error: {result.error}", fg="red"))


@cli.command()
@click.option("--host", default=None)
@click.option("--port", default=None, type=int)
def serve(host: str | None, port: int | None) -> None:
    """Start the HTTP + WebSocket API server."""
    import uvicorn

    from src.api.server import build_app

    config = Config.from_env()
    if host:
        config.host = host
    if port:
        config.port = port
    click.echo(f"ForgeMind API on http://{config.host}:{config.port}")
    uvicorn.run(build_app(config), host=config.host, port=config.port)


@cli.command()
@click.option("--backend", default=None)
@click.option("--model", default=None)
def evaluate(backend: str | None, model: str | None) -> None:
    """Run the built-in eval suite and print a Markdown report."""
    config = Config.from_env()
    if backend:
        config.backend = backend
    if model:
        config.model = model
    registry, tracer = _build_stack(config)

    def factory() -> Coordinator:
        return Coordinator(
            _make_llm(config), registry,
            approvals=ApprovalGate("auto"), tracer=tracer, max_steps=8,
            use_critic=False,
        )

    report = EvalHarness(factory).run_all()
    click.echo(EvalHarness(factory).report_markdown(report))


@cli.command(name="tools")
def list_tools() -> None:
    """List registered tools with their MCP schemas."""
    config = Config.from_env()
    registry, _ = _build_stack(config)
    click.echo(json.dumps(registry.list_mcp_tools(), indent=2))


@cli.command()
@click.argument("run_id")
def trace(run_id: str) -> None:
    """Print a stored run trace as JSON."""
    config = Config.from_env()
    data = Tracer(config.trace_dir).load(run_id)
    click.echo(json.dumps(data, indent=2)[:6000])


if __name__ == "__main__":
    cli()
