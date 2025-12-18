"""Developer implementation agent (LOW-tier)."""

from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool

from bmad_automation.shared.consts import AGENT_DEVELOPER_IMPL


def create_developer_impl_agent(
    model: str,
    implement_tool: FunctionTool,
    commit_tool: FunctionTool,
) -> LlmAgent:
    """Create a LOW-tier developer implementation agent."""
    return LlmAgent(
        name=AGENT_DEVELOPER_IMPL,
        model=model,
        instruction=(
            "You are a developer implementing a story.\n"
            "Read the story from state['current_story'].\n"
            "Use implement_story tool for implementation.\n"
            "Use git_commit tool for incremental commits.\n"
            "Focus on execution, follow the plan exactly."
        ),
        tools=[implement_tool, commit_tool],
        output_key="implementation_result",
    )
