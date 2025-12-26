# Story 5.4: Branch Naming Configuration

Status: ready-for-dev

## Story

As a **user**,
I want **to configure the branch naming prefix**,
so that **branches match my team's conventions**.

## Acceptance Criteria

1. **Given** config specifies `git.branch_prefix: "feature/"`, **When** workflow starts for `epic-001.md`, **Then** branch is named `feature/epic-001` (FR25)
2. **Given** config specifies `git.branch_prefix: "epic/"`, **When** workflow starts, **Then** branch is named `epic/epic-001` (default)
3. **Given** config specifies empty prefix `git.branch_prefix: ""`, **When** workflow starts, **Then** branch is named `epic-001` (no prefix)
4. Branch names are sanitized (no spaces, special chars)
5. Tests verify branch naming with various prefixes

## Tasks / Subtasks

- [ ] Task 1: Implement prefix configuration (AC: 1-3)
  - [ ] Read branch_prefix from config
  - [ ] Default to "epic/" if not specified
  - [ ] Handle empty string for no prefix
- [ ] Task 2: Implement branch name sanitization (AC: 4)
  - [ ] Replace spaces with hyphens
  - [ ] Remove special characters
  - [ ] Ensure valid git branch name
  - [ ] Handle edge cases (leading/trailing hyphens)
- [ ] Task 3: Integrate with branch creation (AC: 1-3)
  - [ ] Pass prefix to derive_branch_name
  - [ ] Use sanitized name in create_branch
- [ ] Task 4: Write tests (AC: 5)
  - [ ] Test "feature/" prefix
  - [ ] Test "epic/" prefix (default)
  - [ ] Test empty prefix
  - [ ] Test sanitization cases

## Dev Notes

### Architecture Patterns & Constraints

- Branch prefix is user-configurable
- Default prefix: "epic/"
- Sanitization must produce valid git branch names
- Handle various filename patterns

### Branch Naming Rules

Git branch names cannot contain:
- Spaces
- `~`, `^`, `:`, `?`, `*`, `[`, `\`
- Double dots `..`
- Start with `/` or end with `/`
- End with `.lock`

### Implementation

```python
def sanitize_branch_name(name: str) -> str:
    """Sanitize string for use in git branch name."""
    # Replace spaces and invalid chars with hyphens
    sanitized = re.sub(r'[~^:?*\[\]\\. ]+', '-', name)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    # Replace multiple hyphens with single
    sanitized = re.sub(r'-+', '-', sanitized)
    return sanitized

def derive_branch_name(epic_path: str, prefix: str = "epic/") -> str:
    """Derive git branch name from epic file path."""
    # Get filename without extension
    filename = Path(epic_path).stem
    # Sanitize
    safe_name = sanitize_branch_name(filename)
    # Apply prefix
    if prefix and not prefix.endswith('/'):
        prefix = f"{prefix}/"
    return f"{prefix}{safe_name}"
```

### Config Example

```yaml
# .bmad-auto.yaml
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "feature/"  # Results in "feature/epic-001"
```

### Source Tree Components

```
src/bmad_auto/
├── core/
│   ├── config.py         # branch_prefix in UserConfig
│   └── orchestrator.py   # derive_branch_name function
└── features/
    └── git_integration/
        └── handler.py    # Uses sanitized branch names
```

### Testing Standards

- Test various prefix configurations
- Test sanitization edge cases
- Verify valid git branch names created

### Test Cases

```python
@pytest.mark.parametrize("prefix,epic,expected", [
    ("feature/", "epic-001.md", "feature/epic-001"),
    ("epic/", "epic-001.md", "epic/epic-001"),
    ("", "epic-001.md", "epic-001"),
    ("feat/", "My Epic File.md", "feat/my-epic-file"),
    ("", "epic with spaces.md", "epic-with-spaces"),
])
def test_branch_naming(prefix, epic, expected):
    assert derive_branch_name(epic, prefix) == expected
```

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-5-git-integration-auto-commit.md#story-54-branch-naming-configuration]
- [Source: _bmad-output/architecture/implementation-patterns-consistency-rules.md#configuration-architecture]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
