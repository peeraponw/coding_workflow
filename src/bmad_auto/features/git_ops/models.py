"""Configuration models for git operations."""

from __future__ import annotations

from pydantic import BaseModel, Field

from bmad_auto.shared.consts import GIT_BRANCH_PREFIX, GIT_COMMIT_PREFIX


class GitConfig(BaseModel):
    """Settings controlling git behaviors."""

    branch_prefix: str = Field(default=GIT_BRANCH_PREFIX)
    commit_prefix: str = Field(default=GIT_COMMIT_PREFIX)
    auto_push: bool = Field(default=False)
    create_pr: bool = Field(default=True)
    pr_draft: bool = Field(default=True)


__all__ = ["GitConfig"]
