from __future__ import annotations

from pathlib import Path

import pytest

from bmad_auto.core.config import Settings
from bmad_auto.core.exceptions import ReviewRejectedError
from bmad_auto.features.agents.models import AgentResult
from bmad_auto.features.orchestrator.engine import WorkflowEngine
from bmad_auto.features.orchestrator.phases import Phase
from bmad_auto.features.orchestrator.prompts import PromptLoader
from bmad_auto.features.state.manager import StateManager
from bmad_auto.features.state.models import WorkflowState
from bmad_auto.shared.consts import (
    MARKER_REVIEW_APPROVED,
    MARKER_REVIEW_REJECTED,
    ROLE_DEVELOPER,
    ROLE_REVIEWER,
    ROLE_SCRUM_MASTER,
)


class FakeAgent:
    def __init__(self, outputs: list[str]) -> None:
        self._outputs = outputs
        self.prompts: list[str] = []

    async def run(self, prompt: str, session_id: str | None = None) -> AgentResult:
        self.prompts.append(prompt)
        output = self._outputs.pop(0)
        return AgentResult(success=True, output=output, duration_seconds=0.0)

    def validate(self) -> None:
        return None


class FakeGitManager:
    def __init__(self, branch_prefix: str = "bmad", commit_prefix: str = "feat(bmad):") -> None:
        self.created_branch: str | None = None
        self.commits: list[str] = []
        self._branch_prefix = branch_prefix
        self._commit_prefix = commit_prefix

    def create_branch(self, name: str) -> None:
        self.created_branch = f"{self._branch_prefix}/{name}" if self._branch_prefix else name

    def commit(self, message: str) -> None:
        self.commits.append(f"{self._commit_prefix} {message}")

    def push_and_create_pr(self, title: str, body: str) -> str:
        return "https://example.test/pr/1"


def _write_templates(root: Path) -> PromptLoader:
    templates = root / "templates"
    templates.mkdir()
    (templates / f"{Phase.CREATE_STORY.value}.md").write_text("Create {story_id}")
    (templates / f"{Phase.DEVELOP.value}.md").write_text("Develop {story_id}")
    (templates / f"{Phase.CODE_REVIEW.value}.md").write_text("Review {story_id}")
    return PromptLoader(templates_dir=templates)


def _write_epic(root: Path) -> Path:
    epic = root / "docs" / "epics" / "epic-001.md"
    epic.parent.mkdir(parents=True)
    epic.write_text(
        "# Epic 001\n\n## Stories\n- STORY-001: Login flow\n",
        encoding="utf-8",
    )
    return epic


def _write_epic_two(root: Path) -> Path:
    epic = root / "docs" / "epics" / "epic-001.md"
    epic.parent.mkdir(parents=True, exist_ok=True)
    epic.write_text(
        "# Epic 001\n\n## Stories\n- STORY-001: Login flow\n- STORY-002: Logout flow\n",
        encoding="utf-8",
    )
    return epic


def _story_markdown() -> str:
    return (
        "# STORY-001 Login flow\n\n"
        "## Context\nUsers sign in.\n\n"
        "## Acceptance Criteria\n- Works\n\n"
        "## Checklist\n- [ ] Task\n"
    )


def _story_markdown_two() -> str:
    return (
        "# STORY-002 Logout flow\n\n"
        "## Context\nUsers sign out.\n\n"
        "## Acceptance Criteria\n- Works\n\n"
        "## Checklist\n- [ ] Task\n"
    )


@pytest.mark.asyncio
async def test_engine_runs_story_success(tmp_path: Path) -> None:
    epic_path = _write_epic(tmp_path)
    prompt_loader = _write_templates(tmp_path)
    state_manager = StateManager(state_dir=tmp_path / ".bmad-auto" / "state")
    git_manager = FakeGitManager(branch_prefix="bmad", commit_prefix="feat(bmad):")
    settings = Settings(
        discovery={"story_output_dir": "docs/stories"},
        workflow={"max_dev_attempts": 2},
        git={"branch_prefix": "bmad", "commit_prefix": "feat(bmad):"},
    )
    agents = {
        ROLE_SCRUM_MASTER: FakeAgent([_story_markdown()]),
        ROLE_DEVELOPER: FakeAgent(["done"]),
        ROLE_REVIEWER: FakeAgent([MARKER_REVIEW_APPROVED]),
    }

    engine = WorkflowEngine(
        agents=agents,
        state_manager=state_manager,
        git_manager=git_manager,
        prompt_loader=prompt_loader,
        settings=settings,
        repo_root=tmp_path,
    )

    state = await engine.run_epic(epic_path)

    assert state.status == "completed"
    assert state.completed_stories == ["STORY-001"]
    assert git_manager.created_branch == "bmad/epic-001"
    assert git_manager.commits == ["feat(bmad): STORY-001 Login flow"]
    story_file = tmp_path / "docs" / "stories" / "STORY-001.md"
    assert story_file.is_file()


@pytest.mark.asyncio
async def test_engine_fails_after_rejections(tmp_path: Path) -> None:
    epic_path = _write_epic(tmp_path)
    prompt_loader = _write_templates(tmp_path)
    state_manager = StateManager(state_dir=tmp_path / ".bmad-auto" / "state")
    git_manager = FakeGitManager(branch_prefix="bmad", commit_prefix="feat(bmad):")
    settings = Settings(
        discovery={"story_output_dir": "docs/stories"},
        workflow={"max_dev_attempts": 2},
        git={"branch_prefix": "bmad", "commit_prefix": "feat(bmad):"},
    )
    agents = {
        ROLE_SCRUM_MASTER: FakeAgent([_story_markdown()]),
        ROLE_DEVELOPER: FakeAgent(["done", "done"]),
        ROLE_REVIEWER: FakeAgent([MARKER_REVIEW_REJECTED, MARKER_REVIEW_REJECTED]),
    }
    engine = WorkflowEngine(
        agents=agents,
        state_manager=state_manager,
        git_manager=git_manager,
        prompt_loader=prompt_loader,
        settings=settings,
        repo_root=tmp_path,
    )

    with pytest.raises(ReviewRejectedError):
        await engine.run_epic(epic_path)

    states = state_manager.list_all()
    assert len(states) == 1
    assert states[0].status == "failed"


@pytest.mark.asyncio
async def test_engine_resume_skips_completed_stories(tmp_path: Path) -> None:
    epic_path = _write_epic_two(tmp_path)
    prompt_loader = _write_templates(tmp_path)
    state_manager = StateManager(state_dir=tmp_path / ".bmad-auto" / "state")
    git_manager = FakeGitManager(branch_prefix="bmad", commit_prefix="feat(bmad):")
    settings = Settings(
        discovery={"story_output_dir": "docs/stories"},
        workflow={"max_dev_attempts": 2},
        git={"branch_prefix": "bmad", "commit_prefix": "feat(bmad):"},
    )
    workflow_id = "epic-001-test"
    state = WorkflowState(
        workflow_id=workflow_id,
        epic_file=str(epic_path),
        status="failed",
        branch_name="bmad/epic-001",
        branch_created=True,
        current_phase=Phase.DEVELOP.value,
        current_story="STORY-002",
        completed_stories=["STORY-001"],
    )
    state_manager.save(state)
    agents = {
        ROLE_SCRUM_MASTER: FakeAgent([_story_markdown_two()]),
        ROLE_DEVELOPER: FakeAgent(["done"]),
        ROLE_REVIEWER: FakeAgent([MARKER_REVIEW_APPROVED]),
    }
    engine = WorkflowEngine(
        agents=agents,
        state_manager=state_manager,
        git_manager=git_manager,
        prompt_loader=prompt_loader,
        settings=settings,
        repo_root=tmp_path,
    )

    resumed = await engine.resume_workflow(workflow_id)

    assert resumed.status == "completed"
    assert resumed.completed_stories == ["STORY-001", "STORY-002"]
    assert git_manager.commits == ["feat(bmad): STORY-002 Logout flow"]
    assert len(agents[ROLE_SCRUM_MASTER].prompts) == 1
    story_one = tmp_path / "docs" / "stories" / "STORY-001.md"
    story_two = tmp_path / "docs" / "stories" / "STORY-002.md"
    assert not story_one.exists()
    assert story_two.is_file()
