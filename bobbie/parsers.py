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
    parse: general parsing function.
    get_contents: returns dict of settings sections with matching keys in those
        sections.
    get_keys: returns list of settings keys that match. 
    get_kinds: returns a dict with keys as the matching str and values as the 
        term which those keys are associated.
    get_sections: returns dict of settings sections with matching section names.
    get_section_keys: returns dict of section names and settings keys within
        those sections that match. 
    get_section_kinds: returns a dict with keys that are section names and 
        values which are dicts returned by 'get_kinds'.
    match_all: returns a matching str (possibly modified based on arguments) and
        the term which matches by matching the entire str.
    match_prefix: returns a matching str (possibly modified based on arguments) 
        and the term which matches by matching a str prefix.
    match_suffix: returns a matching str (possibly modified based on arguments) 
        and the term which matches by matching a str suffix.

ToDo:
       
       
"""
from __future__ import annotations
from collections.abc import MutableMapping, Sequence
from typing import Any, Optional, TYPE_CHECKING

import camina

if TYPE_CHECKING:
    from . import core
    from . import extensions
    

def parse(
    settings: core.Settings,
    parser: Optional[extensions.Parser] = None,
    terms: Optional[tuple[str, ...]] = None,
    match: Optional[extensions.MatchOptions] = 'all',
    returns: Optional[extensions.ReturnsOptions] = 'sections',
    excise: Optional[bool] = True,
    accumulate: Optional[bool] = True,
    divider: Optional[str] = '') -> Any:
    """Returns parsed information from a Settings instance.
    
    Either 'parser' or 'terms' must not be None. If 'parser' is passed, the 
    rest of the arguments (other than 'settings' and 'parser') are ignored and
    the data in 'parser' is used instead.

    Args:
        settings (core.Settings): configuration data.
        parser (Optional[extensions.Parser], optional): a Parser instance with 
            data for the other parameters. Defaults to None.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        match (Optional[extensions.MatchOptions]): how much of the str must be 
            matched. Defaults to 'all'.
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
    # Applies information from 'parser' if it is passed.
    if parser is not None:
        terms = parser.terms
        match = parser.match
        returns = parser.returns
        excise = parser.excise
        accumulate = parser.accumulate
        divider = parser.divider
    elif terms is None:
        raise ValueError('Either parser or terms argument must not be None')
    # Determines name of the appropriate function in the this module to use.
    matcher = globals()[f'get_{returns}']
    # Gets matches based on passed arguments.
    matches = matcher(
        settings = settings, 
        terms = terms, 
        match = match, 
        excise = excise, 
        divider = divider)
    # Returns all matches if 'accumulate' is True. Otherwise, only the first
    # result is returned.
    if accumulate:
        return matches
    elif isinstance(matches, MutableMapping):
        return matches[list(matches.keys())[0]]
    else:
        return matches[0]
  
def get_contents(
    settings: MutableMapping[str, Any],
    terms: Optional[tuple[str, ...]] = None,
    match: Optional[extensions.MatchOptions] = 'all',
    excise: Optional[bool] = True,
    divider: Optional[str] = '') -> dict[str, dict[str, Any]]:
    """Returns parsed information from a Settings instance.
    
    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        match (Optional[extensions.MatchOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'match' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, dict[str, Any]]: keys are section names of 'settings' and
            values are sections of 'settings'.
            
    """
    matcher = globals()[f'match_{match}']
    kwargs = {'terms': terms, 'excise': excise, 'divider': divider}
    matches = {}
    for name, section in settings.items():
        if any(matcher(item = k, **kwargs) for k in section.keys()):
            matches[name] = {
                matcher(item = k, **kwargs)[0]: v for k, v in section.items() 
                if matcher(item = k, **kwargs)}
    return matches

def get_keys(
    settings: MutableMapping[str, Any],
    terms: Optional[tuple[str, ...]] = None,
    match: Optional[extensions.MatchOptions] = 'all',
    excise: Optional[bool] = True,
    divider: Optional[str] = '') -> list[str]:
    """Returns parsed information from a Settings instance.
    
    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        match (Optional[extensions.MatchOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'match' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        list[str]: matching keys
        
    """
    matcher = globals()[f'match_{match}']
    kwargs = {'terms': terms, 'excise': excise, 'divider': divider}
    return [
        matcher(item = k, **kwargs)[0] for k in settings.keys() 
        if matcher(item = k, **kwargs)]

def get_kinds(
    settings: MutableMapping[str, Any],
    terms: Optional[tuple[str, ...]] = None,
    match: Optional[extensions.MatchOptions] = 'all',
    excise: Optional[bool] = True,
    divider: Optional[str] = '') -> dict[str, str]:
    """Returns parsed information from a Settings instance.
    
    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        match (Optional[extensions.MatchOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'match' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, str]: keys are parsed settings keys (possibly modified based
            on 'excise') and values are the associated terms.
        
    """
    matcher = globals()[f'match_{match}']
    kwargs = {'terms': terms, 'excise': excise, 'divider': divider}
    return {
        matcher(item = k, **kwargs)[0]: matcher(item = k, **kwargs)[1]
        for k in settings.keys() if matcher(item = k, **kwargs)}

def get_sections(
    settings: MutableMapping[str, Any],
    terms: Optional[tuple[str, ...]] = None,
    match: Optional[extensions.MatchOptions] = 'all',
    excise: Optional[bool] = True,
    divider: Optional[str] = '') -> dict[str, dict[str, Any]]:
    """Returns parsed information from a Settings instance.
    
    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        match (Optional[extensions.MatchOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'match' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, dict[str, Any]]: keys are names of sections, and values are 
            matching sections.
        
    """
    matcher = globals()[f'match_{match}']
    kwargs = {'terms': terms, 'excise': excise, 'divider': divider}
    return {
        matcher(item = k, **kwargs)[0]: v for k, v in settings.items() 
        if matcher(item = k, **kwargs)}

def get_section_keys(
    settings: MutableMapping[str, Any],
    terms: Optional[tuple[str, ...]] = None,
    match: Optional[extensions.MatchOptions] = 'all',
    excise: Optional[bool] = True,
    divider: Optional[str] = '') -> dict[str, list[str]]:
    """Returns parsed information from a Settings instance.
    
    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        match (Optional[extensions.MatchOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'match' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, list[str]]: keys are names of sections in 'settings' with any 
            matching keys within them and values are a list of matching keys
            from the corresponding sections. 
        
    """
    kwargs = {
        'terms': terms, 
        'match': match, 
        'excise': excise, 
        'divider': divider}
    matches = {}
    for name, section in settings.items():
        if get_keys(settings = section, **kwargs):
            matches[name] = get_keys(settings = section, **kwargs)
    return matches

def get_section_kinds(
    settings: MutableMapping[str, Any],
    terms: Optional[tuple[str, ...]] = None,
    match: Optional[extensions.MatchOptions] = 'all',
    excise: Optional[bool] = True,
    divider: Optional[str] = '') -> dict[str, dict[str, str]]:
    """Returns parsed information from a Settings instance.
    
    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        match (Optional[extensions.MatchOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'match' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, dict[str, str]]: keys section names and values have parsed 
            settings keys (possibly modified based on 'excise') and values are 
            the associated terms.
        
    """
    kwargs = {
        'terms': terms, 
        'match': match, 
        'excise': excise, 
        'divider': divider}
    matches = {}
    for name, section in settings.items():
        if get_kinds(settings = section, **kwargs):
            matches[name] = get_kinds(settings = section, **kwargs)
    return matches

def match_all(
    item: Any, 
    terms: Sequence[str], 
    excise: Optional[extensions.ExciseOptions] = True,
    divider: Optional[str] = '') -> Optional[tuple[str, str]]:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): divider between a term and the rest of 'item'.
            Defaults to ''.

    Returns:
        Optional[tuple[str, str]]: the matching str and matching term or None 
            (if there is no matching term).
        
    """
    for term in terms:
        if item == term:
            return item, term
    return None

def match_prefix(
    item: Any, 
    terms: Sequence[str], 
    excise: Optional[extensions.ExciseOptions] = True,
    divider: Optional[str] = '') -> Optional[tuple[str, str]]:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): divider between a term and the rest of 'item'.
            Defaults to ''.

    Returns:
        Optional[tuple[str, str]]: the matching str and matching term or None 
            (if there is no matching term).
        
    """
    for term in terms:
        substring = term + divider
        if item.startswith(substring):
            if excise:
                return camina.drop_prefix(item = item, prefix = substring), term
            else:
                return item, term 
    return None

def match_suffix(
    item: Any, 
    terms: Sequence[str],  
    excise: Optional[extensions.ExciseOptions] = True,
    divider: Optional[str] = '') -> Optional[tuple[str, str]]:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): divider between a term and the rest of 'item'.
            Defaults to ''.

    Returns:
        Optional[tuple[str, str]]: the matching str and matching term or None 
            (if there is no matching term).
        
    """
    for term in terms:
        substring = divider + term
        if item.endswith(substring):
            if excise:
                excised_term = camina.drop_suffix_from_str(
                    item = item, 
                    suffix = substring)
                return excised_term, term
            else:
                return item, term 
    return None
