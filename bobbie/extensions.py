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
import dataclasses
from typing import Any, ClassVar, Literal, Optional, Type

from . import core
from . import workshop


MatchOptions = Literal['all', 'prefix', 'suffix']
ScopeOptions = Literal['both', 'inner', 'outer']
ReturnsOptions = Literal['sections', 'section_contents']


@dataclasses.dataclass
class Parser(abc.ABC):
    """

    Args:
        name (str): name of parser.
        terms (tuple[str, ...]): strings to match against entries in a Settings
            instance.
        match (Optional[MatchOptions]): how much of the str must be matched.
        scope (Optional[ScopeOptions]):
        
    """
    name: str
    terms: tuple[str, ...]
    match: Optional[MatchOptions] = 'complete'
    scope: Optional[ScopeOptions] = 'outer'
    returns: Optional[ReturnsOptions] = 'sections'
    divider: Optional[str] = ''

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, settings: core.Settings) -> Any:
        """Applies the parser to a Settings instance.

        Args:
            settings (core.Settings): configuration settings to parse.

        Returns:
            Any: information derived from parsing.
            
        """
        func_name = f'get_{self.returns}_{self.scope}'
        func = getattr(workshop, func_name)
        return func(
            settings = settings, 
            terms = self.terms, 
            matching = self.match)
    
    """ Private Nethods """

    def _match_complete(self, setting: dict[Hashable, Any]) -> Any:
        """Applies the parser to a Settings instance.

        Args:
            setting (dict[Hashable, Any]): configuration setting to parse.

        Returns:
            Any: information derived from parsing.
            
        """
        pass

    def _match_prefix(self, item: Any) -> Any:
        """Applies the parser to 'item'.

        Args:
            item (Any: configuration setting to parse.

        Returns:
            Any: information derived from parsing.
            
        """
        for term in self.terms:
            prefix = term + self.divider
            if item.startswith(prefix):
                return True
        return False
    
    def _match_suffix(self, setting: dict[Hashable, Any]) -> Any:
        """Applies the parser to a Settings instance.

        Args:
            setting (dict[Hashable, Any]): configuration setting to parse.

        Returns:
            Any: information derived from parsing.
            
        """
        pass
    
    def _search_both(self, settings: core.Settings) -> Any:
        """Applies the parser to a Settings instance.

        Args:
            settings (core.Settings): configuration settings to parse.

        Returns:
            Any: information derived from parsing.
            
        """
        pass
    
    def _search_inner(self, settings: core.Settings) -> Any:
        """Applies the parser to a Settings instance.

        Args:
            settings (core.Settings): configuration settings to parse.

        Returns:
            Any: information derived from parsing.
            
        """
        pass

    def _search_outer(self, settings: core.Settings) -> Any:
        """Applies the parser to a Settings instance.

        Args:
            settings (core.Settings): configuration settings to parse.

        Returns:
            Any: information derived from parsing.
            
        """
        pass


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

          