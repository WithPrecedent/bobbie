"""
parsers: functions for parsing configuration settings
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
    parse: general 

ToDo:
       
       
"""
from __future__ import annotations
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING

import camina

if TYPE_CHECKING:
    from . import core
    from . import extensions
    

def parse(
    settings: core.Settings,
    parser: Optional[extensions.Parser] = None,
    terms: Optional[tuple[str, ...]] = None,
    match: Optional[extensions.MatchOptions] = 'all',
    scope: Optional[extensions.ScopeOptions] = 'outer',
    returns: Optional[extensions.ReturnsOptions] = 'sections',
    excise: Optional[bool] = True,
    accumulate: Optional[bool] = True,
    divider: Optional[str] = '') -> Any:
    """Returns parsed information from a Settings instance.
    
    Either 'parser' or 'terms' must not be None. If 'parser' is passed, the 
    rest of the arguments (other than 'settings' and 'parser') are ignored and
    the data in 'parser' is used instead.

    Args:
        settings (core.Settings): _description_
        parser (Optional[extensions.Parser], optional): a Parser instance with 
            data for the other parameters. Defaults to None.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        match (Optional[extensions.MatchOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        scope (Optional[extensions.ScopeOptions]): whether to match outer, 
            inner, or all keys. Defaults to 'outer'.
        returns (Optional[extensions.ReturnOptions]): the type of data that 
            should be returned after parsing. Defaults to 'section'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        accumulate (Optional[bool]): whether to return all matching items (True)
            or just the first (False). Defaults to True.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'match' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Raises:
        ValueError: if both 'parser' and 'terms' are None.

    Returns:
        Any: an item parsed from 'settings'.
        
    """
    if parser is not None:
        terms = parser.terms
        match = parser.match
        scope = parser.scope
        returns = parser.returns
        excise = parser.excise
        accumulate = parser.accumulate
        divider = parser.divider
    elif terms is None:
        raise ValueError('Either parser or terms argument must not be None')
    key_getter = globals()[f'get_{scope}_keys']
    keys = key_getter(
        settings = settings,
        terms = terms, 
        match = match, 
        accumuldate = accumulate,
        divider = divider)
    if returns == 'keys':
        return keys
    else:
        final_getter = globals()[f'get_{returns}']
        return final_getter(
            settings = settings,
            terms = terms,
            keys = keys,
            excise = excise,
            divider = divider)

def get_outer_sections(
    settings: core.Settings, 
    terms: Sequence[str], 
    match: Optional[str] = 'all') -> dict[str, dict[str, Any]]:
    """_summary_

    Args:
        settings (core.Settings): a Settings instance with raw data to use.
        terms (Sequence[str]): str to match against entries in 'settings'.
        match (Optional[str]): the scope of the match to look for. Options
            are 'all', 'prefix', and 'suffix'. Defaults to 'all'.

    Returns:
        dict[str, dict[str, Any]]: sections that match 'terms'.
        
    """
    keys = get_outer_keys(
        settings = settings, 
        terms = terms, 
        match = match)
    return {k: settings[k] for k in keys}

def get_outer_section_contents(
    settings: core.Settings, 
    terms: Sequence[str], 
    match: Optional[str] = 'all') -> dict[str, Any]:
    """_summary_

    Args:
        settings (core.Settings): a Settings instance with raw data to use.
        terms (Sequence[str]): str to match against entries in 'settings'.
        match (Optional[str]): the scope of the match to look for. Options
            are 'all', 'prefix', and 'suffix'. Defaults to 'all'.

    Returns:
        dict[str, Any]: key/value pairs from sections that match 'terms'.
        
    """
    keys = get_outer_keys(
        settings = settings, 
        terms = terms, 
        match = match)
    relevant = {}
    for key in keys:
        relevant.update(settings[key])
    return relevant

def get_all_keys(
    settings: core.Settings, 
    terms: Sequence[str], 
    match: Optional[str] = 'all') -> Optional[str]:
    """_summary_

    Args:
        item (Any): _description_
        terms (Sequence[str]): _description_
        match (Optional[str], optional): _description_. Defaults to 'all'.

    Returns:
        Optional[str]: _description_
        
    """
    matches = get_outer_keys(
        settings = settings, 
        terms = terms, 
        match = match)
    matches.extend(get_inner_keys(
        settings = settings, 
        terms = terms, 
        match = match))
    return matches

def get_inner_keys(
    settings: core.Settings, 
    terms: Sequence[str], 
    match: Optional[str] = 'all') -> Optional[str]:
    """_summary_

    Args:
        item (Any): _description_
        terms (Sequence[str]): _description_
        match (Optional[str], optional): _description_. Defaults to 'all'.

    Returns:
        Optional[str]: _description_
    """
    matches = []
    for _, section in settings.items():
        matches.extend(
            get_outer_keys(
                settings = section, 
                terms = terms, 
                match = match))
    return matches

def get_outer_keys(
    settings: dict[str, Any], 
    terms: Sequence[str], 
    match: Optional[str] = 'all') -> Optional[str]:
    """_summary_

    Args:
        item (Any): _description_
        terms (Sequence[str]): _description_
        match (Optional[str], optional): _description_. Defaults to 'all'.

    Returns:
        Optional[str]: _description_
    """
    matcher = globals()[f'match_{match}']
    return [k for k in settings.keys() if matcher(k, terms)]

def get_section_keys(
    settings: core.Settings, 
    terms: Sequence[str], 
    match: Optional[str] = 'all') -> dict[str, list[str]]:
    """_summary_

    Args:
        item (Any): _description_
        terms (Sequence[str]): _description_
        match (Optional[str], optional): _description_. Defaults to 'all'.

    Returns:
        Optional[str]: _description_
        
    """
    matches = {}
    for key, section in settings.items():
        matches[key] = (
            get_outer_keys(
                settings = section, 
                terms = terms, 
                match = match))
    return matches

def get_kinds(
    settings: MutableMapping[str, Any], 
    terms: Sequence[str],
    match: extensions.MatchOptions,
    scope: extensions.ScopeOptions,
    excise: Optional[extensions.ExciseOptions] = True,
    divider: Optional[str] = '') -> MutableMapping[str, Any]:
    """_summary_

    Args:
        settings (MutableMapping[str, Any]): _description_
        terms (Sequence[str]): _description_
        excise (extensions.ExciseOptions): _description_
        divider (str): _description_

    Returns:
        MutableMapping[str, Any]: _description_
        
    """
    kinds = {}
    checker_name = f'match_{match}'
    checker = globals()[checker_name]
    for key in settings.keys():
        matching = checker(item = key, terms = terms, divider = divider)
        if matching is not None:
            if excise:
                kind = camina.drop_prefix(
                    item = key, 
                    prefix = matching, 
                    divider = divider)
            else:
                kind = key
            kinds.update(kind, matching) 
    return kinds

def has_all(item: Any, terms: Sequence[str]) -> bool:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.

    Returns:
        bool: the matching term or None (if there is no matching term).
        
    """
    return any(item == t for t in terms)

def match_all(
    item: Any, 
    terms: Sequence[str], 
    divider: Optional[str] = '') -> Optional[str]:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.
        divider (Optional[str]): divider between a term and the rest of 'item'.
            Defaults to ''.

    Returns:
        Optional[str]: the matching term or None (if there is no matching term).
        
    """
    for term in terms:
        if item == term:
            return term 
    return None

def has_prefix(
    item: Any, 
    terms: Sequence[str], 
    divider: Optional[str] = '') -> bool:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.
        divider (Optional[str]): divider between a term and the rest of 'item'.
            Defaults to ''.

    Returns:
        bool
        
    """
    prefixes = [t + divider for t in terms]
    return any(item.startswith(p) for p in prefixes)

def match_prefix(
    item: Any, 
    terms: Sequence[str], 
    divider: Optional[str] = '') -> Optional[str]:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.
        divider (Optional[str]): divider between a term and the rest of 'item'.
            Defaults to ''.

    Returns:
        Optional[str]: the matching term or None (if there is no matching term).
        
    """
    for term in terms:
        if item.startswith(term + divider):
            return term 
    return None

def has_suffix(
    item: Any, 
    terms: Sequence[str], 
    divider: Optional[str] = '') -> bool:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.
        divider (Optional[str]): divider between a term and the rest of 'item'.
            Defaults to ''.

    Returns:
        bool:.
        
    """
    suffixes = [divider + t for t in terms]
    return any(item.endswith(p) for p in suffixes)

def match_suffix(
    item: Any, 
    terms: Sequence[str], 
    divider: Optional[str] = '') -> Optional[str]:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.
        divider (Optional[str]): divider between a term and the rest of 'item'.
            Defaults to ''.

    Returns:
        Optional[str]: the matching term or None (if there is no matching term).
        
    """
    for term in terms:
        if item.endswith(divider + term):
            return term 
    return None

def excise_settings(
    settings: MutableMapping[str, Any], 
    terms: Sequence[str],
    match: extensions.MatchOptions,
    scope: extensions.ScopeOptions,
    excise: extensions.ExciseOptions,
    divider: str) -> MutableMapping[str, Any]:
    """_summary_

    Args:
        settings (MutableMapping[str, Any]): _description_
        terms (Sequence[str]): _description_
        match (extensions.MatchOptions): _description_
        scope (extensions.ScopeOptions): _description_
        excise (extensions.ExciseOptions): _description_

    Returns:
        MutableMapping[str, Any]: _description_
        
    """
    if excise == 'none':
        return settings
    else:
        func_name = f'excise_{excise}_{match}'
        func = globals()[func_name]
        return func(
            settings = settings, 
            terms = terms, 
            match = match, 
            excise = excise,
            divider = divider)

def excise_terms_prefix(
    settings: MutableMapping[str, Any], 
    terms: Sequence[str],
    excise: extensions.ExciseOptions,
    divider: str) -> MutableMapping[str, Any]:
    """_summary_

    Args:
        settings (MutableMapping[str, Any]): _description_
        terms (Sequence[str]): _description_
        excise (extensions.ExciseOptions): _description_
        divider (str): _description_

    Returns:
        MutableMapping[str, Any]: _description_
        
    """
    if excise == 'terms':
        for term in terms:
            excised = camina.drop_prefix(
                item = settings, 
                prefix = term, 
                divider = divider)
    elif excise == 'remainder':
        excised = {}
        for key, _ in settings.items():
            for term in terms:
                prefix = term + divider
                if term.startswith(prefix):
                    excised.update(key, term)    
    return excised


    
    
    
    

    
