"""Workflow execution engine."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


from bmad_auto.core.config import Settings
from bmad_auto.core.exceptions import ReviewRejectedError, StoryCreationError, WorkflowError
from bmad_auto.core.protocols import (
    AgentProtocol,
    GitManagerProtocol,
    ProgressReporterProtocol,
    StateManagerProtocol,
)
from bmad_auto.features.discovery.epic_parser import EpicParser
from bmad_auto.features.discovery.models import EpicInfo
from bmad_auto.features.discovery.story_parser import StoryParser
from bmad_auto.features.orchestrator.phases import Phase
from bmad_auto.features.orchestrator.prompts import PromptLoader
from bmad_auto.features.agents.models import AgentResult
from bmad_auto.features.state.models import WorkflowState
from bmad_auto.shared.consts import (
    MARKER_REVIEW_APPROVED,
    MARKER_REVIEW_REJECTED,
    ROLE_DEVELOPER,
    ROLE_REVIEWER,
    ROLE_SCRUM_MASTER,
    ROLE_TECH_WRITER,
    STORY_ID_PATTERN,
)



class NullProgressReporter:
    """No-op progress reporter used when no UI is attached."""

    def on_phase_start(self, phase: str, story_id: str | None) -> None:
        return None

    def on_agent_start(self, role: str) -> None:
        return None

    def on_complete(self, success: bool) -> None:
        return None


class WorkflowEngine:
    """Coordinate an epic workflow using configured agents and managers."""

    def __init__(
        self,
        *,
        agents: Mapping[str, AgentProtocol],
        state_manager: StateManagerProtocol,
        git_manager: GitManagerProtocol,
        prompt_loader: PromptLoader,
        settings: Settings,
        repo_root: Path | None = None,
        reporter: ProgressReporterProtocol | None = None,
    ) -> None:
        self._agents = agents
        self._state_manager = state_manager
        self._git_manager = git_manager
        self._prompt_loader = prompt_loader
        self._settings = settings
        self._repo_root = Path(repo_root or ".")
        self._reporter = reporter or NullProgressReporter()

    async def run_epic(self, epic_path: Path) -> WorkflowState:
        epic = EpicParser().parse(epic_path)
        state = self._init_state(epic)
        self._create_branch(state, epic)
        deps = StoryDeps(
            agents=self._agents,
            state_manager=self._state_manager,
            git_manager=self._git_manager,
            prompt_loader=self._prompt_loader,
            settings=self._settings,
            repo_root=self._repo_root,
            reporter=self._reporter,
        )
        runner = StoryRunner(deps)
        try:
            for story_ref in epic.story_refs:
                await runner.run_story(epic, state, story_ref)
            await run_retrospective(deps, epic, state)
            await run_documentation(deps, epic, state)
            await maybe_create_pr(deps, epic, state)
            state.status = "completed"
            self._state_manager.save(state)
            self._reporter.on_complete(True)
        except Exception as exc:
            state.status = "failed"
            state.error = str(exc)
            self._state_manager.save(state)
            self._reporter.on_complete(False)
            raise
        return state

    def _init_state(self, epic: EpicInfo) -> WorkflowState:
        workflow_id = f"{epic.id}-{uuid.uuid4().hex[:8]}"
        state = WorkflowState(
            workflow_id=workflow_id,
            epic_file=str(epic.file_path),
            status="running",
            current_phase=Phase.CREATE_BRANCH.value,
        )
        self._state_manager.save(state)
        return state

    def _create_branch(self, state: WorkflowState, epic: EpicInfo) -> None:
        branch_prefix = self._settings.git.branch_prefix
        branch_name = f"{branch_prefix}/{epic.id}" if branch_prefix else epic.id
        self._set_phase(state, Phase.CREATE_BRANCH, None)
        self._git_manager.create_branch(epic.id)
        state.branch_name = branch_name
        state.branch_created = True
        self._state_manager.save(state)

    def _set_phase(self, state: WorkflowState, phase: Phase, story_id: str | None) -> None:
        state.current_phase = phase.value
        state.current_story = story_id
        self._state_manager.save(state)
        self._reporter.on_phase_start(phase.value, story_id)


@dataclass(frozen=True)
class StoryDeps:
    agents: Mapping[str, AgentProtocol]
    state_manager: StateManagerProtocol
    git_manager: GitManagerProtocol
    prompt_loader: PromptLoader
    settings: Settings
    repo_root: Path
    reporter: ProgressReporterProtocol


class StoryRunner:
    """Execute workflow steps for a single story."""

    def __init__(self, deps: StoryDeps) -> None:
        self._deps = deps

    async def run_story(self, epic: EpicInfo, state: WorkflowState, story_ref: str) -> None:
        story_id, story_title = parse_story_ref(story_ref)
        story_path = story_path_for(self._deps, story_id)
        await create_story(self._deps, epic, state, story_id, story_title, story_path)
        validate_story(self._deps, state, story_id, story_path)
        await add_context(self._deps, epic, state, story_id, story_title, story_path)
        validate_story(self._deps, state, story_id, story_path)
        await develop_and_review(self._deps, epic, state, story_id, story_title, story_path)
        commit_story(self._deps, state, story_id, story_title)
        state.completed_stories.append(story_id)
        self._deps.state_manager.save(state)


def story_path_for(deps: StoryDeps, story_id: str) -> Path:
    output_dir = deps.settings.discovery.story_output_dir
    return deps.repo_root / output_dir / f"{story_id}.md"


def set_phase(
    deps: StoryDeps,
    state: WorkflowState,
    phase: Phase,
    story_id: str | None,
) -> None:
    state.current_phase = phase.value
    state.current_story = story_id
    deps.state_manager.save(state)
    deps.reporter.on_phase_start(phase.value, story_id)


async def run_agent(deps: StoryDeps, role: str, prompt: str) -> AgentResult:
    agent = deps.agents.get(role)
    if agent is None:
        raise WorkflowError(f"Missing agent for role: {role}")
    deps.reporter.on_agent_start(role)
    return await agent.run(prompt)


async def create_story(
    deps: StoryDeps,
    epic: EpicInfo,
    state: WorkflowState,
    story_id: str,
    story_title: str,
    story_path: Path,
) -> None:
    set_phase(deps, state, Phase.CREATE_STORY, story_id)
    context = {
        "epic_id": epic.id,
        "epic_title": epic.title,
        "epic_description": epic.description,
        "story_id": story_id,
        "story_title": story_title,
    }
    prompt = deps.prompt_loader.render(Phase.CREATE_STORY, context)
    result = await run_agent(deps, ROLE_SCRUM_MASTER, prompt)
    if not result.output.strip():
        raise StoryCreationError("Story creation returned empty output")
    story_path.parent.mkdir(parents=True, exist_ok=True)
    story_path.write_text(result.output, encoding="utf-8")


def validate_story(
    deps: StoryDeps,
    state: WorkflowState,
    story_id: str,
    story_path: Path,
) -> None:
    set_phase(deps, state, Phase.VALIDATE_STORY, story_id)
    StoryParser().parse(story_path)


async def develop_and_review(
    deps: StoryDeps,
    epic: EpicInfo,
    state: WorkflowState,
    story_id: str,
    story_title: str,
    story_path: Path,
) -> None:
    attempts = 0
    while attempts < deps.settings.workflow.max_dev_attempts:
        attempts += 1
        await develop_story(deps, epic, state, story_id, story_title, story_path)
        approved = await review_story(deps, epic, state, story_id, story_title, story_path)
        if approved:
            return
    raise ReviewRejectedError(f"Review rejected story {story_id} after {attempts} attempts")


async def develop_story(
    deps: StoryDeps,
    epic: EpicInfo,
    state: WorkflowState,
    story_id: str,
    story_title: str,
    story_path: Path,
) -> None:
    set_phase(deps, state, Phase.DEVELOP, story_id)
    context = {
        "epic_id": epic.id,
        "epic_title": epic.title,
        "story_id": story_id,
        "story_title": story_title,
        "story_path": str(story_path),
    }
    prompt = deps.prompt_loader.render(Phase.DEVELOP, context)
    await run_agent(deps, ROLE_DEVELOPER, prompt)


async def review_story(
    deps: StoryDeps,
    epic: EpicInfo,
    state: WorkflowState,
    story_id: str,
    story_title: str,
    story_path: Path,
) -> bool:
    set_phase(deps, state, Phase.CODE_REVIEW, story_id)
    context = {
        "epic_id": epic.id,
        "epic_title": epic.title,
        "story_id": story_id,
        "story_title": story_title,
        "story_path": str(story_path),
    }
    prompt = deps.prompt_loader.render(Phase.CODE_REVIEW, context)
    result = await run_agent(deps, ROLE_REVIEWER, prompt)
    return review_passed(result.output)


def commit_story(
    deps: StoryDeps,
    state: WorkflowState,
    story_id: str,
    story_title: str,
) -> None:
    set_phase(deps, state, Phase.COMMIT, story_id)
    message = f"{story_id} {story_title}"
    deps.git_manager.commit(message)


def parse_story_ref(story_ref: str) -> tuple[str, str]:
    if ":" in story_ref:
        story_id, title = story_ref.split(":", 1)
    else:
        parts = story_ref.split(" ", 1)
        if len(parts) != 2:
            raise StoryCreationError("Story reference must include an id and title")
        story_id, title = parts
    story_id = story_id.strip()
    title = title.strip()
    if not story_id or not title:
        raise StoryCreationError("Story reference must include an id and title")
    if re.fullmatch(STORY_ID_PATTERN, story_id) is None:
        raise StoryCreationError(f"Invalid story id: {story_id}")
    return story_id, title


def review_passed(output: str) -> bool:
    if MARKER_REVIEW_APPROVED in output:
        return True
    if MARKER_REVIEW_REJECTED in output:
        return False
    raise WorkflowError("Review output missing approval/rejection marker")


async def add_context(
    deps: StoryDeps,
    epic: EpicInfo,
    state: WorkflowState,
    story_id: str,
    story_title: str,
    story_path: Path,
) -> None:
    if not deps.prompt_loader.has_template(Phase.ADD_CONTEXT):
        return
    set_phase(deps, state, Phase.ADD_CONTEXT, story_id)
    story_markdown = story_path.read_text(encoding="utf-8")
    context = {
        "epic_id": epic.id,
        "epic_title": epic.title,
        "epic_description": epic.description,
        "story_id": story_id,
        "story_title": story_title,
        "story_path": str(story_path),
        "story_markdown": story_markdown,
    }
    prompt = deps.prompt_loader.render(Phase.ADD_CONTEXT, context)
    result = await run_agent(deps, ROLE_SCRUM_MASTER, prompt)
    if not result.output.strip():
        raise StoryCreationError("Add context returned empty output")
    story_path.write_text(result.output, encoding="utf-8")


async def run_retrospective(deps: StoryDeps, epic: EpicInfo, state: WorkflowState) -> None:
    if not deps.prompt_loader.has_template(Phase.RETROSPECTIVE):
        return
    set_phase(deps, state, Phase.RETROSPECTIVE, None)
    context = {
        "epic_id": epic.id,
        "epic_title": epic.title,
        "epic_description": epic.description,
        "completed_stories": ", ".join(state.completed_stories),
        "failed_stories": ", ".join(state.failed_stories),
    }
    prompt = deps.prompt_loader.render(Phase.RETROSPECTIVE, context)
    await run_agent(deps, ROLE_SCRUM_MASTER, prompt)


async def run_documentation(deps: StoryDeps, epic: EpicInfo, state: WorkflowState) -> None:
    if not deps.prompt_loader.has_template(Phase.DOCUMENTATION):
        return
    set_phase(deps, state, Phase.DOCUMENTATION, None)
    context = {
        "epic_id": epic.id,
        "epic_title": epic.title,
        "epic_description": epic.description,
        "completed_stories": ", ".join(state.completed_stories),
        "failed_stories": ", ".join(state.failed_stories),
    }
    prompt = deps.prompt_loader.render(Phase.DOCUMENTATION, context)
    await run_agent(deps, ROLE_TECH_WRITER, prompt)


async def maybe_create_pr(deps: StoryDeps, epic: EpicInfo, state: WorkflowState) -> None:
    if not (deps.settings.git.auto_push or deps.settings.git.create_pr):
        return
    set_phase(deps, state, Phase.CREATE_PR, None)
    context = {
        "epic_id": epic.id,
        "epic_title": epic.title,
        "epic_description": epic.description,
        "completed_stories": ", ".join(state.completed_stories),
        "failed_stories": ", ".join(state.failed_stories),
        "branch_name": state.branch_name or "",
    }
    body = ""
    if deps.prompt_loader.has_template(Phase.CREATE_PR):
        prompt = deps.prompt_loader.render(Phase.CREATE_PR, context)
        result = await run_agent(deps, ROLE_SCRUM_MASTER, prompt)
        body = result.output.strip()
    if not body:
        body = (
            f"Epic {epic.id}: {epic.title}\n\n"
            f"Completed: {', '.join(state.completed_stories) or 'None'}\n"
            f"Failed: {', '.join(state.failed_stories) or 'None'}"
        )
    title = f"{epic.id}: {epic.title}"
    deps.git_manager.push_and_create_pr(title, body)


__all__ = ["WorkflowEngine", "NullProgressReporter", "parse_story_ref", "review_passed"]
