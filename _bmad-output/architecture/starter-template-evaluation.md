# Starter Template Evaluation

## Primary Technology Domain

Python CLI Tool (uvx-distributable) based on project requirements analysis.

## Starter Options Considered

| Option | Structure | Pros | Cons |
|--------|-----------|------|------|
| `uv init --package` | src/ layout + hatchling | Simple, matches PRD | Manual tooling setup |
| cookiecutter-uv | Full template | Pre-configured quality tools | Extra files |
| The Hatchlor | Hatch-focused | Deep hatch integration | Hatch-specific |

## Selected Starter: `uv init --package`

**Rationale for Selection:**
- Matches the PRD specification for uvx distribution
- Uses hatchling as already identified in technical research
- Minimal complexity appropriate for solo developer project
- Clean slate for adding project-specific dependencies

**Initialization Command:**

```bash
uv init --package --build-backend hatchling bmad-auto
cd bmad-auto
uv add typer[all] pyyaml claude-agent-sdk
```

## Architectural Decisions Provided by Starter

**Language & Runtime:**
- Python 3.11+ (modern async support)
- Type hints encouraged (Typer leverages them)

**Build System:**
- hatchling backend
- pyproject.toml-only configuration
- `[project.scripts]` entry point for CLI

**CLI Framework:**
- Typer for declarative command structure
- Rich integration for terminal output (via typer[all])
- Manual `asyncio.run()` wrapper for async commands

**Configuration Format:**
- YAML for all configuration (`.bmad-auto.yaml`)
- YAML for state persistence (`.bmad-auto-state.yaml`)
- YAML for inter-agent handoff files
- Rationale: Consistency across all project files over Python convention

**Project Structure:**
```
bmad-auto/
├── pyproject.toml
├── README.md
├── src/
│   └── bmad_auto/
│       ├── __init__.py
│       └── main.py      # CLI entry point
└── uv.lock
```

**Note:** Project initialization using this command should be the first implementation story.
