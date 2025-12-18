from bmad_auto.shared import consts


def test_constants_are_defined() -> None:
    assert consts.CLI_CLAUDE == "claude"
    assert consts.CLI_CODEX == "codex"
    assert consts.DEFAULT_STATE_DIR == ".bmad-auto/state"
    assert consts.DEFAULT_CONFIG_FILE == ".bmad-auto/config.yaml"
    assert consts.MAX_DEV_ATTEMPTS == 3
    assert consts.DEFAULT_AGENT_TIMEOUT == 600
    assert consts.MARKER_NO_MORE_STORIES == "NO_MORE_STORIES"
    assert consts.MARKER_REVIEW_APPROVED == "APPROVED"
    assert consts.MARKER_REVIEW_REJECTED == "REJECTED"
