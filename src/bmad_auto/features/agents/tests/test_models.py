from pathlib import Path

from bmad_auto.features.agents.models import AgentConfig


def test_agent_config_defaults() -> None:
    cfg = AgentConfig(cli="claude")
    assert cfg.timeout > 0
    assert cfg.working_dir == Path(".")
    assert cfg.extra_args == []
