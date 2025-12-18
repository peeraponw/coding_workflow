"""Scrum Master agent for story creation and validation."""

from google.adk.agents import LlmAgent

from bmad_automation.shared.consts import AGENT_SCRUM_MASTER


def create_scrum_master_agent(model: str) -> LlmAgent:
    """Create a HIGH-tier Scrum Master agent."""
    return LlmAgent(
        name=AGENT_SCRUM_MASTER,
        model=model,
        instruction=(
            "You are an agile Scrum Master. Your responsibilities:\n"
            "1. Read epic files and extract stories\n"
            "2. Write detailed story files with acceptance criteria\n"
            "3. Validate story readiness\n\n"
            "Output JSON: {story_id, title, description, acceptance_criteria[], ready}"
        ),
        output_key="current_story",
    )
