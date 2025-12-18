"""Technical Writer agent (HIGH-tier)."""

from google.adk.agents import LlmAgent

from bmad_automation.shared.consts import AGENT_TECH_WRITER


def create_tech_writer_agent(model: str) -> LlmAgent:
    """Create a HIGH-tier technical writer agent."""
    return LlmAgent(
        name=AGENT_TECH_WRITER,
        model=model,
        instruction=(
            "You are a technical writer.\n"
            "Document the changes made in state['implementation_result'].\n"
            "Update README, add inline comments, and create/update ADRs as needed.\n\n"
            "Output JSON: {files_updated: [], summary: str}"
        ),
        output_key="documentation_result",
    )
