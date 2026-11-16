from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class TestSystemChecks(TestCase):
    def test_no_system_check_warnings(self):
        call_command("check", fail_level="WARNING", stdout=StringIO())
