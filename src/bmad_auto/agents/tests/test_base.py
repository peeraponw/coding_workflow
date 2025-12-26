"""Tests for agent protocol and base types."""

import pytest

from bmad_auto.agents.base import AgentProtocol, AgentResult, AgentRole


class TestAgentRole:
    """Test AgentRole enum."""

    def test_sm_role_links_to_constant(self) -> None:
        """AgentRole.SM should match AGENT_SM constant."""
        from bmad_auto.shared.consts import AGENT_SM

        assert AgentRole.SM.value == AGENT_SM
        assert AgentRole.SM.value == "sm"

    def test_dev_role_links_to_constant(self) -> None:
        """AgentRole.DEV should match AGENT_DEV constant."""
        from bmad_auto.shared.consts import AGENT_DEV

        assert AgentRole.DEV.value == AGENT_DEV
        assert AgentRole.DEV.value == "dev"

    def test_reviewer_role_links_to_constant(self) -> None:
        """AgentRole.REVIEWER should match AGENT_REVIEWER constant."""
        from bmad_auto.shared.consts import AGENT_REVIEWER

        assert AgentRole.REVIEWER.value == AGENT_REVIEWER
        assert AgentRole.REVIEWER.value == "reviewer"


class TestAgentResult:
    """Test AgentResult dataclass."""

    def test_ok_factory_creates_success_result(self) -> None:
        """ok() factory should create successful result."""
        result = AgentResult.ok("Task completed")

        assert result.success is True
        assert result.output == "Task completed"
        assert result.error is None

    def test_fail_factory_creates_failure_result(self) -> None:
        """fail() factory should create failed result."""
        result = AgentResult.fail("API error", output="Started...")

        assert result.success is False
        assert result.output == "Started..."
        assert result.error == "API error"

    def test_fail_factory_with_empty_output(self) -> None:
        """fail() without output should use empty string."""
        result = AgentResult.fail("Critical error")

        assert result.success is False
        assert result.output == ""
        assert result.error == "Critical error"

    def test_success_with_error_raises(self) -> None:
        """Creating successful result with error should raise."""
        with pytest.raises(
            ValueError, match="Successful result cannot have error message"
        ):
            AgentResult(success=True, output="Done", error="Oops")

    def test_failure_without_error_raises(self) -> None:
        """Creating failed result without error should raise."""
        with pytest.raises(
            ValueError, match="Failed result must have error message"
        ):
            AgentResult(success=False, output="Failed")

    def test_frozen_immutable(self) -> None:
        """AgentResult should be frozen (immutable)."""
        from dataclasses import FrozenInstanceError

        result = AgentResult.ok("output")

        with pytest.raises(FrozenInstanceError):
            result.success = False  # type: ignore[misc]


class TestAgentProtocol:
    """Test AgentProtocol compliance."""

    @pytest.mark.asyncio
    async def test_concrete_agent_complies_with_protocol(self) -> None:
        """Concrete agent implementation should comply with protocol."""
        # AgentProtocol already has @runtime_checkable, so concrete classes
        # implementing it work with isinstance()
        class MockAgent:
            """Mock agent for testing."""

            async def run(self, command: str) -> AgentResult:
                return AgentResult.ok(f"Executed: {command}")

        agent = MockAgent()
        assert isinstance(agent, AgentProtocol)

        result = await agent.run("test command")
        assert result.success is True
        assert result.output == "Executed: test command"

    def test_protocol_has_run_method(self) -> None:
        """Protocol should define async run method."""
        import inspect

        assert hasattr(AgentProtocol, "run")
        assert inspect.iscoroutinefunction(AgentProtocol.run)
