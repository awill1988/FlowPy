"""
Log Tests.
"""
from flow.log import initialize
from logging import getLogger, RootLogger


def test_initialize():
    # verify it's a method
    assert initialize is not None

    # get the root logging instance
    log: RootLogger = getLogger()

    # verify the number of root logging handlers
    handler_count = len(log.handlers)
    assert handler_count > 0

    # verify we added just a single handler
    initialize(level="ERROR")
    assert handler_count != len(log.handlers)
    assert (handler_count + 1) == len(log.handlers)

    # verify it is idempotent type handler (no duplicates)
    initialize(level="ERROR")
    assert (handler_count + 1) == len(log.handlers)

    # assert root_logger == getLogger()

    # assert root_logger.level != ERROR

    # assert getLogger().level == ERROR
