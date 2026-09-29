# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.2.1

* Fixed loading `ini` files with values that contain a "%" (such as `float_format = %.4f`), which raised a `configparser.InterpolationSyntaxError`. Interpolation is now off by default and can be turned back on with `interpolation = configparser.BasicInterpolation()`.
* Fixed loading a missing `ini` file, which was silently ignored instead of raising a `FileNotFoundError`.
* Fixed `Settings.inject`, which ignored its `overwrite` and `sections` arguments.
* Fixed `Settings.keys`, which called itself forever and raised a `RecursionError`.

## 0.2.0

* Stable release version with all tests and lint checks passed

## 0.1.8

* Switched to `uv` as dependency manager
* Updated GitHub Actions and dependencies
* Added full support for yaml and toml
* Removed support for env (not nested) and xml (rarely used)

## 0.1.7

* Fixed GitHub actions bug with `pdm` and `ruff`
* Fixed typo in readme

## 0.1.6

* Added documentation and readme
* Added more tests
* Added .env support
* Changed required Python version to 3.11 or later

## 0.1.5

* Changelogs not stored before the transitition to the `snickerdoodle` template
