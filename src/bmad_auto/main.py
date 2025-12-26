"""CLI entry point for bmad-auto.

Uses Typer for CLI with anyio.run() at entry point for async orchestrator.
Exit codes from shared/consts.py - never bare integers.
"""

import sys
from typing import Final

import typer

from bmad_auto.shared.consts import EXIT_CONFIG_ERROR, EXIT_ERROR, EXIT_SUCCESS
from bmad_auto.shared.exceptions import ConfigError

app: Final[typer.Typer] = typer.Typer(
    help="bmad-auto - AI-powered development workflow orchestrator"
)


@app.command()
def run(epic: str = typer.Option(..., "--epic", help="Path to epic file")) -> None:
    """Execute story loop for an epic.

    Accepts epic path argument. Actual orchestration implemented in Epic 3.
    """
    try:
        # Stub for now - actual orchestrator will be called with anyio.run()
        # in Epic 3: anyio.run(orchestrator.run_epic, epic)
        typer.echo(f"run command called with epic: {epic} (stub - orchestrator in Epic 3)")
        sys.exit(EXIT_SUCCESS)
    except ConfigError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        sys.exit(EXIT_CONFIG_ERROR)
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        sys.exit(EXIT_ERROR)


@app.command()
def status() -> None:
    """Show current workflow status.

    Stub for now - full implementation in Epic 4.
    """
    try:
        typer.echo("status command (stub - full implementation in Epic 4)")
        sys.exit(EXIT_SUCCESS)
    except ConfigError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        sys.exit(EXIT_CONFIG_ERROR)
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        sys.exit(EXIT_ERROR)


@app.command()
def resume() -> None:
    """Resume a paused workflow.

    Stub for now - full implementation in Epic 2.
    """
    try:
        typer.echo("resume command (stub - full implementation in Epic 2)")
        sys.exit(EXIT_SUCCESS)
    except ConfigError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        sys.exit(EXIT_CONFIG_ERROR)
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        sys.exit(EXIT_ERROR)


if __name__ == "__main__":
    app()
