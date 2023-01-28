PYENV := $(shell python3 -c "import sys; print('.venv' + '.'.join(str(x) for x in sys.version_info[:2]))")
PYSRC := src

.PHONY: python-venv
python-venv: $(PYENV)/bin/python3 # ensures Python virtual environment
	@:

$(PYENV)/bin/python3:
	@ python3 -m venv $(PYENV)
	@ $(PYENV)/bin/pip install --upgrade pip wheel setuptools
	@ $(PYENV)/bin/pip install -r requirements/dev.txt --exists-action i

.PHONY: build-python
build-python: python-venv # Build the Python library in development mode
	@ $(PYENV)/bin/pip install .

.PHONY: clean-python
clean-python: # cleans the python virtual environment
	@ find . -type f -name '*.pyc' -exec rm -r {} + || true;
	@ find . -type d -name "__pycache__" -exec rm -r {} + || true
	@ find . -type d -name ".pytest_cache" -exec rm -r {} + || true
	@ find . -type d -name "generated" -exec rm -r {} + || true
	@ find . -type d -name "*.egg-info" -exec rm -r {} + || true
	@ find . -type d -name ".ipynb_checkpoints" -exec rm -r {} + || true
	@ rm -rf dist build .coverage || true
	@ find . -type d -name "$(PYENV)" -exec rm -r {} + || true

.PHONY: fmt-python
fmt-python: python-venv # Run black to format Python code
	@ $(PYENV)/bin/python3 -m black --exclude \(\.venv.\*\)\|\(.eggs\) $(PYSRC)/flow $(PYSRC)/tests

.PHONY: lint-python
lint-python: python-venv # Run flake8, black, mypy, and pylint for level 9000 linting Python code
	@ $(PYENV)/bin/python3 -m flake8 $(PYSRC)/flow $(PYSRC)/tests
	@ $(PYENV)/bin/python3 -m black --check --exclude \(\.venv.\*\)\|\(.eggs\) $(PYSRC)/flow $(PYSRC)/tests
	@ $(PYENV)/bin/python3 -m mypy $(PYSRC)/flow/ $(PYSRC)/tests/
	@ $(PYENV)/bin/python3 -m pylint $(PYSRC)/flow/ $(PYSRC)/tests/

.PHONY: test-python
test-python: build # Run all Python tests
	@ $(PYENV)/bin/py.test

.PHONY: watch-add-python
watch-add-python:
	@ $(SHELL) bin/watch-add

