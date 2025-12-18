import json
from datetime import datetime, timedelta, timezone

from bmad_auto.features.state.manager import StateManager
from bmad_auto.features.state.models import WorkflowState


def _state() -> WorkflowState:
    return WorkflowState(
        workflow_id="wf-1",
        epic_file="docs/epics/epic-1.md",
        status="pending",
        current_phase="create_branch",
    )


def test_save_and_load_roundtrip(tmp_path) -> None:
    manager = StateManager(state_dir=tmp_path)
    state = _state()
    manager.save(state)
    loaded = manager.load("wf-1")
    assert loaded is not None
    assert loaded.workflow_id == state.workflow_id
    assert loaded.epic_file == state.epic_file
    assert loaded.status == state.status


def test_list_all_returns_saved_states(tmp_path) -> None:
    manager = StateManager(state_dir=tmp_path)
    for idx in range(2):
        state = _state()
        state.workflow_id = f"wf-{idx}"
        manager.save(state)
    all_states = manager.list_all()
    ids = {s.workflow_id for s in all_states}
    assert ids == {"wf-0", "wf-1"}


def test_load_missing_returns_none(tmp_path) -> None:
    manager = StateManager(state_dir=tmp_path)
    assert manager.load("missing") is None


def test_save_updates_timestamp(tmp_path) -> None:
    manager = StateManager(state_dir=tmp_path)
    state = _state()
    past = datetime.now(timezone.utc) - timedelta(days=1)
    state.updated_at = past
    manager.save(state)
    reloaded = manager.load(state.workflow_id)
    assert reloaded is not None
    assert reloaded.updated_at > past
