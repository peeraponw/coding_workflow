"""Story loop workflow using SequentialAgent."""

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent


def create_story_workflow(
    scrum_master: LlmAgent,
    dev_loop: LoopAgent,
    tech_writer: LlmAgent,
) -> SequentialAgent:
    """Create a story workflow: plan -> develop -> document."""
    return SequentialAgent(
        name="StoryWorkflow",
        sub_agents=[
            scrum_master,
            dev_loop,
            tech_writer,
        ],
    )
