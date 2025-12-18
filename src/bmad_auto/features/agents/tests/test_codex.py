import json

import pytest

from bmad_auto.features.agents.codex import CodexAgent
from bmad_auto.features.agents.models import AgentConfig


def test_build_command_resume(tmp_path) -> None:
    cfg = AgentConfig(cli="codex", settings_file=tmp_path / "cfg.toml", extra_args=["--dry-run"])
    agent = CodexAgent(cfg)
    cmd = agent.build_command("ignored", session_id="sess")
    assert cmd[:3] == ["codex", "exec", "--json"]
    assert "resume" in cmd
    assert cmd[-1] == "--dry-run"


def test_build_command_new_prompt(tmp_path) -> None:
    cfg = AgentConfig(cli="codex", settings_file=tmp_path / "cfg.toml")
    agent = CodexAgent(cfg)
    cmd = agent.build_command("do this", session_id=None)
    assert cmd[-1] == "do this"


def test_parse_output_success() -> None:
    event = {
        "event": "task.completed",
        "agent_message": {"text": "ok", "session_id": "s1", "cost_usd": 0.5},
    }
    raw = json.dumps(event)
    agent = CodexAgent(AgentConfig(cli="codex"))
    res = agent.parse_output(raw)
    assert res.success is True
    assert res.output == "ok"
    assert res.session_id == "s1"


def test_parse_output_empty_lines() -> None:
    agent = CodexAgent(AgentConfig(cli="codex"))
    with pytest.raises(json.JSONDecodeError):
        agent.parse_output("")
