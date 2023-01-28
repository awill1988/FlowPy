"""
Contains methods and vars used to implement a CLI program for Flow-Py.
"""
from logging import getLogger as logger
from textwrap import dedent
from typing import Any, Dict, List, Tuple
from argparse import (
    Namespace,
    ArgumentParser,
    RawDescriptionHelpFormatter,
)

_logger = "flow.args"  # this module's logger name


# for common arguments like src-uri / dst-uri / --dry-run
# ---------------------------------------------------------------------------------------
_COMMON_ARGS = "common"  # special type, not literal command

# for CLI sub-commands
# ---------------------------------------------------------------------------------------
_RELEASE_CMD = "release"
_PROFILE_CMD = "profile"


def cli(*args: str) -> Namespace:
    """Returns argparse.Namespace with all arguments required to run Flow-Py."""

    # retrieve logging instance
    # -------------------------------------------------------------------------------------
    log = logger(_logger)

    # create parser so that commands for the CLI can be parsed
    # -------------------------------------------------------------------------------------
    _parser = ArgumentParser(
        prog="flowpy",
        usage="used to generate rasters of a flow path",
        formatter_class=RawDescriptionHelpFormatter,
        description=dedent(
            """\
            FlowPy
            --------------------------------
            """
        ),
    )

    # create sub-parser so that child commands for the CLI can be registered
    # -------------------------------------------------------------------------------------
    _sub = _parser.add_subparsers(
        title="sub-commands", dest="command", help="things you can do"
    )

    _args: List[Tuple[str, List[Tuple[str, Dict[str, Any]]]]] = [
        (
            # -------------------------------------------------------------------------------------
            # profile "sub-command" arguments
            # -------------------------------------------------------------------------------------
            _PROFILE_CMD,
            [],
        ),
        (
            # -------------------------------------------------------------------------------------
            # release "sub-command" arguments
            # -------------------------------------------------------------------------------------
            _RELEASE_CMD,
            [
                (
                    "--alpha",
                    {
                        "dest": "alpha_angle",
                        "type": float,
                        "help": "controls the run out angle induced stopping and routing",
                        "required": True,
                    },
                ),
                (
                    "--exp",
                    {
                        "dest": "exponent",
                        "type": float,
                        "help": "exponent value",
                        "required": True,
                    },
                ),
                (
                    "--infra-uri",
                    {
                        "type": str,
                        "help": "includes infra via valid uri",
                    },
                ),
                (
                    "--flux",
                    {
                        "type": float,
                        "help": "override flux threshold",
                        "default": 3 * 10**-4,
                    },
                ),
                (
                    "--max-z-delta",
                    {
                        "type": float,
                        "help": "max z",
                        # Recommended values:
                        # Avalanche = 270
                        # Rockfall = 50
                        # Soil Slide = 12
                        "default": 8848,
                    },
                ),
            ],
        ),
        (
            # -------------------------------------------------------------------------------------
            # common arguments that live outside of the scope of "sub-commands"
            # -------------------------------------------------------------------------------------
            _COMMON_ARGS,
            [
                (
                    "src",
                    {
                        "help": "URI to source, i.e. location of dir or file",
                    },
                ),
                (
                    "dst",
                    {
                        "help": "URI to destination, i.e. location of dir or file",
                        "default": None,
                    },
                ),
                (
                    "--cwd",
                    # for instance, all subcommands can use a custom "current working directory"
                    {
                        "help": "use the provided current working directory",
                        "required": False,
                        "default": ".",
                    },
                ),
                (
                    "--dry-run",
                    # dry run will read and create intermediary resources but will not persist
                    # the output raster. It is used for sanity checking.
                    {
                        "help": "perform operations but do not write or modify files",
                        "action": "store_true",
                    },
                ),
            ],
        ),
    ]

    # create the parser for the "partition" sub-command
    # -------------------------------------------------------------------------------------
    _profile = _sub.add_parser(_PROFILE_CMD, help="shows raster info about the inputs")

    # create the parser for the "release" sub-command
    # -------------------------------------------------------------------------------------
    _release = _sub.add_parser(_RELEASE_CMD, help="does the flow calculation")

    # use kwargs to add arguments
    # -------------------------------------------------------------------------------------
    for (key, parse_args) in _args:
        for name, kwargs in parse_args:
            if key == _COMMON_ARGS:
                _profile.add_argument(name, **kwargs)
                _release.add_argument(name, **kwargs)
            elif key == _RELEASE_CMD:
                _release.add_argument(name, **kwargs)
            elif key == _PROFILE_CMD:
                _profile.add_argument(name, **kwargs)
            else:
                raise ValueError("unknown cli keyword")

    _parsed = _parser.parse_args(args if args else None)

    log.debug(
        "parsed cli arguments %s",
        # pylint: disable=protected-access
        ",".join([f"{pair[0]}={pair[1]}" for pair in _parsed._get_kwargs()]),
    )
    try:
        if _parsed.src:
            pass
    except AttributeError:
        _parser.error("unable to determine command line arguments")

    return _parsed
