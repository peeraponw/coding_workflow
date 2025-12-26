# Story 5.1: Git Handler Module

Status: ready-for-dev

## Story

As a **developer**,
I want **a git handler module that wraps git CLI operations**,
so that **all git operations are centralized and testable**.

## Acceptance Criteria

1. **Given** the git_integration module is implemented, **When** I import from `bmad_auto.features.git_integration`, **Then** I can access GitHandler with methods:
   - `get_current_branch() -> str`
   - `create_branch(name: str) -> bool`
   - `checkout_branch(name: str) -> bool`
   - `commit(message: str) -> str` (returns commit hash)
   - `get_status() -> GitStatus`
   - `get_diff() -> str`
2. **Given** a git operation fails, **When** the subprocess returns non-zero, **Then** appropriate exception is raised with git error message
3. All operations use subprocess with git CLI (NFR10)
4. Operations are atomic where possible (NFR4)
5. Tests use a temporary git repository fixture

## Tasks / Subtasks

- [ ] Task 1: Create git_integration module structure (AC: 1)
  - [ ] Create `src/bmad_auto/features/git_integration/__init__.py`
  - [ ] Create `src/bmad_auto/features/git_integration/handler.py`
  - [ ] Export GitHandler from __init__.py
- [ ] Task 2: Implement GitHandler class (AC: 1)
  - [ ] Implement `get_current_branch()`
  - [ ] Implement `create_branch(name)`
  - [ ] Implement `checkout_branch(name)`
  - [ ] Implement `commit(message)` returning hash
  - [ ] Implement `get_status()` returning GitStatus dataclass
  - [ ] Implement `get_diff()`
- [ ] Task 3: Implement subprocess wrapper (AC: 3)
  - [ ] Create `_run_git(*args)` helper
  - [ ] Use subprocess.run with capture
  - [ ] Handle encoding properly
- [ ] Task 4: Implement error handling (AC: 2)
  - [ ] Define GitError exception
  - [ ] Raise on non-zero exit code
  - [ ] Include git stderr in error message
- [ ] Task 5: Write tests with git fixture (AC: 5)
  - [ ] Create temp git repo fixture
  - [ ] Test each method
  - [ ] Test error handling

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Git boundary owns ALL git CLI subprocess calls
- No knowledge of agents or workflow state
- Use subprocess for git operations (not GitPython)
- Operations should be atomic where possible

### Implementation

```python
import subprocess
from dataclasses import dataclass
from pathlib import Path

@dataclass
class GitStatus:
    branch: str
    clean: bool
    staged: list[str]
    unstaged: list[str]

class GitHandler:
    def __init__(self, repo_path: Path | None = None):
        self.repo_path = repo_path or Path.cwd()

    def _run_git(self, *args: str) -> str:
        """Run git command and return stdout."""
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise GitError(f"git {args[0]} failed: {result.stderr}")
        return result.stdout.strip()

    def get_current_branch(self) -> str:
        return self._run_git("rev-parse", "--abbrev-ref", "HEAD")

    def create_branch(self, name: str) -> bool:
        self._run_git("checkout", "-b", name)
        return True

    def checkout_branch(self, name: str) -> bool:
        self._run_git("checkout", name)
        return True

    def commit(self, message: str) -> str:
        self._run_git("commit", "-m", message)
        return self._run_git("rev-parse", "HEAD")[:7]

    def get_diff(self) -> str:
        return self._run_git("diff", "HEAD~1")
```

### Source Tree Components

```
src/bmad_auto/features/
└── git_integration/
    ├── __init__.py       # Export GitHandler
    ├── handler.py        # GitHandler implementation
    └── tests/
        └── test_handler.py
```

### Testing Standards

- Use tmp_path with git init for test repo
- Create fixture that initializes git repo
- Test each method independently

### Test Fixture

```python
@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    # Create initial commit
    (tmp_path / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial"], cwd=tmp_path, check=True)
    return tmp_path
```

### References

- [Source: _bmad-output/architecture/project-structure-boundaries.md#git-boundary-featuresgit_integration]
- [Source: _bmad-output/project-context.md#orchestrator-boundaries]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
