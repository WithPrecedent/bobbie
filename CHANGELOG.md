# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## Unreleased

* Added the `py.typed` marker so that type checkers use the type hints in
  `bobbie`.

## 0.3.0

* **Breaking:** `settings + other` now returns a new `Settings` and leaves both operands unchanged. Use `settings += other` to add `other` in place (the old behavior of "+").
* Removed the claim that `Settings.create` accepts a sequence of paths or mappings, which it never supported. Passing one raises a `TypeError`.
* Removed the commented-out `env` and `xml` loaders and their options.
* Updated to the `snickerdoodle` 0.5.0 template (Codecov coverage, a coverage page in the docs, `pydoclint`, Python 3.15, SPDX license metadata, a version read from `__version__`, GitHub CLI releases, and `uv` updates from Dependabot). Added `.cruft.json` so that `cruft update` can apply future template changes.
* Removed the leftovers from `pdm` (`pdm.lock` and the credits page and script, which read `pdm.lock`) and moved the issue templates out of a nested `ISSUE_TEMPLATE` folder.
* Now requires `bunches` 0.3.0 and `wonka` 0.3.0 or later, which ship type information, so `mypy` checks `Settings` against its base classes. The intentional differences from `bunches.Dictionary` (`add`, `update`, `items`, `keys`, and `values`) are marked with `# type: ignore[override]`.
* `Settings` now inherits `fromkeys`, `setdefault`, and `subset` from `bunches.Dictionary` instead of repeating them. `subset` now deep copies the values chosen with `include` (before, they were shared with the original) and accepts a `returns` argument ("class", "copy", or "simple"). `fromkeys` now accepts any iterable of keys and defaults `value` to `None`, as `dict.fromkeys` does.
* Documented type inference in the README, including that `toml`, `yaml`, and Python module values are not converted, and removed the README acknowledgments.
* Added conversion of list and dict strings to Python lists and dicts when inferring types (such as from `ini` files). `[x, y, z]` becomes `['x', 'y', 'z']` and `{a: 1, b: [x, y]}` becomes `{'a': 1, 'b': ['x', 'y']}`. Items are converted recursively, may be nested, and may be quoted to keep commas or prevent conversion.
* Splitting strings on ", " into lists now ignores commas inside brackets or quotes.
* Fixed `Settings.from_toml`, which ignored its keyword arguments (such as `parse_float`).
* Fixed `Settings.from_yaml`, which raised a `TypeError` when given any keyword arguments. They are now accepted and ignored.
* Fixed loading a file with an unsupported extension, which raised a `KeyError` instead of the documented `TypeError`.
* Fixed the `Settings.create` example in the docstring, which was not valid Python.
* Restyled the package (single quotes, spaces around keyword argument `=`, closing brackets on the last line, and complete docstrings). Ruff now enforces single quotes and the 80 character line limit.
* `mypy` now passes and runs in CI. `yaml` is treated as an untyped import.
* Removed the `ruff format` pre-commit hook, which would undo the package style, and set ruff's `force-exclude` so pre-commit does not lint excluded folders.
* Added tests for the `dict` methods, `inject`, `subset`, `fromkeys`, missing and unsupported files, keyword arguments, and the private utilities (44 tests in total).

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
