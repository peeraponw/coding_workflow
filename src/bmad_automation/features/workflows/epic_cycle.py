"""Epic cycle workflow - main orchestrator."""

from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.function_tool import FunctionTool
from google.genai.types import Content, Part

from bmad_automation.core.config import BmadConfig, Settings, resolve_config_path
from bmad_automation.core.logging import get_logger
from bmad_automation.features.agents import (
    create_developer_impl_agent,
    create_developer_review_agent,
    create_scrum_master_agent,
    create_tech_writer_agent,
)
from bmad_automation.features.tools import (
    git_commit,
    git_create_branch,
    git_current_branch,
    parse_epic_file,
)
from bmad_automation.features.tools.cli_wrapper import run_coding_agent
from bmad_automation.features.workflows.dev_loop import create_dev_loop
from bmad_automation.features.workflows.story_loop import create_story_workflow
from bmad_automation.shared.consts import AGENT_DEVELOPER_IMPL
from bmad_automation.shared.exceptions import BmadError

logger = get_logger(__name__)


def _create_agent_tool(agent_name: str, config: BmadConfig) -> FunctionTool:
    """Create a FunctionTool that invokes the CLI with the agent's config."""
    agent_config = config.agents.get(agent_name)
    if not agent_config:
        raise BmadError(f"Agent '{agent_name}' not found in bmad.yaml")

    resolved_path = resolve_config_path(agent_config.config, config.project_root)

    def execute_task(task_description: str) -> str:
        """Execute a task using the configured coding agent."""
        return run_coding_agent(
            prompt=task_description,
            config_path=resolved_path,
            cwd=config.project_root,
        )

    return FunctionTool(execute_task)


async def run_epic_cycle(epic_path: Path, config: BmadConfig, settings: Settings) -> None:
    """Main entry point: Epic -> Stories -> PR."""
    # 1. Parse epic file
    epic = parse_epic_file(epic_path)
    logger.info("Parsed epic", extra={"epic_id": epic.id, "story_count": len(epic.stories)})

    # 2. Create feature branch
    if config.git.auto_branch:
        branch_name = f"{config.git.branch_prefix}{epic.id}"
        try:
            git_create_branch(branch_name, str(config.project_root))
        except BmadError:
            logger.warning("Branch may already exist, continuing...")
    else:
        branch_name = git_current_branch(str(config.project_root))

    # 3. Build tools for each agent using their respective configs
    impl_tool = _create_agent_tool(AGENT_DEVELOPER_IMPL, config)
    commit_tool = FunctionTool(git_commit)

    # 4. Build agent hierarchy
    # For now, we use the same model but different configs via tools
    # TODO: Extract model from config files if needed
    high_model = "gemini-2.0-flash"
    low_model = "gemini-1.5-flash"

    scrum_master = create_scrum_master_agent(high_model)
    developer_impl = create_developer_impl_agent(low_model, impl_tool, commit_tool)
    developer_review = create_developer_review_agent(high_model)
    tech_writer = create_tech_writer_agent(high_model)

    dev_loop = create_dev_loop(developer_impl, developer_review)
    story_workflow = create_story_workflow(scrum_master, dev_loop, tech_writer)

    # 5. Process each story
    session_service = InMemorySessionService()

    for story_outline in epic.stories:
        logger.info("Processing story", extra={"story_id": story_outline.id})

        session = await session_service.create_session(
            app_name="bmad_automation",
            user_id="system",
            state={"story_outline": story_outline.model_dump()},
        )

        runner = Runner(
            agent=story_workflow,
            app_name="bmad_automation",
            session_service=session_service,
        )

        message_content = Content(
            parts=[Part(text=f"Implement story: {story_outline.title}")],
            role="user",
        )

        async for event in runner.run_async(
            session_id=session.id,
            user_id="system",
            new_message=message_content,
        ):
            logger.debug("Event received", extra={"author": event.author})

        logger.info("Completed story", extra={"story_id": story_outline.id})

    # 6. Log completion (PR creation would need GitHub API integration)
    logger.info(
        "Epic cycle complete. Please create PR manually.",
        extra={"branch": branch_name, "epic": epic.title},
    )
