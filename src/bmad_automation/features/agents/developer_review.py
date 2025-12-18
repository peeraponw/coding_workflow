"""Developer review agent (HIGH-tier)."""

from google.adk.agents import LlmAgent

from bmad_automation.shared.consts import AGENT_DEVELOPER_REVIEW


def create_developer_review_agent(model: str) -> LlmAgent:
    """Create a HIGH-tier developer review agent."""
    return LlmAgent(
        name=AGENT_DEVELOPER_REVIEW,
        model=model,
        instruction=(
            "You are a senior code reviewer.\n"
            "Review the implementation in state['implementation_result'].\n"
            "Check against acceptance criteria in state['current_story'].\n\n"
            "Output JSON: {status: 'pass'|'fail', feedback: str, issues: []}"
        ),
        output_key="review_result",
    )
