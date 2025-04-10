"""Base classes for loading and storing configuration options.

Contents:
    Settings: loads and stores configuration settings with easy-to-use parser
        and viewers for accessing those settings.

To Do:
    Add Tests for all types and `dict` methods

"""
from __future__ import annotations

import contextlib
import copy
import dataclasses
import functools
import importlib
import pathlib
import sys
from collections.abc import (
    Collection,
    Hashable,
    ItemsView,
    Iterator,
    KeysView,
    MutableMapping,
    MutableSequence,
    Sequence,
    ValuesView,
)
from types import MethodType
from typing import Any, ClassVar, Self, TypeAlias

import bunches
import wonka

from . import options, utilities

if sys.version_info < (3, 12):
    GenericDict: TypeAlias = MutableMapping[Hashable, Any]
    GenericList: TypeAlias = MutableSequence[Any]
else:
    type GenericDict = MutableMapping[Hashable, Any]
    type GenericList = MutableSequence[Any]


@dataclasses.dataclass
class Settings(wonka.Sourcerer, bunches.Dictionary):
    """Loads and stores configuration settings.

    This class has an interface of an ordinary `dict`. It also adds
    class and instance methods that are helpful for project settings, including
    loading directly from numberous file types, easy injection
    of settings data as attributes into objects, and smart automatic type
    conversion from files when appropriate (depending on whether the file type
    supports typing).

    Currently, supported file extensions are:

    * `env`, `ini`, `json`, `py`, `toml`, `xml`, `yaml`, and `yml`.

    The best way to create a `Settings` instance is to call `Settings.create`
    and pass as the first argument a:
        1) `pathlib` or `str` path to a compatible file (including a Python
            module);
        2) a `dict` or `dict`-like object;
                                        or
        3) a sequence of `pathlib` paths, `str` paths, or mappings (mixed types
           in the sequence are supported).

    Any other arguments that you want passed to `Settings` (such as `name`)
    should be passed to the `parameters` argument. Any additional kwargs that
    you pass will be relayed to the constructor used by `bobbie`. For example,
    in Python 3.11, the builtin `tomllib` library to parse `toml` files. If you
    want to change the float parser to `decimal.Decimal` when loading settings
    from a ".toml" file and name your `Settings` instance "Project Settings",
    you should do this:

    ```py
    Settings.create(
        'configuration.toml',
        parameters = {'name': 'Project Settings'},
        {'parse_float': decimal.Decimal})
    ```

    You may also instance `Settings` directly, like a normal class. However,
    doing so precludes the ability to relay additional keyword arguments to the
    constructor used by `bobbie` (`parse_float` in the above example).

    Args:
        contents: configuration options. Defaults to an empty `dict`.
        default_factory: default value to return or default callable to use to
            create the default value.
        name: the `str` name of `Settings`. The top-level of a `Settings` need
            not have any name, but may include one for use by custom parsers.
            Defaults to `None`.

    Attributes:
        defaults: default options that should be used when a user does not
            provide the corresponding options in their configuration settings,
            but are otherwise necessary for the project. These are automatically
            added as the last mapping in `contents` so that all other loaded and
            stored options are checked first. Defaults to an empty `dict`.
        sources: `dict` with keys that are types and values are substrings of
            the names of methods to call when the key type is passed to the
            `create` method. Defaults to an empty `dict`.

    """

    contents: GenericDict = dataclasses.field(default_factory = dict)
    name: str | None = None
    sources: ClassVar[MutableMapping[type[Any], str]] = {
        pathlib.Path: 'file',
        str: 'file',
        MutableMapping: 'dict'}

    """ Class Methods """

    @functools.singledispatchmethod
    @classmethod
    def create(
        cls,
        source: Any, /,
        parameters: GenericDict | None = None,
        **kwargs:  Any) -> Settings:
        """Calls appropriate class method to create an instance.

        Args:
            source: path to a file or `dict` with data to store in a `Settings`
                instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments).

        Raises:
            TypeError: if `source` is not a `str`, `pathlib.Path`, or `dict`-
                like object.

        Returns:
            A `Settings` instance derived from `source`.

        """
        message = (
            'The first positional argument must be a str, Path, or mapping')
        raise TypeError(message)

    @create.register(MutableMapping)
    @classmethod
    def from_dict(
        cls,
        source: GenericDict, /,
        parameters: GenericDict | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a `dict`-like object.

        Args:
            source: `dict`-like object with settings to store in a `Settings`
                instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: any additional keyword arguments are ignored by this
                constructer method. They are only accepted to ensure
                compatibility with dispatching from the `create` method.

        Returns:
            A `Settings` instance derived from `source`.

        """
        parameters = parameters or {}
        return cls(source, **parameters)

    @create.register(str | pathlib.Path)
    @classmethod
    def from_file(
        cls,
        source: str | pathlib.Path, /,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a file path.

        Args:
            source: path to file with data to store in a `Settings` instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as file encoding arguments).

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.
            TypeError: if no constructor method is found for the passed file
                type.

        Returns:
            A `Settings` instance derived from `source`.

        """
        path = utilities._pathlibify(source)
        file_type, loader = cls._get_loader(path)
        try:
            return cls(loader(path, **kwargs))
        except AttributeError as error:
            message = f'Loading from {file_type} file is not supported'
            raise TypeError(message) from error

    @classmethod
    def from_env(cls,source: pathlib.Path | str, **kwargs:  Any) -> Settings:
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
            contents = dotenv.dotenv_values(source, **kwargs)
        except (KeyError, FileNotFoundError) as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['env']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_ini(cls, source: pathlib.Path | str, **kwargs:  Any) -> Settings:
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
        import configparser
        try:
            contents = configparser.ConfigParser(**kwargs)
            contents.optionxform = lambda option: option
            contents.read(path)
        except (KeyError, FileNotFoundError) as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['ini']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_json(cls, source: pathlib.Path | str, **kwargs:  Any) -> Settings:
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
                contents = json.load(settings_file, **kwargs)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['json']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_module(cls, source: pathlib.Path | str, **kwargs:  Any) -> Settings:
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
            specer = importlib.util.spec_from_file_location
            import_path = specer(path.name, path, **kwargs)
            import_module = importlib.util.module_from_spec(import_path)
            import_path.loader.exec_module(import_module)
            contents = getattr(import_module, options._MODULE_SETTINGS_ATTRIBUTE)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['module']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_toml(cls, source: pathlib.Path | str, **kwargs:  Any) -> Settings:
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
        import tomllib
        loader = tomllib.load
        try:
            contents = loader(path, **kwargs)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['toml']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_xml(cls, source: pathlib.Path | str, **kwargs:  Any) -> Settings:
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
                contents = xmltodict.parse(settings_file.read(), **kwargs)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['xml']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_yaml(cls, source: pathlib.Path | str, **kwargs:  Any) -> Settings:
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
        path = utilities._pathlibify(source)
        import yaml
        try:
            with open(path) as config:
                contents = yaml.safe_load(config, **kwargs)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['yaml']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def fromkeys(
        cls,
        keys: GenericList,
        value: Any,
        **kwargs: Any) -> GenericDict:
        """Emulates the `fromkeys` class method from a python `dict`.

        Args:
            keys: items to be keys in a new mapping.
            value: the value to use for all values in a new mapping.
            kwargs: additional arguments to pass to the `dict.fromkeys` method.

        Returns:
            An instance formed from `keys` and `value`.

        """
        return cls(dict.fromkeys(keys, value), **kwargs)

    """ Instance Methods """

    def add(self, key: Hashable, value: GenericDict) -> None:
        """Adds `key` and `value` to `contents`.

        If `key` is already a key in `contents`, the contents associated with
        that key are updated. If `key` doesn't exist, a new key/value pair is
        added to `contents`. Stored `dict`-like objects in `value` are
        automatically converted to `Settings` objects based on the global
        recursive configuration option.

        Args:
            key: name of key to store `value`.
            value: values to be stored.

        Raises:
            TypeError: if `key` isn't hashable.

        """
        try:
            self[key].update(value)
        except KeyError:
            try:
                self[key] = value
            except TypeError as error:
                message = 'The key must be hashable'
                raise TypeError(message) from error
        return

    def delete(
        self,
        key: Hashable,
        return_error: bool = options._ALWAYS_RETURN_ERROR) -> None:
        """Deletes `item` in `contents`.

        Args:
            key: key in `contents` to delete the key/value pair.
            return_error: returns error if `key` is missing. Defaults to the
                global setting stored in options._ALWAYS_RETURN_ERROR.

        """
        try:
            del self.contents[key]
        except KeyError as error:
            if return_error:
                message = f'{key} is not found in the settings'
                raise KeyError(message) from error
        except TypeError as error:
            message = 'The key must be hashable'
            raise TypeError(message) from error
        return

    def get(self, key: Hashable, default: Any | None = None) -> Any:
        """Returns value in `contents` or default options.

        Args:
            key: key for value in `contents`.
            default: default value to return if `key` is not found in
                `contents`.

        Raises:
            KeyError: if `key` is not in `contents` and `default` and the
                `default_factory` attribute are both `None`.

        Returns:
            Value matching key in `contents` or a default value.

        """
        try:
            return self[key]
        except (KeyError, TypeError) as error:
            if default is not None:
                return default
            if self.default_factory is None:
                raise KeyError(f'{key} is not in the Settings') from error
            try:
                return self.default_factory()
            except TypeError:
                return self.default_factory

    def inject(
        self,
        instance: object,
        sections: Sequence[str] | str | None = None,
        overwrite: bool | None = None) -> object:
        """Injects appropriate items into `instance` from `contents`.

        By default, if `instance` has a `name` attribute, this method will add
        any settings in a section matching that `name` to `instance` as
        attributes.

        Args:
            instance: class instance to be modified.
            sections: other section(s) in `contents` to add to `instance`.
                Defaults to None (which will result in all sections being
                injected).
            overwrite: whether to overwrite a local attribute in `instance` if
                there are existing values stored in that attribute. Defaults to
                None (which will result in the default value in
                `_OVERWRITE_ATTRIBUTES` will be used).

        Returns:
            Instance with modifications made.

        """
        overwrite = options._OVERWRITE_ATTRIBUTES if None else overwrite
        sections = self.keys() if None else sections
        for section in utilities._iterify(sections):
            with contextlib.suppress(KeyError):
                for key, value in self.contents[section].items():
                    if (not hasattr(instance, key)
                            or not getattr(instance, key)
                            or overwrite):
                        setattr(instance, key, value)
        return instance

    def items(self) -> ItemsView:
        """Emulates python dict `items` method.

        Returns:
            A `tuple` equivalent to `dict.items()`.

        """
        return self.contents.items()

    def keys(self) -> KeysView:
        """Returns `contents` keys as a `tuple`.

        Returns:
            A `tuple` equivalent to `dict.keys()`.

        """
        return self.keys()

    def setdefault(self, value: Any) -> None:
        """Sets default value to return when `get` method is used.

        Args:
            value: default value to return when `get` is called and the
                `default` parameter to `get` is None.

        """
        self.default_factory = value
        return

    def subset(
        self,
        include: Collection[Any] | Any | None = None,
        exclude: Collection[Any] | Any | None = None) -> GenericDict:
        """Returns a new instance with a subset of `contents`.

        This method applies `include` before `exclude` if both are passed. If
        `include` is None, all existing items will be added to the new subset
        class instance before `exclude` is applied.

        Args:
            include: item(s) to include in the new `Dictionary`. Defaults to
                `None`.
            exclude: item(s) to exclude from the new `Dictionary`. Defaults to
                `None`.

        Raises:
            ValueError: if `include` and `exclude` are both None.

        Returns:
            A new Settings (or subclass) instance with only keys from `include`
                and no keys in `exclude`.

        """
        if include is None and exclude is None:
            raise ValueError('include or exclude must not be None')
        if include is None:
            contents = copy.deepcopy(self.contents)
        else:
            include = list(utilities._iterify(include))
            contents = {k: self.contents[k] for k in include}
        if exclude is not None:
            exclude = list(utilities._iterify(exclude))
            contents = {k: v for k, v in contents.items() if k not in exclude}
        return self.__class__(contents)

    def update(self, item: GenericDict) -> Self:
        """Updates 'contents' using the 'add' method for key/value pairs.

        Args:
            item: a `dict`-like object to add to `contents`

        """
        for key, value in item.items():
            self.add(key, value)
        return self

    def values(self) -> ValuesView:
        """Returns `contents` values as a `tuple`.

        Returns:
            A `tuple` equivalent to `dict.values()`.

        """
        return self.contents.values()

    """ Private Methods """

    @classmethod
    def _get_loader(cls, path: pathlib.Path) -> tuple[str, MethodType]:
        """_get_loader _summary_

        Args:
            path: _description_

        Returns:
            _description_
        """
        if path.is_file():
            extension = path.suffix[1:]
            file_type = options._FILE_EXTENSIONS[extension]
            loader = getattr(cls, options._LOAD_METHOD(file_type))
            return file_type, loader
        else:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message)

    @classmethod
    def _infer_types(cls, contents: GenericDict) -> GenericDict:
        """Converts stored values to appropriate datatypes.

        Args:
            contents: a `dict` to reparse.

        Returns:
            GenericDict: with the nested values converted to
                the appropriate datatypes.

        """
        new_contents = {}
        for key, value in contents.items():
            if isinstance(value, MutableMapping):
                inner_bundle = {
                    inner_key: options._TYPER(inner_value)
                    for inner_key, inner_value in value.items()}
                new_contents[key] = inner_bundle
            else:
                new_contents[key] = options._TYPER(value)
        return new_contents

    """ Dunder Methods """

    def __add__(self, other: Any) -> Self:
        """Combines argument with `contents` using the `update` method.

        Args:
            other: item to add to `contents` using the `update` method.

        """
        self.update(other)
        return self

    def __delitem__(self, item: Hashable) -> Self:
        """Deletes `item` from `contents`.

        Args:
            item: item or key to delete in `contents`.

        Raises:
            KeyError: if `item` is not in `contents`.

        """
        self.delete(item)
        return self

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value for `key` in `contents`.

        Args:
            key: key in `contents` for which a value is sought.

        Returns:
            Value stored in `contents`.

        """
        return self.contents[key]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Sets `key` in `contents` to `value`.

        Args:
            key: key to set in `contents`.
            value: value to be paired with `key` in `contents`.

        """
        self.contents[key] = value
        return

    def __iter__(self) -> Iterator[Any]:
        """Returns iterator of `contents`.

        Returns:
            Iterator: of `contents`.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of `contents`.

        Returns:
            int: length of `contents`.

        """
        return len(self.contents)
