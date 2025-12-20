"""Utilities to locate epic files within a repository."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from bmad_auto.features.state.models import WorkflowState
from bmad_auto.shared.consts import DEFAULT_EPIC_PATTERNS


class EpicDiscovery:
    """Find epic markdown files using configurable glob patterns."""

    def __init__(self, patterns: Sequence[str] | None = None, repo_root: Path | None = None) -> None:
        self.patterns = list(patterns or DEFAULT_EPIC_PATTERNS)
        self.repo_root = Path(repo_root or ".")

    def discover(self, existing_states: Iterable[WorkflowState] | None = None) -> list[Path]:
        """Return epic file paths, excluding ones already tracked in state."""
        seen = set()    
        if existing_states:
            seen.update(Path(state.epic_file) for state in existing_states)

        results: list[Path] = []
        for pattern in self.patterns:
            for path in self.repo_root.glob(pattern):
                if not path.is_file():
                    continue
                if path in seen:
                    continue
                if path not in results:
                    results.append(path)
        return sorted(results)


__all__ = ["EpicDiscovery"]
