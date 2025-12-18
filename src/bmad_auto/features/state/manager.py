"""JSON-backed workflow state persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from bmad_auto.core.exceptions import StateError
from bmad_auto.features.state.models import WorkflowState
from bmad_auto.shared.consts import DEFAULT_STATE_DIR


class StateManager:
    """Persist workflow state as JSON files in the repository."""

    def __init__(self, state_dir: Path | None = None) -> None:
        self.state_dir = Path(state_dir or DEFAULT_STATE_DIR)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, workflow_id: str) -> Path:
        return self.state_dir / f"{workflow_id}.json"

    def save(self, state: WorkflowState) -> None:
        state.touch()
        path = self._path_for(state.workflow_id)
        try:
            with path.open("w", encoding="utf-8") as handle:
                json.dump(state.model_dump(), handle, indent=2, sort_keys=True, default=str)
        except OSError as exc:  # pragma: no cover - filesystem failure
            raise StateError(f"Failed to write state file: {exc}") from exc

    def load(self, workflow_id: str) -> WorkflowState | None:
        path = self._path_for(workflow_id)
        if not path.is_file():
            return None
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except OSError as exc:  # pragma: no cover - filesystem failure
            raise StateError(f"Failed to read state file: {exc}") from exc
        return WorkflowState.model_validate(data)

    def list_all(self) -> list[WorkflowState]:
        states: list[WorkflowState] = []
        for path in self._iter_state_files():
            loaded = self.load(path.stem)
            if loaded:
                states.append(loaded)
        return states

    def _iter_state_files(self) -> Iterable[Path]:
        return self.state_dir.glob("*.json")


__all__ = ["StateManager"]
