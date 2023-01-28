#!/usr/bin/env bash

# don't continue when there's an unexpected error or for undefined variables
set -eu

# shellcheck source-path=./bin
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# load helper bash functions
. "${here}/rc"

# make sure watchman is installed
type watchman >/dev/null || die 'watchman is not installed. See https://facebook.github.io/watchman/docs/install.html'

#--------------------------------------------------------------------
#                         watchman(add)
#--------------------------------------------------------------------
#   watches the source files for changes and rebuilds debug release
#--------------------------------------------------------------------
watchman watch "${here}/src"

watchman -j <<-EOT
[
    "trigger",
    "${here}/src",
    {
    "name": "build-on-change",
    "expression": ["pcre", ".*\\\.py$", "basename"],
    "command": ["${here}/.venv3.10/bin/pip", "install", ".."]
    }
]
EOT
