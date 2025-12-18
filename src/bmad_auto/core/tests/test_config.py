from pathlib import Path

import pytest

from bmad_auto.core.config import Settings, get_settings


def teardown_function() -> None:
    get_settings.cache_clear()


def test_defaults_present() -> None:
    settings = get_settings()
    assert settings.scrum_master.cli == "claude"
    assert settings.developer.cli == "codex"
    assert settings.workflow.max_dev_attempts == 3
    assert settings.discovery.story_output_dir == "docs/stories"


def test_yaml_override(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
log_level: DEBUG
scrum_master:
  cli: claude
  timeout: 120
developer:
  cli: codex
  timeout: 300
reviewer:
  cli: claude
  timeout: 90
tech_writer:
  cli: claude
  timeout: 180
workflow:
  max_dev_attempts: 5
        """.strip(),
        encoding="utf-8",
    )

    settings = get_settings(config_path=config_path)
    assert settings.log_level == "DEBUG"
    assert settings.scrum_master.timeout == 120
    assert settings.workflow.max_dev_attempts == 5

    # Ensure cache returns same instance when called again without clearing
    again = get_settings(config_path=config_path)
    assert settings is again
