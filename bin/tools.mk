SRC_NO_CONTRIB ?= 1

.git/hooks/pre-commit:
	@ SRC_NO_CONTRIB=$(SRC_NO_CONTRIB) $(SHELL) bin/git/install-hooks

pre-commit: .git/hooks/pre-commit

pre-commit-run:
	@ SRC_NO_CONTRIB=$(SRC_NO_CONTRIB) $(SHELL) bin/git/run-hooks

.PHONY: pre-commit-clean
pre-commit-clean:
	@ rm -r .git/hooks/pre-commit

.PHONY: fmt-prettier
fmt-prettier: # Run prettier to format Javascript & YAML files
	@ echo '[fmt:prettier]'
	@ prettier -cw **/*.{js,y[a]ml}

lint-scripts: # Runs shellcheck
	@ docker run --rm -v "$$PWD:/mnt" koalaman/shellcheck:stable '*.sh'

.PHONY: lint-prettier
lint-prettier:
	@ echo '[lint:prettier]'
	@ prettier -c **/*.{js,y[a]ml}

.PHONY: lint-markdown
lint-markdown:
	@echo '[lint:markdown]'
	@docker run -it --rm -v $$PWD:/workdir ghcr.io/igorshubovych/markdownlint-cli:latest "*.md"

.PHONY: lint-docker
lint-docker: # Runs linting on Dockerfile
	@ docker run --rm -i ghcr.io/hadolint/hadolint < Dockerfile

.PHONY: watch-del
watch-del: # Cleans up watchman configs for git root
	@ $(SHELL) bin/watch-del