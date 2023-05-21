# Changelog

## [Unreleased]
### Added
### Changed
### Fixed
### Removed

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
