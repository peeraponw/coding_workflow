import json

import pytest

from bmad_auto.features.agents.claude import ClaudeAgent
from bmad_auto.features.agents.models import AgentConfig


def test_build_command_with_settings_and_session(tmp_path) -> None:
    cfg = AgentConfig(cli="claude", settings_file=tmp_path / "settings.json", extra_args=["--dry-run"])
    agent = ClaudeAgent(cfg)
    cmd = agent.build_command("do it", session_id="abc")
    assert "--settings" in cmd
    assert "--resume" in cmd
    assert cmd[-1] == "--dry-run"


def test_parse_output_success() -> None:
    output = {
        "result": "success",
        "output": "done",
        "session_id": "sess-1",
        "total_cost_usd": 0.12,
    }
    agent = ClaudeAgent(AgentConfig(cli="claude"))
    res = agent.parse_output(json.dumps(output))
    assert res.success is True
    assert res.output == "done"
    assert res.cost_usd == 0.12


def test_parse_output_failure() -> None:
    output = {"result": "error", "output": "", "error": "bad"}
    agent = ClaudeAgent(AgentConfig(cli="claude"))
    res = agent.parse_output(json.dumps(output))
    assert res.success is False
    assert res.error == "bad"
