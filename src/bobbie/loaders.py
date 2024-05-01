"""Tools to load settings data into a `dict`.

Contents:


To Do:


"""
from __future__ import annotations

# Some modules are loaded lazily within functions to conserve memory. Only
# loaders that are used will have the utilized external module imported.
import configparser
import importlib
import importlib.util
import pathlib
import sys
from typing import TYPE_CHECKING, Any

from . import setup, utilities

if TYPE_CHECKING:
     from collections.abc import Hashable, MutableMapping


def load(
    source: pathlib.Path | str, /,
    **kwargs:  Any) -> MutableMapping[Hashable, Any]:
    """Creates a settings `dict` from a file path to an `ini` file.

    Args:
        source: path to file with data to store in a settings `dict`.
        kwargs: additional parameters and arguments to pass to the
            constructor used by `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the `source` path does not correspond to a file.
        TypeError: if no loading function exists for the file type passed.

    Returns:
        A `dict` of settings from `source`.

    """
    path = utilities._pathlibify(source)
    if path.is_file():
        extension = path.suffix[1:]
        suffix = setup._FILE_EXTENSIONS[extension]
        loader = setup._CREATOR_METHOD(suffix)
        try:
            tool = globals()[loader]
        except KeyError as error:
            message = (
                f'Loading settings from {extension} files is not supported')
            raise TypeError(message) from error
        return tool(source, **kwargs)
    else:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message)

def env_to_dict(
    source: pathlib.Path | str, /,
    **kwargs:  Any) -> MutableMapping[Hashable, Any]:
    """Creates a settings `dict` from a file path to an `ini` file.

    Args:
        source: path to file with data to store in a settings `dict`.
        kwargs: additional parameters and arguments to pass to the
            constructor used by `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the `source` path does not correspond to a file.

    Returns:
        A `dict` of settings from `source`.

    """
    path = utilities._pathlibify(source)
    import dotenv
    try:
        return dotenv.dotenv_values(source, **kwargs)
    except (KeyError, FileNotFoundError) as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error

def ini_to_dict(
    source: pathlib.Path | str, /,
    **kwargs:  Any) -> MutableMapping[Hashable, Any]:
    """Creates a settings `dict` from a file path to an `ini` file.

    Args:
        source: path to file with data to store in a settings `dict`.
        kwargs: additional parameters and arguments to pass to the
            constructor used by `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the `source` path does not correspond to a
            file.

    Returns:
        A `dict` of settings from `source`.

    """
    path = utilities._pathlibify(source)
    try:
        contents = configparser.ConfigParser(dict_type = dict, **kwargs)
        contents.optionxform = lambda option: option
        contents.read(path)
    except (KeyError, FileNotFoundError) as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error
    return contents

def json_to_dict(
    source: pathlib.Path | str, /,
    **kwargs:  Any) -> MutableMapping[Hashable, Any]:
    """Creates a settings `dict` from a file path to a `json` file.

    Args:
        source: path to file with data to store in a settings `dict`.
        kwargs: additional parameters and arguments to pass to the
            constructor used by `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the `source` path does not correspond to a file.

    Returns:
        A `dict` of settings from `source`.

    """
    path = utilities._pathlibify(source)
    import json
    try:
        with open(pathlib.Path(path)) as settings_file:
            return json.load(settings_file, **kwargs)
    except FileNotFoundError as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error

def module_to_dict(
    source: pathlib.Path | str, /,
    **kwargs:  Any) -> MutableMapping[Hashable, Any]:
    """Creates a settings `dict` from a file path to a Python module.

    Args:
        source: path to file with data to store in a settings `dict`.
        kwargs: additional parameters and arguments to pass to the
            constructor used by `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the `source` path does not correspond to a
            file.

    Returns:
        A `dict` of settings from `source`.

    """
    path = utilities._pathlibify(source)
    try:
        path = pathlib.Path(path)
        specer = importlib.util.spec_file_location
        import_path = specer(path.name, path, **kwargs)
        import_module = importlib.util.module_spec(import_path)
        import_path.loader.exec_module(import_module)
        return getattr(import_module, setup._MODULE_SETTINGS_ATTRIBUTE)
    except FileNotFoundError as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error

def toml_to_dict(
    source: pathlib.Path | str, /,
    **kwargs:  Any) -> MutableMapping[Hashable, Any]:
    """Creates a settings `dict` from a file path to a `toml` file.

    Args:
        source: path to file with data to store in a settings `dict`.
        kwargs: additional parameters and arguments to pass to the
            constructor used by `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the `source` path does not correspond to a
            file.

    Returns:
        A `dict` of settings from `source`.

    """
    path = utilities._pathlibify(source)
    if sys.version_info[:3] >= (3,11):
        import tomllib
        loader = tomllib.load
    else:
        import toml
        loader = toml.load
    try:
        return loader(path, **kwargs)
    except FileNotFoundError as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error

def xml_to_dict(
    source: pathlib.Path | str, /,
    **kwargs:  Any) -> MutableMapping[Hashable, Any]:
    """Creates a settings `dict` from a file path to a `toml` file.

    Args:
        source: path to file with data to store in a settings `dict`.
        kwargs: additional parameters and arguments to pass to the
            constructor used by `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the `source` path does not correspond to a
            file.

    Returns:
        A `dict` of settings from `source`.

    """
    path = utilities._pathlibify(source)
    import xmltodict
    try:
        with open(path) as settings_file:
            return xmltodict.parse(settings_file.read(), **kwargs)
    except FileNotFoundError as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error

def yaml_to_dict(
    source: pathlib.Path | str, /,
    **kwargs:  Any) -> MutableMapping[Hashable, Any]:
    """Creates a settings `dict` from a file path to a `yaml` file.

    Args:
        source: path to file with data to store in a settings `dict`.
        kwargs: additional parameters and arguments to pass to the
            constructor used by `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the `source` path does not correspond to a
            file.

    Returns:
        A `dict` of settings from `source`.

    """
    import yaml
    path = utilities._pathlibify(source)
    try:
        with open(path) as config:
            return yaml.safe_load(config, **kwargs)
    except FileNotFoundError as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error
