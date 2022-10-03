"""
core: base class for configuring projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Contents:
    Settings (amos.Dictionary, amos.SourceFactory): stores configuration 
        settings after either loading them from disk or by the passed arguments.

ToDo:
       
       
"""
from __future__ import annotations
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
import configparser
import dataclasses
import importlib
import importlib.util
import pathlib
from typing import Any, ClassVar, Optional, Type, Union

import amos


@dataclasses.dataclass
class Settings(amos.Dictionary, amos.SourcesFactory): # type: ignore
    """Loads and stores configuration settings.

    To create settings instance, a user can pass as the 'contents' parameter a:
        1) pathlib file path of a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) 2-level nested dict.

    If 'contents' is imported from a file, settings creates a dict and can 
    convert the dict values to appropriate datatypes. Currently, supported file 
    types are: ini, json, toml, yaml, and python. If you want to use toml, yaml, 
    or json, the identically named packages must be available in your python
    environment.

    If 'infer_types' is set to True (the default option), str dict values are 
    automatically converted to appropriate datatypes (str, list, float, bool, 
    and int are currently supported). Type conversion is automatically disabled
    if the source file is a python module (assuming the user has properly set
    the types of the stored python dict).

    Because settings uses ConfigParser for .ini files, by default it stores 
    a 2-level dict. The desire for accessibility and simplicity dictated this 
    limitation. A greater number of levels can be achieved by having separate
    sections with names corresponding to the strings in the values of items in 
    other sections. 

    Args:
        contents (MutableMapping[Hashable, Any]): a dict for storing 
            configuration options. Defaults to en empty dict.
        default_factory (Optional[Any]): default value to return when the 'get' 
            method is used. Defaults to an empty dict.
        default (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.

    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = dict
    default: Mapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True
    sources: ClassVar[Mapping[Type, str]] = {
        MutableMapping: 'dictionary', 
        pathlib.Path: 'path',  
        str: 'path'}

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Converts 'contents' if it is not a dict.
        if not (self.contents, Mapping):
            self = self.create(
                item = self.contents,
                default_factory = self.default_factory,
                default = self.default,
                infer_types = self.infer_types)
        # Infers types for values in 'contents', if the 'infer_types' option is 
        # selected.
        if self.infer_types:
            self.contents = self._infer_types(contents = self.contents)
        # Adds default settings as backup settings to 'contents'.
        self.contents = self._add_default(contents = self.contents)

    """ Class Methods """

    @classmethod
    def from_dictionary(
        cls, 
        dictionary: MutableMapping[Hashable, Any], 
        **kwargs: Any) -> Settings:
        """[recap]

        Args:
            path (Union[str, pathlib.Path]): [description]

        Returns:
            settings: [description]
            
        """        
        return cls(contents = dictionary, **kwargs)
        
    @classmethod
    def from_path(
        cls, 
        path: Union[str, pathlib.Path], 
        **kwargs: Any) -> Settings:
        """[summary]

        Args:
            path (Union[str, pathlib.Path]): [description]

        Returns:
            settings: [description]
            
        """
        path = amos.pathlibify(item = path)   
        extension = path.suffix[1:]
        load_method = getattr(cls, f'from_{extension}')
        return load_method(path = path, **kwargs)
    
    @classmethod
    def from_ini(
        cls, 
        path: Union[str, pathlib.Path], 
        **kwargs: Any) -> Settings:
        """Returns settings from an .ini file.

        Args:
            path (str): path to configparser-compatible .ini file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the path does not correspond to a file.

        """
        path = amos.pathlibify(item = path) 
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            contents = configparser.ConfigParser(dict_type = dict)
            contents.optionxform = lambda option: option
            contents.read(path)
            return cls(contents = dict(contents._sections), **kwargs)
        except (KeyError, FileNotFoundError):
            raise FileNotFoundError(f'settings file {path} not found')

    @classmethod
    def from_json(
        cls,
        path: Union[str, pathlib.Path], 
        **kwargs: Any) -> Settings:
        """Returns settings from an .json file.

        Args:
            path (str): path to configparser-compatible .json file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the path does not correspond to a file.

        """
        import json
        path = amos.pathlibify(item = path) 
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            with open(pathlib.Path(path)) as settings_file:
                contents = json.load(settings_file)
            return cls(contents = contents, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {path} not found')

    @classmethod
    def from_py(
        cls,
        path: Union[str, pathlib.Path], 
        **kwargs: Any) -> Settings:
        """Returns a settings dictionary from a .py file.

        Args:
            path (str): path to python module with '__dict__' defined and an 
                attribute named 'settings' that contains the settings to use for 
                creating a settings instance..

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the path does not correspond to a
                file.

        """
        path = amos.pathlibify(item = path) 
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = False
        try:
            path = pathlib.Path(path)
            import_path = importlib.util.spec_from_file_location(
                path.name,
                path)
            import_module = importlib.util.module_from_spec(import_path)
            import_path.loader.exec_module(import_module)
            return cls(contents = import_module.settings, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {path} not found')

    @classmethod
    def from_toml(
        cls,
        path: Union[str, pathlib.Path], 
        **kwargs: Any) -> Settings:
        """Returns settings from a .toml file.

        Args:
            path (str): path to configparser-compatible .toml file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the path does not correspond to a file.

        """
        import toml
        path = amos.pathlibify(item = path) 
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            return cls(contents = toml.load(path), **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {path} not found')
   
    @classmethod
    def from_yaml(
        cls, 
        path: Union[str, pathlib.Path], 
        **kwargs: Any) -> Settings:
        """Returns settings from a .yaml file.

        Args:
            path (str): path to configparser-compatible .toml file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the path does not correspond to a file.

        """
        import yaml
        path = amos.pathlibify(item = path) 
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = False
        try:
            with open(path, 'r') as config:
                return cls(contents = yaml.safe_load(config, **kwargs))
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {path} not found')
        
    """ Public Methods """

    def add(self, section: Hashable, contents: Mapping[Hashable, Any]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (Hashable): name of section to add 'contents' to.
            contents (Mapping[Hashable, Any]): a dict to store in 'section'.

        """
        try:
            self[section].update(contents)
        except KeyError:
            self[section] = contents
        return
        
    def inject(
        self, 
        instance: object,
        additional: Optional[Union[Sequence[str], str]] = None,
        overwrite: bool = False) -> object:
        """Injects appropriate items into 'instance' from 'contents'.
        
        By default, if 'instance' has a 'name' attribute, this method will add
        any settings in a section matching that 'name' to 'instance' as
        attributes.

        Args:
            instance (object): amos class instance to be modified.
            additional (Union[Sequence[str], str]]): other section(s) in 
                'contents' to inject into 'instance'. Defaults to None.
            overwrite (bool]): whether to overwrite a local attribute in 
                'instance' if there are existing values stored in that 
                attribute. Defaults to False.

        Returns:
            instance (object): instance with modifications made.

        """
        sections = []
        try:
            sections.append(instance.name)
        except AttributeError:
            pass
        if additional:
            sections.extend(amos.iterify(additional))
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
       
    """ Private Methods """

    def _infer_types(
        self, 
        contents: MutableMapping[Hashable, Any]) -> (
            MutableMapping[Hashable, Any]):
        """Converts stored values to appropriate datatypes.

        Args:
            contents (MutableMapping[Hashable, Any]): a nested contents dict to 
                review.

        Returns:
            MutableMapping[Hashable, Any]: with the nested values converted to 
                the appropriate datatypes.

        """
        new_contents = {}
        for key, value in contents.items():
            if isinstance(value, dict):
                inner_bundle = {
                    inner_key: amos.typify(inner_value)
                    for inner_key, inner_value in value.items()}
                new_contents[key] = inner_bundle
            else:
                new_contents[key] = amos.typify(value)
        return new_contents

    def _add_default(
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
        new_contents = self.default
        new_contents.update(contents)
        return new_contents

    """ Dunder Methods """

    def __setitem__(self, key: str, value: Mapping[str, Any]) -> None:
        """Creates new key/value pair(s) in a section of the active dictionary.

        Args:
            key (str): name of a section in the active dictionary.
            value (Mapping[str, Any]): the dictionary to be placed in that 
                section.

        Raises:
            TypeError if 'key' isn't a str or 'value' isn't a dict.

        """
        try:
            self.contents[key].update(value)
        except KeyError:
            try:
                self.contents[key] = value
            except TypeError:
                raise TypeError(
                    'key must be a str and value must be a dict type')
        return
