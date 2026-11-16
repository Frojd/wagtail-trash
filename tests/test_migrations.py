from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class TestMigrations(TestCase):
    def test_no_missing_migrations(self):
        out = StringIO()
        try:
            call_command(
                "makemigrations",
                "wagtail_trash",
                "--check",
                "--dry-run",
                stdout=out,
            )
        except SystemExit:
            self.fail(f"Missing migrations for wagtail_trash:\n{out.getvalue()}")
