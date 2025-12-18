"""Tests for settings and config loading."""

from pathlib import Path

import pytest

from bmad_automation.core.config.settings import (
    ConfigNotFoundError,
    Settings,
    load_bmad_config,
    resolve_config_path,
)


def test_settings_default_values() -> None:
    """Test that settings have expected defaults."""
    settings = Settings()
    assert settings.log_level == "INFO"


def test_bmad_config_loads_from_yaml(tmp_path: Path) -> None:
    """Test loading BmadConfig from yaml file."""
    config_file = tmp_path / "bmad.yaml"
    config_file.write_text("""
agents:
  developer_impl:
    config: ~/.codex/low.toml
  scrum_master:
    config: ~/.codex/high.toml
project_root: .
""")

    config = load_bmad_config(config_file)
    assert "developer_impl" in config.agents
    assert config.agents["developer_impl"].config == Path("~/.codex/low.toml")


def test_bmad_config_missing_file_raises(tmp_path: Path) -> None:
    """Test that missing bmad.yaml raises error."""
    with pytest.raises(ConfigNotFoundError, match="not found"):
        load_bmad_config(tmp_path / "missing.yaml")


def test_resolve_config_path_absolute(tmp_path: Path) -> None:
    """Test resolving absolute path."""
    config_file = tmp_path / "config.toml"
    config_file.write_text("model = 'test'")

    resolved = resolve_config_path(config_file, tmp_path)
    assert resolved == config_file


def test_resolve_config_path_relative_to_project(tmp_path: Path) -> None:
    """Test resolving relative path - project first."""
    config_file = tmp_path / "configs" / "low.toml"
    config_file.parent.mkdir()
    config_file.write_text("model = 'test'")

    resolved = resolve_config_path(Path("configs/low.toml"), tmp_path)
    assert resolved == config_file.resolve()


def test_resolve_config_path_not_found_raises(tmp_path: Path) -> None:
    """Test that missing config raises error."""
    with pytest.raises(ConfigNotFoundError, match="not found"):
        resolve_config_path(Path("nonexistent.toml"), tmp_path)
