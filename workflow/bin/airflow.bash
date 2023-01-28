#!/bin/bash
# airflow.bash
#
# This script provides convenient functions to grab versioned and curated docker compose stacks
# from Apache Airflow website and make edits to it to unlock some useful features such as
# integration testing of DAGs / Tasks / etc.
#
# https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

# Apache Airflow: environment varianbles
# -----------------------------------------------------------------------------
AIRFLOW_IMAGE_NAME="${AIRFLOW_IMAGE_NAME:-flowpy:with-airflow}"

# Apache Airflow: *extra* environment varianbles declared in this script
# -----------------------------------------------------------------------------
AIRFLOW_VERSION=${AIRFLOW_VERSION:-2.4.2}
AIRFLOW_WEBSERVER_HOST_PORT=${AIRFLOW_WEBSERVER_HOST_PORT:-2720}
PROJECT_NAME="flowpy"

# -----------------------------------------------------------------------------
# _dbg: logs if debug mode is on
# -----------------------------------------------------------------------------
function _dbg {
    printf 'debug: %s\n' "$1" >&2
}

# -----------------------------------------------------------------------------
# _dc: reliably calls `docker compose`
# -----------------------------------------------------------------------------
function _dc {
    [ ! -s "$(_share_dir)/docker-compose.yaml" ] && {
        _dbg 'warning: not initialized. run "make"' >&2;
        return 0
    }
    COMPOSE_PROJECT_NAME="${PROJECT_NAME}" \
    docker compose -f "$(_share_dir)/docker-compose.yaml" "$@"
}

function _exists {
    if [ "$(docker-compose -p "${PROJECT_NAME}" ps --services | wc -c)" -gt 1 ]; then
        printf '1'
        return
    fi
    printf '0'
}

# -----------------------------------------------------------------------------
# _pydir: virtualenv python directory
# -----------------------------------------------------------------------------
function _pydir() {
    python3 -c '
        import sys
        print(".venv" + ".".join(str(x) for x in sys.version_info[:2]))
    '
}

# -----------------------------------------------------------------------------
# _share_dir: directory where resources created by this script are stored.
# -----------------------------------------------------------------------------
function _share_dir {
    local xdg_data_home
    local root_dirname
    local root_local

    root_local="${HOME}/.local"

    # -------------------------------------------------------------------------
    # XDG_DATA_HOME : system compatibility (i.e. linux, macos)
    # -------------------------------------------------------------------------
    xdg_data_home=${XDG_DATA_HOME:-${root_local}/share}

    root_dirname="flowpy"
    printf '%s/%s' "${xdg_data_home}" "${root_dirname}"
}

# -----------------------------------------------------------------------------
# _src_dir: reliably resolves this project's root context
# -----------------------------------------------------------------------------
function _src_dir {
    printf '%s' "$(git rev-parse --show-toplevel)";
}

# -----------------------------------------------------------------------------
# _mkdir: creates the data directory for the emulation environment.
# -----------------------------------------------------------------------------
function _mkdir {
    {
        [ -d "$(_share_dir)" ] \
        || [ -s "$(_src_dir)/share" ]
    } && _dbg "airflow share dir already initialized" # idempotency

    # create data dir for some persistence
    mkdir -p "$(_share_dir)"
    # convenient symlink
    ln -s "$(_share_dir)" "$(_src_dir)/share"
    _dbg "data is stored here: $(_share_dir)"
}

# -----------------------------------------------------------------------------
# airflow_fetch_compose: fetches the docker compose file and applies edits.
# -----------------------------------------------------------------------------
function airflow_fetch_compose() {
    [ "$(_exists)" -ne 0 ] && echo "warning: compose already exists" # idempotency

    local dst
    local location

    dst="$(_share_dir)/docker-compose.yaml"
    location="https://airflow.apache.org/docs/apache-airflow/${AIRFLOW_VERSION}/docker-compose.yaml"
    #
    # Fetch docker compose file
    # -------------------------------------------------------------------------
    wget -O- --quiet "${location}" > "${dst}"
    # -------------------------------------------------------------------------
    #                       Airflow Common Customization
    # -------------------------------------------------------------------------
    # Airflow's maintainers are using a YAML syntax to populate some common env
    # variables, volume mappings, etc.
    #
    # ```
    #   airflow-cli:
    #     <<: *airflow-common
    #     profiles:
    #       - debug
    # ```
    # -------------------------------------------------------------------------
    #
    # Run everything immediately.
    # -------------------------------------------------------------------------
	sed -i -e "s/PAUSED_AT_CREATION: 'true'/PAUSED_AT_CREATION: 'false'/g" "${dst}"
    #
    # Do not load example / demo / tutorial DAGs.
    # -------------------------------------------------------------------------
	sed -i -e "s/LOAD_EXAMPLES: 'true'/LOAD_EXAMPLES: 'false'/g" "${dst}"

    # -------------------------------------------------------------------------
    #                    Airflow Web Server Customization
    # -------------------------------------------------------------------------
    # Customize host port that maps to the container hosting Apache Airflow's
    # user interface.
    #
    # Default is to map {dags,plugins,logs} from cwd, which is problematic if
    # a harmonious volume mapping is desired.
    # -------------------------------------------------------------------------
    #
    # Declare an additional environment variable to customize the stack.
    #
    # shellcheck disable=SC2016
    sed -i -e 's/- 8080:/- ${AIRFLOW_WEBSERVER_HOST_PORT:-2720}:/g' "${dst}"

    # simply swap relative for absolute paths to src directory (forget logs)
	sed -i -e "s/- .\/dags:/- $(_src_dir | sed 's/\//\\\//g')\/dags:/g" "${dst}"
	sed -i -e "s/- .\/plugins:/- $(_src_dir | sed 's/\//\\\//g')\/plugins:/g" "${dst}"

    # -------------------------------------------------------------------------
    #                       Airflow Init Container
    # -------------------------------------------------------------------------
    # Customize the volume mappings for the init container for convenience.
    #
    # Default is "- .:/sources" which is problematic if harmonious volume
    # mapping is desired. The best strategy is to simply swap relative for
    # absolute paths to src directory (forget logs)
    # -------------------------------------------------------------------------


    # find line number so we can copy mappings for init the same way as others
    line_to_replace=$(grep -n '\- .:/sources' "${dst}" | cut -d : -f 1)

    # replace sources (creates need for additional steps below)
	sed -i -e "s/- .:\/sources/- $(_src_dir | sed 's/\//\\\//g')\/dags:\/sources\/dags:delegated/g" "${dst}"

    # shellcheck disable=SC2016
    sed -i "${line_to_replace}i\\"'
      - '"$(_src_dir)"'/plugins:/sources/plugins:delegated' "${dst}"

    # pass env vars too
    sed -i "${line_to_replace}i\\"'
      - ./.env:/sources/.env:delegated' "${dst}"

}

# -----------------------------------------------------------------------------
# airflow_python: python dependencies (for executing natively)
# -----------------------------------------------------------------------------
function airflow_python {
    [ -f "$(_pydir)/bin/pip" ] && _die 'run "make python-setup"'
    printf "\n\n%s\n\n" 'Installing Apache Airflow Dependencies'
	"$(_pydir)/bin/pip" install --exists-action i \
		"apache-airflow[google,amazon,docker,github]==${APACHE_AIRFLOW_VERSION}" \
    	--constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${APACHE_AIRFLOW_VERSION}/constraints-${PYTHON3_VERSION}.txt"
}

# -----------------------------------------------------------------------------
# airflow_init: initializes compose stack and the database.
# -----------------------------------------------------------------------------
function airflow_init {
  _mkdir                # ensure share directory
  airflow_fetch_compose # grab official file

  [ -f "$(_share_dir)/.env" ] && rm "$(_share_dir)/.env"

  # Initialize Apache Airflow Stack
  #
  # Based on the official Docker Compose guide, there are some environment
  # variables documented that we may be interested in changing.
  #
  # However, some are *not* documented because this script augments the
  # documented features with additional configurations via system environment
  # variables. These additional conifugrations are maintained by onX engineers
  # for internal purposes such as:
  #
  # * AIRFLOW_WEBSERVER_HOST_PORT -- host port (e.g. http://localhost:2720)
  #
  # https://stackoverflow.com/questions/30194596/what-does-this-error-mean-sc2129-consider-using-cmd1-cmd2-file-inste
  {
    # customize the user uid running on compose stack
    echo "AIRFLOW_UID=$(id -u)";
    # use provided airflow version
    echo "AIRFLOW_IMAGE_NAME=${AIRFLOW_IMAGE_NAME}";

    # only load the dags in our source code
    echo "AIRFLOW_WEBSERVER_HOST_PORT=${AIRFLOW_WEBSERVER_HOST_PORT:-}";

    # "_run_image of the DockerOperator returns now a python string
    # https://github.com/fclesio/airflow-docker-operator-with-compose/blob/main/docker-compose.yaml
    echo "AIRFLOW__CORE__ENABLE_XCOM_PICKLING = 'true'";
  } >> "$(_share_dir)/.env"

  # initialize compose
  _dc up --remove-orphans airflow-init
}

# -----------------------------------------------------------------------------
# airflow_up: starts the airflow compose stack.
# -----------------------------------------------------------------------------
function airflow_up {
    # flower - The flower app for monitoring the environment. It is available at http://localhost:5555.
    _dc --profile flower up --remove-orphans -d
}

# -----------------------------------------------------------------------------
# airflow_down: stops the compose stack and the database processes.
# -----------------------------------------------------------------------------
function airflow_down {
    _dc --profile flower down --remove-orphans
}

# -----------------------------------------------------------------------------
# airflow_purge: nuke the compose stack and all its resources.
# -----------------------------------------------------------------------------
function airflow_purge {
    _dbg "nuking the compose stack and all its resources"

    # remove docker compose stack
    _dc --profile flower down --volumes --remove-orphans || true

    # remove all symbolic links
    find "$(_src_dir)" -maxdepth 1 -type l -delete

    # remove if present
    [ -d "$(_share_dir)" ] && rm -r "$(_share_dir)"
}

# -----------------------------------------------------------------------------
# _cli: calls airflow cli via docker.
# -----------------------------------------------------------------------------
function _cli() {
    _dc run -it --rm airflow-cli "$@"
}

# -----------------------------------------------------------------------------
# _die: fail will error message.
# -----------------------------------------------------------------------------
function _die() {
    echo "[error]: $1" >&2
    exit 1
}

# -----------------------------------------------------------------------------
# _run: conditionally invoked when this script is executed rather than sourced.
# -----------------------------------------------------------------------------
function _run() {
    local need_chdir

    need_chdir=0

    # move to the top of the sub project src_directory
    if [ "$(pwd)" != "$(_src_dir)" ]; then
        _dbg "moving form '$(pwd)' to '$(_src_dir)'"
        need_chdir=1
    fi

    # maybe move to src directory
    [ "${need_chdir}" == '1' ] && { pushd "$(_src_dir)" || _die 'pushd'; }

    # no args, default behavior
    # -------------------------------------------------------------------------
    if [ -z "$1" ]; then
        _dbg "no args, default behavior"

        # maybe initialize
        if [ "$(_exists)" -ne 1 ]; then
            _dbg "initializing airflow compose stack"
            airflow_init
        fi
        # bring airflow up
        airflow_up

        return 0
    fi

    # subcommand parsing
    # -------------------------------------------------------------------------
    if [ "$(type -t "airflow_${1}")" == 'function' ]; then
        _dbg "interpreting command $*"
        # capture and shift args
        cmd="${1}"
        shift
        "airflow_${cmd}" "$*"
        return 0
    fi

    # assume it's a Airflow CLI client request and pass to docker
    # -------------------------------------------------------------------------
    _cli "$@"

    [ "${need_chdir}" == '1' ] && { pushd "$(_src_dir)" || _die 'pushd'; }
}

# "How to detect if a script is being sourced"
#
# Code Copied: https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
sourced=0
# shellcheck disable=SC2296,SC2250
if [ -n "$ZSH_VERSION" ]; then
  case $ZSH_EVAL_CONTEXT in *:file) sourced=1;; esac
elif [ -n "$KSH_VERSION" ]; then
  [ "$(cd -- "$(dirname -- "$0")" && pwd -P)/$(basename -- "$0")" != "$(cd -- "$(dirname -- "${.sh.file}")" && pwd -P)/$(basename -- "${.sh.file}")" ] && sourced=1
elif [ -n "$BASH_VERSION" ]; then
  (return 0 2>/dev/null) && sourced=1
else # All other shells: examine $0 for known shell binary filenames.
     # Detects `sh` and `dash`; add additional shell filenames as needed.
  case ${0##*/} in sh|-sh|dash|-dash) sourced=1;; esac
fi

# If we are invoking the script (i.e. CLI purpose)
# Variations:
# -----------------------------------------------------------------------------
#   . docker/bin/airflow.sh   => $sourced = 1
#   docker/bin/airflow.sh up  => $sourced = 0
# -----------------------------------------------------------------------------
if [ "${sourced}" == '0' ]; then
    _dbg "not sourced .. treating file like a script"
    _dbg "executing command ${*:-<default>}"
    _run "$@"
fi
