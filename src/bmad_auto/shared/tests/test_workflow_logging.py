"""Tests for workflow logging functionality in shared/logging.py."""

import re


from bmad_auto.shared.logging import (
    sanitize_log,
    log_phase,
    log_workflow_start,
    log_phase_start,
    log_phase_complete,
    log_story_complete,
    log_error,
    AGENT_COLORS,
    SENSITIVE_PATTERNS,
)


class TestSanitizeLog:
    """Tests for sanitize_log function (NFR14)."""

    def test_redact_anthropic_api_key(self) -> None:
        """Test ANTHROPIC_API_KEY is redacted."""
        message = "Connecting with ANTHROPIC_API_KEY=sk-ant-1234567890"
        result = sanitize_log(message)
        assert "[REDACTED]" in result
        assert "sk-ant-1234567890" not in result

    def test_redact_api_key_variations(self) -> None:
        """Test various api_key patterns are redacted."""
        # Underscore version
        assert "[REDACTED]" in sanitize_log("api_key=secret123")
        # Hyphen version
        assert "[REDACTED]" in sanitize_log("api-key=secret123")
        # With colon
        assert "[REDACTED]" in sanitize_log("api_key:secret123")
        # Case insensitive
        assert "[REDACTED]" in sanitize_log("API_KEY=secret123")

    def test_redact_token(self) -> None:
        """Test token patterns are redacted."""
        assert "[REDACTED]" in sanitize_log("token=abc123xyz")
        assert "[REDACTED]" in sanitize_log("token:abc123xyz")

    def test_redact_bearer_token(self) -> None:
        """Test bearer tokens are redacted."""
        assert "[REDACTED]" in sanitize_log("Authorization: Bearer eyJhbGciOi...")
        assert "eyJhbGciOi..." not in sanitize_log("Authorization: Bearer eyJhbGciOi...")

    def test_redact_password(self) -> None:
        """Test password patterns are redacted."""
        assert "[REDACTED]" in sanitize_log("password=mypass123")
        assert "[REDACTED]" in sanitize_log("password:mypass123")

    def test_no_redaction_in_safe_message(self) -> None:
        """Test safe messages are not modified."""
        message = "Starting story 1 of 5"
        result = sanitize_log(message)
        assert result == message

    def test_multiple_secrets_redacted(self) -> None:
        """Test multiple secrets in one message are all redacted."""
        message = "api_key=secret123 and token=bearer456"
        result = sanitize_log(message)
        assert result.count("[REDACTED]") >= 2
        assert "secret123" not in result
        assert "bearer456" not in result


class TestAgentColors:
    """Tests for AGENT_COLORS constant."""

    def test_all_agent_colors_defined(self) -> None:
        """Test all expected agents have color definitions."""
        expected_agents = ["WORKFLOW", "SM", "DEV", "REVIEWER", "ERROR", "GIT"]
        for agent in expected_agents:
            assert agent in AGENT_COLORS
            assert isinstance(AGENT_COLORS[agent], str)

    def test_sm_color_is_blue(self) -> None:
        """Test SM uses blue color."""
        assert AGENT_COLORS["SM"] == "blue"

    def test_dev_color_is_green(self) -> None:
        """Test DEV uses green color."""
        assert AGENT_COLORS["DEV"] == "green"

    def test_reviewer_color_is_yellow(self) -> None:
        """Test REVIEWER uses yellow color."""
        assert AGENT_COLORS["REVIEWER"] == "yellow"

    def test_error_color_is_red(self) -> None:
        """Test ERROR uses red color."""
        assert AGENT_COLORS["ERROR"] == "red"


class TestSensitivePatterns:
    """Tests for SENSITIVE_PATTERNS constant."""

    def test_sensitive_patterns_are_compiled_regex(self) -> None:
        """Test all sensitive patterns are compiled regex patterns."""
        assert all(isinstance(p, re.Pattern) for p in SENSITIVE_PATTERNS)

    def test_sensitive_patterns_match_secrets(self) -> None:
        """Test patterns match actual secret formats."""
        # ANTHROPIC_API_KEY pattern
        assert SENSITIVE_PATTERNS[0].search("ANTHROPIC_API_KEY=sk-ant-123")
        # API key pattern
        assert SENSITIVE_PATTERNS[1].search("api_key=secret")
        # Token pattern
        assert SENSITIVE_PATTERNS[2].search("token=abc123")
        # Bearer pattern
        assert SENSITIVE_PATTERNS[3].search("Bearer eyJhbGc")
        # Password pattern
        assert SENSITIVE_PATTERNS[4].search("password=mypass")


class TestLogPhase:
    """Tests for log_phase function."""

    def test_log_phase_outputs_timestamp(self, capsys) -> None:
        """Test log_phase includes ISO timestamp."""
        log_phase("SM", "Test message")
        captured = capsys.readouterr()
        output = captured.out

        # Should contain timestamp-like pattern (YYYY-MM-DDTHH:MM:SS)
        assert re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", output)

    def test_log_phase_outputs_agent(self, capsys) -> None:
        """Test log_phase includes agent name."""
        log_phase("DEV", "Test message")
        captured = capsys.readouterr()
        output = captured.out

        assert "DEV:" in output

    def test_log_phase_outputs_message(self, capsys) -> None:
        """Test log_phase includes the message."""
        log_phase("WORKFLOW", "Starting epic")
        captured = capsys.readouterr()
        output = captured.out

        assert "Starting epic" in output

    def test_log_phase_sanitizes_secrets(self, capsys) -> None:
        """Test log_phase sanitizes sensitive data."""
        log_phase("DEV", "Using API_KEY=secret123")
        captured = capsys.readouterr()
        output = captured.out

        assert "[REDACTED]" in output
        assert "secret123" not in output


class TestLogWorkflowStart:
    """Tests for log_workflow_start function."""

    def test_log_workflow_start(self, capsys) -> None:
        """Test logging workflow start."""
        log_workflow_start("docs/epics/epic-001.md")
        captured = capsys.readouterr()
        output = captured.out

        assert "WORKFLOW:" in output
        assert "Starting epic" in output
        assert "docs/epics/epic-001.md" in output


class TestLogPhaseStart:
    """Tests for log_phase_start function."""

    def test_log_phase_start(self, capsys) -> None:
        """Test logging phase start."""
        log_phase_start("SM", 1, 5)
        captured = capsys.readouterr()
        output = captured.out

        assert "SM:" in output
        assert "Creating story 1 of 5" in output


class TestLogPhaseComplete:
    """Tests for log_phase_complete function."""

    def test_log_phase_complete(self, capsys) -> None:
        """Test logging phase complete."""
        log_phase_complete("DEV", "Implementation complete (3 files modified)")
        captured = capsys.readouterr()
        output = captured.out

        assert "DEV:" in output
        assert "Implementation complete" in output


class TestLogStoryComplete:
    """Tests for log_story_complete function."""

    def test_log_story_complete_basic(self, capsys) -> None:
        """Test logging story complete without file count."""
        log_story_complete("1-1")
        captured = capsys.readouterr()
        output = captured.out

        assert "DEV:" in output
        assert "Story complete" in output
        assert "1-1" in output

    def test_log_story_complete_with_files(self, capsys) -> None:
        """Test logging story complete with file count."""
        log_story_complete("1-2", files_modified=3)
        captured = capsys.readouterr()
        output = captured.out

        assert "DEV:" in output
        assert "3 files modified" in output


class TestLogError:
    """Tests for log_error function."""

    def test_log_error(self, capsys) -> None:
        """Test logging error."""
        log_error("rate_limit", "API rate limit exceeded")
        captured = capsys.readouterr()
        output = captured.out

        assert "ERROR:" in output
        assert "rate_limit" in output
        assert "API rate limit exceeded" in output

    def test_log_error_sanitizes_secrets(self, capsys) -> None:
        """Test log_error sanitizes sensitive data."""
        log_error("api_error", "Failed with token=bearer123")
        captured = capsys.readouterr()
        output = captured.out

        assert "[REDACTED]" in output
        assert "bearer123" not in output
