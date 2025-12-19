"""Parser for BMAD story markdown files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from bmad_auto.core.exceptions import StoryCreationError
from bmad_auto.features.discovery.models import StoryInfo


class StoryParser:
    """Parse story markdown files into structured metadata."""

    def parse(self, file_path: Path) -> StoryInfo:
        path = Path(file_path)
        if not path.is_file():
            raise StoryCreationError(f"Story file not found: {path}")

        lines = path.read_text(encoding="utf-8").splitlines()
        title_line = self._find_title(lines)
        story_id, title = self._split_id_title(title_line)
        context = self._extract_section(lines, {"context", "description"})
        acceptance = list(self._extract_list_section(lines, {"acceptance", "criteria"}))
        checklist = list(self._extract_list_section(lines, {"checklist", "tasks"}))

        return StoryInfo(
            id=story_id,
            title=title,
            context=context,
            acceptance_criteria=acceptance,
            checklist=checklist,
            file_path=path,
        )

    def _find_title(self, lines: list[str]) -> str:
        for line in lines:
            if line.startswith("#"):
                return line.lstrip("#").strip()
        raise StoryCreationError("Story file is missing a title heading")

    def _split_id_title(self, line: str) -> tuple[str, str]:
        parts = line.split(" ", 1)
        if len(parts) == 1:
            raise StoryCreationError("Story title must include an identifier prefix")
        return parts[0], parts[1].strip()

    def _extract_section(self, lines: list[str], names: set[str]) -> str:
        in_section = False
        collected: list[str] = []
        for line in lines:
            if line.startswith("##"):
                heading = line.lstrip("#").strip().lower()
                in_section = any(name in heading for name in names)
                if in_section:
                    collected.clear()
                continue
            if in_section:
                if line.startswith("##"):
                    break
                collected.append(line.rstrip())
        return "\n".join(collected).strip()

    def _extract_list_section(self, lines: list[str], names: set[str]) -> Iterable[str]:
        in_section = False
        for line in lines:
            if line.startswith("##"):
                heading = line.lstrip("#").strip().lower()
                in_section = any(name in heading for name in names)
                continue
            if in_section:
                if line.startswith("##"):
                    break
                if line.strip().startswith(("-", "*", "[", "[ ]")):
                    item = line.strip().lstrip("-*").lstrip("[ ]").strip()
                    if item:
                        yield item


__all__ = ["StoryParser"]
