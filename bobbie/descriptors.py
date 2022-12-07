"""
descriptors: descriptors for accessing settings data
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
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
import contextlib
import dataclasses
from typing import Any, ClassVar, Optional, Type, Union

from . import core
from . import extensions
from . import workshop


DEFAULT_PARSERS: dict[str, tuple[str]] = {
    'general': ('general',),
    'files': ('files', 'filer', 'clerk'),
    'parameters': ('parameters',)}


@dataclasses.dataclass
class Maximizer(extensions.Parser):
    """
    """
    terms: tuple[str, ...]
    match: Optional[extensions.MatchOptions] = 'complete'
    scope: Optional[extensions.ScopeOptions] = 'outer'
    returns: Optional[extensions.ReturnsOptions] = 'sections'
    divider: Optional[str] = ''
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates an instance."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        self.set_parser()

    def __set_name__(self, owner: Type[Any], name: str) -> None:
        """_summary_

        Args:
            owner (Type[Any]): _description_
            name (str): _description_
            
        """
        self.name = name
        return

    """ Public Methods """
    
    def set_parser(self) -> None:
        """Sets 'parser' attribute to the appropriate function."""
        parser_name = f'accumulate_{self.returns}_{self.scope}'
        self.parser = getattr(workshop, parser_name)     
        return self        

    """ Dunder Methods """
    
    def __get__(self, obj: object) -> Any:
        """_summary_

        Args:
            obj (object): _description_

        Returns:
            Any: _description_
        """
        return self.parser(
            settings = obj.settings, 
            terms = self.terms, 
            matching = self.match)

    def __set__(self, obj: object, value: Any) -> None:
        """_summary_

        Args:
            obj (object): _description_
            value (Any): _description_
        """
        key = self.terms[0]
        for term in self.terms:
            if term in obj.settings.contents.keys():
                key = term
                break
        obj.settings[key] = value
        return
        
class Maximizer(extensions.Parser):
    
    name: str
    terms: tuple[str, ...]
    match: Optional[extensions.MatchOptions] = 'complete'
    scope: Optional[extensions.ScopeOptions] = 'outer'
    returns: Optional[extensions.ReturnsOptions] = 'sections'
    divider: Optional[str] = ''

    """ Public Methods """
    
    def apply(self, settings: core.Settings) -> Any:
        """Applies the parser to a Settings instance.

        Args:
            settings (core.Settings): configuration settings to parse.

        Returns:
            Any: information derived from parsing.
            
        """
        keys = workshop.get_matching_outer_keys(
            settings = settings, 
            terms = self.terms, 
            matching = self.match)
        func_name = f'accumulate_{self.returns}_{self.scope}'
        func = getattr(workshop, func_name)
        return func(
            settings = settings, 
            terms = self.terms, 
            matching = self.match)
    
 
class Satisficer(extensions.Parser):
    
    name: str
    terms: tuple[str, ...]
    match: Optional[extensions.MatchOptions] = 'complete'
    scope: Optional[extensions.ScopeOptions] = 'outer'
    returns: Optional[extensions.ReturnsOptions] = 'sections'
    divider: Optional[str] = ''

    """ Public Methods """
    
    def apply(self, settings: core.Settings) -> Any:
        """Applies the parser to a Settings instance.

        Args:
            settings (core.Settings): configuration settings to parse.

        Returns:
            Any: information derived from parsing.
            
        """
        func_name = f'accumulate_{self.returns}_{self.scope}'
        func = getattr(workshop, func_name)
        return func(
            settings = settings, 
            terms = self.terms, 
            matching = self.match)
    
           
files = extensions.Parser(
    name = 'files',
    terms = ('files', 'filer', 'clerk'),
    match = 'complete',
    scope = 'outer',
    returns = 'section_contents',
    divider = '')

general = extensions.Parser(
    name = 'general',
    terms = ('general',),
    match = 'complete',
    scope = 'outer',
    returns = 'section_contents',
    divider = '')

parameters = extensions.Parser(
    name = 'parameters',
    terms = ('parameters',),
    match = 'suffix',
    scope = 'outer',
    returns = 'sections',
    divider = '_')