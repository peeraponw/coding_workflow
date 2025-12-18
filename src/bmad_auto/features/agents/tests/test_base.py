import asyncio
from pathlib import Path
from typing import Sequence

import pytest

from bmad_auto.core.exceptions import AgentExecutionError, AgentNotFoundError, AgentTimeoutError
from bmad_auto.features.agents.base import BaseAgent
from bmad_auto.features.agents.models import AgentConfig, AgentResult


class DummyAgent(BaseAgent):
    def __init__(self, command: Sequence[str]) -> None:
        super().__init__(AgentConfig(cli="claude"))
        self._command = list(command)
        self._binary = command[0]

    def build_command(self, prompt: str, session_id: str | None):  # pragma: no cover - not used
        return self._command

    def parse_output(self, raw_output: str) -> AgentResult:  # pragma: no cover - not used
        return AgentResult(success=True, output=raw_output, duration_seconds=0.0)


async def _run_echo(tmp_path: Path) -> AgentResult:
    cfg = AgentConfig(cli="claude", working_dir=tmp_path)

    class EchoAgent(BaseAgent):
        def build_command(self, prompt: str, session_id: str | None):
            return ["/bin/echo", prompt]

        def parse_output(self, raw_output: str) -> AgentResult:
            return AgentResult(success=True, output=raw_output.strip(), duration_seconds=0.0)

    agent = EchoAgent(cfg)
    agent._binary = "/bin/echo"
    return await agent.run("hello")


@pytest.mark.asyncio
async def test_base_agent_runs_echo(tmp_path: Path) -> None:
    result = await _run_echo(tmp_path)
    assert result.success is True
    assert result.output == "hello"


def test_validate_missing_binary() -> None:
    agent = DummyAgent(["/not/a/real/binary"])
    with pytest.raises(AgentNotFoundError):
        agent.validate()


@pytest.mark.asyncio
async def test_timeout_handling(monkeypatch, tmp_path: Path) -> None:
    cfg = AgentConfig(cli="codex", working_dir=tmp_path, timeout=0)

    class SleepAgent(BaseAgent):
        def build_command(self, prompt: str, session_id: str | None):
            return ["/bin/sleep", "1"]

        def parse_output(self, raw_output: str) -> AgentResult:
            return AgentResult(success=True, output=raw_output, duration_seconds=0.0)

    agent = SleepAgent(cfg)
    agent._binary = "/bin/sleep"
    with pytest.raises(AgentTimeoutError):
        await agent.run("ignored")


@pytest.mark.asyncio
async def test_nonzero_exit(monkeypatch, tmp_path: Path) -> None:
    cfg = AgentConfig(cli="claude", working_dir=tmp_path, timeout=1)

    class FailAgent(BaseAgent):
        def build_command(self, prompt: str, session_id: str | None):
            return ["/bin/sh", "-c", "exit 2"]

        def parse_output(self, raw_output: str) -> AgentResult:
            return AgentResult(success=True, output=raw_output, duration_seconds=0.0)

    agent = FailAgent(cfg)
    agent._binary = "/bin/sh"
    with pytest.raises(AgentExecutionError):
        await agent.run("")
