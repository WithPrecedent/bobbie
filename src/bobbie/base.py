"""Base classes for loading and storing configuration options.

Contents:
    Settings: loads and stores configuration settings with easy-to-use parser
        and viewers for accessing those settings.

To Do:


"""
from __future__ import annotations

import contextlib
import copy
import dataclasses
import functools
import itertools
import pathlib
from collections.abc import (
    Hashable,
    Iterator,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from typing import Any, ClassVar, Self, TypeAlias

import bunches
import wonka

from . import loaders, setup, utilities

GenericDict: TypeAlias = MutableMapping[Hashable, Any]
GenericList: TypeAlias = MutableSequence[Any]


@dataclasses.dataclass
class Settings(wonka.Sourcerer, bunches.Dictionary):
    """Stores configuration settings and supports loading them from files.

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

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        # # Converts all stored `dict`-like objects as `Settings` or
        # # `Settings` subclass instances.
        # if setup._RECURSIVE_SETTINGS:
        #     self.contents = self._recursify(self.contents)

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
        parameters: GenericDict | None = None,
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
        if path.is_file():
            parameters = parameters or {}
            extension = path.suffix[1:]
            file_type = setup._FILE_EXTENSIONS[extension]
            name = setup._LOAD_FUNCTION(file_type)
            creator = getattr(loaders, name)
            try:
                return cls(creator(path, **kwargs), **parameters)
            except AttributeError as error:
                message = f'Loading from {file_type} file is not supported'
                raise TypeError(message) from error
        else:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message)

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

    def add(
        self,
        key: Hashable,
        value: GenericDict) -> None:
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
            TypeError: if `key` isn't a `str`.

        """
        if (isinstance(value, MutableMapping) and setup._RECURSIVE_SETTINGS):
            value = self._recursify(value)
        try:
            self[key].update(value)
        except KeyError:
            try:
                self[key] = value
            except TypeError as error:
                message = 'The key must be hashable'
                raise TypeError(message) from error
        return

    def delete(self, item: Hashable) -> None:
        """Deletes `item` in `contents`.

        Because a chained mapping can have identical keys in different stored
        mappings, this method searches through all of the stored mappings
        and removes the key wherever it appears.

        Args:
            item: key in `contents` to delete the key/value pair.

        """
        for dictionary in self.contents:
            with contextlib.suppress(KeyError):
                del dictionary[item]
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
        overwrite = setup._OVERWRITE_ATTRIBUTES if None else overwrite
        sections = self.keys() if None else sections
        for section in utilities._iterify(sections):
            with contextlib.suppress(KeyError):
                for key, value in self.contents[section].items():
                    if (not hasattr(instance, key)
                            or not getattr(instance, key)
                            or overwrite):
                        setattr(instance, key, value)
        return instance

    def items(self) -> tuple[tuple[Hashable, Any], ...]:
        """Emulates python dict `items` method.

        Returns:
            A `tuple` equivalent to `dict.items()`.

        """
        return tuple(zip(self.keys(), self.values(), strict = True))

    def keys(self) -> tuple[Hashable, ...]:
        """Returns `contents` keys as a `tuple`.

        Returns:
            A `tuple` equivalent to `dict.keys()`.

        """
        return tuple(
            itertools.chain.from_iterable([d.keys() for d in self.contents]))

    def new_child(self, m: GenericDict) -> None:
        """Inserts `m` as the first mapping in `contents`.

        This method mirrors the functionality and parameters of
        `collections.Chainmap.new_child`.

        Args:
            m: A new mapping to add to `contents` at index 0.
        """
        self.contents.insert(0, m)
        return

    def parents(self) -> Settings:
        """Returns an instance with `contents` after the first.

        This method mirrors the functionality of `collections.Chainmap.parents`.

        Returns:
            An isntance with all stored Settings instances after the first.

        """
        return self.__class__(
            self.contents[1:],
            default_factory = self.default_factory)

    def setdefault(self, value: Any) -> None:
        """Sets default value to return when `get` method is used.

        Args:
            value: default value to return when `get` is called and the
                `default` parameter to `get` is None.

        """
        self.default_factory = value
        return

    def values(self) -> tuple[Any, ...]:
        """Returns `contents` values as a `tuple`.

        Returns:
            A `tuple` equivalent to `dict.values()`.

        """
        return tuple(
            itertools.chain.from_iterable([d.values() for d in self.contents]))

    """ Private Methods """

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
            if isinstance(value, dict):
                inner_bundle = {
                    inner_key: utilities._typify(inner_value)
                    for inner_key, inner_value in value.items()}
                new_contents[key] = inner_bundle
            else:
                new_contents[key] = utilities._typify(value)
        return new_contents

    def _integrate_defaults(self) -> None:
        """Adds `default` options when no similar stored settings exists."""
        new_contents = self.defaults
        new_contents.update(self.contents)
        self.contents = new_contents
        return self

    def _recursify(self, contents: GenericDict) -> GenericDict:
        """Converts any stored `dict` in `contents` to a `Settings`.

        Args:
            contents: `dict` of settings.

        Returns:
            A mapping with all internal `dict` like objects converted to
                `Settings` or `Settings` subclass objects.

        """
        new_contents = {}
        base = copy.deepcopy(self.__class__)
        base.defaults = {}
        for key, value in contents.items():
            if isinstance(key, Hashable) and isinstance(value, MutableMapping):
                section = base(value, name = key)
                new_contents[key] = section
            else:
                new_contents[key] = value
        return new_contents

    """ Dunder Methods """

    def __add__(self, other: Any) -> Self:
        """Combines argument with `contents` using the `add` method.

        Args:
            other: item to add to `contents` using the `add` method.

        """
        self.add(item = other)
        return self

    def __delitem__(self, item: Hashable) -> Self:
        """Deletes `item` from `contents`.

        Args:
            item: item or key to delete in `contents`.

        Raises:
            KeyError: if `item` is not in `contents`.

        """
        self.delete(item = item)
        return self

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value(s) for `key` in `contents`.

        If there are multiple matches for `key` and the `return_first` attribute
        is `False`, this method returns all matches in a `list`. Otherwise, only
        the first match is returned

        Args:
            key: key in `contents` for which a value is sought.

        Returns:
            Value(s) stored in `contents`.

        """
        matches = []
        for dictionary in self.contents:
            with contextlib.suppress(KeyError):
                matches.append(dictionary[key])
                if self.return_first:
                    return matches[0]
        if not matches:
            raise KeyError(f'{key} is not found in the ChainDict')
        return matches[0] if len(matches) > 1 else matches

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

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Sets `key` in `contents` to `value`.

        This method stores the passed `key` and `value` in the first stored
        mappings. If none exists, one is created to stored `key` and `value`.

        Args:
            key: key to set in `contents`.
            value: value to be paired with `key` in `contents`.

        """
        if len(self) == 0:
            self.contents = [{key: value}]
        else:
            self.contents[0].update({key: value})
        return


@dataclasses.dataclass
class Configuration(MutableMapping):
    """Stores configuration settings and supports loading them from files.

    This class has an interface of an ordinary `dict` with the same
    functionality of `collections.ChainMap` and `collections.defaultdict` in
    the builtin library. It also adds class and instance methods that are
    helpful for project settings, including default options, loading directly
    from numberous file types, easy injection of settings data as attributes
    into objects, and smart automatic type conversion from files when
    appropriate (depending on whether the file type supports typing).

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
        {parse_float: decimal.Decimal})
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

    """

    contents: GenericList[GenericDict] = dataclasses.field(
        default_factory = list)
    default_factory: GenericDict | None = Settings
    name: str | None = None
    defaults: ClassVar[GenericDict] = {}

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        # # Transforms `contents` into chained mappings.
        # self._construct_chained_mappings()
        # # Converts all stored `dict`-like objects as `Settings` or
        # # `Settings` subclass instances.
        # if setup._RECURSIVE_SETTINGS:
        #     self.contents = self._recursify(self.contents)

    """ Properties """

    @property
    def maps(self) -> GenericList[GenericDict]:
        """Returns `contents` attribute.

        Returns:
            Stored mappings in `contents`.

        """
        return self.contents

    @maps.setter
    def maps(self, value: GenericList[GenericDict]) -> None:
        """Sets `contents` to `value`.

        Args:
            value: new `list`-like instance to assign `contents` to.

        """
        self.contents = value
        return

    @maps.deleter
    def maps(self) -> None:
        """Sets `contents` to an empty list."""
        self.contents = []
        return

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
        return cls([source], **parameters)

    @create.register(str | pathlib.Path)
    @classmethod
    def from_file(
        cls,
        source: str | pathlib.Path, /,
        parameters: GenericDict | None = None,
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
        if path.is_file():
            parameters = parameters or {}
            extension = path.suffix[1:]
            file_type = setup._FILE_EXTENSIONS[extension]
            name = setup._LOAD_FUNCTION(file_type)
            creator = getattr(loaders, name)
            try:
                return cls(creator(path, **kwargs), **parameters)
            except AttributeError as error:
                message = f'Loading from {file_type} file is not supported'
                raise TypeError(message) from error
        else:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message)

    @create.register(Sequence)
    @classmethod
    def from_list(
        cls,
        source: GenericDict, /,
        parameters: GenericDict | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a `list`-like object.

        Args:
            source: `list`-like object with settings to store in a `Settings`
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
        return cls([dict.fromkeys(keys, value)], **kwargs)

    """ Instance Methods """

    def add(self, item: GenericDict, **kwargs: Any) -> None:
        """Adds `item` to the `contents` attribute.

        Args:
            item: new `Settings` to add to `contents` attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        """
        if isinstance(item, self.default_factory):
            self.contents.append(item, **kwargs)
        else:
            self.contents.append(self.default_factory(item), **kwargs)
        return

    def delete(self, item: str | int) -> None:
        """Deletes `item` in `contents`.

        Because a chained mapping can have identical keys in different stored
        mappings, this method searches through all of the stored mappings
        and removes the key wherever it appears.

        Args:
            item: index of item in `contents` to delete.

        """
        for dictionary in self.contents:
            with contextlib.suppress(KeyError):
                del dictionary[item]
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
        overwrite = setup._OVERWRITE_ATTRIBUTES if None else overwrite
        sections = self.keys() if None else sections
        for section in utilities._iterify(sections):
            with contextlib.suppress(KeyError):
                for key, value in self.contents[section].items():
                    if (not hasattr(instance, key)
                            or not getattr(instance, key)
                            or overwrite):
                        setattr(instance, key, value)
        return instance

    def items(self) -> tuple[tuple[Hashable, Any], ...]:
        """Emulates python dict `items` method.

        Returns:
            A `tuple` equivalent to `dict.items()`.

        """
        return tuple(zip(self.keys(), self.values(), strict = True))

    def keys(self) -> tuple[Hashable, ...]:
        """Returns `contents` keys as a `tuple`.

        Returns:
            A `tuple` equivalent to `dict.keys()`.

        """
        return tuple(
            itertools.chain.from_iterable([d.keys() for d in self.contents]))

    def new_child(self, m: GenericDict) -> None:
        """Inserts `m` as the first mapping in `contents`.

        This method mirrors the functionality and parameters of
        `collections.Chainmap.new_child`.

        Args:
            m: A new mapping to add to `contents` at index 0.
        """
        self.contents.insert(0, m)
        return

    def parents(self) -> Settings:
        """Returns an instance with `contents` after the first.

        This method mirrors the functionality of `collections.Chainmap.parents`.

        Returns:
            An isntance with all stored Settings instances after the first.

        """
        return self.__class__(
            self.contents[1:],
            default_factory = self.default_factory)

    def setdefault(self, value: Any) -> None:
        """Sets default value to return when `get` method is used.

        Args:
            value: default value to return when `get` is called and the
                `default` parameter to `get` is None.

        """
        self.default_factory = value
        return

    def values(self) -> tuple[Any, ...]:
        """Returns `contents` values as a `tuple`.

        Returns:
            A `tuple` equivalent to `dict.values()`.

        """
        return tuple(
            itertools.chain.from_iterable([d.values() for d in self.contents]))

    """ Private Methods """

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
            if isinstance(value, dict):
                inner_bundle = {
                    inner_key: utilities._typify(inner_value)
                    for inner_key, inner_value in value.items()}
                new_contents[key] = inner_bundle
            else:
                new_contents[key] = utilities._typify(value)
        return new_contents

    def _integrate_defaults(self) -> None:
        """Adds `default` options when no similar stored settings exists."""
        new_contents = self.defaults
        new_contents.update(self.contents)
        self.contents = new_contents
        return self

    def _recursify(self, contents: GenericDict) -> GenericDict:
        """Converts any stored `dict` in `contents` to a `Settings`.

        Args:
            contents: `dict` of settings.

        Returns:
            A mapping with all internal `dict` like objects converted to
                `Settings` or `Settings` subclass objects.

        """
        new_contents = {}
        base = copy.deepcopy(self.__class__)
        base.defaults = {}
        for key, value in contents.items():
            if isinstance(key, Hashable) and isinstance(value, MutableMapping):
                section = base(value, name = key)
                new_contents[key] = section
            else:
                new_contents[key] = value
        return new_contents

    """ Dunder Methods """

    def __add__(self, other: Any) -> Self:
        """Combines argument with `contents` using the `add` method.

        Args:
            other: item to add to `contents` using the `add` method.

        """
        self.add(item = other)
        return self

    def __delitem__(self, item: Hashable) -> Self:
        """Deletes `item` from `contents`.

        Args:
            item: item or key to delete in `contents`.

        Raises:
            KeyError: if `item` is not in `contents`.

        """
        self.delete(item = item)
        return self

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value(s) for `key` in `contents`.

        If there are multiple matches for `key` and the `return_first` attribute
        is `False`, this method returns all matches in a `list`. Otherwise, only
        the first match is returned

        Args:
            key: key in `contents` for which a value is sought.

        Returns:
            Value(s) stored in `contents`.

        """
        matches = []
        for dictionary in self.contents:
            with contextlib.suppress(KeyError):
                matches.append(dictionary[key])
                if self.return_first:
                    return matches[0]
        if not matches:
            raise KeyError(f'{key} is not found in the ChainDict')
        return matches[0] if len(matches) > 1 else matches

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

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Sets `key` in `contents` to `value`.

        This method stores the passed `key` and `value` in the first stored
        mappings. If none exists, one is created to stored `key` and `value`.

        Args:
            key: key to set in `contents`.
            value: value to be paired with `key` in `contents`.

        """
        if len(self) == 0:
            self.contents = [GenericDict({key: value})]
        else:
            self.contents[0].update({key: value})
        return