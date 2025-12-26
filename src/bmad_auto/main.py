"""CLI entry point for bmad-auto.

Uses Typer for CLI with anyio.run() at entry point for async orchestrator.
Exit codes from shared/consts.py - never bare integers.
"""

from pathlib import Path
from typing import Final

import typer

from bmad_auto.shared.consts import (
    EXIT_CONFIG_ERROR,
    EXIT_ERROR,
    EXIT_SUCCESS,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    STATUS_PAUSED,
)
from bmad_auto.shared.exceptions import ConfigError, StateCorruptionError

app: Final[typer.Typer] = typer.Typer(
    help="bmad-auto - AI-powered development workflow orchestrator"
)


def get_state_path() -> Path:
    """Get the path to the workflow state file.

    Returns:
        Path to .bmad-auto-state.yaml in current directory.

    Note: In future versions, this may read from user config.
    """
    return Path.cwd() / ".bmad-auto-state.yaml"


@app.command()
def run(epic: str = typer.Option(..., "--epic", help="Path to epic file")) -> None:
    """Execute story loop for an epic.

    Accepts epic path argument. Actual orchestration implemented in Epic 3.
    """
    try:
        state_path = get_state_path()

        # Check for existing in-progress workflow (conflict detection)
        if state_path.exists():
            from bmad_auto.core.state import load

            try:
                existing_state = load(state_path)

                # Check if there's an in-progress workflow for the SAME epic
                if existing_state.workflow.status == STATUS_IN_PROGRESS:
                    # Normalize paths for comparison
                    existing_epic = str(Path(existing_state.workflow.epic_path).resolve())
                    new_epic = str(Path(epic).resolve())

                    if existing_epic == new_epic:
                        typer.echo(
                            f"[yellow]Warning:[/yellow] Workflow already in progress for this epic.\n"
                            f"[dim]Epic: {existing_state.workflow.epic_path}[/dim]\n"
                            f"[dim]Current Story: {existing_state.current_story.id}[/dim]\n"
                            f"[dim]Phase: {existing_state.current_story.phase}[/dim]\n"
                            "\n"
                            f"[blue]Use 'bmad-auto resume' to continue the existing workflow.[/blue]\n"
                            "\n"
                            "[dim]If you want to start over, delete the state file first:[/dim]\n"
                            f"  rm {state_path}"
                        )
                        raise typer.Exit(EXIT_ERROR)

            except StateCorruptionError:
                # State file is corrupted - warn user but allow new run
                typer.echo(
                    "[yellow]Warning:[/yellow] Existing state file is corrupted.\n"
                    "[dim]A new workflow will overwrite it.[/dim]"
                )

        # Stub for now - actual orchestrator will be called with anyio.run()
        # in Epic 3: anyio.run(orchestrator.run_epic, epic)
        typer.echo(f"run command called with epic: {epic} (stub - orchestrator in Epic 3)")
        raise typer.Exit(EXIT_SUCCESS)

    except StateCorruptionError as exc:
        typer.echo(f"[red]State file error: {exc}[/red]", err=True)
        raise typer.Exit(EXIT_ERROR)
    except ConfigError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        raise typer.Exit(EXIT_CONFIG_ERROR)
    except typer.Exit:
        raise  # Re-raise typer.Exit for proper exit code handling
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(EXIT_ERROR)


@app.command()
def status() -> None:
    """Show current workflow status.

    Reads state file without locking (non-blocking).
    """
    try:
        state_path = get_state_path()

        # Check if state file exists
        if not state_path.exists():
            from bmad_auto.core.display import display_no_workflow

            display_no_workflow()
            raise typer.Exit(EXIT_SUCCESS)

        # Load state (non-blocking read)
        from bmad_auto.core.state import load
        from bmad_auto.core.display import (
            display_status,
            display_paused_status,
            display_completion_summary,
        )

        state = load(state_path)

        # Handle different statuses
        if state.workflow.status == STATUS_PAUSED:
            display_paused_status(state)
            raise typer.Exit(EXIT_SUCCESS)

        if state.workflow.status == STATUS_COMPLETED:
            display_completion_summary(state)
            raise typer.Exit(EXIT_SUCCESS)

        # Default: show full status (in_progress, pending, etc.)
        display_status(state)
        raise typer.Exit(EXIT_SUCCESS)

    except StateCorruptionError as exc:
        typer.echo(f"[red]State file error: {exc}[/red]", err=True)
        raise typer.Exit(EXIT_ERROR)
    except ConfigError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        raise typer.Exit(EXIT_CONFIG_ERROR)
    except typer.Exit:
        raise  # Re-raise typer.Exit for proper exit code handling
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(EXIT_ERROR)


@app.command()
def resume() -> None:
    """Resume a paused workflow from the exact point where it stopped."""
    try:
        state_path = get_state_path()

        # Check if state file exists
        if not state_path.exists():
            typer.echo(
                "[red]No workflow to resume[/red]\n"
                "[dim]No state file found. Start a new workflow with:[/dim]\n"
                "  bmad-auto run --epic <path-to-epic>",
                err=True,
            )
            raise typer.Exit(EXIT_ERROR)

        # Load state
        from bmad_auto.core.state import load

        state = load(state_path)

        # Handle completed workflow
        if state.workflow.status == STATUS_COMPLETED:
            typer.echo(
                f"[yellow]Workflow already complete[/yellow]\n"
                f"[dim]Epic: {state.workflow.epic_path}[/dim]\n"
                f"[dim]All {state.stories.total} stories completed.[/dim]"
            )
            raise typer.Exit(EXIT_SUCCESS)

        # Handle resumable statuses (in_progress, paused)
        if state.workflow.status in (STATUS_IN_PROGRESS, STATUS_PAUSED):
            # Display current position
            typer.echo(
                f"[blue]Resuming workflow[/blue]\n"
                f"[dim]Epic:[/dim] {state.workflow.epic_path}\n"
                f"[dim]Current Story:[/dim] {state.current_story.id}\n"
                f"[dim]Phase:[/dim] {state.current_story.phase}\n"
                f"[dim]Iteration:[/dim] {state.current_story.iteration}\n"
                f"[dim]Branch:[/dim] {state.workflow.branch}\n"
                "\n"
                f"[dim](Orchestrator integration in Epic 3 - stub for now)[/dim]"
            )
            # In Epic 3, this will call: anyio.run(orchestrator.resume, state)
            raise typer.Exit(EXIT_SUCCESS)

        # Unknown status
        typer.echo(
            f"[red]Cannot resume workflow with status: {state.workflow.status}[/red]",
            err=True,
        )
        raise typer.Exit(EXIT_ERROR)

    except StateCorruptionError as exc:
        typer.echo(f"[red]State file error: {exc}[/red]", err=True)
        raise typer.Exit(EXIT_ERROR)
    except ConfigError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        raise typer.Exit(EXIT_CONFIG_ERROR)
    except typer.Exit:
        raise  # Re-raise typer.Exit for proper exit code handling
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(EXIT_ERROR)


if __name__ == "__main__":
    app()
