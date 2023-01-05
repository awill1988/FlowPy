include bin/python.mk
include bin/tools.mk

.DEFAULT_GOAL: shell
.PHONY: shell

shell: # starts a developer shell
	@ docker build -t flowpy:develop --target=develop .

watch: watch-add-python ## build via watching src files

clean: clean-python ## removes all development and build artifacts

build: build-python ## builds all targets for distribution

test: test-python ## runs all testing facilities

lint: lint-prettier lint-markdown ## runs all linting facilities

fmt: fmt-python # formats the python code
