FROM python:3.12-slim

WORKDIR /srv

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONPATH=/srv/ \
    DJANGO_SETTINGS_MODULE=settings_dev \
    DJANGO_SUPERUSER_PASSWORD=admin

COPY . /srv/

RUN apt-get update \
        && apt-get install -y netcat-traditional \
        binutils libproj-dev \
        gettext libpq-dev build-essential \
        --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN pip install psycopg2-binary -e .

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["runserver"]
