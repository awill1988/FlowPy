.PHONY: docker-build
docker-build: # Build the Python library with airflow using Docker.
	@echo '[docker:build]'
	@docker build -t 'ates:with-airflow' --target=with-airflow .

.PHONY: lint-docker
lint-docker: # Lints the dockerfile
	@echo '[lint:docker]'
	@docker run --rm -i ghcr.io/hadolint/hadolint < Dockerfile
