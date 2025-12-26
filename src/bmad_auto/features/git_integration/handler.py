"""Git handler module for wrapping git CLI operations.

This module provides GitHandler which centralizes all git operations using subprocess.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitError(Exception):
    """Exception raised when git command fails."""

    pass


@dataclass
class GitStatus:
    """Git repository status."""

    branch: str
    clean: bool
    staged: list[str]
    unstaged: list[str]


class GitHandler:
    """Handler for git CLI operations.

    All git operations are centralized here using subprocess.
    """

    def __init__(self, repo_path: Path | None = None) -> None:
        """Initialize GitHandler with repository path.

        Args:
            repo_path: Path to git repository. Defaults to current working directory.
        """
        self.repo_path = repo_path or Path.cwd()

    def _run_git(self, *args: str) -> str:
        """Run git command and return stdout.

        Args:
            *args: Git command arguments

        Returns:
            Git command stdout

        Raises:
            GitError: If git command returns non-zero exit code
        """
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise GitError(f"git {args[0]} failed: {result.stderr.strip()}")
        # Strip trailing whitespace but preserve leading whitespace (important for porcelain format)
        return result.stdout.rstrip("\n\r")

    def get_current_branch(self) -> str:
        """Get current git branch name.

        Returns:
            Current branch name

        Raises:
            GitError: If command fails
        """
        return self._run_git("rev-parse", "--abbrev-ref", "HEAD")

    def create_branch(self, name: str) -> bool:
        """Create and checkout a new branch.

        Args:
            name: Branch name to create

        Returns:
            True if successful

        Raises:
            GitError: If branch creation fails
        """
        self._run_git("checkout", "-b", name)
        return True

    def checkout_branch(self, name: str) -> bool:
        """Checkout an existing branch.

        Args:
            name: Branch name to checkout

        Returns:
            True if successful

        Raises:
            GitError: If checkout fails
        """
        self._run_git("checkout", name)
        return True

    def commit(self, message: str) -> str:
        """Commit staged changes with message.

        Args:
            message: Commit message

        Returns:
            Short commit hash (7 characters)

        Raises:
            GitError: If commit fails
        """
        self._run_git("commit", "-m", message)
        return self._run_git("rev-parse", "HEAD")[:7]

    def get_status(self) -> GitStatus:
        """Get repository status.

        Returns:
            GitStatus object with branch, cleanliness, and file lists

        Raises:
            GitError: If command fails
        """
        branch = self.get_current_branch()

        # Get status in porcelain format
        status_output = self._run_git("status", "--porcelain")

        staged = []
        unstaged = []

        for line in status_output.splitlines():
            if not line:
                continue

            # Format: XY filename
            # X = staged status, Y = working tree status
            # Filename starts after first space
            staged_status = line[0]
            working_tree_status = line[1]
            filepath = line[3:] if working_tree_status != " " else line[2:]

            # Check for renamed files (R) which have format: R  old -> new
            if " -> " in filepath:
                filepath = filepath.split(" -> ")[1]

            if staged_status in "MADRC":
                staged.append(filepath)
            if working_tree_status in "MADRC":
                unstaged.append(filepath)

        clean = not staged and not unstaged

        return GitStatus(branch=branch, clean=clean, staged=staged, unstaged=unstaged)

    def get_diff(self) -> str:
        """Get diff against previous commit.

        Returns:
            Diff output

        Raises:
            GitError: If command fails
        """
        return self._run_git("diff", "HEAD~1")

    def branch_exists(self, name: str) -> bool:
        """Check if a branch exists.

        Args:
            name: Branch name to check

        Returns:
            True if branch exists, False otherwise
        """
        try:
            # git rev-parse --verify <branch> returns success if branch exists
            self._run_git("rev-parse", "--verify", name)
            return True
        except GitError:
            return False

    def stage_all(self) -> None:
        """Stage all changes.

        Raises:
            GitError: If staging fails
        """
        self._run_git("add", ".")

    def has_staged_changes(self) -> bool:
        """Check if there are staged changes.

        Returns:
            True if there are staged changes, False otherwise
        """
        status = self.get_status()
        return len(status.staged) > 0
