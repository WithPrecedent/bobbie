# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.3.3

* The API documentation now has one page for each public object (the names in `__all__`), so it only documents `Settings`, and only once. Before, it had a page for every module, including the private `options` and `utilities`, and showed `Settings` twice.
* The `Settings` page now includes the public methods inherited from `bunches.Dictionary` (`fromkeys`, `setdefault`, and `subset`) and leaves out the unused `sources` attribute inherited from `wonka.Sourcerer`.
* Added a `griffe` extension so that section markers (such as `""" Class Methods """`) after an attribute are not shown as that attribute's description.
* Type inference now splits a list on a comma followed by any whitespace, not only a space, so an `ini` list can span several lines (`steps = a, b,` followed by an indented `c`). Before, a comma at the end of a line did not split the value.
* **Possibly breaking:** `ini` files can have comments after values. A `#` with whitespace before and after it starts a comment that runs to the end of its line (as in `label = target # the column to predict`), on any line of a value. A `#` without whitespace on both sides (as in `#1f77b4` or `a#b`) is kept. Set `options._INLINE_COMMENTS` to `False` to keep comments in values, as before.

## 0.3.2

* Fixed type inference, which raised a `RecursionError` for strings with a ", " only inside brackets, parentheses, or quotes (such as an `ini` value of `see (a, b)`). Those strings now stay strings.
* Fixed `Settings.create` and `Settings.from_file`, which passed `parameters` to the file parser (raising a `TypeError`) instead of to the new `Settings`, as the `Settings` docstring describes.
* **Possibly breaking:** `ini`, `json`, and `yaml` files are now read as UTF-8 instead of the platform's default encoding for `json` and `yaml` (such as cp1252 on Windows). Pass `encoding` to read another encoding.
* Fixed `options._ALWAYS_RETURN_ERROR`, which was read once at import, so changing it had no effect on `delete` and `del`.
* A file type in `options._FILE_EXTENSIONS` with no `from_<type>` loader now raises the documented `TypeError` instead of an `AttributeError`. A Python module without a `settings` variable now raises an `AttributeError` that names the variable, instead of a `TypeError` saying that modules are not supported.
* Removed the `Settings.sources` class attribute, which `create` never used (it dispatches with `functools.singledispatchmethod`).
* Added `default_factory` to the `Settings` fields so that it appears in the API documentation and `mkdocs build --strict` passes.
* Removed the "To Do" sections from the module docstrings so that they do not appear in the documentation.
* Wrote the Tutorial, Advanced User Guide, and Recipes pages of the documentation, documented the `yaml` extra in the README, and fixed the README comparison table and links. Added the docs build, lint, and `mypy` commands to the Contribution Guide.
* Added tests for the fixes above (51 tests in total).

## 0.3.1

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
