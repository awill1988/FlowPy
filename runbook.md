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

| Purpose                            | Subcommand   |
| ---------------------------------- | ------------ |
| build container & open shell       | `make shell` |
| build with host machine python env | `make`       |
| nuke host machine build files      | `make clean` |

## 2. Docker CLI

| Purpose          | Command                                                                             |
| ---------------- | ----------------------------------------------------------------------------------- |
| shell            | `docker run -it flowpy:develop bash` (requires previous build)                      |
| lint dockerfile  | `docker run --rm -i ghcr.io/hadolint/hadolint < Dockerfile`                         |
| lint shell files | `docker run --rm -v "$PWD:/mnt" koalaman/shellcheck:stable myscript`                |
| lint markdown    | `docker run -v $PWD:/workdir ghcr.io/igorshubovych/markdownlint-cli:latest "*.md"`  |
| apt version pin  | `docker run -it debian:bullseye-slim bash -c 'apt update && apt-cache madison g++'` |

## 4. Misc

| Purpose                | Command                             |
| ---------------------- | ----------------------------------- |
| lint javascript / yaml | `prettier --check **/*.{js,y[a]ml}` |
