from sys import stdout, stderr

import logging
from logging import StreamHandler, getLogger, NOTSET
from typing import Optional
from json_log_formatter import JSONFormatter
from datetime import datetime

from .settings import LOGLEVEL

_hndlr: Optional[StreamHandler] = None


class LogFormatter(JSONFormatter):
    """overrides json_log_formatter record creation so the timestamp uses more precision."""

    def json_record(self, message, extra, record):
        extra["level"] = record.levelname.lower()
        extra["name"] = record.name
        if not extra.get("timestamp"):
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            extra["timestamp"] = now
        extra = super(LogFormatter, self).json_record(message, extra, record)
        del extra["time"]
        return extra


def initialize(writer: Optional[str] = None, level: Optional[int] = None) -> None:
    """adds a root logging handler to the python process so the application's logging
    will target stdout or stderr in json format.
    """
    global _hndlr  # pylint: disable=global-statement

    # maybe set the default value of writer arg with stdout
    _writer = writer.upper() if writer else "STDOUT"

    # verify the name of the output
    if _writer == "STDOUT":
        _out = stdout
    elif writer == "STDERR":
        _out = stderr
    else:
        raise ValueError(
            f"unsupported writer. options=('STDOUT', 'STDERR'), received: '{writer}'"
        )

    # parse the log level into an integer
    _lvl = logging.getLevelName(level or LOGLEVEL)
    # retrieve the root logger instance
    log = getLogger()

    if not _hndlr:

        # reset root log level to 'notset'
        log.setLevel(NOTSET)

        # create the stream handler and pass in the selected TextIO instance
        _hndlr = StreamHandler(_out)

        # set the stream's formatter, using our customized json output format defined above
        _hndlr.setFormatter(
            LogFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
        )

        # clear handlers
        # log.handlers.clear()

        log.addHandler(_hndlr)

    # finally, set log level
    return _hndlr.setLevel(_lvl)
