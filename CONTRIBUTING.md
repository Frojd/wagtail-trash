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

The code is formatted and linted with [ruff](https://docs.astral.sh/ruff/),
configured in `pyproject.toml` and enforced in CI. All lint rules are enabled, the
ones that do not fit the project are ignored there with a reason. Prefer fixing a
finding over ignoring it, and use `# noqa: <code>` for a single line rather than
adding to the ignore list. To format and apply fixes:

```bash
make format_code
```

To run the same checks as CI:

```bash
make lint
```

Both run the exact ruff version locked in `uv.lock`, the same one CI uses, so they
need [uv](https://docs.astral.sh/uv/).

## CI workflows

CI is split in two workflows in `.github/workflows/`:

- `ci.yml` runs on every push and pull request: `lint`, `test`, `test-lowest`,
  `security` (Trivy) and `security-actions` (zizmor)
- `deploy.yml` is a reusable workflow that `ci.yml` calls on `v*` and `testv*` tags
  once all checks pass. It builds the package and publishes it

Actions must be pinned to a full commit SHA, the repository policy rejects tags.
Reusable workflows in this repo are referenced with `$/.github/workflows/...`.

Workflows are audited with [zizmor](https://docs.zizmor.sh/), configured in
`zizmor.yml`. Run it locally before changing them:

```bash
uv run --frozen --only-group lint zizmor --config zizmor.yml .github/workflows
```

[Trivy](https://trivy.dev/) scans for vulnerable dependencies, misconfigurations and
leaked secrets, configured in `trivy.yaml`. Accepted findings go in
`.trivyignore.yaml` with a comment explaining why. To run it locally:

```bash
trivy fs --config trivy.yaml .
```

## CI dependencies

The tools CI uses to lint and build (uv, ruff, zizmor, setuptools, wheel) are
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
`testv*` tag publishes to TestPyPI. The package is built once in the `build` job in
`deploy.yml` and the same files are uploaded by `deploy-pypi` or `deploy-testpypi`,
which run in the `pypi` and `testpypi` GitHub environments.

The tag must match the version in `wagtail_trash/version.py`, otherwise the `build`
job fails. To release:

1. Set the version in `wagtail_trash/version.py` and push `testv<version>`, for
   example `testv3.3.0`
2. Check the release on https://test.pypi.org/project/wagtail-trash/ and install it
   without dependencies, since anyone can upload packages such as `wagtail` to
   TestPyPI:

   ```bash
   uv pip install --no-deps --index-url https://test.pypi.org/simple/ wagtail-trash==<version>
   ```

3. Merge the release into `main` and push `v<version>`

If a publish job fails, re-run that job. It uploads the same files and skips the
ones already published. If a broken build was published to TestPyPI, test again
with a release candidate such as `3.3.0rc1` before tagging the final version.
