"""Base classes for loading and storing configuration options.

Contents:
    GenericDict: type alias for a mutable mapping with hashable keys.
    GenericList: type alias for a mutable sequence.
    Settings: loads and stores configuration settings with easy-to-use parser
        and viewers for accessing those settings.

"""

from __future__ import annotations

import contextlib
import copy
import dataclasses
import functools
import importlib
import importlib.util
import pathlib
from collections.abc import (
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
from typing import Any, Self, TypeAlias, cast

import bunches
import wonka

from . import options, utilities

GenericDict: TypeAlias = MutableMapping[Hashable, Any]
GenericList: TypeAlias = MutableSequence[Any]


@dataclasses.dataclass
class Settings(wonka.Sourcerer, bunches.Dictionary):
    """Loads and stores configuration settings.

    This class has an interface of an ordinary `dict`. It also adds
    class and instance methods that are helpful for project settings, including
    loading directly from numerous file types, easy injection
    of settings data as attributes into objects, and smart automatic type
    conversion from files when appropriate (depending on whether the file type
    supports typing).

    Currently, supported file extensions are:

    * `ini`, `json`, `py`, `toml`, `yaml`, and `yml`.

    The best way to create a `Settings` instance is to call `Settings.create`
    and pass as the first argument either:
        1) a `pathlib` or `str` path to a compatible file (including a Python
            module); or
        2) a `dict` or `dict`-like object.

    Any other arguments that you want passed to `Settings` (such as `name`)
    should be passed to the `parameters` argument. Any additional kwargs that
    you pass will be relayed to the constructor used by `bobbie`. For example,
    `bobbie` uses the builtin `tomllib` library to parse `toml` files. If you
    want to change the float parser to `decimal.Decimal` when loading settings
    from a ".toml" file and name your `Settings` instance "Project Settings",
    you should do this:

    ```py
    Settings.create(
        'configuration.toml',
        parameters = {'name': 'Project Settings'},
        parse_float = decimal.Decimal)
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

    """

    contents: GenericDict = dataclasses.field(default_factory = dict)
    # Repeats the field from `bunches.Dictionary` (in the same position) so
    # that the documentation includes it in the signature.
    default_factory: Any | None = None
    name: str | None = None

    """ Class Methods """

    @functools.singledispatchmethod
    @classmethod
    def create(
            cls,
            source: Any,
            /,
            parameters: MutableMapping[str, Any] | None = None,
            **kwargs: Any) -> Settings:
        """Calls appropriate class method to create an instance.

        Args:
            source: path to a file or `dict` with data to store in a `Settings`
                instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            **kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments).

        Returns:
            A `Settings` instance derived from `source`.

        Raises:
            TypeError: if `source` is not a `str`, `pathlib.Path`, or `dict`-
                like object.

        """
        message = (
            'The first positional argument must be a str, Path, or mapping')
        raise TypeError(message)

    @create.register(MutableMapping)
    @classmethod
    def from_dict(
            cls,
            source: GenericDict,
            /,
            parameters: MutableMapping[str, Any] | None = None,
            **kwargs: Any) -> Settings:
        """Creates a `Settings` instance from a `dict`-like object.

        Args:
            source: `dict`-like object with settings to store in a `Settings`
                instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            **kwargs: any additional keyword arguments are ignored by this
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
            source: str | pathlib.Path,
            /,
            parameters: MutableMapping[str, Any] | None = None,
            **kwargs: Any) -> Settings:
        """Creates a `Settings` instance from a file path.

        Args:
            source: path to file with data to store in a `Settings` instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            **kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as `encoding`).

        Returns:
            A `Settings` instance derived from `source`.

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.
            TypeError: if no constructor method is found for the passed file
                type or `parameters` has an argument that `Settings` does not
                accept.

        """
        path = utilities._pathlibify(source)
        loader = cls._get_loader(path)
        settings: Settings = loader(path, **kwargs)
        if parameters:
            # Rebuilds the instance so that `parameters` are passed to the
            # constructor, as they are by `from_dict`.
            settings = dataclasses.replace(settings, **parameters)
        return settings

    @classmethod
    def from_ini(cls, source: pathlib.Path | str, **kwargs: Any) -> Settings:
        """Creates a `Settings` instance from a file path to an `ini` file.

        Args:
            source: path to file with data to store in a `Settings` instance.
            **kwargs: additional parameters and arguments to pass to the
                `configparser.ConfigParser` constructor (such as
                `interpolation`), except for `encoding`, which is the file
                encoding (defaults to 'utf-8').

        Returns:
            A `Settings` instance derived from `source`.

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        """
        path = utilities._pathlibify(source)
        import configparser

        if not path.is_file():
            message = f'settings file {path} not found'
            raise FileNotFoundError(message)
        encoding = kwargs.pop('encoding', 'utf-8')
        # Interpolation is turned off by default so that values such as '%.4f'
        # are not treated as `configparser` interpolation syntax.
        kwargs.setdefault('interpolation', None)
        parser = configparser.ConfigParser(**kwargs)
        parser.optionxform = lambda option: option  # type: ignore
        parser.read(path, encoding = encoding)
        # Uses `dict` types so that the implicit "DEFAULT" section is not
        # included as a section of its own (its values are already part of
        # every other section).
        contents: GenericDict = {
            name: dict(parser[name]) for name in parser.sections()}
        if options._INFER_TYPES['ini']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_json(cls, source: pathlib.Path | str, **kwargs: Any) -> Settings:
        """Creates a `Settings` instance from a file path to a `json` file.

        Args:
            source: path to file with data to store in a `Settings` instance.
            **kwargs: additional parameters and arguments to pass to
                `json.load` (such as `parse_float`), except for `encoding`,
                which is the file encoding (defaults to 'utf-8').

        Returns:
            A `Settings` instance derived from `source`.

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        """
        path = utilities._pathlibify(source)
        import json

        encoding = kwargs.pop('encoding', 'utf-8')
        try:
            with open(path, encoding = encoding) as settings_file:
                contents = json.load(settings_file, **kwargs)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['json']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_module(
            cls,
            source: pathlib.Path | str,
            **kwargs: Any) -> Settings:
        """Creates a `Settings` instance from a file path to a Python module.

        The settings are read from the module-level variable named in
        `options._MODULE_SETTINGS_ATTRIBUTE` ('settings' by default).

        Args:
            source: path to file with data to store in a `Settings` instance.
            **kwargs: additional parameters and arguments to pass to
                `importlib.util.spec_from_file_location`.

        Returns:
            A `Settings` instance derived from `source`.

        Raises:
            AttributeError: if the module does not have a variable named in
                `options._MODULE_SETTINGS_ATTRIBUTE`.
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        """
        path = utilities._pathlibify(source)
        name = options._MODULE_SETTINGS_ATTRIBUTE
        try:
            specer = importlib.util.spec_from_file_location
            import_path = specer(path.name, path, **kwargs)
            import_module = importlib.util.module_from_spec(
                import_path)  # type: ignore
            import_path.loader.exec_module(import_module)  # type: ignore
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        try:
            contents = getattr(import_module, name)
        except AttributeError as error:
            message = f'settings file {path} has no variable named {name}'
            raise AttributeError(message) from error
        if options._INFER_TYPES['module']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_toml(cls, source: pathlib.Path | str, **kwargs: Any) -> Settings:
        """Creates a `Settings` instance from a file path to a `toml` file.

        Args:
            source: path to file with data to store in a `Settings` instance.
            **kwargs: additional parameters and arguments to pass to
                `tomllib.load` (such as `parse_float`).

        Returns:
            A `Settings` instance derived from `source`.

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        """
        path = utilities._pathlibify(source)
        import tomllib

        try:
            with open(path, 'rb') as settings_file:
                contents = cast(
                    'GenericDict', tomllib.load(settings_file, **kwargs))
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['toml']:
            contents = cls._infer_types(contents)
        return cls(contents)

    @classmethod
    def from_yaml(cls, source: pathlib.Path | str, **kwargs: Any) -> Settings:
        """Creates a `Settings` instance from a file path to a `yaml` file.

        Args:
            source: path to file with data to store in a `Settings` instance.
            **kwargs: `encoding` is the file encoding (defaults to 'utf-8').
                Any other keyword arguments are accepted for compatibility
                with the other loaders. They are not used because
                `yaml.safe_load` takes no other arguments.

        Returns:
            A `Settings` instance derived from `source`.

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        """
        path = utilities._pathlibify(source)
        import yaml

        encoding = kwargs.pop('encoding', 'utf-8')
        try:
            with open(path, encoding = encoding) as config:
                contents = yaml.safe_load(config)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error
        if options._INFER_TYPES['yaml']:
            contents = cls._infer_types(contents)
        return cls(contents)

    """ Public Methods """

    def add(  # type: ignore[override]
            self,
            key: Hashable,
            value: GenericDict) -> None:
        """Adds `key` and `value` to `contents`.

        If `key` is already a key in `contents`, the contents associated with
        that key are updated. If `key` doesn't exist, a new key/value pair is
        added to `contents`.

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
            return_error: bool | None = None) -> None:
        """Deletes `key` in `contents`.

        Args:
            key: key in `contents` to delete the key/value pair.
            return_error: returns error if `key` is missing. Defaults to None
                (which will result in the global setting stored in
                `options._ALWAYS_RETURN_ERROR` being used).

        Raises:
            KeyError: if `key` is not in `contents` and `return_error` is
                True.
            TypeError: if `key` isn't hashable.

        """
        if return_error is None:
            return_error = options._ALWAYS_RETURN_ERROR
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

        Returns:
            Value matching key in `contents` or a default value.

        Raises:
            KeyError: if `key` is not in `contents` and `default` and the
                `default_factory` attribute are both `None`.

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

        Each key/value pair in the chosen sections is added to `instance` as
        an attribute. Sections missing from `contents` are skipped.

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
        overwrite = (
            options._OVERWRITE_ATTRIBUTES if overwrite is None else overwrite)
        names = self.keys() if sections is None else sections
        for section in utilities._iterify(names):
            with contextlib.suppress(KeyError):
                for key, value in self.contents[section].items():
                    if (
                            not hasattr(instance, key)
                            or not getattr(instance, key)
                            or overwrite):
                        setattr(instance, key, value)
        return instance

    def items(self) -> ItemsView:  # type: ignore[override]
        """Emulates python dict `items` method.

        Returns:
            The `ItemsView` of `contents`.

        """
        return self.contents.items()

    def keys(self) -> KeysView:  # type: ignore[override]
        """Emulates python dict `keys` method.

        Returns:
            The `KeysView` of `contents`.

        """
        return self.contents.keys()

    def update(self, item: GenericDict) -> Self:  # type: ignore[override]
        """Updates `contents` using the `add` method for key/value pairs.

        Args:
            item: a `dict`-like object to add to `contents`.

        Returns:
            This instance with `item` added.

        """
        for key, value in item.items():
            self.add(key, value)
        return self

    def values(self) -> ValuesView:  # type: ignore[override]
        """Emulates python dict `values` method.

        Returns:
            The `ValuesView` of `contents`.

        """
        return self.contents.values()

    """ Private Methods """

    @classmethod
    def _get_loader(cls, path: pathlib.Path) -> MethodType:
        """Returns the loading method for `path`.

        Args:
            path: path to a settings file.

        Returns:
            The class method that loads the file type for the extension of
                `path`.

        Raises:
            FileNotFoundError: if `path` does not correspond to a file.
            TypeError: if the extension of `path` is not supported or there
                is no class method for its file type.

        """
        if path.is_file():
            extension = path.suffix[1:]
            try:
                file_type = options._FILE_EXTENSIONS[extension]
            except KeyError as error:
                message = f'Loading from {extension} file is not supported'
                raise TypeError(message) from error
            try:
                loader: MethodType = getattr(
                    cls, options._LOAD_METHOD(file_type))
            except AttributeError as error:
                message = f'Loading from {file_type} file is not supported'
                raise TypeError(message) from error
            return loader
        else:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message)

    @classmethod
    def _infer_types(cls, contents: GenericDict) -> GenericDict:
        """Converts stored values to appropriate datatypes.

        Args:
            contents: a `dict` to reparse.

        Returns:
            A `dict` with the nested values converted to the appropriate
                datatypes.

        """
        new_contents: GenericDict = {}
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

    def __add__(self, other: GenericDict) -> Self:
        """Returns a new instance that combines this instance and `other`.

        Neither this instance nor `other` is changed. Use "+=" to add `other`
        to this instance in place.

        Args:
            other: `dict`-like object to add to a copy of this instance using
                the `update` method.

        Returns:
            A new instance with the contents of this instance and `other`.

        """
        combined = copy.deepcopy(self)
        combined.update(other)
        return combined

    def __iadd__(self, other: GenericDict) -> Self:
        """Adds `other` to `contents` in place using the `update` method.

        Args:
            other: `dict`-like object to add to `contents`.

        Returns:
            This instance with `other` added.

        """
        self.update(other)
        return self

    def __delitem__(self, item: Hashable) -> None:
        """Deletes `item` from `contents`.

        Args:
            item: item or key to delete in `contents`.

        Raises:
            KeyError: if `item` is not in `contents` and
                `options._ALWAYS_RETURN_ERROR` is True.

        """
        self.delete(item)
        return

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value for `key` in `contents`.

        Args:
            key: key in `contents` for which a value is sought.

        Returns:
            Value stored in `contents`.

        Raises:
            KeyError: if `key` is not in `contents`.

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
            An iterator over the keys of `contents`.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of `contents`.

        Returns:
            The number of keys in `contents`.

        """
        return len(self.contents)
