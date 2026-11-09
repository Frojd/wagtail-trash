# Contributing

Thanks for wanting to help out! This guide gets you from clone to running tests.

## Get started

The quickest way to get a working environment is Docker:

```bash
git clone https://github.com/Frojd/wagtail-trash.git
cd wagtail-trash
docker compose up
```

This starts Postgres, runs migrations and creates a superuser. When it's up, open
http://localhost:8080/admin/ and log in with `admin` / `admin`.

The `wagtail_trash` and `tests` directories are mounted into the container, so your
edits show up right away.

### Without Docker

You can also run things directly, which is what CI does:

```bash
python -m pip install -e ".[testing]"
python -m pip install wagtail-modeladmin
```

## Running tests

With Docker:

```bash
make test
```

Or directly:

```bash
python runtests.py
```

`runtests.py` passes any extra arguments on to Django's test runner, so you can
narrow things down:

```bash
python runtests.py tests.test_admin
```

The package supports both the built-in Wagtail admin and `wagtail-modeladmin`, so
the suite is run twice in CI. To run the second variant:

```bash
DJANGO_SETTINGS_MODULE=tests.app.settings_with_wagtail_modeladmin python runtests.py
```

## Code style

The code is formatted with [black](https://github.com/psf/black) and
[isort](https://pycqa.org/isort/), both enforced in CI:

```bash
make format_code
```

`make format_code` runs the exact black and isort versions locked in `uv.lock`, the
same ones CI uses, so it needs [uv](https://docs.astral.sh/uv/).

## CI workflows

Workflows in `.github/workflows/` are audited with [zizmor](https://docs.zizmor.sh/)
in CI. Run it locally before changing them:

```bash
uv run --frozen --only-group lint zizmor .github/workflows
```

Actions must be pinned to a full commit SHA, the repository policy rejects tags.

## CI dependencies

The tools CI uses to lint and build (uv, black, isort, zizmor, setuptools, wheel) are
declared as dependency groups in `pyproject.toml` and locked with hashes in
`uv.lock`. Publishing uses `uv publish`. `requirements/uv.txt` (used to install uv
itself) and `requirements/build-constraints.txt` are exported from `uv.lock`.

To change a version, edit `pyproject.toml`, then regenerate everything:

```bash
make lock
```

`make lock` also upgrades unpinned packages to their latest versions. Commit
`pyproject.toml`, `uv.lock` and `requirements/` together.

The test matrix is not locked on purpose: it installs the latest releases within
the supported ranges, the same way users do. A separate job tests the lowest
versions declared in `setup.py`:

```bash
uv pip install --resolution lowest-direct ".[testing]"
```

## Migrations

If you change a model, generate the migration with:

```bash
make makemigrations
```

Commit the generated migration along with your change.

## Branches and pull requests

This project uses git flow:

- `main` holds the current release
- `develop` holds ongoing development

Branch off `develop` and open your pull request against `develop`. Add a line to
`CHANGELOG.md` describing your change.

Releases are published automatically: pushing a `v*` tag publishes to PyPI, and a
`testv*` tag publishes to TestPyPI. The package is built once in a `build` job and
the same files are uploaded by the publish job, which runs in the `pypi` or
`testpypi` GitHub environment.
