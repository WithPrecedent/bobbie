"""Base class for loading and storing configuration options.

Contents:
    Settings (MutableMapping): stores configuration settings after either
        loading them from disk or by the passed arguments.

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
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING, Any

from . import configuration, utilities

if TYPE_CHECKING:
     from . import extensions


@dataclasses.dataclass
class Settings(MutableMapping):
    """Loads and stores configuration settings.

    To create settings instance, a user can pass as the `contents` parameter a:
        1) `pathlib` file path of a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) a `dict` (or `dict`-like object).

    Currently, supported file types are:

    * `ini`, `json`, `py`, `toml`, and `yaml`.

    If `infer_types` is set to True (the default option), `contents` values are
    converted to appropriate datatypes (`str`, `list`, `float`, `bool`, and
    `int` are currently supported). However, datatype conversion is disabled
    if the source file is a python module or other file type that supports
    typing.

    Args:
        contents: stores configuration options. Defaults to en empty dict.
        defaults: default options that should be used when a user does not
            provide the corresponding options in their configuration settings.
            Defaults to an empty dict.
        infer_types: whether values in `contents` are converted to other
            datatypes (True) or left alone (False). Defaults to True.
        nested_factory: default mapping type to use for subsections of
            `contents`. Defaults to `dataclasses.MISSING`, which will result in
            this class being used for all nested mappings.
        Parsers: keys are str names of Parser instances and the values are
            Parser instances. The keys are used as attribute names when the
            `Parser` method is called if `Parsers` is not None. Defaults to
            None.

    """

    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    defaults: Mapping[Hashable, Any] = dataclasses.field(default_factory = dict)
    infer_types: bool = True
    nested_factory: Any | None = dataclasses.MISSING
    name: str | None = None
    Parsers: MutableMapping[Hashable, extensions.Parser] | None = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__() 
        # Converts `contents` if it is not a dict.
        if not (self.contents, MutableMapping):
            self = self.create(
                item = self.contents,
                defaults = self.defaults,
                infer_types = self.infer_types,
                nested_factory = self.nested_factory,
                Parsers = self.Parsers)
        # Infers types for values in `contents`, if the `infer_types` option is
        # selected.
        if self.infer_types:
            self.contents = self._infer_types(contents = self.contents)
        # Adds default settings as backup settings to `contents`.
        self.contents = self._add_defaults(contents = self.contents)
        # Adds descriptora from `Parsers`,
        self.Parser()

    """ Class Methods """

    @classmethod
    def create(cls, source: Any, **kwargs: Any) -> Settings:
        """Calls corresponding creation class method to instance a class.

        Args:
            source: data source for the contents of the created instance.
            kwargs: additional parameters to pass to the Settings instance being
                created.

        Raises:
            TypeError: if `source` is not a str, pathlib.Path, or dict-like
                object.

        Returns:
            Settings: instance of Settings.

        """
        if isinstance(source, (str, pathlib.Path)):
            return cls.from_path(source = source, **kwargs)
        elif isinstance(source, MutableMapping):
            return cls.from_dictionary(source = source, **kwargs)
        else:
            raise TypeError(
                'source must be a str, Path, or dict-like object')

    @classmethod
    def from_dictionary(
        cls, 
        source: MutableMapping[Hashable, Any], 
        **kwargs: Any) -> Settings:
        """Creates an instance from a dict-like object.

        Args:
            source: dict with settings to store in a Settings instance.
            kwargs: additional parameters to pass to the Settings instance being
                created.

        Returns:
            Settings: an instance derived from `source`.

        """
        return cls(contents = source, **kwargs)

    @classmethod
    def from_path(
        cls,
        source: str | pathlib.Path,
        **kwargs: Any) -> Settings:
        """Creates an instance from a file.

        Args:
            source: path to file with settings to store in a Settings instance.
            kwargs: additional parameters to pass to the Settings instance being 
                created.

        Returns:
            Settings: an instance derived from `source`.

        """
        path = utilities._pathlibify(source)
        extension = path.suffix[1:]
        load_method = getattr(cls, f'from_{extension}')
        return load_method(source = path, **kwargs)

    @classmethod
    def from_ini(
        cls, 
        source: str | pathlib.Path, 
        **kwargs: Any) -> Settings:
        """Returns settings from an .ini file.

        Args:
            source: path to file with settings to store in a Settings instance.
            kwargs: additional parameters to pass to the Settings instance being 
                created.

        Returns:
            Settings: an instance derived from `source`.

        Raises:
            FileNotFoundError: if the path does not correspond to a file.

        """
        path = utilities._pathlibify(source)
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            contents = configparser.ConfigParser(dict_type = dict)
            contents.optionxform = lambda option: option
            contents.read(path)
            return cls(contents = dict(contents._sections), **kwargs)
        except (KeyError, FileNotFoundError) as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error

    @classmethod
    def fromkeys(
        cls,
        keys: Sequence[Hashable],
        value: Any) -> Settings:
        """Emulates the `fromkeys` class method from a python dict.

        Args:
            keys: items to be keys in a new Settings.
            value: the value to use for all values in a new Settings.

        Returns:
            Settings: formed from `keys` and `value`.

        """
        return cls(contents = dict.fromkeys(keys, value))

    @classmethod
    def from_json(
        cls,
        source: str | pathlib.Path, 
        **kwargs: Any) -> Settings:
        """Returns settings from an .json file.

        Args:
            source: path to file with settings to store in a Settings instance.
            kwargs: additional parameters to pass to the Settings instance being 
                created.

        Returns:
            Settings: an instance derived from `source`.

        Raises:
            FileNotFoundError: if the path does not correspond to a file.

        """
        import json
        path = utilities._pathlibify(source)
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            with open(pathlib.Path(path)) as settings_file:
                contents = json.load(settings_file)
            return cls(contents = contents, **kwargs)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error

    @classmethod
    def from_py(
        cls,
        source: str | pathlib.Path,
        **kwargs: Any) -> Settings:
        """Returns a settings dictionary from a .py file.

        Args:
            source: path to a Python module with settings to store in a Settings 
                instance. The path to a python module must have a `__dict__` 
                defined and an attribute named `settings` that contains the 
                settings to use for creating an instance.
            kwargs: additional parameters to pass to the Settings instance being 
                created.

        Returns:
            Settings: an instance derived from `source`.

        Raises:
            FileNotFoundError: if the path does not correspond to a
                file.

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
            return cls(contents = import_module.settings, **kwargs)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error

    @classmethod
    def from_toml(
        cls,
        source: str | pathlib.Path,
        **kwargs: Any) -> Settings:
        """Returns settings from a .toml file.

        Args:
            source: path to file with settings to store in a Settings instance.
            kwargs: additional parameters to pass to the Settings instance being 
                created.

        Returns:
            Settings: an instance derived from `source`.

        Raises:
            FileNotFoundError: if the path does not correspond to a file.

        """
        import toml
        path = utilities._pathlibify(source) 
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            return cls(contents = toml.load(path), **kwargs)
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error

    @classmethod
    def from_yaml(
        cls, 
        source: str | pathlib.Path, 
        **kwargs: Any) -> Settings:
        """Returns settings from a .yaml file.

        Args:
            source: path to file with settings to store in a Settings instance.
            kwargs: additional parameters to pass to the Settings instance being 
                created.

        Returns:
            Settings: an instance derived from `source`.

        Raises:
            FileNotFoundError: if the path does not correspond to a file.

        """
        import yaml
        path = utilities._pathlibify(source) 
        kwargs['infer_types'] = False
        try:
            with open(path) as config:
                return cls(contents = yaml.safe_load(config, **kwargs))
        except FileNotFoundError as error:
            message = f'settings file {path} not found'
            raise FileNotFoundError(message) from error

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
            try:
                for key, value in self.contents[section].items():
                    if (not hasattr(instance, key)
                            or not getattr(instance, key)
                            or overwrite):
                        setattr(instance, key, value)
            except KeyError:
                pass
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

    def setdefault(self, value: Any) -> None:
        """Sets default value to return when `get` method is used.

        Args:
            value (Any): default value to return when `get` is called and the
                `default` parameter to `get` is None.

        """
        self.default_factory = value
        return

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
        else:  # noqa: RET506
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

    def parse(self) -> None:
        """Adds key/value pairs in `Parsers` as class attributes."""
        if self.Parsers:
            for key, parse in self.parses.items():
                setattr(self.__class__, key, parse)
        return self

    """ Private Methods """

    def _add_defaults(
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
