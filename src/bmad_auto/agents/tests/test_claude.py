"""Tests for Claude Agent SDK adapter."""

import os
import pytest
from typing import NamedTuple
from unittest.mock import patch

from bmad_auto.agents.claude import ClaudeAgent
from bmad_auto.agents.base import AgentResult


class MockMessage(NamedTuple):
    """Mock SDK message."""

    type: str
    delta: str | None = None
    result: str | None = None
    error: str | None = None


class TestClaudeAgentInit:
    """Test ClaudeAgent initialization."""

    def test_init_with_use_logged_in(self) -> None:
        """Should initialize with use_logged_in=True."""
        agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
        assert agent.working_dir == "/project"
        assert agent.use_logged_in is True
        assert agent.api_key is None

    def test_init_with_api_key(self) -> None:
        """Should initialize with api_key."""
        agent = ClaudeAgent(
            working_dir="/project", use_logged_in=False, api_key="sk-test-key"
        )
        assert agent.working_dir == "/project"
        assert agent.use_logged_in is False
        assert agent.api_key == "sk-test-key"

    def test_init_without_auth_fails(self) -> None:
        """Should raise ValueError if neither use_logged_in nor api_key."""
        with pytest.raises(ValueError, match="Either use_logged_in=True or api_key"):
            ClaudeAgent(working_dir="/project", use_logged_in=False, api_key=None)


class TestClaudeAgentRun:
    """Test ClaudeAgent.run method."""

    @pytest.mark.asyncio
    async def test_run_success_with_output(self) -> None:
        """Should return AgentResult.ok() on successful execution."""
        # Mock SDK messages
        async def mock_query(*args, **kwargs):
            yield MockMessage(type="content", delta="Processing...")
            yield MockMessage(type="result", result="Task completed successfully")

        with patch("claude_agent_sdk.query", mock_query):
            agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
            result = await agent.run("/bmad:bmm:agents:sm create stories")

        assert result.success is True
        assert "Task completed successfully" in result.output
        assert result.error is None

    @pytest.mark.asyncio
    async def test_run_success_with_content_deltas(self) -> None:
        """Should combine content deltas with result."""
        async def mock_query(*args, **kwargs):
            yield MockMessage(type="content", delta="Step 1")
            yield MockMessage(type="content", delta="Step 2")
            yield MockMessage(type="result", result="Done")

        with patch("claude_agent_sdk.query", mock_query):
            agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
            result = await agent.run("test command")

        assert result.success is True
        assert "Step 1" in result.output
        assert "Step 2" in result.output
        assert "Done" in result.output

    @pytest.mark.asyncio
    async def test_run_sdk_error_message(self) -> None:
        """Should return AgentResult.fail() on SDK error message."""
        async def mock_query(*args, **kwargs):
            yield MockMessage(type="error", error="API request failed")

        with patch("claude_agent_sdk.query", mock_query):
            agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
            result = await agent.run("test command")

        assert result.success is False
        assert result.error == "API request failed"

    @pytest.mark.asyncio
    async def test_run_exception_auth_error(self) -> None:
        """Should map auth exceptions to meaningful error."""
        with patch(
            "claude_agent_sdk.query",
            side_effect=Exception("Invalid api_key credential"),
        ):
            agent = ClaudeAgent(
                working_dir="/project", use_logged_in=False, api_key="bad-key"
            )
            result = await agent.run("test command")

        assert result.success is False
        assert result.error is not None
        assert "Authentication failed" in result.error

    @pytest.mark.asyncio
    async def test_run_exception_rate_limit(self) -> None:
        """Should detect rate limit errors."""
        with patch(
            "claude_agent_sdk.query", side_effect=Exception("Rate limit exceeded")
        ):
            agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
            result = await agent.run("test command")

        assert result.success is False
        assert result.error is not None
        assert "Rate limit" in result.error

    @pytest.mark.asyncio
    async def test_run_exception_timeout(self) -> None:
        """Should detect timeout errors."""
        with patch("claude_agent_sdk.query", side_effect=Exception("Request timeout")):
            agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
            result = await agent.run("test command")

        assert result.success is False
        assert result.error is not None
        assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_run_exception_generic(self) -> None:
        """Should handle generic exceptions."""
        with patch("claude_agent_sdk.query", side_effect=Exception("Unknown error")):
            agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
            result = await agent.run("test command")

        assert result.success is False
        assert result.error is not None
        assert "Unknown error" in result.error

    @pytest.mark.asyncio
    async def test_run_empty_output(self) -> None:
        """Should handle case with no output messages."""
        async def mock_query(*args, **kwargs):
            # Empty stream
            return
            yield  # Make it a generator

        with patch("claude_agent_sdk.query", mock_query):
            agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
            result = await agent.run("test command")

        assert result.success is True


class TestClaudeAgentProtocolCompliance:
    """Test ClaudeAgent implements AgentProtocol."""

    def test_claude_agent_is_protocol_compliant(self) -> None:
        """ClaudeAgent should comply with AgentProtocol."""
        from bmad_auto.agents.base import AgentProtocol

        agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
        assert isinstance(agent, AgentProtocol)

    def test_claude_agent_has_run_method(self) -> None:
        """ClaudeAgent should have async run method."""
        import inspect

        agent = ClaudeAgent(working_dir="/project", use_logged_in=True)
        assert hasattr(agent, "run")
        assert inspect.iscoroutinefunction(agent.run)


class TestClaudeAgentIntegration:
    """Integration tests (marked - run separately)."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_agent_invocation(self) -> None:
        """Test real Claude Agent invocation.

        NOTE: This test requires:
        - Claude Code desktop installed and logged in, OR
        - ANTHROPIC_API_KEY environment variable set

        Run with: pytest -m integration
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set - skipping integration test")

        agent = ClaudeAgent(
            working_dir=os.getcwd(),
            use_logged_in=False,
            api_key=api_key,
        )
        result = await agent.run('Echo "hello world"')

        # Basic sanity check - actual output depends on agent
        assert isinstance(result, AgentResult)
        assert isinstance(result.success, bool)
        assert isinstance(result.output, str)
