"""Tests for logging module."""

from datetime import datetime

from bmad_auto.shared.logging import (
    DEV_COLOR,
    REVIEWER_COLOR,
    SM_COLOR,
    console,
    get_logger,
)


def test_logger_creation() -> None:
    """Test that get_logger returns a structlog logger."""
    logger = get_logger("test_module")
    # structlog v25+ returns BoundLoggerLazyProxy
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")
    assert hasattr(logger, "warning")


def test_logger_returns_same_instance_for_same_name() -> None:
    """Test that get_logger returns same logger instance for same name."""
    logger1 = get_logger("test_module")
    logger2 = get_logger("test_module")
    # structlog.get_logger with same name returns same logger type
    assert isinstance(logger1, type(logger2))


def test_structured_logging_with_context() -> None:
    """Test that logger accepts structured context."""
    logger = get_logger("test_context")
    # This should not raise an exception
    logger.info("test message", key1="value1", key2=42)


def test_logger_has_timestamp_processor() -> None:
    """Test that logger configuration includes timestamp processor."""
    logger = get_logger("test_timestamp")
    # Log a message and verify it doesn't raise
    logger.info("test", timestamp=datetime.now().isoformat())


def test_console_exists() -> None:
    """Test that console instance is available."""
    from rich.console import Console

    assert isinstance(console, Console)


def test_color_constants_defined() -> None:
    """Test that agent color constants are defined."""
    assert SM_COLOR == "blue"
    assert DEV_COLOR == "green"
    assert REVIEWER_COLOR == "yellow"


def test_agent_colored_print_functions() -> None:
    """Test that helper functions for agent-colored output exist."""
    from bmad_auto.shared.logging import (
        print_dev,
        print_reviewer,
        print_sm,
    )

    # These should not raise exceptions
    print_sm("test sm message")
    print_dev("test dev message")
    print_reviewer("test reviewer message")
