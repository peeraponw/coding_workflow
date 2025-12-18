# BMAD Methodology Reference

**Source**: [BMAD-METHOD GitHub](https://github.com/bmad-code-org/BMAD-METHOD)
**Date Researched**: December 2025

---

## What is BMAD?

BMAD (Breakthrough Method for Agile AI-Driven Development) is a comprehensive, open-source framework designed to bring structure, collaboration, and engineering discipline to AI-powered development.

---

## Core Philosophy

BMAD is built on two key innovations:

1. **Agentic Planning**: Employs a team of dedicated AI agents (Analyst, Project Manager, Architect) that collaborate to create detailed, consistent PRDs and System Architecture

2. **Core Development Cycle**: A team of agents (Story Master, Developer, QA) work through "story files" in a structured, agile-like workflow, ensuring robust, tested code aligned with the initial vision

---

## Development Lifecycle Phases

### Phase 1: Analysis (Optional)
- Brainstorming and research
- Solution exploration
- Requirements gathering

### Phase 2: Planning
- Creating Product Requirement Documents (PRDs)
- Technical specifications
- Design documents

### Phase 3: Solutioning
- System architecture design
- UX design
- Technical approach definition

### Phase 4: Implementation
- Story-driven development
- Continuous validation
- Code review cycles

---

## Specialized Agent Roles

BMAD employs 12+ specialized agents:

| Agent | Role | Tier |
|-------|------|------|
| **Product Manager** | Requirements and vision | High |
| **Analyst** | Requirements analysis | High |
| **Architect** | System design and technical decisions | High |
| **Scrum Master** | Process management and coordination | High |
| **Developer** | Code implementation | Low |
| **Test Architect** | Quality assurance strategy | High |
| **UX Designer** | User experience design | High |
| **Tech Writer** | Documentation | High |
| **BMad Master** | Overall coordination | High |

### For bmad-auto Implementation

| Phase | Agent | Tier | Description |
|-------|-------|------|-------------|
| CREATE_STORY | Scrum Master | High | Generate next story from epic |
| VALIDATE_STORY | Scrum Master | High | Validate story quality |
| ADD_CONTEXT | Scrum Master | High | Add context if story needs detail |
| DEVELOP | Developer | Low | Implement the story |
| CODE_REVIEW | Reviewer | High | Review implementation |
| RETROSPECTIVE | Scrum Master | High | Review completed stories |
| DOCUMENTATION | Tech Writer | High | Generate/update documentation |

---

## Epic and Story Structure

### Epic Sharding

The comprehensive PRD is systematically broken down into focused, self-contained development units called "epics". Each epic is then "sharded" into individual stories.

This addresses "context collapse" - the gradual decline of AI understanding as projects grow. Sharding reduces token usage by up to 90%.

### Epic File Structure
```markdown
# Epic: [Epic ID] - [Title]

## Description
[High-level description of the epic]

## Dependencies
- [List of dependent epics]

## Stories
1. [Story ID] - [Story Title]
2. [Story ID] - [Story Title]
...

## Acceptance Criteria
- [Epic-level acceptance criteria]

## Technical Context
[References to architecture documents, tech stack details]
```

### Story File Structure
```markdown
# Story: [Story ID] - [Title]

## Context
[Full implementation context from epic and architecture]

## Acceptance Criteria
Given [precondition]
When [action]
Then [expected result]

## Technical Notes
[Specific technical guidance from architecture]

## Checklist
- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Write tests
- [ ] Update documentation
```

---

## Scale-Adaptive Intelligence

BMAD automatically adjusts planning depth based on project complexity:

| Scale | Use Case | Components | Time |
|-------|----------|------------|------|
| **Quick Flow** | Bug fixes, small features | Technical spec only | <5 min |
| **BMad Method** | Products, platforms | PRD + Architecture + UX | <15 min |
| **Enterprise** | Compliance, scale | Full governance suite | <30 min |

---

## Story-Driven Development Loop

The core development cycle (as specified in bmad-auto):

```
FOR each story in epic:
    1. CREATE_STORY (scrum master) -> story file
    2. IF story needs context:
         ADD_CONTEXT (scrum master) -> updated story
    3. DEVELOPMENT LOOP (max N attempts):
         a. DEVELOP (developer) -> code changes
         b. CODE_REVIEW (reviewer) -> pass/fail
         c. IF pass: break loop
         d. IF fail: continue loop with feedback
    4. IF all attempts failed: mark story failed, continue
    5. COMMIT changes
    6. Mark story completed
END FOR

RETROSPECTIVE (scrum master)
DOCUMENTATION (tech writer)
CREATE_PR
```

---

## Key Markers

For parsing agent output:

| Marker | Purpose |
|--------|---------|
| `NO_MORE_STORIES` | Scrum master signals all stories created |
| `APPROVED` | Reviewer approves code changes |
| `REJECTED` | Reviewer rejects code changes |

---

## File Organization Conventions

### Epic Location
```
docs/epics/
├── epic-001.md
├── epic-002.md
└── epic-003/
    └── epic-003.md
```

### Story Output Location
```
docs/stories/
├── epic-001/
│   ├── story-001.md
│   ├── story-002.md
│   └── story-003.md
└── epic-002/
    └── ...
```

---

## Benefits of BMAD

1. **Context-Engineered Development**: Solves context collapse through epic sharding
2. **Reduced Token Usage**: Up to 90% reduction through focused story units
3. **Consistent Architecture**: Agents maintain alignment with initial vision
4. **Quality Assurance**: Built-in review cycles catch issues early
5. **Documentation**: Automated documentation generation

---

## Integration with IDE Tools

BMAD works with:
- Claude Code
- Cursor
- Windsurf
- VS Code

---

## Installation

```bash
npx bmad-method install
```

---

## Sources

- [GitHub - bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- [What is BMAD-METHOD? - Medium](https://medium.com/@visrow/what-is-bmad-method-a-simple-guide-to-the-future-of-ai-driven-development-412274f91419)
- [Using Cursor AI with the BMAD Method](https://www.geeky-gadgets.com/bmad-agile-ai-coding-method/)
- [Applied BMAD - Reclaiming Control in AI Development](https://bennycheung.github.io/bmad-reclaiming-control-in-ai-dev)
- [BMad Method Agentic Agile AI Development Framework](https://bmadcodes.com/bmad-method/)
