"""CLI entry point for BMAD automation."""

import argparse
import asyncio
from pathlib import Path

from bmad_automation.core.config import get_settings, load_bmad_config
from bmad_automation.core.logging import get_logger, setup_logging
from bmad_automation.features.workflows import run_epic_cycle

logger = get_logger(__name__)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BMAD Implementation Automation",
        epilog="Expects bmad.yaml in the current directory (or use --config to specify).",
    )
    parser.add_argument("epic", type=Path, help="Path to epic file")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("bmad.yaml"),
        help="Path to bmad.yaml (default: ./bmad.yaml)",
    )
    parser.add_argument("--log-level", default="INFO", help="Log level")
    args = parser.parse_args()

    setup_logging(args.log_level)

    try:
        bmad_config = load_bmad_config(args.config)
    except FileNotFoundError as e:
        logger.error(str(e))
        parser.error(f"Config not found: {args.config}")

    settings = get_settings()

    logger.info(
        "Starting BMAD automation",
        extra={"epic": str(args.epic), "config": str(args.config)},
    )
    asyncio.run(run_epic_cycle(args.epic, bmad_config, settings))


if __name__ == "__main__":
    main()
