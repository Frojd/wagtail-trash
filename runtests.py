import argparse
import os
import sys

import django
import wagtail
from django.core.management import execute_from_command_line

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.app.settings")

print("Using settings: {}".format(os.environ["DJANGO_SETTINGS_MODULE"]))
print("Using django: {}".format(django.get_version()))
print("Using Wagtail {}".format(wagtail.__version__))


def runtests():
    args, rest = argparse.ArgumentParser().parse_known_args()

    argv = [sys.argv[0], "test"] + rest
    execute_from_command_line(argv)


if __name__ == "__main__":
    runtests()
