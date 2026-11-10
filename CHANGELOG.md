# Changelog

## [Unreleased]
### Added
- Add support for Wagtail 7.4 (@marteinn)
- Add support for Python 3.14 (@marteinn)
- Add support for Wagtail 8.0 and 8.1 (@marteinn)
- Add support for Django 6.0 and 6.1 (@marteinn)
- Add requirements section with supported Python, Django and Wagtail versions to README (@marteinn)

### Changed
- Require wagtail-modeladmin 2.5 or newer (@marteinn)
- Require wagtail-factories 4.5 or newer for testing (@marteinn)
- Lock CI tooling with hashes in uv.lock using dependency groups and add make lock to regenerate them (@marteinn)
- Split CI publish into build and publish jobs using GitHub environments and uv publish, and limit workflow permissions (@marteinn)
- Test lowest declared dependency versions in CI (@marteinn)
- Lint GitHub Actions workflows with zizmor in CI (@marteinn)
- Remove deprecated setup_requires from setup.py (@marteinn)

### Fixed
- Replace removed _editor_js.html template include with insert_editor_js hook output in restore view (@marteinn)
- Escape page titles in trash can listing to prevent XSS (@marteinn)
- Show an error instead of crashing when restoring a page whose parent was deleted or whose slug is taken at the destination (@marteinn)
- Prevent restoring pages into a parent or destination that is itself in the trash can (@marteinn)
- Check restore permissions against the destination so non-superusers can restore pages, and require add and publish rights there (@marteinn)
- Show a form error instead of crashing when restore and move gets an unknown destination page (@marteinn)
- Ignore /plans/ dir for boilerplate (@marteinn)
- Pin GitHub Actions to commit SHAs and upgrade checkout and setup-python to v7 for Node.js 24 (@marteinn)

### Removed
- Drop support for Wagtail versions below 7.4 (@marteinn)
- Drop support for Python 3.9 and 3.10 (@marteinn)
- Drop support for Django 4.2 and 5.1 (@marteinn)

## [3.2.0] - 2025-08-23
### Added
- Add support for Wagtail 7.0 and 7.1 (@marteinn)
- Make it possible to exclude pages in trash from sitemap using SkipSitemapIfInTrashMixin (@marteinn)
- Exclude TrashCanPage from sitemap (@marteinn)
- Add support for Django 5.2 (@marteinn)

### Fixed
- Bump postgres version to 15 in local dev environment (@marteinn)
- Use python 3.13 when running linting/publish in CI (@marteinn)
- Update usage examples (@marteinn)

### Removed
- Drop support for Wagtail 5.2 (@marteinn)
- Drop support for Wagtail 6.2 (@marteinn)
- Drop support for Django 5.0 (@marteinn)

## [3.1.0] - 2025-02-01
### Added
- Add Wagtail 6.2 and 6.3 support (@marteinn)
- Add python 3.13 support (@marteinn)

### Changed
- Set Wagtail 5.2 as min version (@marteinn)

### Fixed
- Add form validation before moving page (@marteinn)

### Removed
- Drop EOL python 3.8 (@marteinn)
- Drop Django 3.2 support (@marteinn)

## [3.0.0] - 2024-02-10
### Added
- Add Wagtail 6 support (@marteinn)

### Changed
- Add wagtail-modeladmin as a dependency (@marteinn)

### Removed
- Drop EOL Wagtail 4.1 support (@marteinn)
- Drop EOL Wagtail 5.1 support (@marteinn)

## [2.0.0] - 2023-12-30
### Added
- Add Python 3.12 support (@marteinn)
- Add Wagtail 5.1 support (@marteinn)
- Add Wagtail 5.2 support (@marteinn)
- Add wagtail-modeladmin support (@marteinn)

### Fixed
- Upgrade python version in example environment and resolve build issues
- Replace deprecated assertEquals with assertEqual
- Upgrade github actions (@marteinn)

### Removed
- Drop EOL Python 3.7 support (@marteinn)
- Drop EOL Wagtail 4.2 support (@marteinn)
- Drop EOL Wagtail 5.0 support (@marteinn)

## [1.0.1] - 2023-05-21
### Added
- Add Wagtail 5 support (@marteinn)

## [1.0.0] - 2023-03-23
### Added
- Add delete_stray_pages command for clearing stray pages in trash can (@marteinn)
- Add support for moving deleted pages to trash can when using bulk actions (@rinti)

### Fixed
- Add Wagtail 4.1 and 4.2 support (@marteinn)
- Add python 3.11 support (@marteinn)
- Remove wagtailadmin.W003 warning in development (@marteinn)
- Fix incorrect test alias in docker-entrypoint.sh (@marteinn)
- Fix bug where pages deleted from trashcan was not properly deleted (@marteinn)
- Fix bug where two pages with the same slug couldn't be in the trash can at the same time (@rinti)

### Removed
- Drop Wagtail 2 support
- Drop Wagtail 3 support

## Upgrade considerations
- Due to a bug in delete pages are not properly removed, this was fixed in 1.0.0. Run `python manage.py delete_stray_pages` to fix this

## [0.3.0] - 2022-07-29
### Added
- Add Wagtail 3.0 compatibility (Thanks @polesello!)

### Fixed
- Add code and tests verifying urls gets preserved when moving pages (Andreas Bernacca)

## [0.2.1] - 2022-02-13
### Added
- Add Wagtail 2.16 compability (Andreas Bernacca)

### Fixed
- Make datetime time zone aware (Martin Sandström)
- Add custom text for when trash can is empty


## [0.2.0] - 2022-02-12
### Added
- Add changelog (Andreas Bernacca)
- Add translations (Alexandre Marinho)
- Add spanish translations (Yamil Jaskolowsk)
- Add swedish translations (Martin Sandström)

### Fixed
- Add CI/CD deployment (Martin Sandström)
- Add Django 4.0 compability

### Removed
- Drop Wagtail <2.14 support
- Drop Python 3.5 and 3.6 support

## [0.1.1] - 2021-06-09
### Fixed
- Rename template directory from the legacy name `wagtail_recycle_bin` to `wagtail_trash`. (cspollar)


## [0.1.0]

- Initial release
