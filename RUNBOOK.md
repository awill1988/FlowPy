# Runbook

This document contains some easy copy-and-paste commands you can run from this project.

## Python Virtual Environment

First thing to setup is to make sure you have Python >= 3.10:

`python --version`

should look like `Python 3.10.7`

Next, run `make`

## Docker Image with GDAL 3.6.1

```bash
docker build -t flowpy:develop --target=develop .
docker run -it flowpy:develop gdal-config --version
```

## 1. GNU Make

| Purpose                    | Subcommand          |
| -------------------------- | ------------------- |
| build release              | `make`              |
| start airflow emulation    | `make airflow`      |
| nuke everything            | `make clean`        |
| build with host python env | `make build-python` |

## 2. Docker CLI

| Purpose           | Command                                                                                      |
| ----------------- | -------------------------------------------------------------------------------------------- |
| airflow emulation | `docker build -t 'ates:with-airflow' --target=with-airflow .`                                |
| shell             | `docker run -it ates:with-airflow bash`                                                      |
| apt version pin   | `docker run -it debian:bullseye-slim bash -c 'apt update && apt-cache madison g++'`          |
| lint docker       | `docker run --rm -i ghcr.io/hadolint/hadolint < Dockerfile`                                  |
| lint docker size  | `docker run -it --rm -v $(pwd):/workdir dslim/docker-slim lint --target /workdir/Dockerfile` |
| lint markdown     | `docker run -v $PWD:/workdir ghcr.io/igorshubovych/markdownlint-cli:latest "*.md"`           |

## 3. Docker Compose

| Purpose | Command                             |
| ------- | ----------------------------------- |
| builds  | `docker compose build develop`      |
| shell   | `docker compose run -it shell bash` |

## 4. Misc

| Purpose                | Command                                     |
| ---------------------- | ------------------------------------------- |
| lints commit messages  | `pre-commit install --hook-type commit-msg` |
| lint javascript / yaml | `prettier --check **/*.{js,y[a]ml}`         |
