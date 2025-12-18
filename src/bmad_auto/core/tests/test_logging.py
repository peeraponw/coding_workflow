import logging

from bmad_auto.core.logging import configure_logging


def test_configure_logging_sets_level() -> None:
    configure_logging(debug=True, json_output=False)
    root_level = logging.getLogger().getEffectiveLevel()
    assert root_level == logging.DEBUG
