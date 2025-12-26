"""Tests for GitHandler."""

import subprocess

import pytest

from bmad_auto.features.git_integration import GitError, GitHandler


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    # Create initial commit
    (tmp_path / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    return tmp_path


class TestGitHandler:
    """Test GitHandler class."""

    def test_init_default_path(self, git_repo):
        """Test GitHandler initializes with default path."""
        handler = GitHandler(git_repo)
        assert handler.repo_path == git_repo

    def test_get_current_branch(self, git_repo):
        """Test get_current_branch returns branch name."""
        handler = GitHandler(git_repo)
        assert handler.get_current_branch() == "main"

    def test_create_branch(self, git_repo):
        """Test create_branch creates and checks out new branch."""
        handler = GitHandler(git_repo)
        result = handler.create_branch("feature/test")
        assert result is True
        assert handler.get_current_branch() == "feature/test"

    def test_checkout_branch(self, git_repo):
        """Test checkout_branch switches to existing branch."""
        handler = GitHandler(git_repo)
        handler.create_branch("existing-branch")
        handler.checkout_branch("main")
        assert handler.get_current_branch() == "main"
        handler.checkout_branch("existing-branch")
        assert handler.get_current_branch() == "existing-branch"

    def test_commit_returns_hash(self, git_repo):
        """Test commit returns short commit hash."""
        handler = GitHandler(git_repo)
        (git_repo / "test.txt").write_text("content")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)

        commit_hash = handler.commit("Test commit")
        assert len(commit_hash) == 7
        assert commit_hash.isalnum()

    def test_get_status_clean(self, git_repo):
        """Test get_status returns clean status."""
        handler = GitHandler(git_repo)
        status = handler.get_status()
        assert status.clean is True
        assert status.branch == "main"
        assert status.staged == []
        assert status.unstaged == []

    def test_get_status_with_changes(self, git_repo):
        """Test get_status detects changes."""
        handler = GitHandler(git_repo)

        # Create unstaged change by modifying existing file
        (git_repo / "README.md").write_text("modified content")
        status = handler.get_status()
        assert status.clean is False
        assert len(status.unstaged) == 1
        assert "README.md" in status.unstaged[0]

        # Stage the change
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        status = handler.get_status()
        assert status.clean is False
        assert len(status.staged) == 1
        assert "README.md" in status.staged[0]

    def test_get_diff(self, git_repo):
        """Test get_diff returns diff output."""
        handler = GitHandler(git_repo)

        # Make a commit to have diff against
        (git_repo / "file.txt").write_text("new content")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)
        handler.commit("Add file")

        diff = handler.get_diff()
        assert "new content" in diff

    def test_git_error_on_invalid_command(self, git_repo):
        """Test GitError is raised for invalid git command."""
        handler = GitHandler(git_repo)
        with pytest.raises(GitError) as exc_info:
            handler.checkout_branch("nonexistent-branch-xyz")
        assert "failed" in str(exc_info.value)

    def test_git_error_on_commit_fail(self, git_repo):
        """Test GitError is raised when commit fails."""
        handler = GitHandler(git_repo)
        # Try to commit without staged changes
        with pytest.raises(GitError) as exc_info:
            handler.commit("No changes")
        assert "failed" in str(exc_info.value)


    def test_branch_exists_true(self, git_repo):
        """Test branch_exists returns True for existing branch."""
        handler = GitHandler(git_repo)
        handler.create_branch("test-branch")
        assert handler.branch_exists("test-branch") is True

    def test_branch_exists_false(self, git_repo):
        """Test branch_exists returns False for non-existent branch."""
        handler = GitHandler(git_repo)
        assert handler.branch_exists("nonexistent-branch") is False

    def test_stage_all(self, git_repo):
        """Test stage_all stages all changes."""
        handler = GitHandler(git_repo)

        # Create untracked file
        (git_repo / "newfile.txt").write_text("content")

        # Stage all
        handler.stage_all()

        # Check status - file should be staged
        status = handler.get_status()
        assert len(status.staged) == 1
        assert "newfile.txt" in status.staged[0]

    def test_has_staged_changes_true(self, git_repo):
        """Test has_staged_changes returns True when there are staged changes."""
        handler = GitHandler(git_repo)

        # Modify and stage a file
        (git_repo / "README.md").write_text("modified")
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)

        assert handler.has_staged_changes() is True

    def test_has_staged_changes_false(self, git_repo):
        """Test has_staged_changes returns False when no staged changes."""
        handler = GitHandler(git_repo)
        assert handler.has_staged_changes() is False


    def test_get_status_renamed_file(self, git_repo):
        """Test get_status handles renamed files correctly."""
        handler = GitHandler(git_repo)

        # Rename a file using git mv
        subprocess.run(["git", "mv", "README.md", "NEWREADME.md"], cwd=git_repo, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=git_repo, check=True, capture_output=True)

        status = handler.get_status()
        # The renamed file should appear with the new name
        assert "NEWREADME.md" in status.staged[0]
