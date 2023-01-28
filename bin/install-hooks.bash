#!/usr/bin/env bash

# don't continue when there's an unexpected error or for undefined variables
set -eu

# shellcheck source-path=./bin
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# load helper bash functions
. "${here}/bashrc"

# used to avoid requiring software that is required for code contributors.
SRC_NO_CONTRIB=${SRC_NO_CONTRIB:-0}

# non-contributors do not need pre-commit
[ "${SRC_NO_CONTRIB}" == "1" ] && \
    echo "skipping pre-commit due to non-contributing mode" && \
    exit 0

# make sure pre-commit is installed
type pre-commit >/dev/null || die "to contribute, please install the pre-commit software. See https://pre-commit.com/"

#--------------------------------------------------------------------
#                   git hooks (register)
#--------------------------------------------------------------------
#  pre-commit will now run on every commit. Every time you clone a
#  project using pre-commit running pre-commit install should always
#  be the first thing you do.
#--------------------------------------------------------------------

# absolute path to top directory
top="$(git rev-parse --show-toplevel)"

[ -f "${top}/../.git/hooks/pre-commit" ] || pre-commit install
