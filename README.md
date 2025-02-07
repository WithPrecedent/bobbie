# bobbie

| | |
| --- | --- |
| Version | [![PyPI Latest Release](https://img.shields.io/pypi/v/bobbie.svg?style=for-the-badge&color=steelblue&label=PyPI&logo=PyPI&logoColor=yellow)](https://pypi.org/project/bobbie/) [![GitHub Latest Release](https://img.shields.io/github/v/tag/WithPrecedent/bobbie?style=for-the-badge&color=navy&label=GitHub&logo=github)](https://github.com/WithPrecedent/bobbie/releases)
| Status | [![Build Status](https://img.shields.io/github/actions/workflow/status/WithPrecedent/bobbie/ci.yml?branch=main&style=for-the-badge&color=cadetblue&label=Tests&logo=pytest)](https://github.com/WithPrecedent/bobbie/actions/workflows/ci.yml?query=branch%3Amain) [![Development Status](https://img.shields.io/badge/Development-Active-seagreen?style=for-the-badge&logo=git)](https://www.repostatus.org/#active) [![Project Stability](https://img.shields.io/pypi/status/bobbie?style=for-the-badge&logo=pypi&label=Stability&logoColor=yellow)](https://pypi.org/project/bobbie/)
| Documentation | [![Hosted By](https://img.shields.io/badge/Hosted_by-Github_Pages-blue?style=for-the-badge&color=navy&logo=github)](https://WithPrecedent.github.io/bobbie)
| Tools | [![Documentation](https://img.shields.io/badge/MkDocs-magenta?style=for-the-badge&color=deepskyblue&logo=markdown&labelColor=gray)](https://squidfunk.github.io/mkdocs-material/) [![Linter](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/charliermarsh/Ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/Ruff) [![Dependency Manager](https://img.shields.io/badge/PDM-mediumpurple?style=for-the-badge&logo=affinity&labelColor=gray)](https://PDM.fming.dev) [![Pre-commit](https://img.shields.io/badge/pre--commit-darkolivegreen?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=gray)](https://github.com/TezRomacH/python-package-template/blob/master/.pre-commit-config.yaml) [![CI](https://img.shields.io/badge/GitHub_Actions-navy?style=for-the-badge&logo=githubactions&labelColor=gray&logoColor=white)](https://github.com/features/actions) [![Editor Settings](https://img.shields.io/badge/Editor_Config-paleturquoise?style=for-the-badge&logo=editorconfig&labelColor=gray)](https://editorconfig.org/) [![Repository Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/bobbie) [![Dependency Maintainer](https://img.shields.io/badge/dependabot-navy?style=for-the-badge&logo=dependabot&logoColor=white&labelColor=gray)](https://github.com/dependabot)
| Compatibility | [![Compatible Python Versions](https://img.shields.io/pypi/pyversions/bobbie?style=for-the-badge&color=steelblue&label=Python&logo=python&logoColor=yellow)](https://pypi.python.org/pypi/bobbie/) [![Linux](https://img.shields.io/badge/Linux-lightseagreen?style=for-the-badge&logo=linux&labelColor=gray&logoColor=white)](https://www.linux.org/) [![MacOS](https://img.shields.io/badge/MacOS-snow?style=for-the-badge&logo=apple&labelColor=gray)](https://www.apple.com/macos/) [![Windows](https://img.shields.io/badge/windows-blue?style=for-the-badge&logo=Windows&labelColor=gray&color=orangered)](https://www.microsoft.com/en-us/windows?r=1)
| Stats | [![PyPI Download Rate (per month)](https://img.shields.io/pypi/dm/bobbie?style=for-the-badge&color=steelblue&label=Downloads%20💾&logo=pypi&logoColor=yellow)](https://pypi.org/project/bobbie) [![GitHub Stars](https://img.shields.io/github/stars/WithPrecedent/bobbie?style=for-the-badge&color=navy&label=Stars%20⭐&logo=github)](https://github.com/WithPrecedent/bobbie/stargazers) [![GitHub Contributors](https://img.shields.io/github/contributors/WithPrecedent/bobbie?style=for-the-badge&color=navy&label=Contributors%20🙋&logo=github)](https://github.com/WithPrecedent/bobbie/graphs/contributors) [![GitHub Issues](https://img.shields.io/github/issues/WithPrecedent/bobbie?style=for-the-badge&color=navy&label=Issues%20📘&logo=github)](https://github.com/WithPrecedent/bobbie/graphs/contributors) [![GitHub Forks](https://img.shields.io/github/forks/WithPrecedent/bobbie?style=for-the-badge&color=navy&label=Forks%20🍴&logo=github)](https://github.com/WithPrecedent/bobbie/forks)
| | |

-----

## What is bobbie?

<p align="center">
<img src="https://media.giphy.com/media/53wQ8r97DCk2gAalDq/giphy.gif" alt="It's better to know what you want and who you are" style="width:400px;"/>
</p>

`bobbie` provides
a lightweight, easy-to-use, flexible, and extensible `Settings` class for loading and
storing configuration settings for a Python project.

## Why use bobbie?

There are [numerous options](#similar-projects) for storing project configuration settings in Python.
So, what makes `bobbie` different?

* **Flexible**: a `Settings` instance is easily built from a `dict`, Python module, or file.
* **Lightweight**: an efficient codebase ensures a very small memory footprint.
* **Intuitive**: a `create` class method constructs `Settings` (from any data source).
* **Convenient**: unlike `configparser`, automatic data and type validation is performed when
  `Settings` is created.

<p align="center">
<img src="https://media.giphy.com/media/ErQfoFJN1YNQroZUcL/giphy.gif" alt="This could be a really big deal" style="width:300px;"/>
</p>

The [comparison table](#feature-comparison-of-python-configuration-libraries)
below shows how `bobbie` compares to the other major options that store
configuration options for Python projects.

## Getting started

### Installation

To install `bobbie`, use `pip`:

```sh
pip install bobbie
```

### Create a Settings instance

`bobbie` supports several ways to create a `Settings` instance. However, you can
opt to always use the `create` class method for any data source.

#### From `dict`

```python
import bobbie

configuration = {
  'general': {
    'verbose': False,
    'seed': 43,
    'parallelize': False},
  'files': {
    'source_format': 'csv',
    'file_encoding': 'windows-1252',
    'float_format': '%.4f',
    'export_results': True}}
# You may use the general `create` method.
settings = bobbie.Settings.create(configuration)
# Or, just send a `dict` to `Settings` itself.
settings = bobbie.Settings(configuration)
```

#### From file

```python
import bobbie

# You may use the general `create` method.
settings = bobbie.Settings.create('settings_file.yaml')
# Or, the `from_file` method.
settings = bobbie.Settings.from_file('settings_file.yaml')
# Or, the `from_yaml` method. They all do the same thing.
settings = bobbie.Settings.from_yaml('settings_file.yaml')
```

If the file is a Python module, it must contain a variable named `settings`
(unless you change the global setting for the variable name).

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/bobbie/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/bobbie/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/bobbie/code_of_conduct.md).

## Similar projects

There are a lot of great packages for storing project settings. The table below
shows the features of the leading libraries.

### Feature Comparison of Python Configuration Libraries

<p align="center">
<img src="https://media.giphy.com/media/l0ExlIJRtK1yr345y/giphy.gif" alt="Bobbie Draper destroys a robotic arm in an arm-wrestling match" style="width:300px;"/>
</p>


| Library | Typing | Secrets | dict | env | ini | json | py | toml | yaml |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `bobbie`| ✅ | | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| [`configParser`](https://docs.python.org/3/library/configParser.html) | | | | | ✅ | | | | |
| [`dynaconf`](https://github.com/dynaconf/dynaconf) | ✅ | ✅ | | ✅ | ✅ | ✅ | | ✅ | ✅ |
| [`Parser-it`](https://github.com/naorlivne/Parser_it) | ✅ | | | ✅ | ✅ | ✅ | | ✅ | ✅ |
| [`python-decouple`](https://github.com/HBNetwork/python-decouple) | ✅ | ✅ | | ✅ | ✅ | | | | |
| [`pyconfig`](https://github.com/shakefu/pyconfig) | | ✅ | | | |  | | |  || |
| [`pydantic-settings`](https://docs.pydantic.dev/latest/usage/pydantic_settings/) | ✅ | ✅ | | | | | | | | |

As you can see, `bobbie` lacks a method for storing passwords, encryption keys,
and other secrets. That is largely because it is focused on internal Python
projects and the goal of keeping its resource usage as low as possible. So, if
you need secrets stored in your project settings, there are several good options
listed above that you should explore.

## Acknowledgments

I would like to thank the University of Kansas School of Law for tolerating and
supporting this law professor's coding efforts, an endeavor which is well
outside the typical scholarly activities in the discipline.

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/bobbie/blog/main/LICENSE).
