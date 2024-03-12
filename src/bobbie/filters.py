"""Tools for filtering configuration settings.

Contents:
    match: general filtering function.
    match_all: returns a matching str (possibly modified based on arguments) and
        the term which matches by matching the entire str.
    match_prefix: returns a matching str (possibly modified based on arguments)
        and the term which matches by matching a str prefix.
    match_suffix: returns a matching str (possibly modified based on arguments)
        and the term which matches by matching a str suffix.

To Do:


"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import configuration, utilities

if TYPE_CHECKING:
    from collections.abc import Sequence

    from . import extensions

def match(
    item: Any,
    terms: Sequence[str],
    scope: extensions.ScopeOptions | None = 'all',
    excise: extensions.ExciseOptions | None = True,
    divider: str | None = '') -> tuple[str, str] | None:
    """Applies the Parser to 'item'.

    Args:
        item (Any): item to Parser.
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
    excise: extensions.ExciseOptions | None = True,
    divider: str | None = '') -> tuple[str, str] | None:
    """Applies the Parser to 'item'.

    Args:
        item (Any): item to Parser.
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
    excise: extensions.ExciseOptions | None = True,
    divider: str | None = '') -> tuple[str, str] | None:
    """Applies the Parser to 'item'.

    Args:
        item (Any): item to Parser.
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
                return (utilities._drop_prefix_from_str(
                    item = item,
                    prefix = substring),
                        term)
            else:
                return item, term
    return None

def match_suffix(
    item: Any,
    terms: Sequence[str],
    excise: extensions.ExciseOptions | None = True,
    divider: str | None = '') -> tuple[str, str] | None:
    """Applies the Parser to 'item'.

    Args:
        item (Any): item to Parser.
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
                excised_term = utilities._drop_suffix_from_str(
                    item = item,
                    suffix = substring)
                return excised_term, term
            else:
                return item, term
    return None
