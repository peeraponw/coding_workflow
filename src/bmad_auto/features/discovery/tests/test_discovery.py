from pathlib import Path

from bmad_auto.features.discovery.epic_discovery import EpicDiscovery
from bmad_auto.features.state.models import WorkflowState


def _state(epic_path: Path) -> WorkflowState:
    return WorkflowState(
        workflow_id="wf-1",
        epic_file=str(epic_path),
        status="pending",
        current_phase="create_branch",
    )


def test_discover_returns_matching_files(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "epics"
    docs.mkdir(parents=True)
    (docs / "epic-a.md").write_text("# Epic A\n")
    (docs / "epic-b.md").write_text("# Epic B\n")

    discovery = EpicDiscovery(repo_root=tmp_path)
    results = discovery.discover()

    assert {p.name for p in results} == {"epic-a.md", "epic-b.md"}


def test_discover_filters_existing_states(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "epics"
    docs.mkdir(parents=True)
    epic_a = docs / "epic-a.md"
    epic_b = docs / "epic-b.md"
    epic_a.write_text("# Epic A\n")
    epic_b.write_text("# Epic B\n")

    existing = [_state(epic_a)]
    discovery = EpicDiscovery(repo_root=tmp_path)
    results = discovery.discover(existing_states=existing)

    assert [p.name for p in results] == ["epic-b.md"]

