"""External CLI wrapper with auto-detection from config file extension."""

import subprocess
from pathlib import Path

from bmad_automation.core.logging import get_logger
from bmad_automation.shared.consts import CLI_TIMEOUT_SECONDS
from bmad_automation.shared.exceptions import CliExecutionError

logger = get_logger(__name__)


def detect_cli_tool(config_path: Path) -> str:
    """Detect CLI tool from config file extension."""
    suffix = config_path.suffix.lower()
    if suffix == ".toml":
        return "codex"
    elif suffix == ".json":
        return "claude"
    else:
        raise CliExecutionError(f"Unknown config format: {suffix}. Expected .toml or .json")


def run_coding_agent(prompt: str, config_path: Path, cwd: Path) -> str:
    """Execute coding agent with auto-detected CLI tool."""
    cli_tool = detect_cli_tool(config_path)

    if cli_tool == "codex":
        cmd = ["codex", "--config", str(config_path), prompt]
    else:  # claude
        cmd = ["claude", "--settings", str(config_path), prompt]

    logger.info(
        "Executing CLI",
        extra={"cli_tool": cli_tool, "config": str(config_path), "cwd": str(cwd)},
    )

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=CLI_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CliExecutionError(f"CLI timed out after {CLI_TIMEOUT_SECONDS}s") from exc
    except FileNotFoundError as exc:
        raise CliExecutionError(f"CLI tool '{cli_tool}' not found. Is it installed?") from exc

    if result.returncode != 0:
        raise CliExecutionError(f"CLI failed (exit {result.returncode}): {result.stderr}")

    return result.stdout
