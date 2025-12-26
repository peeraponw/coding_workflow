"""Configuration loading for bmad-auto.

Three-layer configuration with NO overlap:
- Internal: pydantic_settings (timeouts, retries)
- User: .bmad-auto.yaml (epic path, models, git)
- Secrets: .env (API keys)
"""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

from bmad_auto.shared.exceptions import ConfigError


# Internal Settings (pydantic_settings)
class InternalSettings(BaseSettings):
    """Internal settings with defaults (timeouts, retries).

    These are pre-distribution settings that can be overridden via env vars.
    """

    default_timeout: int = 600
    max_retries: int = 3

    model_config = SettingsConfigDict(
        env_prefix="BMAD_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# User Config (YAML)
@dataclass(frozen=True)
class WorkflowConfig:
    """Workflow configuration from .bmad-auto.yaml."""

    epic_path: str
    state_file: str


@dataclass(frozen=True)
class AgentsConfig:
    """Agent model configuration from .bmad-auto.yaml."""

    sm_model: str
    dev_model: str
    reviewer_model: str


@dataclass(frozen=True)
class GitConfig:
    """Git integration configuration from .bmad-auto.yaml."""

    auto_branch: bool
    auto_commit: bool
    branch_prefix: str


@dataclass(frozen=True)
class UserConfig:
    """Complete user configuration from .bmad-auto.yaml."""

    workflow: WorkflowConfig
    agents: AgentsConfig
    git: GitConfig


# Credentials (Environment Variables)
@dataclass(frozen=True)
class Credentials:
    """API credentials from environment variables.

    CRITICAL: These are never written to any config or state files.
    """

    api_key: str
    base_url: str | None = None


def load_user_config(config_path: str) -> UserConfig:
    """Load and validate user configuration from .bmad-auto.yaml.

    Args:
        config_path: Path to .bmad-auto.yaml file.

    Returns:
        UserConfig with validated data.

    Raises:
        ConfigError: If file missing, invalid YAML, or missing required fields.
    """
    path = Path(config_path)

    # Check file exists
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    # Load YAML content
    try:
        content = path.read_text()
    except OSError as e:
        raise ConfigError(f"Cannot read configuration file: {e}") from e

    # Parse YAML
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML syntax in {config_path}: {e}") from e

    if not isinstance(data, dict):
        raise ConfigError(f"Configuration must be a dictionary, got {type(data).__name__}")

    # Validate required sections
    required_sections = ["workflow", "agents", "git"]
    missing_sections = [s for s in required_sections if s not in data]
    if missing_sections:
        raise ConfigError(f"Missing required fields: {', '.join(missing_sections)}")

    # Parse workflow section
    workflow_data = data["workflow"]
    if not isinstance(workflow_data, dict):
        raise ConfigError("'workflow' must be a dictionary")

    workflow_required = ["epic_path", "state_file"]
    workflow_missing = [f for f in workflow_required if f not in workflow_data]
    if workflow_missing:
        raise ConfigError(f"Missing required workflow fields: {', '.join(workflow_missing)}")

    workflow = WorkflowConfig(
        epic_path=str(workflow_data["epic_path"]),
        state_file=str(workflow_data["state_file"]),
    )

    # Parse agents section
    agents_data = data["agents"]
    if not isinstance(agents_data, dict):
        raise ConfigError("'agents' must be a dictionary")

    agents_required = ["sm_model", "dev_model", "reviewer_model"]
    agents_missing = [f for f in agents_required if f not in agents_data]
    if agents_missing:
        raise ConfigError(f"Missing required agent fields: {', '.join(agents_missing)}")

    agents = AgentsConfig(
        sm_model=str(agents_data["sm_model"]),
        dev_model=str(agents_data["dev_model"]),
        reviewer_model=str(agents_data["reviewer_model"]),
    )

    # Parse git section
    git_data = data["git"]
    if not isinstance(git_data, dict):
        raise ConfigError("'git' must be a dictionary")

    git_required = ["auto_branch", "auto_commit", "branch_prefix"]
    git_missing = [f for f in git_required if f not in git_data]
    if git_missing:
        raise ConfigError(f"Missing required git fields: {', '.join(git_missing)}")

    git = GitConfig(
        auto_branch=bool(git_data["auto_branch"]),
        auto_commit=bool(git_data["auto_commit"]),
        branch_prefix=str(git_data["branch_prefix"]),
    )

    return UserConfig(workflow=workflow, agents=agents, git=git)


def requires_glm_credentials(config: UserConfig) -> bool:
    """Check if any agent configuration requires GLM credentials.

    GLM credentials (ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL) are required when
    any agent uses a glm-* model pattern.

    Args:
        config: UserConfig to check.

    Returns:
        True if any agent uses glm-* model, False otherwise.
    """
    glm_models = {config.agents.sm_model, config.agents.dev_model, config.agents.reviewer_model}
    return any(model.startswith("glm-") for model in glm_models)


def get_credentials() -> Credentials:
    """Load API credentials from environment variables.

    Returns:
        Credentials with API key and optional base URL.

    Raises:
        ConfigError: If ANTHROPIC_API_KEY is not set.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ConfigError("ANTHROPIC_API_KEY environment variable is required")

    base_url = os.getenv("ANTHROPIC_BASE_URL")

    return Credentials(api_key=api_key, base_url=base_url)
