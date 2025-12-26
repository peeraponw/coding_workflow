# Story 5.2: Feature Branch Creation

Status: ready-for-dev

## Story

As a **user**,
I want **a feature branch created automatically when I start an epic**,
so that **my work is isolated from main branch**.

## Acceptance Criteria

1. **Given** I run `bmad-auto run --epic docs/epics/epic-001.md`, **When** the workflow starts, **Then** a feature branch is created: `epic/epic-001` (FR22), the branch is checked out, and state records `workflow.branch: epic/epic-001`
2. **Given** config has `git.auto_branch: true`, **When** workflow starts, **Then** branch is created automatically
3. **Given** config has `git.auto_branch: false`, **When** workflow starts, **Then** no branch is created (user manages branches)
4. **Given** the target branch already exists, **When** workflow starts, **Then** user is warned and asked to confirm using existing branch
5. Branch name is derived from epic filename
6. Tests verify branch creation scenarios

## Tasks / Subtasks

- [ ] Task 1: Implement branch creation in orchestrator (AC: 1)
  - [ ] Extract branch name from epic filename
  - [ ] Call GitHandler.create_branch()
  - [ ] Update state with branch name
- [ ] Task 2: Implement config check (AC: 2-3)
  - [ ] Check git.auto_branch setting
  - [ ] Skip branch creation if false
- [ ] Task 3: Implement existing branch handling (AC: 4)
  - [ ] Check if branch exists
  - [ ] Warn user and prompt for confirmation
  - [ ] Allow checkout of existing branch
- [ ] Task 4: Implement branch name derivation (AC: 5)
  - [ ] Extract filename from epic path
  - [ ] Remove .md extension
  - [ ] Apply branch_prefix from config
  - [ ] Sanitize for git branch naming rules
- [ ] Task 5: Write tests (AC: 6)
  - [ ] Test auto branch creation
  - [ ] Test branch creation disabled
  - [ ] Test existing branch warning
  - [ ] Test branch name derivation

## Dev Notes

### Architecture Patterns & Constraints

- Orchestrator delegates to GitHandler for git operations
- Branch name derived from epic filename
- User config controls auto_branch behavior
- Save branch name to state for resume

### Branch Name Derivation

```python
def derive_branch_name(epic_path: str, prefix: str) -> str:
    """Derive git branch name from epic file path."""
    filename = Path(epic_path).stem  # "epic-001"
    # Sanitize for git branch naming
    safe_name = re.sub(r'[^a-zA-Z0-9-]', '-', filename)
    return f"{prefix}{safe_name}"  # "epic/epic-001"
```

### Orchestrator Integration

```python
async def start_workflow(self, epic_path: str):
    """Start new workflow for epic."""
    if self.config.git.auto_branch:
        branch_name = derive_branch_name(epic_path, self.config.git.branch_prefix)

        if self.git.branch_exists(branch_name):
            if not self.confirm_use_existing_branch(branch_name):
                raise typer.Exit(EXIT_ERROR)
            self.git.checkout_branch(branch_name)
        else:
            self.git.create_branch(branch_name)

        self.state.workflow.branch = branch_name
        save(self.state)
```

### Source Tree Components

```
src/bmad_auto/
├── core/
│   └── orchestrator.py   # Branch creation logic
└── features/
    └── git_integration/
        └── handler.py    # GitHandler methods
```

### Testing Standards

- Use git_repo fixture from Story 5.1
- Test with various config combinations
- Mock user prompts for confirmation

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-5-git-integration-auto-commit.md#story-52-feature-branch-creation]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#git-boundary-featuresgit_integration]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
