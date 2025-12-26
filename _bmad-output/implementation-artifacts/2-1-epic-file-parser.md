# Story 2.1: Epic File Parser

Status: done

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

- [x] Task 1: Create epic parser module (AC: 1)
  - [x] Create parser in appropriate location (consider core/ or features/)
  - [x] Define Epic dataclass with title, description, stories list
  - [x] Define Story dataclass with id, title, content
- [x] Task 2: Implement markdown parsing (AC: 1)
  - [x] Parse `# Epic:` header for title
  - [x] Parse description between epic header and first story
  - [x] Parse `# Story N:` or `## Story N.M:` patterns
  - [x] Extract story content including acceptance criteria
  - [x] Return story count for progress tracking
- [x] Task 3: Implement error handling (AC: 2)
  - [x] Raise descriptive error if no epic header found
  - [x] Raise descriptive error if no stories found
  - [x] Include line numbers in error messages
- [x] Task 4: Handle edge cases (AC: 3)
  - [x] Handle empty story content gracefully
  - [x] Handle missing description
  - [x] Handle various markdown heading styles
- [x] Task 5: Write comprehensive tests (AC: 4)
  - [x] Test valid epic parsing
  - [x] Test malformed epic (no header)
  - [x] Test malformed epic (no stories)
  - [x] Test edge cases

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

claude-opus-4-5-20251101

### Debug Log References

None - implementation completed without issues.

### Completion Notes List

- Implemented `parse_epic()` pure function following TDD red-green-refactor cycle
- Created dataclasses `Story` and `Epic` with frozen immutability
- Used verbose regex with `re.VERBOSE` for maintainable pattern matching
- ParseError includes line numbers for debugging
- All 9 tests pass (valid, malformed, edge cases)
- Full test suite (94 tests) passes with no regressions

### File List

- `src/bmad_auto/core/parser.py` (new) - Epic parser module with dataclasses and parse_epic function
- `src/bmad_auto/core/tests/test_parser.py` (new) - Comprehensive test suite with fixtures
