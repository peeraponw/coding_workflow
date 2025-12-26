"""Tests for agent handoff logging functionality."""

import re


from bmad_auto.shared.logging import (
    log_handoff,
    log_review_approved,
)


class TestLogHandoff:
    """Tests for log_handoff function."""

    def test_log_handoff_sm_to_dev(self, capsys) -> None:
        """Test SM → Dev handoff with reason."""
        log_handoff("SM", "DEV", "story ready for implementation")
        captured = capsys.readouterr()
        output = captured.out

        assert "HANDOFF:" in output
        assert "SM" in output
        assert "DEV" in output
        assert "→" in output
        assert "story ready for implementation" in output

    def test_log_handoff_dev_to_reviewer(self, capsys) -> None:
        """Test Dev → Reviewer handoff."""
        log_handoff("DEV", "REVIEWER", "code ready for review")
        captured = capsys.readouterr()
        output = captured.out

        assert "HANDOFF:" in output
        assert "DEV" in output
        assert "REVIEWER" in output
        assert "→" in output
        assert "code ready for review" in output

    def test_log_handoff_reviewer_to_dev(self, capsys) -> None:
        """Test Reviewer → Dev handoff (revision needed)."""
        log_handoff("REVIEWER", "DEV", "revision needed: missing error handling")
        captured = capsys.readouterr()
        output = captured.out

        assert "HANDOFF:" in output
        assert "REVIEWER" in output
        assert "DEV" in output
        assert "revision needed" in output
        assert "missing error handling" in output

    def test_log_handoff_includes_timestamp(self, capsys) -> None:
        """Test handoff includes timestamp."""
        log_handoff("SM", "DEV", "test reason")
        captured = capsys.readouterr()
        output = captured.out

        # Should contain time pattern (HH:MM:SS)
        assert re.search(r"\d{2}:\d{2}:\d{2}", output)

    def test_log_handoff_sanitizes_secrets(self, capsys) -> None:
        """Test handoff reason sanitizes sensitive data."""
        log_handoff("DEV", "REVIEWER", "Using API_KEY=secret123")
        captured = capsys.readouterr()
        output = captured.out

        assert "[REDACTED]" in output
        assert "secret123" not in output

    def test_log_handoff_agent_colors(self, capsys) -> None:
        """Test handoff uses agent colors."""
        log_handoff("SM", "DEV", "test")
        log_handoff("DEV", "REVIEWER", "test")
        log_handoff("REVIEWER", "SM", "test")

        captured = capsys.readouterr()
        output = captured.out

        # All three agents should appear in output
        assert output.count("SM") >= 2
        assert output.count("DEV") >= 2
        assert output.count("REVIEWER") >= 2

    def test_log_handoff_unknown_agent(self, capsys) -> None:
        """Test handoff with unknown agent uses default color."""
        log_handoff("UNKNOWN", "DEV", "test reason")
        captured = capsys.readouterr()
        output = captured.out

        assert "HANDOFF:" in output
        assert "UNKNOWN" in output
        assert "DEV" in output


class TestLogReviewApproved:
    """Tests for log_review_approved function."""

    def test_log_review_approved(self, capsys) -> None:
        """Test review approval logging."""
        log_review_approved()
        captured = capsys.readouterr()
        output = captured.out

        assert "REVIEW:" in output
        assert "Approved" in output
        assert "proceeding to commit" in output

    def test_log_review_approved_includes_timestamp(self, capsys) -> None:
        """Test review approval includes timestamp."""
        log_review_approved()
        captured = capsys.readouterr()
        output = captured.out

        # Should contain time pattern (HH:MM:SS)
        assert re.search(r"\d{2}:\d{2}:\d{2}", output)


class TestHandoffReasons:
    """Tests for handoff reason content."""

    def test_sm_to_dev_reason(self, capsys) -> None:
        """Test SM → Dev uses expected reason."""
        log_handoff("SM", "DEV", "story ready for implementation")
        captured = capsys.readouterr()
        output = captured.out

        assert "story ready for implementation" in output

    def test_dev_to_reviewer_reason(self, capsys) -> None:
        """Test Dev → Reviewer uses expected reason."""
        log_handoff("DEV", "REVIEWER", "code ready for review")
        captured = capsys.readouterr()
        output = captured.out

        assert "code ready for review" in output

    def test_reviewer_to_dev_reason_format(self, capsys) -> None:
        """Test Reviewer → Dev reason format."""
        log_handoff("REVIEWER", "DEV", "revision needed: type hints missing")
        captured = capsys.readouterr()
        output = captured.out

        assert "revision needed:" in output
        assert "type hints missing" in output

    def test_reason_length_limit(self, capsys) -> None:
        """Test that long reasons are handled (no crash)."""
        long_reason = "this is a very long reason that exceeds the recommended 50 character limit but should still be handled gracefully"
        log_handoff("DEV", "REVIEWER", long_reason)
        captured = capsys.readouterr()
        output = captured.out

        # Should contain key parts of the reason (Rich may add newlines and extra spaces)
        # Remove newlines and extra whitespace for assertion
        output_normalized = " ".join(output.split())
        assert "exceeds" in output_normalized
        assert "recommended" in output_normalized
        assert "handled gracefully" in output_normalized

    def test_empty_reason(self, capsys) -> None:
        """Test empty reason is handled."""
        log_handoff("SM", "DEV", "")
        captured = capsys.readouterr()
        output = captured.out

        # Should still have HANDOFF prefix
        assert "HANDOFF:" in output
