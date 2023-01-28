#!/usr/bin/env bash

set -eu

# used to avoid requiring software that is required for code contributors.
SRC_NO_CONTRIB=${SRC_NO_CONTRIB:-0}

# absolute path of project
gitroot=$(git rev-parse --show-toplevel)

# bash function import
source "${gitroot}/bin/rc"

# don't continue when there's an unexpected error
set -e

# non-contributors do not need pre-commit
[ "${SRC_NO_CONTRIB}" == "1" ] && \
    echo "skipping pre-commit due to non-contributing mode" && \
    exit 0

# make sure pre-commit is installed
type pre-commit >/dev/null || die "to contribute, please install the pre-commit software. See https://pre-commit.com/"

#--------------------------------------------------------------------
#                   git hooks (run)
#--------------------------------------------------------------------
#  pre-commit will now run on every commit. Every time you clone a
#  project using pre-commit running pre-commit install should always
#  be the first thing you do. You can run that here too.
#--------------------------------------------------------------------
pre-commit run --all-files
