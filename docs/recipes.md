# Recipes

Short solutions to common configuration tasks. Each one assumes
`import bobbie`.

## Layer local settings over defaults

Keep shared defaults in one file and let each user or machine override some
of them in a second file that is not committed:

```python
import pathlib

settings = bobbie.Settings.create('defaults.toml')
local = pathlib.Path('local.toml')
if local.exists():
    settings += bobbie.Settings.create(local)
```

Because `+=` merges the options within each section, `local.toml` only needs
the options that it changes.

## Choose settings for an environment

Combine base settings with a file for the current environment, chosen with an
environment variable:

```python
import os

environment = os.environ.get('APP_ENV', 'development')
settings = (
    bobbie.Settings.create('settings.toml')
    + bobbie.Settings.create(f'settings.{environment}.toml'))
```

## Override settings with environment variables

`bobbie` does not read environment variables itself, but you can add them as
another layer. Here, `MYAPP__GENERAL__SEED=7` sets `settings['general']['seed']`:

```python
import os

overrides: dict[str, dict[str, str]] = {}
for key, value in os.environ.items():
    if key.startswith('MYAPP__'):
        _, section, option = key.lower().split('__', 2)
        overrides.setdefault(section, {})[option] = value
settings += overrides
```

Environment variables are always strings, so convert the values that need
another type.

## Load a settings file that ships with a package

Use `importlib.resources` to find a file inside an installed package, even
when the package is not a normal folder:

```python
from importlib import resources

source = resources.files('my_package') / 'settings.toml'
with resources.as_file(source) as path:
    settings = bobbie.Settings.create(path)
```

## Share one Settings across a project

Load the settings once in a module and import that module wherever the
settings are needed:

```python
# my_package/configuration.py
import bobbie

settings = bobbie.Settings.create('settings.toml')
```

```python
# my_package/analysis.py
from my_package.configuration import settings

seed = settings['general']['seed']
```

## Configure a dataclass

To build a dataclass from a section, unpack the section as keyword arguments.
This also checks that every option matches a field:

```python
import dataclasses


@dataclasses.dataclass
class FileOptions:
    source_format: str = 'csv'
    file_encoding: str = 'utf-8'


file_options = FileOptions(**settings['files'])
```

To set attributes on an existing object instead, use `inject`:

```python
file_options = settings.inject(FileOptions(), sections = 'files')
```

## Keep a value as a string

Type inference turns `ini` and `json` strings that look like numbers into
numbers, so a ZIP code such as `02134` becomes `2134`. Store values like this
in a `toml` or `yaml` file (which keep strings as strings), or turn off
inference for the file type before loading:

```python
from bobbie import options

options._INFER_TYPES['ini'] = False
settings = bobbie.Settings.create('addresses.ini')
settings['address']['zip']  # '02134'
```

Inside a list or dict string, you can also quote an item to keep it a string,
as in `zips = ['02134', '10001']`.

## Use exact decimals

Load `toml` or `json` floats as `decimal.Decimal` to avoid rounding errors:

```python
import decimal

settings = bobbie.Settings.create('rates.toml', parse_float = decimal.Decimal)
```

## Reuse values in an `ini` file

Turn on `configparser` interpolation to refer to other options. Options in
the `DEFAULT` section are available in every section:

```ini
[DEFAULT]
root = /data

[paths]
raw = %(root)s/raw
processed = %(root)s/processed
```

```python
import configparser

settings = bobbie.Settings.create(
    'paths.ini', interpolation = configparser.BasicInterpolation())
settings['paths']['raw']  # '/data/raw'
```

## Save settings

Use `to_file` (or the `to_` method for the file type) to save settings, such
as after changing them in code:

```python
settings['general']['seed'] = 7
settings.to_file('settings.json')
```

## Convert a settings file to another format

Load the file and export it with the extension of the new format:

```python
bobbie.Settings.create('settings.ini').to_file('settings.toml')
```

Values that `bobbie` infers from an `ini` or `json` file keep their inferred
types in the new file. For example, `seed = 43` in the `ini` file becomes the
`toml` integer `43`, not the string `"43"`.

## Write a starter settings file

Build the defaults in code and export them, so that users have a file to
edit:

```python
defaults = bobbie.Settings({
    'general': {'verbose': False, 'seed': 43},
    'files': {'source_format': 'csv', 'file_encoding': 'utf-8'}})
defaults.to_file('settings.yaml')
```

## Pass only some sections to a component

Give a component its own copy of the sections it needs, so that it cannot
change the rest of the settings:

```python
model_settings = settings.subset(include = ['model', 'training'])
```
