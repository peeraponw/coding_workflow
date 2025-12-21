"""Centralized constant values used across the project."""

CLI_CLAUDE = "claude"
CLI_CODEX = "codex"

DEFAULT_STATE_DIR = ".bmad-auto/state"
DEFAULT_CONFIG_FILE = ".bmad-auto/config.yaml"
USER_CONFIG_DIR = "~/.config/bmad-auto"

MAX_DEV_ATTEMPTS = 3
DEFAULT_AGENT_TIMEOUT = 600

MARKER_NO_MORE_STORIES = "NO_MORE_STORIES"
MARKER_REVIEW_APPROVED = "APPROVED"
MARKER_REVIEW_REJECTED = "REJECTED"

GIT_BRANCH_PREFIX = "bmad"
GIT_COMMIT_PREFIX = "feat(bmad):"

DEFAULT_EPIC_PATTERNS = (
    "docs/epics/*.md",
    "docs/epics/**/*.md",
)
DEFAULT_STORY_OUTPUT_DIR = "docs/stories"

DEFAULT_TEMPLATES_DIR = "templates"
TEMPLATE_EXTENSION = ".md"

ROLE_SCRUM_MASTER = "scrum_master"
ROLE_DEVELOPER = "developer"
ROLE_REVIEWER = "reviewer"
ROLE_TECH_WRITER = "tech_writer"

STORY_ID_PATTERN = r"^[A-Za-z0-9_-]+$"
