from pathlib import Path

import pytest

from bmad_auto.core.exceptions import ConfigurationError
from bmad_auto.features.orchestrator.phases import Phase
from bmad_auto.features.orchestrator.prompts import PromptLoader


def test_prompt_loader_renders_template(tmp_path: Path) -> None:
    templates = tmp_path / "templates"
    templates.mkdir()
    template_path = templates / f"{Phase.CREATE_STORY.value}.md"
    template_path.write_text("Story {story_id}: {story_title}")

    loader = PromptLoader(templates_dir=templates)
    rendered = loader.render(Phase.CREATE_STORY, {"story_id": "STORY-001", "story_title": "Login"})

    assert rendered == "Story STORY-001: Login"


def test_prompt_loader_missing_template_raises(tmp_path: Path) -> None:
    loader = PromptLoader(templates_dir=tmp_path / "templates")
    with pytest.raises(ConfigurationError):
        loader.render(Phase.DEVELOP, {"story_id": "STORY-001"})


def test_prompt_loader_rejects_non_string_context(tmp_path: Path) -> None:
    templates = tmp_path / "templates"
    templates.mkdir()
    template_path = templates / f"{Phase.DEVELOP.value}.md"
    template_path.write_text("Develop {story_id}")

    loader = PromptLoader(templates_dir=templates)
    with pytest.raises(ConfigurationError):
        loader.render(Phase.DEVELOP, {"story_id": 123})
