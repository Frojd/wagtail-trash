from tests.app.settings import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": "db",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
    },
}

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ["wagtail.contrib.styleguide"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
