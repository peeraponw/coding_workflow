"""Shared fixtures for CLI tests."""

import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a CliRunner instance for testing CLI commands."""
    return CliRunner()
