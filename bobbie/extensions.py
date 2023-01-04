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
    Parser (object): a descriptor for parsing Settings data.
    Parsers (camina.Dictionary): a dict-like class to store Parser instances. It
        can be passed as an argument to Settings to automatically add Parser
        instances as attributes to Settings.

ToDo:
       
       
"""
from __future__ import annotations
from collections.abc import Hashable, MutableMapping
import dataclasses
from typing import Any, Literal, Optional, Type

import camina

from . import parsers

""" Limited Option Types for Static Type Checkers """

ScopeOptions = Literal['all', 'prefix', 'suffix']
ReturnsOptions = Literal[
    'contents',
    'keys', 
    'kinds', 
    'sections', 
    'section_keys',
    'section_kinds']


""" Extension Classes """

@dataclasses.dataclass
class Parser(object):
    """A descriptor which supports a different view of Settigs data.

    Args:
        terms (tuple[str, ...]): strings to match against entries in a Settings
            instance.
        scope (Optional[ScopeOptions]): how much of the str must be scopeed.
            Defaults to 'all'.
        returns (Optional[ReturnOptions]): the type of data that should be 
            returned after parsing. Defaults to 'section'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        accumulate (Optional[bool]): whether to return all matching items (True)
            or just the first (False). Defaults to True.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'scope' is 'all', 'divider' has no effect. Defaults to 
            ''.
        
    """
    terms: tuple[str, ...]
    scope: Optional[ScopeOptions] = 'all'
    returns: Optional[ReturnsOptions] = 'sections'
    excise: Optional[bool] = True
    accumulate: Optional[bool] = True
    divider: Optional[str] = ''

    """ Dunder Methods """
    
    def __get__(self, obj: object, objtype: Type[Any] = None) -> Any:
        """Getter for use as a descriptor.

        Args:
            obj (object): the object which has a Parser instance as a 
                descriptor.

        Returns:
            Any: stored value(s).
            
        """
        try:
            settings = obj.settings
        except AttributeError:
            settings = obj
        return parsers.parse(settings = settings, parser = self)

    def __set__(self, obj: object, value: Any) -> None:
        """Setter for use as a descriptor.

        Args:
            obj (object): the object which has a Parser instance as a 
                descriptor.
            value (Any): the value to assign when accessed.
            
        """
        try:
            settings = obj.settings
        except AttributeError:
            settings = obj
        keys = parsers.get_keys(
            settings = settings,
            terms = self.terms,
            scope = 'all',
            excise = False)
        try:
            key = keys[0]
        except IndexError:
            key = self.terms[0]
        settings[key] = value
        return

    def __set_name__(self, owner: Type[Any], name: str) -> None:
        """Stores the attribute name in 'owner' of the Parser descriptor.

        Args:
            owner (Type[Any]): the class which has a Parser instance as a 
                descriptor.
            name (str): the str name of the descriptor.
            
        """
        self.name = name
        return


@dataclasses.dataclass
class Parsers(camina.Dictionary):
    """Rules for parsing a Settings instance.

    Args:
        contents (MutableMapping[Hashable, Any]): a dict for storing 
            configuration options. Defaults to en empty dict.
        default_factory (Optional[Any]): default value to return when the 'get' 
            method is used. Defaults to an empty camina.Dictionary.
        
    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = camina.Dictionary
    
    """ Instance Methods """
    
    def validate(self) -> None:
        """Validates types in 'contents'.
        
        Raises:
            TypeError: if not all keys are Hashable or all values are not Parser
                instances.
                
        """
        if not all(isinstance(k, Hashable) for k in self.contents.keys()):
            raise TypeError('All keys in Parsers must be Hashable')
        if not all(isinstance(v, Parser) for v in self.contents.values()):
            raise TypeError('All values in Parsers must be Parser instances')
        return

   