PYENV := $(shell python3 -c "import sys; print('.venv' + '.'.join(str(x) for x in sys.version_info[:2]))")
PYSRC := src

python-setup: $(PYENV)/bin/python3 # ensures Python virtual environment
	@:

$(PYENV)/bin/python3:
	python3 -m venv $(PYENV)
	$(PYENV)/bin/pip install --upgrade pip wheel setuptools
	$(PYENV)/bin/pip install -r requirements/dev.txt --exists-action i

.PHONY: clean
clean: # cleans the python virtual environment
	@find . -type f -name '*.pyc' -exec rm -r {} + || true;
	@find . -type d -name "__pycache__" -exec rm -r {} + || true
	@find . -type d -name ".pytest_cache" -exec rm -r {} + || true
	@find . -type d -name "generated" -exec rm -r {} + || true
	@find . -type d -name "*.egg-info" -exec rm -r {} + || true
	@find . -type d -name ".ipynb_checkpoints" -exec rm -r {} + || true
	@rm -rf dist build .coverage || true
	@find . -type d -name "$(PYENV)" -exec rm -r {} + || true

.PHONY: lint
lint: python-setup # Run flake8 and black to lint Python code
	$(PYENV)/bin/python3 -m flake8 $(PYSRC)/flow $(PYSRC)/tests examples
	$(PYENV)/bin/python3 -m black --check --exclude \(\.venv.\*\)\|\(.eggs\) $(PYSRC)/flow $(PYSRC)/tests examples
	$(PYENV)/bin/python3 -m mypy $(PYSRC)/flow/ $(PYSRC)/tests/
	$(PYENV)/bin/python3 -m pylint $(PYSRC)/flow/ $(PYSRC)/tests/

.PHONY: fmt
fmt: python-setup # Run black to format Python code
	$(PYENV)/bin/python3 -m black --exclude \(\.venv.\*\)\|\(.eggs\) $(PYSRC)/flow $(PYSRC)/tests examples

.PHONY: test
test: build # Run all Python tests
	$(PYENV)/bin/py.test

.PHONY: build
build: python-setup # Build the Python library in development mode
	$(PYENV)/bin/pip install .

.PHONY: watch
watch:	## build via watching src files
	@$(MAKE) watch-add-python

.PHONY: watch-add-python
watch-add-python:
	@$(SHELL) bin/watch-add

.PHONY: watch-del-python
watch-del-python:
	@$(SHELL) bin/watch-del
