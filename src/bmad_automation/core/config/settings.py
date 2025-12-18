"""Centralized settings via pydantic_settings and bmad.yaml config."""

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings

from bmad_automation.shared.exceptions import BmadError


class ConfigNotFoundError(BmadError):
    """Raised when a configuration file cannot be found."""


class AgentConfig(BaseModel):
    """Configuration for a single agent."""

    config: Path


class GitConfig(BaseModel):
    """Git-related configuration."""

    auto_branch: bool = True
    branch_prefix: str = "feature/"


class BmadConfig(BaseModel):
    """BMAD configuration loaded from bmad.yaml."""

    agents: dict[str, AgentConfig]
    project_root: Path = Path(".")
    git: GitConfig = GitConfig()

    @field_validator("project_root", mode="before")
    @classmethod
    def expand_project_root(cls, v: str | Path) -> Path:
        """Expand ~ in project root path."""
        return Path(v).expanduser()


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    log_level: str = "INFO"

    model_config = {
        "env_prefix": "BMAD_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


def resolve_config_path(config_path: Path, project_root: Path) -> Path:
    """
    Resolve config path with fallback logic.

    Resolution order:
    1. Absolute path (including ~/...) - use as-is
    2. Relative to project_root - if exists
    3. Relative to home directory - fallback
    """
    # Expand ~ first
    expanded = config_path.expanduser()

    # If it's now absolute and exists, use it
    if expanded.is_absolute():
        if expanded.exists():
            return expanded
        raise ConfigNotFoundError(f"Config file not found: {expanded}")

    # Try relative to project root first
    project_path = project_root / config_path
    if project_path.exists():
        return project_path.resolve()

    # Fallback to home directory
    home_path = Path.home() / config_path
    if home_path.exists():
        return home_path.resolve()

    raise ConfigNotFoundError(f"Config file not found. Tried:\n  - {project_path}\n  - {home_path}")


def load_bmad_config(config_path: Path = Path("bmad.yaml")) -> BmadConfig:
    """Load BMAD configuration from yaml file."""
    if not config_path.exists():
        raise ConfigNotFoundError(f"bmad.yaml not found: {config_path}")

    with open(config_path) as f:
        data = yaml.safe_load(f)

    return BmadConfig(**data)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
