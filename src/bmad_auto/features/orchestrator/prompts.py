"""Prompt template loading and rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from bmad_auto.core.exceptions import ConfigurationError
from bmad_auto.features.orchestrator.phases import Phase
from bmad_auto.shared.consts import DEFAULT_TEMPLATES_DIR, TEMPLATE_EXTENSION


class PromptLoader:
    """Load and render prompt templates from disk."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        self.templates_dir = Path(templates_dir or DEFAULT_TEMPLATES_DIR)

    def render(self, phase: Phase, context: Mapping[str, str]) -> str:
        template = self._load_template(phase)
        self._validate_context(context)
        try:
            return template.format_map(context)
        except KeyError as exc:
            raise ConfigurationError(f"Missing prompt context key: {exc}") from exc

    def _load_template(self, phase: Phase) -> str:
        path = self._template_path(phase)
        if not path.is_file():
            raise ConfigurationError(f"Prompt template not found: {path}")
        return path.read_text(encoding="utf-8")

    def _template_path(self, phase: Phase) -> Path:
        filename = f"{phase.value}{TEMPLATE_EXTENSION}"
        return self.templates_dir / filename

    def _validate_context(self, context: Mapping[str, str]) -> None:
        for key, value in context.items():
            if not isinstance(key, str):
                raise ConfigurationError("Prompt context keys must be strings")
            if not isinstance(value, str):
                raise ConfigurationError(f"Prompt context value for {key!r} must be a string")


__all__ = ["PromptLoader"]
