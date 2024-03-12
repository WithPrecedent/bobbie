"""Base class for loading and storing configuration options.

Contents:
    Settings: loads and stores configuration settings with easy-to-use parser
        and viewers for accessing those settings.

To Do:


"""
from __future__ import annotations

import configparser
import contextlib
import copy
import dataclasses
import importlib
import importlib.util
import pathlib
import sys
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
from typing import Any, ClassVar

from . import configuration, extensions, utilities


@dataclasses.dataclass
class Settings(MutableMapping):
    """Loads and stores configuration settings.

    The best way to create a `Settings` instance is to call `Settings.create`
    and pass as the first argument a:
        1) `pathlib` or `str` path to a compatible file (including a Python
            module);
                                or
        2) a `dict` or `dict`-like object.
    Any other arguments that you want passed to `Settings` (such as `defaults`)
    you should pass to the `parameters` argument. Any additional kwargs that you
    pass will be relayed to the constructor used by `bobbie`. For example, if
    you are using Python 3.11, `bobbie` uses the builtin `tomllib` library to
    parse `toml` files. If you want to change the float parser to
    `decimal.Decimal` and make all internal sections in the instance to also be
    `Settings` type, you would do this:

    ```py
    Settings.create(
        'configuration.toml',
        parameters = {'parse_float': decimal.Decimal},
        recursive = True)
    ```

    You may also instance `Settings` directly, like a normal class. However,
    doing so precludes the abilitiy to:
        1) relay additional kwargs o the constructor used by `bobbie`
            (`parse_float` in the above example).
        2) add `Parser` descriptors to `Settings` (although you may do so
           manually by using the `add_parsers` class method)

    Currently, supported file extensions are:

    * `env`, `ini`, `json`, `py`, `toml`, `xml`, `yaml`, and `yml`.

    Args:
        contents: configuration options. Defaults to whatever option is stored
            in `configuration._INTERNAL_STORAGE` (en empty `dict` by default).
        recursive: whether to transform any stored `dict`-like values in
            `contents` into the present class type (`True`) or leave them in
            whatever form they start with (`False`). If the `recursive` argument
            is `True` is valuable if you want to take advantage of `Settings` in
            subparts of the overall `Settings` object.
        name: the `str` name of `Settings`. This is used when `recursive` is
            `True` and nested instances want to keep track of their section name
            when using various parsers and views. The top-level of `Settings`
            need not have any name, but may include one for use by custom
            parsers. Defaults to `None`.

    Attributes:
        defaults: default options that should be used when a user does not
            provide the corresponding options in their configuration settings,
            but are otherwise necessary for the project. Defaults to whatever
            option is stored in `configuration._INTERNAL_STORAGE` (en empty
            `dict` by default).

    """

    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = configuration._INTERNAL_STORAGE)
    recursive: bool = configuration._RECURSIVE_SETTINGS
    name: str | None = None
    defaults: ClassVar[Mapping[Hashable, Any]] = (
        configuration._INTERNAL_STORAGE())

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        # Adds non-duplicative default settings to `contents`.
        self.contents = self._integrate_defaults(contents = self.contents)
        # Adds descriptors from `parsers`.
        self._add_views()

    """ Class Methods """

    @classmethod
    def create(
        cls,
        source: Any,
        parameters: MutableMapping[Hashable, Any] | None = None,
        parsers: Sequence[str] | None = None,
        **kwargs:  Any) -> Settings:
        """Calls appropriate class method to create an instance.

        Args:
            source: path to a file or `dict` with data to store in a `Settings`
                instance.
            parameters: additional parameters and arguments to pass to the
                constructor function used by `bobbie`. The specific function
                used for each file type is stored in the `configuration` model.
            parsers: `str` names of parsers stored in the `bobbie.Parsers`
                registry. The corresponding Parser instances will be added to
                the newly created `Settings` instance as custom descriptors
                (properties). This allows for different views of the stored
                configuration options without altering the stored data.
            kwargs: additional parameters and arguments to pass to the
                created `Settings` instance.

        Raises:
            TypeError: if `source` is not a `str`, `pathlib.Path`, or `dict`-
                like object.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        parameters = parameters or {}
        if isinstance(source, (str, pathlib.Path)):
            creator = cls.from_path
        elif isinstance(source, MutableMapping):
            creator = cls.from_dict
        else:
            message = 'source must be a str, Path, or dict-like object'
            raise TypeError(message)
        return creator(source, parameters, parsers, **kwargs)

    @classmethod
    def from_dict(
        cls,
        source: MutableMapping[Hashable, Any],
        parameters: MutableMapping[Hashable, Any] | None = None,
        parsers: MutableMapping[Hashable, extensions.Parser] | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a `dict`-like object.

        Args:
            source: `dict`-like object with settings to store in a `Settings`
                instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments). These
                are ignored by `from_dict` because the `source` `dict` has
                already been instanced.

        Raises:
            TypeError: if `source` is not a `dict`-like object.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        source = _validate_source(source, MutableMapping)
        return cls(source, **parameters)

    @classmethod
    def from_path(
        cls,
        source: pathlib.Path | str,
        parameters: MutableMapping[Hashable, Any] | None = None,
        parsers: MutableMapping[Hashable, extensions.Parser] | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a file path.

        Args:
            source: path to file with data to store in a `Settings` instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments).

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.
            TypeError: if no constructor method exists for the file type.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        parameters = parameters or {}
        source = _validate_source(source, (str, pathlib.Path))
        path = utilities._pathlibify(source)
        if path.isfile():
            extension = path.suffix[1:]
            creator = getattr(cls, f'from_{extension}')
            try:
                return creator(path, parameters, **kwargs)
            except AttributeError as error:
                message = f'there is no constructor for a {extension} file'
                raise TypeError(message) from error
        else:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message)

    @classmethod
    def from_ini(
        cls,
        source: pathlib.Path | str,
        parameters: MutableMapping[Hashable, Any] | None = None,
        parsers: MutableMapping[Hashable, extensions.Parser] | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a file path to an `ini` file.

        Args:
            source: path to file with data to store in a `Settings` instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments).

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        parameters = parameters or {}
        source = _validate_source(source, (str, pathlib.Path))
        path = utilities._pathlibify(source)
        if ('infer_types' not in parameters
                and 'ini' in configuration._TYPED_FORMATS
                and configuration._INFER_TYPES):
            parameters['infer_types'] = True
        try:
            contents = configparser.ConfigParser(dict_type = dict)
            contents.optionxform = lambda option: option
            contents.read(path)
            return cls(contents = dict(contents._sections), **kwargs)
        except (KeyError, FileNotFoundError) as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error

    @classmethod
    def from_json(
        cls,
        source: pathlib.Path | str,
        parameters: MutableMapping[Hashable, Any] | None = None,
        parsers: MutableMapping[Hashable, extensions.Parser] | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a file path to a `json` file.

        Args:
            source: path to file with data to store in a `Settings` instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments).

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        import json
        parameters = parameters or {}
        source = _validate_source(source, (str, pathlib.Path))
        path = utilities._pathlibify(source)
        if ('infer_types' not in parameters and configuration._INFER_TYPES):
            parameters['infer_types'] = True
        try:
            with open(pathlib.Path(path)) as settings_file:
                contents = json.load(settings_file)
            return cls(contents = contents, **parameters)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error

    @classmethod
    def from_module(
        cls,
        source: pathlib.Path | str,
        parameters: MutableMapping[Hashable, Any] | None = None,
        parsers: MutableMapping[Hashable, extensions.Parser] | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a file path to a Python module.

        Args:
            source: path to file with data to store in a `Settings` instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments).

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        parameters = parameters or {}
        source = _validate_source(source, (str, pathlib.Path))
        path = utilities._pathlibify(source)
        if 'infer_types' not in parameters:
            parameters['infer_types'] = False
        try:
            path = pathlib.Path(path)
            specer = importlib.util.spec_from_file_location
            import_path = specer(path.name, path)
            import_module = importlib.util.module_from_spec(import_path)
            import_path.loader.exec_module(import_module)
            return cls(contents = import_module.settings, **kwargs)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error

    @classmethod
    def from_toml(
        cls,
        source: pathlib.Path | str,
        parameters: MutableMapping[Hashable, Any] | None = None,
        parsers: MutableMapping[Hashable, extensions.Parser] | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a file path to a `toml` file.

        Args:
            source: path to file with data to store in a `Settings` instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments).

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        parameters = parameters or {}
        source = _validate_source(source, (str, pathlib.Path))
        path = utilities._pathlibify(source)
        if sys.version_info[:3] >= (3,11):
            import tomllib
            loader = tomllib.load
        else:
            import toml
            loader = toml.load
        contents = loader(path, **kwargs)
        return cls(contents, **parameters)

    @classmethod
    def from_yaml(
        cls,
        source: pathlib.Path | str,
        parameters: MutableMapping[Hashable, Any] | None = None,
        parsers: MutableMapping[Hashable, extensions.Parser] | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a file path to a `yaml` file.

        Args:
            source: path to file with data to store in a `Settings` instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments).

        Raises:
            FileNotFoundError: if the `source` path does not correspond to a
                file.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        import yaml
        parameters = parameters or {}
        source = _validate_source(source, (str, pathlib.Path))
        path = utilities._pathlibify(source)
        kwargs['infer_types'] = False
        try:
            with open(path) as config:
                return cls(contents = yaml.safe_load(config, **kwargs))
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error

    @classmethod
    def fromkeys(
        cls,
        keys: Sequence[Hashable],
        value: Any) -> Settings:
        """Emulates the `fromkeys` class method from a python `dict`.

        Args:
            keys: items to be keys in a new Settings.
            value: the value to use for all values in a new Settings.

        Returns:
            Settings: formed from `keys` and `value`.

        """
        return cls(contents = dict.fromkeys(keys, value))

    """ Instance Methods """

    def add(
        self,
        section: Hashable,
        contents: MutableMapping[Hashable, Any]) -> None:
        """Adds `section` to `contents`.

        If `section` is already a key in `contents`, the contents associated
        with that key are updated. If `section` doesn't exist, a new key/value
        pair is added to `contents`.

        Args:
            section (Hashable): name of section to add `contents` to.
            contents (MutableMapping[Hashable, Any]): a dict to store in
            `section`.

        """
        try:
            self[section].update(contents)
        except KeyError:
            self[section] = contents
        return

    def add_parsers(self, parsers: Sequence[str]) -> None:
        """Adds values from the `Parsers` registry as class attributes.

        This method is automatically called by `create` and other constructor
        class methods. It is included as a public method in case you want to add
        additional parsers if you created a `Settings` instance directly, but
        still want to use custom parsers.

        Args:
            parsers: `str` names of parsers stored in the `Parsers` registry.

        """
        if parsers:
            for name in parsers:
                parser = extensions.Parsers[name]
                setattr(self.__class__, name, parser())
        return self

    def delete(self, item: Hashable) -> None:
        """Deletes `item` in `contents`.

        Args:
            item (Hashable): key in `contents` to delete the key/value pair.

        """
        del self.contents[item]
        return

    def inject(
        self,
        instance: object,
        include_global: bool = True,
        additional: Sequence[str] | str | None = None,
        overwrite: bool = False) -> object:
        """Injects appropriate items into `instance` from `contents`.

        By default, if `instance` has a `name` attribute, this method will add
        any settings in a section matching that `name` to `instance` as
        attributes.

        Args:
            instance (object): class instance to be modified.
            additional (Optional[Sequence[str] | str]): other section(s) in
                `contents` to inject into `instance`. Defaults to None.
            overwrite (bool]): whether to overwrite a local attribute in
                `instance` if there are existing values stored in that
                attribute. Defaults to False.

        Returns:
            instance (object): instance with modifications made.

        """
        sections = []
        with contextlib.suppress(AttributeError):
            sections.append(instance.name)
        if additional:
            sections.extend(utilities._iterify(additional))
        for section in sections:
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
            tuple[tuple[Hashable], Any]: a tuple equivalent to dict.items().

        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> tuple[Hashable, ...]:
        """Returns `contents` keys as a tuple.

        Returns:
            tuple[Hashable, ...]: a tuple equivalent to dict.keys().

        """
        return tuple(self.contents.keys())

    def subset(
        self,
        include: Hashable | Sequence[Hashable] | None = None,
        exclude: Hashable | Sequence[Hashable] | None = None) -> Settings:
        """Returns a new instance with a subset of `contents`.

        This method applies `include` before `exclude` if both are passed. If
        `include` is None, all existing items will be added to the new subset
        class instance before `exclude` is applied.

        Args:
            include (Optional[Hashable | Sequence[Hashable]]): key(s) to
                include in the new Settings instance.
            exclude (Optional[Hashable | Sequence[Hashable]]): key(s) to
                exclude from the new Settings instance.

        Raises:
            ValueError: if `include` and `exclude` are both None.

        Returns:
            Settings: with only keys from `include` and no keys in `exclude`.

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
            contents = {
                k: v for k, v in contents.items()
                if k not in exclude}
        new_dictionary = copy.deepcopy(self)
        new_dictionary.contents = contents
        return new_dictionary

    def values(self) -> tuple[Any, ...]:
        """Returns `contents` values as a tuple.

        Returns:
            tuple[Any, ...]: a tuple equivalent to dict.values().

        """
        return tuple(self.contents.values())

    """ Private Methods """

    def _integrate_defaults(
        self,
        contents: MutableMapping[Hashable, Any]) -> (
            MutableMapping[Hashable, Any]):
        """Creates a backup set of mappings for bobbie settings lookup.

        Args:
            contents (MutableMapping[Hashable, Any]): a nested contents dict to
                add default to.

        Returns:
            MutableMapping[Hashable, Any]: with stored default added.

        """
        new_contents = self.defaults
        new_contents.update(contents)
        return new_contents

    def _infer_types(
        self,
        contents: MutableMapping[Hashable, Any]) -> (
            MutableMapping[Hashable, Any]):
        """Converts stored values to appropriate datatypes.

        Args:
            contents (MutableMapping[Hashable, Any]): a nested contents dict to
                reparse.

        Returns:
            MutableMapping[Hashable, Any]: with the nested values converted to
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

    """ Dunder Methods """

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value for `key` in `contents`.

        Args:
            key (Hashable): key in `contents` for which a value is sought.

        Returns:
            Any: value stored in `contents`.

        """
        return self.contents[key]

    def __setitem__(self, key: str, value: Mapping[str, Any]) -> None:
        """Creates new key/value pair(s) in a section of the active dictionary.

        Args:
            key: name of a section in the active dictionary.
            value: the dictionary to be placed in that section.

        Raises:
            TypeError if `key` isn't a str or `value` isn't a dict.

        """
        try:
            self.contents[key].update(value)
        except KeyError:
            try:
                self.contents[key] = value
            except TypeError as error:
                message = 'key must be a str and value must be a dict type'
                raise TypeError(message) from error
        return


""" Public Functions """

# def create_settings(
#     base: Settings,
#     parsers: str | Sequence[str],
#     views: str | Sequence[str]):

""" Private Functions """

# def _load_from_file(
#     loader: Callable,
#     file_path: pathlib.Path) -> MutableMapping[Hashable, Any]:

def _validate_source(
    source: Any,
    kind: type[Any] | tuple[type[Any], ...]) -> Any:
    """Validates that `source` is an instance of `kind`.

    Args:
        source: item to test.
        kind: type(s) to see if `source` is an instance of.

    Raise:
        TypeError: if `source` is not an instance of `kind`.

    Returns:
        Unaltered `source`, if it is an instance of `kind`.

    """
    if isinstance(source, kind):
        return source
    message = f'source argument must be {kind}'
    raise TypeError(message)
