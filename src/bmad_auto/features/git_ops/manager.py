"""Git operations using GitPython and gh CLI."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from bmad_auto.core.exceptions import GitOperationError
from bmad_auto.features.git_ops.models import GitConfig


class GitManager:
    """High-level git operations for the workflow."""

    def __init__(self, repo_path: Path | None = None, config: GitConfig | None = None) -> None:
        self.repo_path = Path(repo_path or ".").resolve()
        self.config = config or GitConfig()
        try:
            self.repo = Repo(self.repo_path)
        except (InvalidGitRepositoryError, NoSuchPathError) as exc:
            raise GitOperationError(f"Not a git repository: {self.repo_path}") from exc

    def create_branch(self, name: str) -> None:
        """Create and checkout a new branch from HEAD."""
        full_name = f"{self.config.branch_prefix}/{name}"
        try:
            self.repo.git.checkout("-b", full_name)
        except GitCommandError as exc:
            raise GitOperationError(f"Failed to create branch {full_name}: {exc}") from exc

    def commit(self, message: str) -> None:
        """Stage all changes and create a commit."""
        try:
            self.repo.git.add(all=True)
            if not self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
                raise GitOperationError("No changes to commit")
            self.repo.index.commit(f"{self.config.commit_prefix} {message}")
        except GitCommandError as exc:
            raise GitOperationError(f"Failed to commit changes: {exc}") from exc

    def push_and_create_pr(self, title: str, body: str) -> str:
        """Push current branch and open a PR via gh CLI; returns PR URL."""
        branch = self.repo.active_branch.name
        try:
            self.repo.git.push("--set-upstream", "origin", branch)
        except GitCommandError as exc:
            raise GitOperationError(f"Failed to push branch {branch}: {exc}") from exc

        if not self.config.create_pr:
            return ""
        if shutil.which("gh") is None:
            raise GitOperationError("GitHub CLI 'gh' not found in PATH")

        cmd = [
            "gh",
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
        ]
        if self.config.pr_draft:
            cmd.append("--draft")
        try:
            output = subprocess.check_output(cmd, cwd=self.repo_path, text=True).strip()
        except subprocess.CalledProcessError as exc:
            raise GitOperationError(f"Failed to create PR: {exc.output}") from exc
        return output


__all__ = ["GitManager"]
