"""Typer CLI definitions for bmad-auto."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
import yaml

from bmad_auto.core import config as config_module
from bmad_auto.core.config import AgentSettings, Settings
from bmad_auto.core.exceptions import ConfigurationError, WorkflowError
from bmad_auto.core.logging import configure_logging
from bmad_auto.core.protocols import AgentProtocol, ProgressReporterProtocol
from bmad_auto.features.agents.factory import create_agent
from bmad_auto.features.agents.models import AgentConfig
from bmad_auto.features.discovery.epic_discovery import EpicDiscovery
from bmad_auto.features.discovery.epic_parser import EpicParser
from bmad_auto.features.git_ops.manager import GitManager
from bmad_auto.features.git_ops.models import GitConfig
from bmad_auto.features.orchestrator import Phase, PromptLoader, WorkflowEngine
from bmad_auto.features.orchestrator.engine import parse_story_ref
from bmad_auto.features.state.manager import StateManager
from bmad_auto.features.tui.app import WorkflowApp
from bmad_auto.features.tui.headless import HeadlessReporter
from bmad_auto.shared.consts import DEFAULT_CONFIG_FILE, DEFAULT_STATE_DIR, DEFAULT_TEMPLATES_DIR

app = typer.Typer(add_completion=False, help="Automate BMAD workflows.")


@app.callback()
def _startup(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logs"),
) -> None:
    """Configure logging and preload settings."""
    configure_logging(debug=verbose)
    config_module.get_settings()


@app.command()
def version() -> None:
    """Show the current version."""
    from bmad_auto import __version__

    typer.echo(__version__)


@app.command()
def init(repo_path: Path = typer.Argument(Path("."), help="Repository root path")) -> None:
    """Initialize repository config and state directories."""
    repo_root = repo_path.resolve()
    config_path = repo_root / DEFAULT_CONFIG_FILE
    state_dir = repo_root / DEFAULT_STATE_DIR
    config_path.parent.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        typer.echo(f"Config already exists: {config_path}", err=True)
        raise typer.Exit(code=1)

    settings = Settings()
    config_data = settings.model_dump(mode="json")
    config_path.write_text(yaml.safe_dump(config_data, sort_keys=False), encoding="utf-8")
    typer.echo(f"Wrote {config_path}")


@app.command()
def run(
    epic: Path = typer.Argument(..., help="Epic markdown file"),
    tui: bool = typer.Option(False, "--tui", help="Launch Textual UI"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate epic and exit"),
) -> None:
    """Run an epic workflow."""
    epic_path = epic.resolve()
    if not epic_path.is_file():
        raise typer.BadParameter(f"Epic file not found: {epic_path}")

    settings = config_module.get_settings()
    if dry_run:
        epic_info = EpicParser().parse(epic_path)
        typer.echo(f"Epic: {epic_info.title}")
        for ref in epic_info.story_refs:
            story_id, title = parse_story_ref(ref)
            typer.echo(f"- {story_id}: {title}")
        return

    repo_root = Path(".").resolve()
    if tui:
        app_tui = WorkflowApp(engine=None, epic_path=epic_path)
        engine = _build_engine(settings=settings, repo_root=repo_root, reporter=app_tui.reporter)
        app_tui.engine = engine
        app_tui.run()
        if app_tui.error:
            raise WorkflowError(str(app_tui.error))
        return

    reporter = HeadlessReporter()
    engine = _build_engine(settings=settings, repo_root=repo_root, reporter=reporter)
    asyncio.run(engine.run_epic(epic_path))


@app.command()
def resume(workflow_id: str = typer.Argument(..., help="Workflow id to resume")) -> None:
    """Resume a workflow by workflow id."""
    settings = config_module.get_settings()
    repo_root = Path(".").resolve()
    reporter = HeadlessReporter()
    engine = _build_engine(settings=settings, repo_root=repo_root, reporter=reporter)
    asyncio.run(engine.resume_workflow(workflow_id))


@app.command()
def status(repo_path: Path = typer.Argument(Path("."), help="Repository root path")) -> None:
    """Show workflow status from saved state files."""
    repo_root = repo_path.resolve()
    settings = config_module.get_settings()
    state_dir = repo_root / settings.state_dir
    manager = StateManager(state_dir=state_dir)
    states = manager.list_all()
    if not states:
        typer.echo("No workflows found.")
        return
    for state in states:
        status_line = (
            f"{state.workflow_id} | {state.status} | {state.current_phase} | "
            f"{state.current_story or '-'}"
        )
        typer.echo(status_line)


@app.command()
def list_epics(repo_path: Path = typer.Argument(Path("."), help="Repository root path")) -> None:
    """List available epic files that are not already in progress."""
    repo_root = repo_path.resolve()
    settings = config_module.get_settings()
    state_dir = repo_root / settings.state_dir
    state_manager = StateManager(state_dir=state_dir)
    discovery = EpicDiscovery(patterns=settings.discovery.epic_patterns, repo_root=repo_root)
    epics = discovery.discover(state_manager.list_all())
    if not epics:
        typer.echo("No epics found.")
        return
    for epic in epics:
        typer.echo(str(epic))


@app.command()
def config_validate(
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Config path"),
) -> None:
    """Validate configuration and required templates."""
    if config_path and not config_path.is_file():
        raise typer.BadParameter(f"Config file not found: {config_path}")
    settings = config_module.get_settings(config_path=config_path)
    _validate_agents(settings, Path(".").resolve())
    _validate_templates(Path(".").resolve())
    typer.echo("Configuration OK.")


@app.command()
def config_show(
    config_path: Path | None = typer.Option(None, "--config", "-c", help="Config path"),
) -> None:
    """Display effective configuration as JSON."""
    settings = config_module.get_settings(config_path=config_path)
    typer.echo(settings.model_dump_json(indent=2))


def _build_engine(
    *,
    settings: Settings,
    repo_root: Path,
    reporter: ProgressReporterProtocol | None,
) -> WorkflowEngine:
    agents = _build_agents(settings, repo_root)
    state_dir = repo_root / settings.state_dir
    state_manager = StateManager(state_dir=state_dir)
    git_config = GitConfig(**settings.git.model_dump())
    git_manager = GitManager(repo_path=repo_root, config=git_config)
    prompt_loader = PromptLoader(templates_dir=repo_root / DEFAULT_TEMPLATES_DIR)
    return WorkflowEngine(
        agents=agents,
        state_manager=state_manager,
        git_manager=git_manager,
        prompt_loader=prompt_loader,
        settings=settings,
        repo_root=repo_root,
        reporter=reporter,
    )


def _build_agents(settings: Settings, repo_root: Path) -> dict[str, AgentProtocol]:
    return {
        "scrum_master": _create_agent(settings.scrum_master, repo_root),
        "developer": _create_agent(settings.developer, repo_root),
        "reviewer": _create_agent(settings.reviewer, repo_root),
        "tech_writer": _create_agent(settings.tech_writer, repo_root),
    }


def _create_agent(agent_settings: AgentSettings, repo_root: Path) -> AgentProtocol:
    settings_path = agent_settings.settings_file
    if settings_path and not settings_path.is_absolute():
        settings_path = repo_root / settings_path
    config = AgentConfig(
        cli=agent_settings.cli,
        settings_file=settings_path,
        working_dir=repo_root,
        timeout=agent_settings.timeout,
        extra_args=list(agent_settings.extra_args),
    )
    return create_agent(config)


def _validate_agents(settings: Settings, repo_root: Path) -> None:
    try:
        _build_agents(settings, repo_root)
    except Exception as exc:  # pragma: no cover - surfaces user config issues
        raise ConfigurationError(str(exc)) from exc


def _validate_templates(repo_root: Path) -> None:
    prompt_loader = PromptLoader(templates_dir=repo_root / DEFAULT_TEMPLATES_DIR)
    required = [Phase.CREATE_STORY, Phase.DEVELOP, Phase.CODE_REVIEW]
    missing = [phase.value for phase in required if not prompt_loader.has_template(phase)]
    if missing:
        raise ConfigurationError(f"Missing templates: {', '.join(missing)}")
