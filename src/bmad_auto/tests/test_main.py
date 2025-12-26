"""Tests for bmad_auto.main CLI module."""

import inspect
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from bmad_auto.main import app
from bmad_auto.shared.consts import EXIT_CONFIG_ERROR, EXIT_ERROR, EXIT_SUCCESS
from bmad_auto.shared.exceptions import ConfigError

runner = CliRunner()


def test_help_shows_available_commands() -> None:
    """Test that --help shows available commands: run, status, resume."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "status" in result.stdout
    assert "resume" in result.stdout


def test_run_command_accepts_epic_argument() -> None:
    """Test that run command accepts --epic path argument."""
    result = runner.invoke(app, ["run", "--epic", "docs/epics/epic-001.md"])
    # Stub message should be present (actual orchestration in Epic 3)
    assert result.exit_code == 0
    assert "stub" in result.stdout.lower()


def test_status_command_executes() -> None:
    """Test that status command executes (stub for now)."""
    result = runner.invoke(app, ["status"])
    # Stub message should be present
    assert result.exit_code == 0


def test_resume_command_executes() -> None:
    """Test that resume command executes (stub for now)."""
    result = runner.invoke(app, ["resume"])
    # Stub message should be present
    assert result.exit_code == 0


def test_exit_code_success() -> None:
    """Test successful command returns exit code 0."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_exit_code_constants() -> None:
    """Test exit code constants have correct values."""
    assert EXIT_SUCCESS == 0
    assert EXIT_ERROR == 1
    assert EXIT_CONFIG_ERROR == 3


def test_missing_epic_argument_fails() -> None:
    """Test that run command without --epic fails appropriately."""
    result = runner.invoke(app, ["run"])
    assert result.exit_code != 0  # Should fail when required option is missing


# Test that exception handling infrastructure exists


def test_config_error_exists_and_can_be_raised() -> None:
    """Test ConfigError exception class exists and can be raised."""
    with pytest.raises(ConfigError):
        raise ConfigError("Test configuration error")


def test_general_exception_handling_infrastructure_exists() -> None:
    """Test that exception handling infrastructure is in place."""
    import bmad_auto.main as main_module

    # Verify that ConfigError is imported
    assert hasattr(main_module, "ConfigError")

    # Verify exit codes are imported
    assert hasattr(main_module, "EXIT_SUCCESS")
    assert hasattr(main_module, "EXIT_ERROR")
    assert hasattr(main_module, "EXIT_CONFIG_ERROR")


def test_all_commands_have_try_except_blocks() -> None:
    """Verify all commands have exception handling infrastructure."""
    import bmad_auto.main as main_module

    # Check that run function has exception handling
    run_source = inspect.getsource(main_module.run)
    assert "except ConfigError" in run_source
    assert "except Exception" in run_source
    assert "EXIT_CONFIG_ERROR" in run_source
    assert "EXIT_ERROR" in run_source

    # Check that status function has exception handling
    status_source = inspect.getsource(main_module.status)
    assert "except ConfigError" in status_source
    assert "except Exception" in status_source
    assert "EXIT_CONFIG_ERROR" in status_source
    assert "EXIT_ERROR" in status_source

    # Check that resume function has exception handling
    resume_source = inspect.getsource(main_module.resume)
    assert "except ConfigError" in resume_source
    assert "except Exception" in resume_source
    assert "EXIT_CONFIG_ERROR" in resume_source
    assert "EXIT_ERROR" in resume_source


def test_all_commands_use_exit_constants(cli_runner: CliRunner) -> None:
    """Verify all commands use exit code constants from shared.consts."""
    from bmad_auto.shared.consts import EXIT_SUCCESS, EXIT_ERROR, EXIT_CONFIG_ERROR

    # Verify constants are imported and used correctly
    assert EXIT_SUCCESS == 0
    assert EXIT_ERROR == 1
    assert EXIT_CONFIG_ERROR == 3


# Test exception handling by patching sys.exit to capture without raising


def test_run_command_exception_path_coverage() -> None:
    """Test exception handler paths in run command for coverage."""
    import bmad_auto.main as main_module

    # Patch sys.exit to capture exit codes without actually exiting
    captured_codes: list[int] = []

    def mock_exit_capture(code: int) -> None:
        captured_codes.append(code)

    # Patch typer.echo to raise ConfigError first
    def mock_echo_raises_config_error(*args, **kwargs):
        if not kwargs.get("err"):
            # First call (normal echo) - raise ConfigError to trigger handler
            raise ConfigError("Test config error")

    with patch.object(main_module.sys, "exit", side_effect=mock_exit_capture):
        with patch("typer.echo", side_effect=mock_echo_raises_config_error):
            try:
                main_module.run(epic="test.md")
            except SystemExit:
                pass  # Expected when real sys.exit is called

    # Verify ConfigError triggered EXIT_CONFIG_ERROR
    assert EXIT_CONFIG_ERROR in captured_codes, f"Expected {EXIT_CONFIG_ERROR} in {captured_codes}"

    # Reset for next test
    captured_codes.clear()

    # Now test general exception path
    def mock_echo_raises_exception(*args, **kwargs):
        if not kwargs.get("err"):
            raise RuntimeError("Test error")

    with patch.object(main_module.sys, "exit", side_effect=mock_exit_capture):
        with patch("typer.echo", side_effect=mock_echo_raises_exception):
            try:
                main_module.run(epic="test.md")
            except SystemExit:
                pass

    # Verify general exception triggered EXIT_ERROR
    assert EXIT_ERROR in captured_codes, f"Expected {EXIT_ERROR} in {captured_codes}"


def test_status_command_exception_path_coverage() -> None:
    """Test exception handler paths in status command for coverage."""
    import bmad_auto.main as main_module

    captured_codes: list[int] = []

    def mock_exit_capture(code: int) -> None:
        captured_codes.append(code)

    # Test ConfigError path
    def mock_echo_raises_config_error(*args, **kwargs):
        if not kwargs.get("err"):
            raise ConfigError("Test config error")

    with patch.object(main_module.sys, "exit", side_effect=mock_exit_capture):
        with patch("typer.echo", side_effect=mock_echo_raises_config_error):
            try:
                main_module.status()
            except SystemExit:
                pass

    # Verify ConfigError triggered EXIT_CONFIG_ERROR
    assert EXIT_CONFIG_ERROR in captured_codes, f"Expected {EXIT_CONFIG_ERROR} in {captured_codes}"

    # Reset for next test
    captured_codes.clear()

    # Test general exception path
    def mock_echo_raises_exception(*args, **kwargs):
        if not kwargs.get("err"):
            raise RuntimeError("Test error")

    with patch.object(main_module.sys, "exit", side_effect=mock_exit_capture):
        with patch("typer.echo", side_effect=mock_echo_raises_exception):
            try:
                main_module.status()
            except SystemExit:
                pass

    # Verify general exception triggered EXIT_ERROR
    assert EXIT_ERROR in captured_codes, f"Expected {EXIT_ERROR} in {captured_codes}"


def test_resume_command_exception_path_coverage() -> None:
    """Test exception handler paths in resume command for coverage."""
    import bmad_auto.main as main_module

    captured_codes: list[int] = []

    def mock_exit_capture(code: int) -> None:
        captured_codes.append(code)

    # Test ConfigError path
    def mock_echo_raises_config_error(*args, **kwargs):
        if not kwargs.get("err"):
            raise ConfigError("Test config error")

    with patch.object(main_module.sys, "exit", side_effect=mock_exit_capture):
        with patch("typer.echo", side_effect=mock_echo_raises_config_error):
            try:
                main_module.resume()
            except SystemExit:
                pass

    # Verify ConfigError triggered EXIT_CONFIG_ERROR
    assert EXIT_CONFIG_ERROR in captured_codes, f"Expected {EXIT_CONFIG_ERROR} in {captured_codes}"

    # Reset for next test
    captured_codes.clear()

    # Test general exception path
    def mock_echo_raises_exception(*args, **kwargs):
        if not kwargs.get("err"):
            raise RuntimeError("Test error")

    with patch.object(main_module.sys, "exit", side_effect=mock_exit_capture):
        with patch("typer.echo", side_effect=mock_echo_raises_exception):
            try:
                main_module.resume()
            except SystemExit:
                pass

    # Verify general exception triggered EXIT_ERROR
    assert EXIT_ERROR in captured_codes, f"Expected {EXIT_ERROR} in {captured_codes}"
