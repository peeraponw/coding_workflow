"""Parser for BMAD epic markdown files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from bmad_auto.core.exceptions import EpicNotFoundError
from bmad_auto.features.discovery.models import EpicInfo


class EpicParser:
    """Parse epic markdown files into structured metadata."""

    def parse(self, file_path: Path) -> EpicInfo:
        path = Path(file_path)
        if not path.is_file():
            raise EpicNotFoundError(f"Epic file not found: {path}")

        lines = path.read_text(encoding="utf-8").splitlines()
        title = self._extract_title(lines)
        description = self._extract_description(lines)
        story_refs = list(self._extract_section_items(lines, {"stories", "story"}))
        dependencies = list(self._extract_section_items(lines, {"dependencies", "dependency"}))

        epic_id = path.stem
        return EpicInfo(
            id=epic_id,
            title=title,
            description=description,
            story_refs=story_refs,
            dependencies=dependencies,
            file_path=path,
        )

    def _extract_title(self, lines: list[str]) -> str:
        for line in lines:
            if line.startswith("#"):
                return line.lstrip("#").strip()
        raise ValueError("Epic file is missing a title heading")

    def _extract_description(self, lines: list[str]) -> str:
        description_lines: list[str] = []
        started = False
        for line in lines:
            if line.startswith("#"):
                if started:
                    break
                started = True
                continue
            if started:
                if line.startswith("##"):
                    break
                description_lines.append(line.rstrip())
        return "\n".join(description_lines).strip()

    def _extract_section_items(self, lines: list[str], names: set[str]) -> Iterable[str]:
        """Yield bullet list items under a heading matching provided names."""
        in_section = False
        for line in lines:
            if line.startswith("##"):
                heading = line.lstrip("#").strip().lower()
                in_section = any(name in heading for name in names)
                continue
            if in_section:
                if line.startswith("##"):
                    break
                if line.strip().startswith(("-", "*")):
                    item = line.strip().lstrip("-*").strip()
                    if item:
                        yield item


__all__ = ["EpicParser"]
