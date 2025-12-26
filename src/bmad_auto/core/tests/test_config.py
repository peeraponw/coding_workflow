"""Tests for bmad_auto configuration loading.

Follows TDD: tests written before implementation.
"""

from typing import Any

import pytest

from bmad_auto.shared.exceptions import ConfigError


class TestInternalSettings:
    """Tests for InternalSettings (pydantic_settings defaults)."""

    def test_default_timeout(self) -> None:
        """InternalSettings should have default_timeout of 600."""
        # Arrange & Act
        from bmad_auto.core.config import InternalSettings

        settings = InternalSettings()

        # Assert
        assert settings.default_timeout == 600

    def test_default_max_retries(self) -> None:
        """InternalSettings should have max_retries of 3."""
        # Arrange & Act
        from bmad_auto.core.config import InternalSettings

        settings = InternalSettings()

        # Assert
        assert settings.max_retries == 3

    def test_custom_timeout_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """InternalSettings should load custom timeout from env."""
        # Arrange
        monkeypatch.setenv("BMAD_DEFAULT_TIMEOUT", "900")

        # Act
        from bmad_auto.core.config import InternalSettings

        settings = InternalSettings()

        # Assert
        assert settings.default_timeout == 900

    def test_custom_max_retries_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """InternalSettings should load custom max_retries from env."""
        # Arrange
        monkeypatch.setenv("BMAD_MAX_RETRIES", "5")

        # Act
        from bmad_auto.core.config import InternalSettings

        settings = InternalSettings()

        # Assert
        assert settings.max_retries == 5


class TestUserConfig:
    """Tests for UserConfig dataclass."""

    def test_valid_config(self, tmp_path: Any) -> None:
        """UserConfig should load valid .bmad-auto.yaml."""
        # Arrange
        config_content = """
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"
agents:
  sm_model: "opus-4.5"
  dev_model: "glm-4.7"
  reviewer_model: "sonnet-4.5"
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
"""
        config_file = tmp_path / ".bmad-auto.yaml"
        config_file.write_text(config_content)

        # Act
        from bmad_auto.core.config import load_user_config

        config = load_user_config(str(config_file))

        # Assert
        assert config.workflow.epic_path == "docs/epics"
        assert config.workflow.state_file == ".bmad-auto-state.yaml"
        assert config.agents.sm_model == "opus-4.5"
        assert config.agents.dev_model == "glm-4.7"
        assert config.agents.reviewer_model == "sonnet-4.5"
        assert config.git.auto_branch is True
        assert config.git.auto_commit is True
        assert config.git.branch_prefix == "epic/"

    def test_missing_config_file(self, tmp_path: Any) -> None:
        """load_user_config should raise ConfigError if file missing."""
        # Arrange
        missing_file = tmp_path / ".bmad-auto.yaml"

        # Act & Assert
        from bmad_auto.core.config import load_user_config

        with pytest.raises(ConfigError, match="Configuration file not found"):
            load_user_config(str(missing_file))

    def test_invalid_yaml_syntax(self, tmp_path: Any) -> None:
        """load_user_config should raise ConfigError if YAML is malformed."""
        # Arrange
        config_file = tmp_path / ".bmad-auto.yaml"
        config_file.write_text("workflow:\n  epic_path: [unclosed")

        # Act & Assert
        from bmad_auto.core.config import load_user_config

        with pytest.raises(ConfigError, match="Invalid YAML syntax"):
            load_user_config(str(config_file))

    def test_missing_required_fields(self, tmp_path: Any) -> None:
        """load_user_config should raise ConfigError if required fields missing."""
        # Arrange
        config_content = """
workflow:
  epic_path: "docs/epics"
# Missing state_file, agents, git sections
"""
        config_file = tmp_path / ".bmad-auto.yaml"
        config_file.write_text(config_content)

        # Act & Assert
        from bmad_auto.core.config import load_user_config

        with pytest.raises(ConfigError, match="Missing required fields"):
            load_user_config(str(config_file))

    def test_workflow_not_dict_raises_config_error(self, tmp_path: Any) -> None:
        """load_user_config should raise ConfigError if workflow is not a dict."""
        # Arrange
        config_content = """
workflow: "not-a-dict"
agents:
  sm_model: "opus-4.5"
  dev_model: "glm-4.7"
  reviewer_model: "sonnet-4.5"
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
"""
        config_file = tmp_path / ".bmad-auto.yaml"
        config_file.write_text(config_content)

        # Act & Assert
        from bmad_auto.core.config import load_user_config

        with pytest.raises(ConfigError, match="'workflow' must be a dictionary"):
            load_user_config(str(config_file))

    def test_agents_not_dict_raises_config_error(self, tmp_path: Any) -> None:
        """load_user_config should raise ConfigError if agents is not a dict."""
        # Arrange
        config_content = """
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"
agents: "not-a-dict"
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
"""
        config_file = tmp_path / ".bmad-auto.yaml"
        config_file.write_text(config_content)

        # Act & Assert
        from bmad_auto.core.config import load_user_config

        with pytest.raises(ConfigError, match="'agents' must be a dictionary"):
            load_user_config(str(config_file))

    def test_git_not_dict_raises_config_error(self, tmp_path: Any) -> None:
        """load_user_config should raise ConfigError if git is not a dict."""
        # Arrange
        config_content = """
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"
agents:
  sm_model: "opus-4.5"
  dev_model: "glm-4.7"
  reviewer_model: "sonnet-4.5"
git: "not-a-dict"
"""
        config_file = tmp_path / ".bmad-auto.yaml"
        config_file.write_text(config_content)

        # Act & Assert
        from bmad_auto.core.config import load_user_config

        with pytest.raises(ConfigError, match="'git' must be a dictionary"):
            load_user_config(str(config_file))


class TestEnvironmentVariableLoading:
    """Tests for environment variable loading (credentials)."""

    def test_load_anthropic_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should load ANTHROPIC_API_KEY from environment."""
        # Arrange
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key-12345")

        # Act
        from bmad_auto.core.config import get_credentials

        creds = get_credentials()

        # Assert
        assert creds.api_key == "sk-test-key-12345"

    def test_load_anthropic_base_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should load ANTHROPIC_BASE_URL from environment."""
        # Arrange
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

        # Act
        from bmad_auto.core.config import get_credentials

        creds = get_credentials()

        # Assert
        assert creds.base_url == "https://api.anthropic.com"

    def test_credentials_never_written_to_files(self, tmp_path: Any) -> None:
        """Credentials should never appear in config files."""
        # Arrange
        config_content = """
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"
agents:
  sm_model: "opus-4.5"
  dev_model: "glm-4.7"
  reviewer_model: "sonnet-4.5"
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
"""
        config_file = tmp_path / ".bmad-auto.yaml"
        config_file.write_text(config_content)

        # Act
        config_text = config_file.read_text()

        # Assert - API keys should never be in YAML
        assert "sk-" not in config_text
        assert "ANTHROPIC_API_KEY" not in config_text
        assert "api_key" not in config_text

    def test_get_credentials_raises_config_error_when_api_key_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_credentials should raise ConfigError when ANTHROPIC_API_KEY not set."""
        # Arrange
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        # Act & Assert
        from bmad_auto.core.config import get_credentials

        with pytest.raises(ConfigError, match="ANTHROPIC_API_KEY environment variable is required"):
            get_credentials()

    def test_credentials_not_required_when_no_glm_model(self, tmp_path: Any) -> None:
        """get_credentials should NOT be required when no agent uses glm-* model."""
        # Arrange - config uses only Anthropic models
        config_content = """
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"
agents:
  sm_model: "opus-4.5"
  dev_model: "sonnet-4.5"
  reviewer_model: "haiku-3.5"
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
"""
        config_file = tmp_path / ".bmad-auto.yaml"
        config_file.write_text(config_content)

        # Act
        from bmad_auto.core.config import load_user_config, requires_glm_credentials

        config = load_user_config(str(config_file))

        # Assert
        assert requires_glm_credentials(config) is False

    def test_credentials_required_when_any_agent_uses_glm(self, tmp_path: Any) -> None:
        """get_credentials should be required when any agent uses glm-* model."""
        # Arrange - config uses one GLM model
        config_content = """
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"
agents:
  sm_model: "opus-4.5"
  dev_model: "glm-4.7"
  reviewer_model: "sonnet-4.5"
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
"""
        config_file = tmp_path / ".bmad-auto.yaml"
        config_file.write_text(config_content)

        # Act
        from bmad_auto.core.config import load_user_config, requires_glm_credentials

        config = load_user_config(str(config_file))

        # Assert
        assert requires_glm_credentials(config) is True

    def test_requires_glm_credentials_detects_all_glm_patterns(
        self, tmp_path: Any
    ) -> None:
        """requires_glm_credentials should detect any glm-* pattern."""
        # Arrange
        from bmad_auto.core.config import load_user_config, requires_glm_credentials

        test_cases = [
            ("glm-4.7", True),
            ("glm-4.5", True),
            ("glm-latest", True),
            ("opus-4.5", False),
            ("sonnet-4.5", False),
            ("haiku-3.5", False),
        ]

        for model_name, expected_result in test_cases:
            config_content = f"""
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"
agents:
  sm_model: "{model_name}"
  dev_model: "opus-4.5"
  reviewer_model: "sonnet-4.5"
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
"""
            config_file = tmp_path / ".bmad-auto.yaml"
            config_file.write_text(config_content)

            config = load_user_config(str(config_file))

            # Assert
            assert (
                requires_glm_credentials(config) == expected_result
            ), f"Model {model_name} should result in {expected_result}"
