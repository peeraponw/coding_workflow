"""bmad-auto CLI entry point."""

from bmad_auto.cli import app


def main() -> None:
    """Invoke the Typer application."""
    app()


if __name__ == "__main__":
    main()
