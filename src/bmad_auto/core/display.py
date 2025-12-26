"""Status display utilities for bmad-auto.

Uses Rich for formatted output. All functions are read-only - never modify state.
"""

from datetime import datetime, timezone

from rich.console import Console

from bmad_auto.core.state import WorkflowState
from bmad_auto.shared.consts import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_IN_PROGRESS,
    STATUS_PAUSED,
)

console = Console()

# Status colors for Rich output
STATUS_COLORS = {
    STATUS_IN_PROGRESS: "green",
    STATUS_PAUSED: "yellow",
    STATUS_COMPLETED: "blue",
    STATUS_FAILED: "red",
}


def calculate_duration(started_at: datetime) -> str:
    """Calculate human-readable duration from ISO timestamp.

    Args:
        started_at: Datetime when the story started.

    Returns:
        Duration string like "12m 34s" or "1h 05m 12s".
    """
    delta = datetime.now(timezone.utc) - started_at
    total_seconds = int(delta.total_seconds())

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"
    return f"{minutes}m {seconds:02d}s"


def format_time(started_at: datetime) -> str:
    """Format datetime to readable time string.

    Args:
        started_at: Datetime to format.

    Returns:
        Time string like "14:23:07".
    """
    return started_at.strftime("%H:%M:%S")


def display_status(state: WorkflowState) -> None:
    """Display complete workflow status.

    Args:
        state: Current workflow state.

    Displays:
        - Epic path
        - Overall status
        - Progress (Story X of Y)
        - Current story details
        - Completed stories with commits
    """
    # Epic and status
    status_color = STATUS_COLORS.get(state.workflow.status, "white")
    console.print()
    console.print(f"[bold]Epic:[/bold] {state.workflow.epic_path}")
    console.print(f"[bold]Status:[/bold] [{status_color}]{state.workflow.status}[/{status_color}]")

    # Progress
    current_num = state.stories.current_index + 1
    total = state.stories.total
    console.print(f"[bold]Progress:[/bold] Story {current_num} of {total}")

    # Current story
    _display_current_story(state)

    # Completed stories
    if state.stories.completed:
        _display_completed_stories(state)


def _display_current_story(state: WorkflowState) -> None:
    """Display current story progress.

    Args:
        state: Current workflow state.
    """
    console.print()
    console.print(f"[bold]Current Story:[/bold] \"{state.current_story.id}\"")

    # Phase with iteration
    phase_display = state.current_story.phase
    if state.current_story.iteration > 1:
        phase_display += f" (iteration {state.current_story.iteration})"
    console.print(f"  Phase: {phase_display}")

    # Started time
    console.print(f"  Started: {format_time(state.current_story.started_at)}")

    # Duration
    duration = calculate_duration(state.current_story.started_at)
    console.print(f"  Duration: {duration}")


def _display_completed_stories(state: WorkflowState) -> None:
    """Display completed stories with commit references.

    Args:
        state: Current workflow state.
    """
    console.print()
    console.print("[bold]Completed Stories:[/bold]")

    for story in state.stories.completed:
        short_hash = story.commit[:7] if story.commit else "pending"
        console.print(f"  [green]✓[/green] Story {story.story_id} - committed ({short_hash})")


def display_no_workflow() -> None:
    """Display message when no workflow is active."""
    console.print()
    console.print("[yellow]No active workflow.[/yellow]")
    console.print("[dim]Run 'bmad-auto run --epic <file>' to start.[/dim]")


def display_paused_status(state: WorkflowState) -> None:
    """Display paused workflow status with error details.

    Args:
        state: Current workflow state (should have STATUS_PAUSED).
    """
    console.print()
    console.print("[bold yellow]Status:[/bold yellow] PAUSED")

    if state.error.message:
        console.print()
        console.print(f"[red]Error:[/red] {state.error.message}")
        if state.error.type:
            console.print(f"[dim]Error type: {state.error.type}[/dim]")
        if state.error.phase:
            console.print(f"[dim]Phase: {state.error.phase}[/dim]")

    console.print()
    console.print("[blue]Resume instructions:[/blue]")
    console.print("  bmad-auto resume")


def display_completion_summary(state: WorkflowState) -> None:
    """Display workflow completion summary.

    Args:
        state: Current workflow state (should have STATUS_COMPLETED).
    """
    console.print()
    console.print("[bold blue]Status:[/bold blue] COMPLETED")
    console.print()
    console.print(f"[bold]Total Stories:[/bold] {state.stories.total}")
    console.print(f"[bold]Total Commits:[/bold] {len(state.stories.completed)}")
    console.print(f"[bold]Branch:[/bold] {state.workflow.branch}")

    # Calculate total duration from first story start to now
    if state.stories.completed and state.current_story.started_at:
        duration = calculate_duration(state.current_story.started_at)
        console.print(f"[bold]Duration:[/bold] {duration}")
