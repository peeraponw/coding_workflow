# Story 2.1: Epic File Parser

Status: ready-for-dev

## Story

As a **user**,
I want **bmad-auto to parse my epic markdown files**,
so that **stories can be extracted and executed sequentially**.

## Acceptance Criteria

1. **Given** an epic file in standard BMAD markdown format with `# Epic:` header and `# Story N:` sections, **When** I run `bmad-auto run --epic path/to/epic.md`, **Then** the parser extracts: epic title and description, list of stories with their content, story count for progress tracking
2. **Given** an epic file with invalid format, **When** parsing is attempted, **Then** a clear error message identifies the parsing issue
3. Parser handles edge cases (empty stories, missing sections)
4. Tests cover valid epics, malformed epics, and edge cases (FR3)

## Tasks / Subtasks

- [ ] Task 1: Create epic parser module (AC: 1)
  - [ ] Create parser in appropriate location (consider core/ or features/)
  - [ ] Define Epic dataclass with title, description, stories list
  - [ ] Define Story dataclass with id, title, content
- [ ] Task 2: Implement markdown parsing (AC: 1)
  - [ ] Parse `# Epic:` header for title
  - [ ] Parse description between epic header and first story
  - [ ] Parse `# Story N:` or `## Story N.M:` patterns
  - [ ] Extract story content including acceptance criteria
  - [ ] Return story count for progress tracking
- [ ] Task 3: Implement error handling (AC: 2)
  - [ ] Raise descriptive error if no epic header found
  - [ ] Raise descriptive error if no stories found
  - [ ] Include line numbers in error messages
- [ ] Task 4: Handle edge cases (AC: 3)
  - [ ] Handle empty story content gracefully
  - [ ] Handle missing description
  - [ ] Handle various markdown heading styles
- [ ] Task 5: Write comprehensive tests (AC: 4)
  - [ ] Test valid epic parsing
  - [ ] Test malformed epic (no header)
  - [ ] Test malformed epic (no stories)
  - [ ] Test edge cases

## Dev Notes

### Architecture Patterns & Constraints

- Parser should be pure function with no side effects
- Return typed dataclasses (Epic, Story)
- Use regex for pattern matching markdown headers
- Raise custom exceptions from shared/exceptions.py

### Expected Epic Format

```markdown
# Epic: User Authentication

Description of the epic goes here.

## Story 1.1: User Registration

...acceptance criteria...

## Story 1.2: User Login

...acceptance criteria...
```

### Data Structures

```python
@dataclass
class Story:
    id: str           # e.g., "1.1"
    title: str        # e.g., "User Registration"
    content: str      # Full markdown content

@dataclass
class Epic:
    title: str
    description: str
    stories: list[Story]

    @property
    def story_count(self) -> int:
        return len(self.stories)
```

### Source Tree Components

```
src/bmad_auto/core/
├── parser.py       # Epic file parser
└── tests/
    └── test_parser.py
```

### Testing Standards

- Use fixture files for test epics
- Test with realistic epic content
- Verify story extraction accuracy

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-2-state-persistence-resume-capability.md#story-21-epic-file-parser]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#data-flow]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
