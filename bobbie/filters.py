"""
filters: functions for filtering configuration settings
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
    match: general filtering function.
    match_all: returns a matching str (possibly modified based on arguments) and
        the term which matches by matching the entire str.
    match_prefix: returns a matching str (possibly modified based on arguments) 
        and the term which matches by matching a str prefix.
    match_suffix: returns a matching str (possibly modified based on arguments) 
        and the term which matches by matching a str suffix.

ToDo:
       
       
"""
from __future__ import annotations
from collections.abc import Sequence
from typing import Any, Optional, TYPE_CHECKING

import camina

if TYPE_CHECKING:
    from . import extensions
    

def match(
    item: Any, 
    terms: Sequence[str], 
    scope: Optional[extensions.ScopeOptions] = 'all',
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
    matcher = globals()[f'match_{scope}']
    kwargs = {
        'item': item, 
        'terms': terms, 
        'excise': excise, 
        'divider': divider}
    return matcher(**kwargs)
    
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
