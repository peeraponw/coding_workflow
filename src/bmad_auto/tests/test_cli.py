from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from bmad_auto.cli import app
from bmad_auto.core.config import get_settings


def teardown_function() -> None:
    get_settings.cache_clear()


def test_run_dry_run_lists_stories(tmp_path: Path) -> None:
    epic = tmp_path / "epic-001.md"
    epic.write_text(
        "# Epic 001\n\n## Stories\n- STORY-001: Login flow\n",
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(app, ["run", str(epic), "--dry-run"])

    assert result.exit_code == 0
    assert "STORY-001" in result.output
