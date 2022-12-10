"""
extensions: additional functionality for Settings class
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


ToDo:
       
       
"""
from __future__ import annotations
import abc
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
import contextlib
import dataclasses
from typing import Any, ClassVar, Literal, Optional, Type

from . import core
from . import workshop


MatchOptions = Literal['all', 'prefix', 'suffix']
ScopeOptions = Literal['both', 'inner', 'outer']
ReturnsOptions = Literal['keys','sections', 'section_contents']
ExciseOptions = Literal['terms', 'remainder', 'none']


@dataclasses.dataclass
class Parser(abc.ABC):
    """

    Args:
        terms (tuple[str, ...]): strings to match against entries in a Settings
            instance.
        match (Optional[MatchOptions]): how much of the str must be matched.
        scope (Optional[ScopeOptions]):
        
    """
    terms: tuple[str, ...]
    match: Optional[MatchOptions] = 'all'
    scope: Optional[ScopeOptions] = 'outer'
    returns: Optional[ReturnsOptions] = 'sections'
    excise: Optional[ExciseOptions] = 'none'
    accumulate: Optional[bool] = True
    divider: Optional[str] = ''

    """ Dunder Methods """
    
    def __get__(self, obj: object) -> Any:
        """_summary_

        Args:
            obj (object): _description_

        Returns:
            Any: _description_
            
        """
        return workshop.parse(
            settings = obj.settings, 
            terms = self.terms, 
            match = self.match,
            scope = self.scope,
            returns = self.returns,
            excise = self.excise,
            accumualte = self.accumulate,
            divider = self.divider)

    def __set__(self, obj: object, value: Any) -> None:
        """_summary_

        Args:
            obj (object): _description_
            value (Any): _description_
            
        """
        keys = workshop.get_outer_keys(
            settings = obj.settings,
            terms = self.terms,
            match = self.match)
        try:
            key = keys[0]
        except IndexError:
            key = self.terms[0]
        obj.settings[key] = value
        return

    def __set_name__(self, owner: Type[Any], name: str) -> None:
        """_summary_

        Args:
            owner (Type[Any]): _description_
            name (str): _description_
            
        """
        self.name = name
        return


@dataclasses.dataclass
class Rules(abc.ABC):
    """Default values and rules for building a chrisjen project.
    
    Every attribute in Rules should be a class attribute so that it is 
    accessible without instancing it (which it cannot be).

    Args:
        parsers (ClassVar[dict[str, tuple[str]]]): keys are the names of
            special categories of settings and values are tuples of suffixes or
            whole words that are associated with those special categories in
            user settings.
        default_settings (ClassVar[dict[Hashable, dict[Hashable, Any]]]):
            default settings for a chrisjen project's idea. 
        default_manager (ClassVar[str]): key name of the default manager.
            Defaults to 'publisher'.
        default_librarian (ClassVar[str]): key name of the default librarian.
            Defaults to 'as_needed'.
        default_task (ClassVar[str]): key name of the default task design.
            Defaults to 'technique'.
        default_workflow (ClassVar[str]): key name of the default worker design.
            Defaults to 'waterfall'.
        null_node_names (ClassVar[list[Any]]): lists of key names that indicate 
            a null node should be used. Defaults to ['none', 'None', None].   
        
    """
    parsers: ClassVar[dict[str, tuple[str, ...]]] = {
        'criteria': ('criteria',),
        'design': ('design', 'structure'),
        'manager': ('manager', 'project'),
        'files': ('filer', 'files', 'clerk'),
        'general': ('general',),
        'librarian': ('efficiency', 'librarian'),
        'parameters': ('parameters',), 
        'workers': ('workers',)}
    default_settings: ClassVar[dict[Hashable, dict[Hashable, Any]]] = {
        'general': {
            'verbose': False,
            'parallelize': False,
            'efficiency': 'up_front'},
        'files': {
            'file_encoding': 'windows-1252',
            'threads': -1}}


@dataclasses.dataclass
class View(abc.ABC):
    """Provides a different view of settings data.

    Args:
        parsers (Optional[dict[str, tuple[str]]]): dict of parsers with keys
            being the name of the parsers and values being the matching str in a
            tuple. Defaults to an empty dict.

    """
    parsers: Optional[dict[str, tuple[str]]] = dataclasses.field(
        default_factory = dict)

          