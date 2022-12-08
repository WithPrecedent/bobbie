"""
workshop: helper functions and utilities
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
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING

import camina

if TYPE_CHECKING:
    from . import core


def accumulate_outer_sections(
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
    keys = get_matching_outer_keys(
        settings = settings, 
        terms = terms, 
        match = match)
    return {k: settings[k] for k in keys}

def accumulate_outer_section_contents(
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
    keys = get_matching_outer_keys(
        settings = settings, 
        terms = terms, 
        match = match)
    relevant = {}
    for key in keys:
        relevant.update(settings[key])
    return relevant

def get_matching_all_keys(
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
    matches = get_matching_outer_keys(
        settings = settings, 
        terms = terms, 
        match = match)
    matches.extend(get_matching_inner_keys(
        settings = settings, 
        terms = terms, 
        match = match))
    return matches

def get_matching_inner_keys(
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
            get_matching_outer_keys(
                settings = section, 
                terms = terms, 
                match = match))
    return matches

def get_matching_outer_keys(
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

def get_matching_section_keys(
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
            get_matching_outer_keys(
                settings = section, 
                terms = terms, 
                match = match))
    return matches

def match_complete(item: Any, terms: Sequence[str]) -> bool:
    """Applies the parser to 'item'.

    Args:
        item (Any): item to parse.
        terms (Sequence[str]): strings to find matches for.

    Returns:
        bool: the matching term or None (if there is no matching term).
        
    """
    return any(item == t for t in camina.terms)

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
    prefixes = [t + divider for t in terms]
    return any(item.startswith(p) for p in prefixes)

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
    suffixes = [divider + t for t in terms]
    return any(item.endswith(p) for p in suffixes)
