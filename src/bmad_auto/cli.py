"""Typer CLI definitions for bmad-auto."""

from pathlib import Path

import typer

from bmad_auto.core import config as config_module
from bmad_auto.core.logging import configure_logging

app = typer.Typer(add_completion=False, help="Automate BMAD workflows.")


@app.callback()
def _startup(verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logs")) -> None:
    """Configure logging and preload settings."""
    configure_logging(debug=verbose)
    config_module.get_settings()


@app.command()
def version() -> None:
    """Show the current version."""
    from bmad_auto import __version__

    typer.echo(__version__)


@app.command()
def config_show(config_path: Path | None = typer.Option(None, "--config", "-c", help="Config path")) -> None:
    """Display effective configuration as JSON."""
    settings = config_module.get_settings(config_path=config_path)
    typer.echo(settings.model_dump_json(indent=2))
