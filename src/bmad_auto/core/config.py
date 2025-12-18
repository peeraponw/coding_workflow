"""Configuration management using pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from bmad_auto.shared.consts import (
    DEFAULT_AGENT_TIMEOUT,
    DEFAULT_CONFIG_FILE,
    DEFAULT_EPIC_PATTERNS,
    DEFAULT_STATE_DIR,
    DEFAULT_STORY_OUTPUT_DIR,
    GIT_BRANCH_PREFIX,
    GIT_COMMIT_PREFIX,
    MAX_DEV_ATTEMPTS,
    USER_CONFIG_DIR,
)


def _load_yaml_files(paths: Iterable[Path]) -> dict[str, Any]:
    """Load the first existing YAML file from the provided paths."""
    for path in paths:
        if path.is_file():
            with path.open("r", encoding="utf-8") as handle:
                return yaml.safe_load(handle) or {}
    return {}


class AgentSettings(BaseModel):
    """Settings for an individual agent role."""

    cli: str = Field(description="CLI tool name, e.g. claude or codex")
    settings_file: Path | None = Field(default=None, description="Path to CLI settings file")
    timeout: int = Field(default=DEFAULT_AGENT_TIMEOUT, description="Timeout in seconds")
    extra_args: list[str] = Field(default_factory=list, description="Extra CLI args")


class GitSettings(BaseModel):
    """Git operation configuration."""

    branch_prefix: str = Field(default=GIT_BRANCH_PREFIX)
    commit_prefix: str = Field(default=GIT_COMMIT_PREFIX)
    auto_push: bool = Field(default=False)
    create_pr: bool = Field(default=True)
    pr_draft: bool = Field(default=True)


class WorkflowSettings(BaseModel):
    """Workflow behavior toggles."""

    max_dev_attempts: int = Field(default=MAX_DEV_ATTEMPTS)
    pause_between_stories: bool = Field(default=False)
    pause_before_pr: bool = Field(default=True)


class DiscoverySettings(BaseModel):
    """Discovery patterns for epics and stories."""

    epic_patterns: tuple[str, ...] = Field(default=DEFAULT_EPIC_PATTERNS)
    story_output_dir: str = Field(default=DEFAULT_STORY_OUTPUT_DIR)


class Settings(BaseSettings):
    """Root application settings."""

    scrum_master: AgentSettings = Field(
        default_factory=lambda: AgentSettings(cli="claude"),
    )
    developer: AgentSettings = Field(
        default_factory=lambda: AgentSettings(cli="codex"),
    )
    reviewer: AgentSettings = Field(
        default_factory=lambda: AgentSettings(cli="claude"),
    )
    tech_writer: AgentSettings = Field(
        default_factory=lambda: AgentSettings(cli="claude"),
    )

    git: GitSettings = Field(default_factory=GitSettings)
    workflow: WorkflowSettings = Field(default_factory=WorkflowSettings)
    discovery: DiscoverySettings = Field(default_factory=DiscoverySettings)

    state_dir: str = Field(default=DEFAULT_STATE_DIR)
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_prefix="BMAD_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        user_config = Path(USER_CONFIG_DIR).expanduser() / "config.yaml"
        repo_config = Path(DEFAULT_CONFIG_FILE)

        def yaml_source() -> Dict[str, Any]:
            search_paths: list[Path] = []
            if _CONFIG_PATH_OVERRIDE:
                search_paths.append(_CONFIG_PATH_OVERRIDE)
            search_paths.extend([repo_config, user_config])
            return _load_yaml_files(search_paths)

        return (
            init_settings,
            env_settings,
            yaml_source,
            dotenv_settings,
            file_secret_settings,
        )


_CONFIG_PATH_OVERRIDE: Path | None = None


@lru_cache
def get_settings(config_path: Path | None = None) -> Settings:
    """Load settings with caching; highest priority is the explicit config path."""
    global _CONFIG_PATH_OVERRIDE
    _CONFIG_PATH_OVERRIDE = config_path
    return Settings()
