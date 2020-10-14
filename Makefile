format_code:
	black --exclude "/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|migrations)/" ./

makemigrations:
	docker-compose exec web django-admin makemigrations

migrate:
	docker-compose exec web django-admin makemigrations

test:
	docker-compose exec web django-admin makemigrations
