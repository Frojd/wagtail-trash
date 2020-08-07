from pathlib import Path
import subprocess
import sys

import black
from django.test import TestCase

code_root = Path(__file__).parent.parent


class TestBlack(TestCase):
    def test_black_is_used(self):
        result = subprocess.run(
            [
                "black",
                "--exclude",
                "/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|migrations)/",
                "--check",
                str(code_root),
            ],
        )
        self.assertEqual(result.returncode, 0)
