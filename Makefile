include bin/python.mk
include bin/tools.mk

watch: watch-add-python ## build via watching src files

clean: clean-python ## removes all development and build artifacts

build: build-python ## builds all targets for distribution

test: test-python ## runs all testing facilities

lint: lint-prettier lint-markdown
lint: ## runs all linting facilities

fmt: fmt-python # formats the python code
