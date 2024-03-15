"""Tools to load settings data into a `dict`.

Contents:


To Do:


"""
from __future__ import annotations

import configparser
import importlib
import importlib.util
import pathlib
import sys
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any

from . import configuration, utilities

if TYPE_CHECKING:
     from collections.abc import Hashable

     from . import base


def from_dict(
    source: MutableMapping[Hashable, Any],
    base: type[base.Settings],
    parameters: MutableMapping[Hashable, Any] | None = None,
    **kwargs:  Any) -> base.Settings:
    """Creates a `Settings` instance from a dict-like object.

    Args:
        source: dict with settings to store in a `Settings` instance.
        base: `Settings` or a subclass to store data from `source` in.
        parameters: additional parameters and arguments to pass to `base` when
            it is instanced. Defaults to None.
        kwargs: additional parameters and arguments to pass to the constructor
            used `bobbie` (such as encoding arguments). These are ignored by
            `from_dict` because there is no type conversion.

    Raises:
        TypeError: if `source` is not a `dict`-like object.

    Returns:
        A `Settings` or `Settings` subclass instance derived from `source`.

    """
    if isinstance(source, MutableMapping):
        return base(source, **parameters)
    else:
        message = {"source must be a dict-like type to use this constructor"}
        raise TypeError(message)

def from_path(
    source: pathlib.Path | str,
    base: type[base.Settings],
    parameters: MutableMapping[Hashable, Any] | None = None,
    **kwargs:  Any) -> base.Settings:
    """Creates a `Settings` instance from a file path.

    Args:
        source: path to file with data to store in a `Settings` instance.
        base: `Settings` or a subclass to store data from `source` in.
        parameters: additional parameters and arguments to pass to `base` when
            it is instanced. Defaults to None.
        kwargs: additional parameters and arguments to pass to the constructor
            used `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the path does not correspond to a file.

    Returns:
        A `Settings` or `Settings` subclass instance derived from `source`.

    """
    path = utilities._pathlibify(source)
    if path.isfile():
        extension = path.suffix[1:]
        loader = getattr(base, f'from_{extension}')
        return loader(path, parameters, **kwargs)
    else:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message)

def from_env(
    source: pathlib.Path | str,
    base: type[base.Settings],
    parameters: MutableMapping[Hashable, Any] | None = None,
    **kwargs:  Any) -> base.Settings:
    """Creates a `Settings` instance from a file path.

    Args:
        source: path to file with data to store in a `Settings` instance.
        base: `Settings` or a subclass to store data from `source` in.
        parameters: additional parameters and arguments to pass to `base` when
            it is instanced. Defaults to None.
        kwargs: additional parameters and arguments to pass to the constructor
            used `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the path does not correspond to a file.
        TypeError: if `source` is not a file path.

    Returns:
        A `Settings` or `Settings` subclass instance derived from `source`.

    """
    path = utilities._pathlibify(source)
    if path.isfile():
        import dotenv
        if ('infer_types' not in parameters
                and 'env' in configuration._TYPED_FORMATS
                and configuration._INFER_TYPES):
            parameters['infer_types'] = True
        return base(dotenv.dotenv_values(path, **kwargs), **parameters)
    else:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message)

def from_ini(
    source: pathlib.Path | str,
    base: type[base.Settings],
    parameters: MutableMapping[Hashable, Any] | None = None,
    **kwargs:  Any) -> base.Settings:
    """Creates a `Settings` instance from a file path.

    Args:
        source: path to file with data to store in a `Settings` instance.
        base: `Settings` or a subclass to store data from `source` in.
        parameters: additional parameters and arguments to pass to `base` when
            it is instanced. Defaults to None.
        kwargs: additional parameters and arguments to pass to the constructor
            used `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the path does not correspond to a file.
        TypeError: if `source` is not a file path.

    Returns:
        A `Settings` or `Settings` subclass instance derived from `source`.

    """
    path = utilities._pathlibify(source)
    if 'infer_types' not in kwargs:
        kwargs['infer_types'] = True
    try:
        contents = configparser.ConfigParser(dict_type = dict)
        contents.optionxform = lambda option: option
        contents.read(path)
        return base(dict(contents._sections), **parameters)
    except (KeyError, FileNotFoundError) as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error

def from_json(
    source: pathlib.Path | str,
    base: type[base.Settings],
    parameters: MutableMapping[Hashable, Any] | None = None,
    **kwargs:  Any) -> base.Settings:
    """Creates a `Settings` instance from a `json` file path.

    Args:
        source: path to file with data to store in a `Settings` instance.
        base: `Settings` or a subclass to store data from `source` in.
        parameters: additional parameters and arguments to pass to `base` when
            it is instanced. Defaults to None.
        kwargs: additional parameters and arguments to pass to the constructor
            used `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the path does not correspond to a file.
        TypeError: if `source` is not a file path.

    Returns:
        A `Settings` or `Settings` subclass instance derived from `source`.

    """
    import json
    path = utilities._pathlibify(source)
    if 'infer_types' not in kwargs:
        kwargs['infer_types'] = True
    try:
        with open(pathlib.Path(path)) as settings_file:
            contents = json.load(settings_file)
        return base(contents, **parameters)
    except FileNotFoundError as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error

def from_module(
    source: pathlib.Path | str,
    base: type[base.Settings],
    parameters: MutableMapping[Hashable, Any] | None = None,
    **kwargs:  Any) -> base.Settings:
    """Creates a `Settings` instance from a `py` module file path.

    Args:
        source: path to file with data to store in a `Settings` instance.
        base: `Settings` or a subclass to store data from `source` in.
        parameters: additional parameters and arguments to pass to `base` when
            it is instanced. Defaults to None.
        kwargs: additional parameters and arguments to pass to the constructor
            used `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the path does not correspond to a file.
        TypeError: if `source` is not a file path.

    Returns:
        A `Settings` or `Settings` subclass instance derived from `source`.

    """
    path = utilities._pathlibify(source) 
    kwargs['infer_types'] = False
    try:
        path = pathlib.Path(path)
        import_path = importlib.util.spec_from_file_location(
            path.name,
            path)
        import_module = importlib.util.module_from_spec(import_path)
        import_path.loader.exec_module(import_module)
        return base(import_module.settings, **parameters)
    except FileNotFoundError as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error

def from_toml(
    source: pathlib.Path | str,
    base: type[base.Settings],
    parameters: MutableMapping[Hashable, Any] | None = None,
    **kwargs:  Any) -> base.Settings:
    """Creates a `Settings` instance from a `toml` file path.

    Args:
        source: path to file with data to store in a `Settings` instance.
        base: `Settings` or a subclass to store data from `source` in.
        parameters: additional parameters and arguments to pass to `base` when
            it is instanced. Defaults to None.
        kwargs: additional parameters and arguments to pass to the constructor
            used `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the path does not correspond to a file.
        TypeError: if `source` is not a file path.

    Returns:
        A `Settings` or `Settings` subclass instance derived from `source`.

    """
    path = utilities._pathlibify(source)
    if sys.version_info[:3] >= (3,11):
        loader = _from_toml_builtin
    else:
        loader = _from_toml_external
    return loader(path, parameters = parameters)


def from_xml(
    source: pathlib.Path | str,
    base: type[base.Settings],
    parameters: MutableMapping[Hashable, Any] | None = None,
    **kwargs:  Any) -> base.Settings:
    """Creates a `Settings` instance from an `xml` file path.

    Args:
        source: path to file with data to store in a `Settings` instance.
        base: `Settings` or a subclass to store data from `source` in.
        parameters: additional parameters and arguments to pass to `base` when
            it is instanced. Defaults to None.
        kwargs: additional parameters and arguments to pass to the constructor
            used `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the path does not correspond to a file.
        TypeError: if `source` is not a file path.

    Returns:
        A `Settings` or `Settings` subclass instance derived from `source`.

    """
    import xmltodict
    path = utilities._pathlibify(source)
    try:
        xmltodict.parse
        with open(path) as config:
            return base(xmltodict.parse(config.read(), **parameters))
    except FileNotFoundError as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error

def from_yaml(
    source: pathlib.Path | str,
    base: type[base.Settings],
    parameters: MutableMapping[Hashable, Any] | None = None,
    **kwargs:  Any) -> base.Settings:
    """Creates a `Settings` instance from a `yaml` file path.

    Args:
        source: path to file with data to store in a `Settings` instance.
        base: `Settings` or a subclass to store data from `source` in.
        parameters: additional parameters and arguments to pass to `base` when
            it is instanced. Defaults to None.
        kwargs: additional parameters and arguments to pass to the constructor
            used `bobbie` (such as encoding arguments).

    Raises:
        FileNotFoundError: if the path does not correspond to a file.
        TypeError: if `source` is not a file path.

    Returns:
        A `Settings` or `Settings` subclass instance derived from `source`.

    """
    import yaml
    path = utilities._pathlibify(source) 
    kwargs['infer_types'] = False
    try:
        with open(path) as config:
            return base(yaml.safe_load(config, **parameters))
    except FileNotFoundError as error:
        message = f'settings file {path} not found'
        raise FileNotFoundError(message) from error
