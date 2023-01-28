#!/usr/bin/env bash

# absolute path to this file's directory
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# load helper bash functions
. "${here}/rc"

# absolute path to top directory
top="$(git rev-parse --show-toplevel)"

# make sure watchman is installed
type watchman >/dev/null || \
    die 'watchman is not installed. See facebook.github.io/watchman/docs/install.html'

# bool <- check if entire directory is watched
is_installed=$(watchman watch-list | jq -c '[.roots[] | select(. | contains("'"${top}"'"))] | length')

# do nothing if already not watching
[[ "0" -eq "${is_installed}" ]] && exit 0

#--------------------------------------------------------------------
#                         watchman(del)
#--------------------------------------------------------------------
#   stop watching the src directory for changes and remove watch
#--------------------------------------------------------------------
watchman watch-del "${top}"
