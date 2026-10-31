# Tutorial

This tutorial walks through the everyday use of `bobbie`: installing it,
loading settings, reading and changing them, and passing them to the rest of
a project.

## Installation

Install `bobbie` with `pip`:

```sh
pip install bobbie
```

`bobbie` reads `ini`, `json`, `toml`, and Python module files with the Python
standard library. Reading `yaml` files also requires
[`PyYAML`](https://pypi.org/project/PyYAML/), which you can install with the
`yaml` extra:

```sh
pip install "bobbie[yaml]"
```

## The Settings class

Everything in `bobbie` goes through one class, `Settings`. A `Settings`
instance stores its data in a `dict` named `contents` and behaves like a
`dict`, so you can use `[]`, `in`, `len`, iteration, `keys`, `values`, and
`items` just as you would with a `dict`.

Project settings are usually organized into sections, each of which is a
`dict` of options:

```python
import bobbie

settings = bobbie.Settings({
    'general': {
        'verbose': False,
        'seed': 43},
    'files': {
        'source_format': 'csv',
        'file_encoding': 'windows-1252'}})

settings['general']['seed']  # 43
'files' in settings  # True
list(settings)  # ['general', 'files']
```

Several methods (`add`, `update`, `inject`, and the `+` operator) expect this
sectioned layout. See [Changing settings](#changing-settings) below.

## Creating Settings

There are four ways to create a `Settings` instance. They all produce the same
result.

```python
import bobbie

# 1. Let `create` pick the right constructor for the source.
settings = bobbie.Settings.create('settings.toml')
# 2. Use the constructor for the general kind of source.
settings = bobbie.Settings.from_file('settings.toml')
# 3. Use the constructor for the specific file type.
settings = bobbie.Settings.from_toml('settings.toml')
# 4. Pass a `dict` directly to `Settings`.
settings = bobbie.Settings({'general': {'seed': 43}})
```

`create` accepts a `str` path, a `pathlib.Path`, or any `dict`-like object
(`MutableMapping`). Anything else raises a `TypeError`.

### Supported files

`from_file` (and `create`, when it is given a path) chooses a loader from the
file extension:

| Extension | Loader | Parsed with |
| --- | --- | --- |
| `.ini` | `from_ini` | `configparser.ConfigParser` |
| `.json` | `from_json` | `json.load` |
| `.py` | `from_module` | `importlib` |
| `.toml` | `from_toml` | `tomllib.load` |
| `.yaml`, `.yml` | `from_yaml` | `yaml.safe_load` |

A path that does not exist raises a `FileNotFoundError`, and an unsupported
extension raises a `TypeError`.

Here are the same settings in each format.

=== "toml"

    ```toml
    [general]
    verbose = false
    seed = 43

    [files]
    source_format = "csv"
    file_encoding = "windows-1252"

    [tasks]
    things_to_do = ["stop", "drop", "roll"]
    ```

=== "yaml"

    ```yaml
    general:
        verbose: false
        seed: 43

    files:
        source_format: csv
        file_encoding: windows-1252

    tasks:
        things_to_do:
            - stop
            - drop
            - roll
    ```

=== "ini"

    ```ini
    [general]
    verbose = false
    seed = 43

    [files]
    source_format = csv
    file_encoding = windows-1252

    [tasks]
    things_to_do = stop, drop, roll
    ```

=== "json"

    ```json
    {
        "general": {
            "verbose": false,
            "seed": 43
        },
        "files": {
            "source_format": "csv",
            "file_encoding": "windows-1252"
        },
        "tasks": {
            "things_to_do": ["stop", "drop", "roll"]
        }
    }
    ```

=== "py"

    ```python
    settings = {
        'general': {
            'verbose': False,
            'seed': 43},
        'files': {
            'source_format': 'csv',
            'file_encoding': 'windows-1252'},
        'tasks': {
            'things_to_do': ['stop', 'drop', 'roll']}}
    ```

Each of these files loads as the same `Settings`:

```python
settings = bobbie.Settings.create('settings.ini')
settings['general']['verbose']  # False
settings['tasks']['things_to_do']  # ['stop', 'drop', 'roll']
```

!!! note "Python modules"
    A Python settings file must define a module-level variable named
    `settings` that holds the `dict` of settings. The module is run when it is
    loaded, so only load modules that you trust. See the
    [Advanced User Guide](advanced.md#global-options) to use a different
    variable name.

### Type inference

`ini` files store every value as a string, and `json` files often do, too. So,
`bobbie` converts the values that it loads from those formats to the matching
Python types:

| Stored string | Loaded value |
| --- | --- |
| `'42'` | `42` |
| `'2.5'` | `2.5` |
| `'true'`, `'yes'` (any case) | `True` |
| `'false'`, `'no'` (any case) | `False` |
| `'[x, y, z]'` | `['x', 'y', 'z']` |
| `'x, y, z'` | `['x', 'y', 'z']` |
| `'{a: 1, b: [x, y]}'` | `{'a': 1, 'b': ['x', 'y']}` |
| `'csv'` | `'csv'` (unchanged) |

Values in `toml`, `yaml`, and Python module files are left as they are,
because those formats already store their own types. The
[Advanced User Guide](advanced.md#type-inference-rules) covers the exact rules
and how to turn inference on or off for each format.

## Reading settings

Use `[]` to read a section or a value:

```python
settings['files']  # {'source_format': 'csv', 'file_encoding': ...}
settings['files']['source_format']  # 'csv'
```

`get` returns a fallback for a missing key:

```python
settings.get('database', {})  # {}
```

!!! warning "`get` differs from `dict.get`"
    If there is no fallback, `get` raises a `KeyError` for a missing key
    instead of returning `None`. Pass a `default` or set a
    [default factory](advanced.md#defaults-for-missing-keys) if you want
    missing keys to return something.

`keys`, `values`, and `items` return the same views as a `dict`:

```python
for section, options in settings.items():
    print(section, options)
```

To get a plain `dict` back, use `contents` (or copy it):

```python
import copy

plain = copy.deepcopy(settings.contents)
```

## Changing settings

Assign to a key to add or replace a whole section:

```python
settings['database'] = {'host': 'localhost', 'port': 5432}
```

`add` merges options into a section. If the section exists, its options are
updated. If it does not, it is created:

```python
settings.add('general', {'seed': 7, 'workers': 4})
settings['general']  # {'verbose': False, 'seed': 7, 'workers': 4}
```

`update` calls `add` for each section in a `dict`, and `+=` does the same:

```python
settings.update({'general': {'verbose': True}, 'cache': {'size': 100}})
settings += {'cache': {'size': 200}}
```

`+` returns a new `Settings` that combines both and leaves the original
unchanged:

```python
debug_settings = settings + {'general': {'verbose': True}}
```

!!! note "Merging is one level deep"
    `add`, `update`, `+`, and `+=` merge the options *within* each section.
    An option whose value is itself a `dict` is replaced, not merged. Also,
    adding to an existing key whose value is not a `dict` (such as
    `settings.add('seed', {...})` when `settings['seed']` is `43`) raises an
    `AttributeError`.

To remove a section, use `delete` or `del`:

```python
settings.delete('cache')
del settings['database']
```

Deleting a missing key does nothing by default. Pass `return_error = True` to
`delete` to raise a `KeyError` instead:

```python
settings.delete('cache', return_error = True)  # KeyError
```

## Choosing some sections

`subset` returns a new `Settings` with only some of the sections. Pass the
keys to keep to `include`, the keys to drop to `exclude`, or both (`include`
is applied first):

```python
files_only = settings.subset(include = 'files')
no_tasks = settings.subset(exclude = ['tasks'])
```

The values in the subset are deep copies, so changing them does not change
the original. Pass `returns = 'simple'` to get a plain `dict` instead of a
`Settings`.

## Injecting settings into objects

`inject` copies the options in one or more sections onto an object as
attributes. This is a quick way to configure a class instance:

```python
class Loader:
    source_format = None
    file_encoding = 'utf-8'

loader = settings.inject(Loader(), sections = 'files')
loader.source_format  # 'csv'
loader.file_encoding  # 'windows-1252'
```

Leave out `sections` to inject every section. Sections that are not in the
settings are skipped.

By default, `inject` overwrites existing attributes. Pass `overwrite = False`
to keep them:

```python
loader = settings.inject(Loader(), sections = 'files', overwrite = False)
loader.source_format  # 'csv' (the existing value, None, was empty)
loader.file_encoding  # 'utf-8'
```

!!! note
    With `overwrite = False`, an attribute is only kept if its value is
    truthy. Attributes that are `None`, `False`, `0`, or empty are still
    replaced.

## Next steps

* The [Advanced User Guide](advanced.md) covers passing arguments to the file
  parsers, the global options, defaults for missing keys, and subclassing.
* The [Recipes](recipes.md) show common patterns, such as layering default
  and local settings.
* The [API reference](reference/Settings.md) documents every method.
