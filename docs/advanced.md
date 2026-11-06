# Advanced User Guide

This guide covers the parts of `bobbie` beyond the [Tutorial](tutorial.md):
how `create` chooses a constructor, passing arguments to the file parsers, the
exact type inference rules, the global options, and extending `Settings`.

## How `create` works

`Settings.create` dispatches on the type of its first argument:

| Source type | Constructor |
| --- | --- |
| `str` or `pathlib.Path` | `from_file` |
| `MutableMapping` (such as a `dict`) | `from_dict` |
| Anything else | raises `TypeError` |

`from_file` then looks up the file extension in
`bobbie.options._FILE_EXTENSIONS` and calls the matching `from_<type>` class
method (`from_ini`, `from_json`, `from_module`, `from_toml`, or `from_yaml`).

Any keyword arguments that you pass to `create` or `from_file` are relayed to
that loader, which passes them to its parser.

### Setting attributes of the new instance

`create`, `from_dict`, and `from_file` accept a `parameters` `dict` of
arguments for the new `Settings` itself (such as `name` or `default_factory`).
They are kept apart from the keyword arguments for the parser:

```python
import decimal

settings = bobbie.Settings.create(
    'settings.toml',
    parameters = {'name': 'Project Settings'},
    parse_float = decimal.Decimal)
settings.name  # 'Project Settings'
```

An argument in `parameters` that `Settings` does not accept raises a
`TypeError`.

## Parser arguments

Each loader passes its keyword arguments to a different parser:

| Loader | Keyword arguments go to | Useful arguments |
| --- | --- | --- |
| `from_ini` | `configparser.ConfigParser` | `interpolation`, `delimiters`, `default_section` |
| `from_json` | `json.load` | `parse_float`, `parse_int`, `object_hook` |
| `from_module` | `importlib.util.spec_from_file_location` | rarely needed |
| `from_toml` | `tomllib.load` | `parse_float` |
| `from_yaml` | ignored | (accepted so that `create` works the same way for every type) |

For example, to load `toml` floats as `decimal.Decimal`:

```python
import decimal

settings = bobbie.Settings.create('settings.toml', parse_float = decimal.Decimal)
```

### File encoding

`ini`, `json`, and `yaml` files are read as UTF-8. Pass `encoding` to read a
file with another encoding:

```python
settings = bobbie.Settings.create('legacy.ini', encoding = 'cp1252')
```

`toml` files are always UTF-8, as the `toml` format requires.

The exporters take `encoding` too (see [Writer arguments](#writer-arguments)).

### `ini` files

A few details are specific to `ini` files:

* **Interpolation is off by default**, so values such as `%.4f` load as they
  are. To use `configparser` interpolation (such as `%(root)s`), pass
  `interpolation = configparser.BasicInterpolation()` or
  `configparser.ExtendedInterpolation()`.
* **Option names keep their case.** `configparser` normally lowercases them,
  but `bobbie` does not.
* **The `DEFAULT` section is not a section of its own.** Its options are
  added to every other section, as `configparser` does.
* **Comments can follow values.** A `#` with whitespace before and after it
  starts a comment that runs to the end of its line, on the first line of a
  value or any line after it. A `#` without whitespace on both sides (as in
  `#1f77b4` or `a#b`) is part of the value. Set `_INLINE_COMMENTS` to `False`
  to keep comments in values (see [Global options](#global-options)).
* **A list can span several lines**, since a comma followed by a line break
  separates its items (see [Type inference rules](#type-inference-rules)).

```ini
[tasks]
label = target  # the column to predict
steps = stop, drop,  # the first two steps
    roll
```

```python
settings = bobbie.Settings.create('tasks.ini')
settings['tasks']  # {'label': 'target', 'steps': ['stop', 'drop', 'roll']}
```

```ini
[DEFAULT]
root = /data

[paths]
raw = %(root)s/raw
```

```python
import configparser

settings = bobbie.Settings.create(
    'paths.ini', interpolation = configparser.BasicInterpolation())
settings['paths']  # {'raw': '/data/raw', 'root': '/data'}
```

### Python modules

`from_module` runs the module and reads its `settings` variable. If the
variable is missing, it raises an `AttributeError`. You can change the
variable name with
`_MODULE_SETTINGS_ATTRIBUTE` (see [Global options](#global-options)).

## Writer arguments

Each exporter passes its keyword arguments to a different writer, and some
change a default so that the file is easier to read:

| Exporter | Keyword arguments go to | Defaults set by `bobbie` | Useful arguments |
| --- | --- | --- | --- |
| `to_ini` | `configparser.ConfigParser` | `interpolation = None` | `delimiters`, `encoding` |
| `to_json` | `json.dump` | `indent = 4` | `ensure_ascii`, `sort_keys`, `encoding` |
| `to_module` | `pprint.pformat` | `sort_dicts = False` | `width`, `indent` |
| `to_toml` | `tomli_w.dump` | | `indent`, `multiline_strings` |
| `to_yaml` | `yaml.safe_dump` | `sort_keys = False` | `allow_unicode`, `default_flow_style`, `encoding` |

`to_file` passes its keyword arguments to the exporter for the file type. For
example, to write a `json` file with keys in sorted order:

```python
settings.to_file('settings.json', sort_keys = True)
```

`ini`, `json`, and `yaml` files are written as UTF-8 unless you pass
`encoding`. `json` and `yaml` escape characters that are not ASCII unless you
pass `ensure_ascii = False` or `allow_unicode = True`. `toml` files and Python
modules are always UTF-8.

### Exporting `ini` files

`to_ini` converts each value to a string that `from_ini` converts back to the
same value:

* Lists (and tuples) are written in square brackets and dicts in curly braces,
  such as `[stop, drop, roll]` and `{small: 1, big: [2.5, True]}`.
* Items in a list or dict are quoted when they would otherwise be converted or
  split, such as `['1', 'a, b', '']`.
* Interpolation is off, as it is when loading, so values such as `%.4f` are
  written as they are.

A few values cannot be written so that they load back unchanged:

* **Top-level values outside a section.** `ini` files only hold values inside
  sections, so `to_ini` raises a `TypeError` if a top-level value is not a
  `dict`.
* **Strings that look like other types.** A string value of `'42'`, `'yes'`, or
  `'a, b'` in a section is written without quotes (`ini` values have none) and
  loads as `42`, `True`, or `['a', 'b']`. Turn off type inference for `ini`
  files if you need these strings (see [Global options](#global-options)).
* **Comments.** A `#` with whitespace before and after it (as in `a # b`)
  loads as the start of a comment, even inside quotes. Set `_INLINE_COMMENTS`
  to `False` to keep it.
* **`None`.** It is written as `None` and loads as the string `'None'`.

The other file types store their own types, so they do not have these limits
(except that `toml` has no `None` and `json` keys must be strings).

## Type inference rules

When type inference is on for a file type (by default, `ini` and `json`),
`bobbie` converts string values with these rules, in order:

1. A string that `int` accepts becomes an `int` (such as `'42'`, `' 42 '`, or
   `'1_000'`). So, `'1'` becomes `1`, not `True`, and `'02134'` becomes
   `2134`.
2. A string that `float` accepts becomes a `float` (such as `'2.5'`, `'1e3'`,
   `'nan'`, or `'inf'`).
3. `'true'` and `'yes'` become `True`, and `'false'` and `'no'` become `False`
   (in any case). Other words, such as `'on'`, `'none'`, or `'null'`, stay
   strings.
4. A string in square brackets (such as `'[x, y, z]'`) becomes a `list`.
5. A string in curly braces (such as `'{a: 1, b: 2}'`) becomes a `dict` if
   every entry has a key and a value separated by `:`. Otherwise, it stays a
   string.
6. A string that contains a comma followed by whitespace, such as a space or
   a line break (as in `'x, y, z'` or `'x,\ny'`), becomes a `list`. A comma
   with no whitespace after it (such as `'a,b'`) does not split the string.
7. Any other string is unchanged. Values that are not strings (such as `json`
   numbers) are never changed.

Items in lists and dicts are converted with the same rules and may be nested
(such as `'[[1, 2], [3]]'`). Commas inside brackets or quotes do not split an
item, and quotes around an item keep it as a string and are removed:

| Stored string | Loaded value |
| --- | --- |
| `'[1, 2.5, true]'` | `[1, 2.5, True]` |
| `'["a, b", c]'` | `['a, b', 'c']` |
| `"['1']"` | `['1']` |
| `'{a: {b: no}}'` | `{'a': {'b': False}}` |
| `'{url: "http://x.com"}'` | `{'url': 'http://x.com'}` |
| `'[x, y], z'` | `[['x', 'y'], 'z']` |
| `"x not in ['a', 'b']"` | `"x not in ['a', 'b']"` |

Inference reaches the values at the top level and the values in each section.
Values nested more deeply (such as a `json` object inside a section) are left
as they are.

## Global options

`bobbie.options` stores the module-level options that `Settings` uses. They
are private (their names start with `_`), but you can change them to adjust
`bobbie` for a whole project. Change them before loading any settings.

| Option | Default | Effect |
| --- | --- | --- |
| `_INFER_TYPES` | `{'ini': True, 'json': True, 'toml': False, 'module': False, 'yaml': False}` | Whether to infer types for each file type. |
| `_MODULE_SETTINGS_ATTRIBUTE` | `'settings'` | Name of the variable that holds the settings in a Python module. |
| `_OVERWRITE_ATTRIBUTES` | `True` | Default for the `overwrite` argument of `inject`. |
| `_FILE_EXTENSIONS` | `{'ini': 'ini', 'json': 'json', 'toml': 'toml', 'py': 'module', 'yaml': 'yaml', 'yml': 'yaml'}` | Maps file extensions to file types (and so to `from_<type>` loaders and `to_<type>` exporters). |
| `_TYPER` | `bobbie.utilities._typify` | Function used to infer the type of each value. |
| `_INLINE_COMMENTS` | `True` | Whether to remove comments after values in `ini` files. |
| `_ALWAYS_RETURN_ERROR` | `False` | Default for the `return_error` argument of `delete` (and so whether `del` raises a `KeyError` for a missing key). |

For example:

```python
from bobbie import options

# Keeps `json` values exactly as they are stored.
options._INFER_TYPES['json'] = False
# Reads settings from a `CONFIG` variable in Python modules.
options._MODULE_SETTINGS_ATTRIBUTE = 'CONFIG'
```

## Defaults for missing keys

`Settings` can return a default for missing keys, like
`collections.defaultdict`. The default is only used by `get`, not by `[]`.

Set it with the `default_factory` argument or the `setdefault` method. If the
default is callable, `get` calls it and returns the result. Otherwise, `get`
returns the default itself:

```python
settings = bobbie.Settings({'general': {'seed': 43}}, default_factory = dict)
settings.get('database')  # {}

settings.setdefault('missing')
settings.get('database')  # 'missing'
settings['database']  # KeyError
```

A `default` passed to `get` takes priority over `default_factory`. Because
`None` means "no default," `get` cannot return `None` as a fallback. Set
`default_factory` to `lambda: None` if you need that.

## Differences from `dict`

`Settings` behaves like a `dict` in most ways, with these exceptions:

* `get` raises a `KeyError` for a missing key when there is no default
  (instead of returning `None`).
* `setdefault(value)` sets the default for `get` (see
  [above](#defaults-for-missing-keys)). It does not take a key.
* `del settings[key]` does nothing if `key` is missing (unless
  `_ALWAYS_RETURN_ERROR` is `True`).
* `update`, `+`, and `+=` merge the options within each section (see the
  [Tutorial](tutorial.md#changing-settings)) instead of replacing whole
  sections.
* `fromkeys` returns a `Settings` and accepts keyword arguments for it (such
  as `name`).
* A `Settings` is a dataclass, so `==` compares it to other `Settings`
  instances and is `False` for a plain `dict`. Compare `settings.contents` to
  a `dict` instead.
* Sections are not attributes. Use `settings['general']`, not
  `settings.general`.

## Subclassing and new file types

`Settings` is a dataclass, so you can subclass it to add fields or methods.
The class methods (`create`, `from_file`, and the loaders) return an instance
of the subclass.

To support another file type, add a `from_<type>` class method that returns
an instance, and map the extension to `<type>` in
`options._FILE_EXTENSIONS`. Call `_infer_types` on the loaded contents if
the format stores values as strings. For example, for a file of
`section.option = value` lines:

```python
import pathlib
from typing import Any

import bobbie
from bobbie import options


class ProjectSettings(bobbie.Settings):
    """Settings that can also load ".conf" files."""

    @classmethod
    def from_conf(
            cls,
            source: pathlib.Path | str,
            **kwargs: Any) -> ProjectSettings:
        """Creates an instance from a ".conf" file."""
        contents: dict[str, dict[str, Any]] = {}
        text = pathlib.Path(source).read_text(encoding = 'utf-8')
        for line in text.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                section, option = key.strip().split('.', 1)
                contents.setdefault(section, {})[option] = value.strip()
        return cls(cls._infer_types(contents))


options._FILE_EXTENSIONS['conf'] = 'conf'
settings = ProjectSettings.create('project.conf')
```

Only `ProjectSettings` can load the new file type. Loading a ".conf" file with
`bobbie.Settings` raises a `TypeError`, because it has no `from_conf` method.

To export the new file type too, add a `to_<type>` method that takes the path
and keyword arguments. `to_file` finds it through the same extension mapping:

```python
class ProjectSettings(bobbie.Settings):
    """Settings that can also load and export ".conf" files."""

    # from_conf as above.

    def to_conf(self, path: pathlib.Path | str, **kwargs: Any) -> None:
        """Exports the settings to a ".conf" file."""
        lines = [
            f'{section}.{option} = {value}'
            for section, options in self.items()
            for option, value in options.items()]
        pathlib.Path(path).write_text('\n'.join(lines) + '\n', encoding = 'utf-8')


settings.to_file('copy.conf')
```

Exporting a ".conf" file with `bobbie.Settings` raises a `TypeError`, because
it has no `to_conf` method.
