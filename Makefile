include bin/python.mk
include bin/tools.mk

.PHONY: shell
shell: # starts a developer shell
	@ docker build -t flowpy:develop --target=develop .
	@ docker run \
		--name FlowPy \
		-it --rm \
		-v $(PWD)/src/flow:/usr/src/src/flow:delegated \
		-v $(PWD)/src/tests:/usr/src/src/tests:delegated \
		-v $(PWD)/src/py.typed:/usr/src/src/py.typed:delegated \
		-v $(PWD)/src/setup.py:/usr/src/src/setup.py:delegated \
		-v $(PWD)/bin:/usr/src/bin:delegated \
		-v $(PWD)/requirements:/usr/src/requirements:delegated \
		flowpy:develop bash

watch: watch-add-python ## build via watching src files

clean: clean-python ## removes all development and build artifacts

build: build-python ## builds all targets for distribution

test: test-python ## runs all testing facilities

lint: lint-prettier lint-markdown ## runs all linting facilities

fmt: fmt-python # formats the python code
