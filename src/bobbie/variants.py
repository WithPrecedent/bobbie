"""Base class for loading and storing configuration options.

Contents:
    Settings: loads and stores configuration settings with easy-to-use parser
        and viewers for accessing those settings.

To Do:


"""
from __future__ import annotations

# Some modules are lazily loaded by constructor methods of `Settings` to
# conserve memory.
import configparser
import contextlib
import copy
import dataclasses
import functools
import importlib
import importlib.util
import pathlib
import sys
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
from typing import Any, ClassVar

from . import configuration, utilities


@dataclasses.dataclass
class Settings(MutableMapping):
    """Loads and stores configuration settings.

    The best way to create a `Settings` instance is to call `Settings.create`
    and pass as the first argument a:
        1) `pathlib` or `str` path to a compatible file (including a Python
            module);
                                or
        2) a `dict` or `dict`-like object.
    Any other arguments that you want passed to `Settings` (such as `name`) or a
    `Settings` subclass, you should pass to the `parameters` argument. Any
    additional kwargs that you pass will be relayed to the constructor used by
    `bobbie`. For example, if you are using Python 3.11, `bobbie` uses the
    builtin `tomllib` library to parse `toml` files. If you want to change the
    float parser to `decimal.Decimal` and name your `Settings` instance "Project
    Settings", you would do this:

    ```py
    Settings.create(
        'configuration.toml',
        parameters = {'name': 'Project Settings"},
        parse_float: decimal.Decimal})
    ```

    You may also instance `Settings` directly, like a normal class. However,
    doing so precludes the abilitiy to relay additional keyword arguments to the
    constructor used by `bobbie` (`parse_float` in the above example).

    Currently, supported file extensions are:

    * `env`, `ini`, `json`, `py`, `toml`, `xml`, `yaml`, and `yml`.

    Args:
        contents: configuration options. Defaults to whatever option is stored
            in `configuration._INTERNAL_STORAGE` (en empty `dict` by default).
        name: the `str` name of `Settings`. The top-level of `Settings` need not
            have any name, but may include one for use by custom parsers.
            Defaults to `None`.

    Attributes:
        defaults: default options that should be used when a user does not
            provide the corresponding options in their configuration settings,
            but are otherwise necessary for the project. Defaults to an empty
            `dict`.

    """

    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = configuration._INTERNAL_STORAGE)
    name: str | None = None
    defaults: ClassVar[Mapping[Hashable, Any]] = {}

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        # Adds non-duplicative default settings to `contents`.
        self.contents = self._integrate_defaults(contents = self.contents)

    """ Class Methods """

    @functools.singledispatchmethod
    @classmethod
    def create(
        cls,
        source: Any, /,
        parameters: Mapping[Hashable, Any] | None = None,
        **kwargs:  Any) -> Settings:
        """Calls appropriate class method to create an instance.

        Args:
            source: path to a file or `dict` with data to store in a `Settings`
                instance.
            parameters: additional parameters and arguments to pass to the
                constructor function used by `bobbie`. The specific function
                used for each file type is stored in the `configuration` model.
            kwargs: additional parameters and arguments to pass to the created
                `Settings` instance.

        Raises:
            TypeError: if `source` is not a `str`, `pathlib.Path`, or `dict`-
                like object.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        message = (
            'The first positional argument must be a str, Path, or mapping')
        raise TypeError(message)

    @create.register(Mapping)
    @classmethod
    def from_dict(
        cls,
        source: Mapping, /,
        parameters: Mapping[Hashable, Any] | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a `dict`-like object.

        Args:
            source: `dict`-like object with settings to store in a `Settings`
                instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: any additional keyword arguments are ignored by this
                constructer method. They are only accepted to ensure
                compatiability with dispatching from the `create` method.

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        return cls(source, **parameters)

    @create.register(str | pathlib.Path)
    @classmethod
    def from_path(
        cls,
        source: str | pathlib.Path, /,
        parameters: Mapping[Hashable, Any] | None = None,
        **kwargs:  Any) -> Settings:
        """Creates a `Settings` instance from a file path.

        Args:
            source: path to file with data to store in a `Settings` instance.
            parameters: additional parameters and arguments to pass to the
                created `Settings` instance. Defaults to None.
            kwargs: additional parameters and arguments to pass to the
                constructor used by `bobbie` (such as encoding arguments).

        Returns:
            A `Settings` or `Settings` subclass instance derived from `source`.

        """
        parameters = parameters or {}
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
        source: pathlib.Path | str, /,
        parameters: Mapping[Hashable, Any] | None = None,
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
        source: pathlib.Path | str, /,
        parameters: Mapping[Hashable, Any] | None = None,
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
        source: pathlib.Path | str, /,
        parameters: Mapping[Hashable, Any] | None = None,
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
        source: pathlib.Path | str, /,
        parameters: Mapping[Hashable, Any] | None = None,
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
        source: pathlib.Path | str, /,
        parameters: Mapping[Hashable, Any] | None = None,
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
        value: Any, /) -> Settings:
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

        Raises:
            TypeError if `key` isn't a `str`.

        """
        try:
            self[section].update(contents)
        except KeyError:
            try:
                contents = self.__class__(contents, name = section)
                self[section] = contents
            except TypeError as error:
                message = 'The key must be hashable'
                raise TypeError(message) from error
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
            instance (object): instance with modifications made.

        """
        overwrite = configuration._OVERWRITE_ATTRIBUTES if None else overwrite
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
            TypeError if `key` isn't a `str`.

        """
        self.add(section = key, contents = value)
        return
