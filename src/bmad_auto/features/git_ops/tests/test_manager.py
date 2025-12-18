from pathlib import Path

import pytest
from git import Repo

from bmad_auto.core.exceptions import GitOperationError
from bmad_auto.features.git_ops.manager import GitManager
from bmad_auto.features.git_ops.models import GitConfig


def _init_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    (tmp_path / "README.md").write_text("root\n", encoding="utf-8")
    repo.git.add(all=True)
    repo.index.commit("init")
    return repo


def test_init_non_repo_raises(tmp_path) -> None:
    with pytest.raises(GitOperationError):
        GitManager(repo_path=tmp_path / "not_repo")


def test_create_branch(tmp_path) -> None:
    repo = _init_repo(tmp_path)
    manager = GitManager(repo_path=tmp_path)
    manager.create_branch("epic-1")
    assert repo.active_branch.name == "bmad/epic-1"


def test_commit_with_changes(tmp_path) -> None:
    repo = _init_repo(tmp_path)
    manager = GitManager(repo_path=tmp_path, config=GitConfig(commit_prefix="feat(bmad):"))
    (tmp_path / "file.txt").write_text("content", encoding="utf-8")
    manager.commit("story-1 implement")
    assert repo.head.commit.message.startswith("feat(bmad): story-1 implement")


def test_commit_without_changes_raises(tmp_path) -> None:
    _init_repo(tmp_path)
    manager = GitManager(repo_path=tmp_path)
    with pytest.raises(GitOperationError):
        manager.commit("nothing")


def test_push_returns_when_pr_disabled(tmp_path) -> None:
    repo = _init_repo(tmp_path)
    # create bare remote
    remote_path = tmp_path / "remote.git"
    Repo.init(remote_path, bare=True)
    repo.create_remote("origin", remote_path.as_posix())
    manager = GitManager(repo_path=tmp_path, config=GitConfig(create_pr=False))
    manager.create_branch("epic-2")
    (tmp_path / "change.txt").write_text("x", encoding="utf-8")
    manager.commit("change")
    url = manager.push_and_create_pr("title", "body")
    assert url == ""
