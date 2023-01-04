.PHONY: lint-prettier
lint-prettier:
	@ echo '[lint:prettier]'
	@ prettier -c **/*.{js,y[a]ml}

.PHONY: lint-markdown
lint-markdown:
	@ echo '[lint:markdown]'
	@ docker run -it --rm -v $$PWD:/workdir ghcr.io/igorshubovych/markdownlint-cli:latest "*.md"
