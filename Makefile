format_code:
	black --exclude "/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|venv|_build|buck-out|build|dist|migrations)/" ./
	isort .

makemigrations:
	docker-compose exec web django-admin makemigrations

migrate:
	docker-compose exec web django-admin migrate

test:
	docker-compose exec web python runtests.py
