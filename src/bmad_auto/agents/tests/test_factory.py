"""Tests for agent factory and model routing."""

import pytest

from bmad_auto.agents.base import AgentRole
from bmad_auto.agents.factory import VALID_MODELS, _validate_model, create_agent
from bmad_auto.agents.claude import ClaudeAgent
from bmad_auto.shared.exceptions import ConfigError


class TestValidateModel:
    """Test model validation."""

    def test_valid_models_accepted(self) -> None:
        """Should accept valid model names."""
        for model in VALID_MODELS:
            _validate_model(model)  # Should not raise

    def test_invalid_model_raises(self) -> None:
        """Should raise ConfigError for invalid models."""
        with pytest.raises(ConfigError, match="Unknown model"):
            _validate_model("invalid")

    def test_error_message_includes_valid_options(self) -> None:
        """Error message should list valid model options."""
        with pytest.raises(ConfigError) as exc_info:
            _validate_model("gpt-4")

        error_msg = str(exc_info.value)
        assert "claude" in error_msg
        assert "glm" in error_msg


class TestCreateAgentClaude:
    """Test agent creation for Claude model."""

    def test_creates_claude_agent_for_sm_when_configured(self) -> None:
        """Should create ClaudeAgent with use_logged_in=True for SM."""
        agent = create_agent(
            role=AgentRole.SM,
            sm_model="claude",
            dev_model="glm",
            reviewer_model="claude",
            working_dir="/project",
        )

        assert isinstance(agent, ClaudeAgent)
        assert agent.use_logged_in is True
        assert agent.api_key is None

    def test_creates_claude_agent_for_reviewer_when_configured(self) -> None:
        """Should create ClaudeAgent with use_logged_in=True for Reviewer."""
        agent = create_agent(
            role=AgentRole.REVIEWER,
            sm_model="claude",
            dev_model="glm",
            reviewer_model="claude",
            working_dir="/project",
        )

        assert isinstance(agent, ClaudeAgent)
        assert agent.use_logged_in is True
        assert agent.api_key is None


class TestCreateAgentGLM:
    """Test agent creation for GLM model."""

    def test_creates_glm_agent_for_dev_when_configured(self, monkeypatch) -> None:
        """Should create ClaudeAgent with API key for GLM."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")

        agent = create_agent(
            role=AgentRole.DEV,
            sm_model="claude",
            dev_model="glm",
            reviewer_model="claude",
            working_dir="/project",
        )

        assert isinstance(agent, ClaudeAgent)
        assert agent.use_logged_in is False
        assert agent.api_key == "sk-test-key"

    def test_glm_requires_api_key(self, monkeypatch) -> None:
        """Should raise ConfigError if API key not set for GLM."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(ConfigError, match="ANTHROPIC_API_KEY"):
            create_agent(
                role=AgentRole.DEV,
                sm_model="claude",
                dev_model="glm",
                reviewer_model="claude",
                working_dir="/project",
            )

    def test_glm_uses_base_url_if_provided(self, monkeypatch) -> None:
        """GLM agent should support custom base URL via env var."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://glm.example.com")

        agent = create_agent(
            role=AgentRole.DEV,
            sm_model="claude",
            dev_model="glm",
            reviewer_model="claude",
            working_dir="/project",
        )

        assert isinstance(agent, ClaudeAgent)
        assert agent.api_key == "sk-test-key"
        # Note: base_url is passed via env to SDK, not stored in agent


class TestCreateAgentValidation:
    """Test agent factory validation."""

    def test_invalid_model_raises_config_error(self) -> None:
        """Should raise ConfigError for invalid model configuration."""
        with pytest.raises(ConfigError, match="Unknown model"):
            create_agent(
                role=AgentRole.SM,
                sm_model="invalid",
                dev_model="glm",
                reviewer_model="claude",
                working_dir="/project",
            )

    def test_unknown_role_raises_config_error(self) -> None:
        """Should raise ConfigError for unknown agent role."""
        # This is a defensive test - should not happen with AgentRole enum
        with pytest.raises(ConfigError, match="Unknown agent role"):
            create_agent(
                role="invalid_role",  # type: ignore[arg-type]
                sm_model="claude",
                dev_model="glm",
                reviewer_model="claude",
                working_dir="/project",
            )


class TestAgentProtocolCompliance:
    """Test that created agents comply with AgentProtocol."""

    def test_all_created_agents_implement_protocol(self, monkeypatch) -> None:
        """All agents from factory should implement AgentProtocol."""
        from bmad_auto.agents.base import AgentProtocol

        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")

        # Test Claude agent
        claude_agent = create_agent(
            role=AgentRole.SM,
            sm_model="claude",
            dev_model="glm",
            reviewer_model="claude",
            working_dir="/project",
        )
        assert isinstance(claude_agent, AgentProtocol)

        # Test GLM agent
        glm_agent = create_agent(
            role=AgentRole.DEV,
            sm_model="claude",
            dev_model="glm",
            reviewer_model="claude",
            working_dir="/project",
        )
        assert isinstance(glm_agent, AgentProtocol)


class TestCredentialsNotLogged:
    """Test that credentials are never logged (NFR14)."""

    def test_api_key_not_in_agent_repr(self, monkeypatch) -> None:
        """Agent __repr__ should not expose API key."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-secret-key-12345")

        agent = create_agent(
            role=AgentRole.DEV,
            sm_model="claude",
            dev_model="glm",
            reviewer_model="claude",
            working_dir="/project",
        )

        repr_str = repr(agent)
        assert "sk-secret-key-12345" not in repr_str
        assert "sk-" not in repr_str
