"""Git operations tools."""

from git import Repo
from git.exc import GitCommandError

from bmad_automation.core.logging import get_logger
from bmad_automation.shared.exceptions import GitOperationError

logger = get_logger(__name__)


def git_create_branch(branch_name: str, repo_path: str = ".") -> str:
    """Create and checkout a new git branch."""
    try:
        repo = Repo(repo_path)
        repo.git.checkout("-b", branch_name)
        logger.info("Created branch", extra={"branch": branch_name})
        return f"Created branch: {branch_name}"
    except GitCommandError as exc:
        raise GitOperationError(f"Failed to create branch {branch_name}: {exc}") from exc


def git_commit(message: str, repo_path: str = ".") -> str:
    """Stage all changes and commit."""
    try:
        repo = Repo(repo_path)
        repo.git.add("-A")
        repo.index.commit(message)
        logger.info("Committed changes", extra={"message": message[:50]})
        return f"Committed: {message}"
    except GitCommandError as exc:
        raise GitOperationError(f"Failed to commit: {exc}") from exc


def git_push(repo_path: str = ".") -> str:
    """Push current branch to origin."""
    try:
        repo = Repo(repo_path)
        origin = repo.remote("origin")
        origin.push()
        branch = repo.active_branch.name
        logger.info("Pushed to origin", extra={"branch": branch})
        return f"Pushed branch {branch} to origin"
    except GitCommandError as exc:
        raise GitOperationError(f"Failed to push: {exc}") from exc


def git_current_branch(repo_path: str = ".") -> str:
    """Get the current branch name."""
    try:
        repo = Repo(repo_path)
        return repo.active_branch.name
    except GitCommandError as exc:
        raise GitOperationError(f"Failed to get current branch: {exc}") from exc
