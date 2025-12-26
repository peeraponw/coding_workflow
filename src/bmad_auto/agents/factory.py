"""Agent factory for creating agents with model routing.

Factory function that creates appropriate agent instances based on
configuration (Claude vs GLM model routing).
"""

from bmad_auto.agents.base import AgentProtocol, AgentRole
from bmad_auto.agents.claude import ClaudeAgent
from bmad_auto.core.config import get_credentials
from bmad_auto.shared.exceptions import ConfigError

# Valid model names
VALID_MODELS = {"claude", "glm"}


def _validate_model(model: str) -> None:
    """Validate model name is supported.

    Args:
        model: Model name to validate

    Raises:
        ConfigError: If model name is not supported
    """
    if model not in VALID_MODELS:
        raise ConfigError(
            f"Unknown model '{model}'. Valid options: {', '.join(sorted(VALID_MODELS))}"
        )


def create_agent(
    role: AgentRole,
    sm_model: str,
    dev_model: str,
    reviewer_model: str,
    working_dir: str,
) -> AgentProtocol:
    """Create agent with appropriate model routing based on role.

    Args:
        role: Agent role (SM, DEV, or REVIEWER)
        sm_model: Model name for SM agent
        dev_model: Model name for Dev agent
        reviewer_model: Model name for Reviewer agent
        working_dir: Working directory for agent execution

    Returns:
        AgentProtocol instance configured for the specified model

    Raises:
        ConfigError: If model name is invalid or GLM credentials missing

    Example:
        >>> agent = create_agent(
        ...     AgentRole.DEV,
        ...     sm_model="claude",
        ...     dev_model="glm",
        ...     reviewer_model="claude",
        ...     working_dir="/project"
        ... )
        >>> isinstance(agent, ClaudeAgent)
        True
    """
    # Select model config based on role
    model_map = {
        AgentRole.SM: sm_model,
        AgentRole.DEV: dev_model,
        AgentRole.REVIEWER: reviewer_model,
    }

    model_name = model_map.get(role)
    if model_name is None:
        raise ConfigError(f"Unknown agent role: {role}")

    # Validate model name
    _validate_model(model_name)

    # Create agent based on model type
    if model_name == "claude":
        # Claude uses logged-in Claude Code desktop credentials
        return ClaudeAgent(working_dir=working_dir, use_logged_in=True)

    elif model_name == "glm":
        # GLM uses API key and base URL from environment
        credentials = get_credentials()
        return ClaudeAgent(
            working_dir=working_dir,
            use_logged_in=False,
            api_key=credentials.api_key,
        )

    else:
        # This should not happen due to validation above
        raise ConfigError(f"Unhandled model type: {model_name}")
