format_code:
	uv run --frozen --only-group lint black --exclude "/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|venv|_build|buck-out|build|dist|migrations)/" ./
	uv run --frozen --only-group lint isort .

makemigrations:
	docker-compose exec web django-admin makemigrations

migrate:
	docker-compose exec web django-admin migrate

test:
	docker-compose exec web python runtests.py

lock:
	uv lock --upgrade
	uv export --frozen --only-group uv --format requirements-txt -o requirements/uv.txt -q
	uv export --frozen --only-group build --format requirements-txt -o requirements/build-constraints.txt -q
