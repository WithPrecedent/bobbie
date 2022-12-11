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
ReturnsOptions = Literal['keys','sections', 'section_contents', 'contents']
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
    """Default values and rules for parsing a Settings instance.
    
    Every attribute in Rules should be a class attribute so that it is 
    accessible without instancing it (which it cannot be).

    Args:
        parsers (ClassVar[dict[str, Parser]]): keys are the names of parsers and
            values are Parser instances.
        default_settings (ClassVar[dict[Hashable, dict[Hashable, Any]]]):
            default settings for a python project.  
        
    """
    parsers: ClassVar[dict[str, Parser]] = {
        'files': Parser(
            terms = ('filer', 'files', 'clerk'),
            match = 'all',
            scope = 'outer',
            returns = 'sections',
            excise = 'none',
            accumulate = False,
            divider = ''),
        'general': Parser(
            terms = ('general',),
            match = 'all',
            scope = 'outer',
            returns = 'sections',
            excise = 'none',
            accumulate = False,
            divider = ''),
        'parameters': Parser(
            terms = ('parameters',),
            match = 'suffix',
            scope = 'outer',
            returns = 'sections',
            excise = 'terms',
            accumulate = True,
            divider = '_')}
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
    rules: Rules
        
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates an instance."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        self.activate()
        
    def activate(self) -> None:
        """Adds parsers in 'rules' as attributes."""
        for key, parser in self.rules.parsers.items():
            setattr(self, key, parser)
        return self

          