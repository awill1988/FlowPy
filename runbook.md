# Runbook

This document contains some easy copy-and-paste commands you can run from this project.

## 1. Docker CLI

| Purpose         | Command                                                                             |
| --------------- | ----------------------------------------------------------------------------------- |
| build shell           | `docker build -t flowpy:develop --target=shell .`                    |
| run shell           | `docker run -it flowpy:develop bash` (requires previous build)                      |
| run GUI (maybe?) | `docker run --rm -it --network host -e "DISPLAY=${DISPLAY}" -v "${HOME}/.Xauthority:/root/.Xauthority" -v /tmp/.X11-unix:/tmp/.X11-unix flowpy:develop python3 main.py --gui` |
| lint dockerfile | `docker run --rm -i ghcr.io/hadolint/hadolint < Dockerfile`                         |

## 2. Docker Compose CLI

| Purpose         | Command                                                                             |
| --------------- | ----------------------------------------------------------------------------------- |
| build & run developer shell           | `docker compose run -it --build shell bash`                    |
| run example from `main.py`           | `docker compose run example`                    |
