"""Workflow phase definitions."""

from enum import StrEnum


class Phase(StrEnum):
    """Named phases of the BMAD workflow."""

    CREATE_BRANCH = "create_branch"
    CREATE_STORY = "create_story"
    VALIDATE_STORY = "validate_story"
    ADD_CONTEXT = "add_context"
    DEVELOP = "develop"
    CODE_REVIEW = "code_review"
    COMMIT = "commit"
    RETROSPECTIVE = "retrospective"
    DOCUMENTATION = "documentation"
    CREATE_PR = "create_pr"


__all__ = ["Phase"]
