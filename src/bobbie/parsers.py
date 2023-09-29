"""Tools for parsing configuration settings

Contents:
    parse: offers different parse of `Settings` data based on arguments passed.
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

To Do:


"""
from __future__ import annotations

from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any

from . import filters

if TYPE_CHECKING:
    from . import core, extensions


def parse(
    settings: core.Settings,
    parse: extensions.parse | None = None,
    terms: tuple[str, ...] | None = None,
    scope: extensions.ScopeOptions | None = 'all',
    returns: extensions.ReturnsOptions | None = 'sections',
    excise: bool | None = True,
    accumulate: bool | None = True,
    divider: str | None = '') -> Any:
    """Returns parse of select information from a `Settings` instance.

    Either 'parse' or 'terms' must not be None. If 'parse' is passed, the 
    rest of the arguments (other than 'settings' and 'parse') are ignored and
    the data in 'parse' is used instead.

    Args:
        settings: a `Settings` or subclass instance with configuration data.
        parse: a `Parser` or subclass instance with data for the other parameters. 
            Defaults to None.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        scope (Optional[extensions.ScopeOptions]): how much of the str must be 
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
            the str. If 'scope' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Raises:
        ValueError: if both 'parse' and 'terms' are None.

    Returns:
        Any: an item parsed from 'settings'.

    """
    # Applies information from 'parse' if it is passed.
    if parse is not None:
        terms = parse.terms
        scope = parse.scope
        returns = parse.returns
        excise = parse.excise
        accumulate = parse.accumulate
        divider = parse.divider
    elif terms is None:
        raise ValueError('Either parse or terms argument must not be None')
    # Determines name of the appropriate function in the this module to use.
    filters.match = globals()[f'get_{returns}']
    # Gets matches based on passed arguments.
    matches = filters.match(
        settings = settings, 
        terms = terms, 
        scope = scope, 
        excise = excise, 
        divider = divider)
    # Returns all matches if 'accumulate' is True. Otherwise, only the first
    # result is returned.
    if accumulate:
        return matches
    elif isinstance(matches, MutableMapping):
        return matches[next(iter(matches.keys()))]
    else:
        return matches[0]
  
def get_contents(
    settings: MutableMapping[str, Any],
    terms: tuple[str, ...] | None = None,
    scope: extensions.ScopeOptions | None = 'all',
    excise: bool | None = True,
    divider: str | None = '') -> dict[str, dict[str, Any]]:
    """Returns parsed information from a Settings instance.

    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        scope (Optional[extensions.ScopeOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'scope' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, dict[str, Any]]: keys are section names of 'settings' and
            values are sections of 'settings'.

    """
    kwargs = {'terms': terms, 'excise': excise, 'divider': divider}
    matches = {}
    for name, section in settings.items():
        if any(filters.match(item = k, **kwargs) for k in section.keys()):
            matches[name] = {
                filters.match(item = k, **kwargs)[0]: v for k, v in section.items() 
                if filters.match(item = k, **kwargs)}
    return matches

def get_keys(
    settings: MutableMapping[str, Any],
    terms: tuple[str, ...] | None = None,
    scope: extensions.ScopeOptions | None = 'all',
    excise: bool | None = True,
    divider: str | None = '') -> list[str]:
    """Returns parsed information from a Settings instance.

    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        scope (Optional[extensions.ScopeOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'scope' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        list[str]: matching keys

    """
    kwargs = {'terms': terms, 'excise': excise, 'divider': divider}
    return [
        filters.match(item = k, **kwargs)[0] for k in settings.keys() 
        if filters.match(item = k, **kwargs)]

def get_kinds(
    settings: MutableMapping[str, Any],
    terms: tuple[str, ...] | None = None,
    scope: extensions.ScopeOptions | None = 'all',
    excise: bool | None = True,
    divider: str | None = '') -> dict[str, str]:
    """Returns parsed information from a Settings instance.

    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        scope (Optional[extensions.ScopeOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'scope' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, str]: keys are parsed settings keys (possibly modified based
            on 'excise') and values are the associated terms.

    """
    kwargs = {'terms': terms, 'excise': excise, 'divider': divider}
    return {
        filters.match(item = k, **kwargs)[0]: filters.match(item = k, **kwargs)[1]
        for k in settings if filters.match(item = k, **kwargs)}

def get_sections(
    settings: MutableMapping[str, Any],
    terms: tuple[str, ...] | None = None,
    scope: extensions.ScopeOptions | None = 'all',
    excise: bool | None = True,
    divider: str | None = '') -> dict[str, dict[str, Any]]:
    """Returns parsed information from a Settings instance.

    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        scope (Optional[extensions.ScopeOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'scope' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, dict[str, Any]]: keys are names of sections, and values are 
            matching sections.

    """
    kwargs = {'terms': terms, 'excise': excise, 'divider': divider}
    return {
        filters.match(item = k, **kwargs)[0]: v for k, v in settings.items() 
        if filters.match(item = k, **kwargs)}

def get_section_keys(
    settings: MutableMapping[str, Any],
    terms: tuple[str, ...] | None = None,
    scope: extensions.ScopeOptions | None = 'all',
    excise: bool | None = True,
    divider: str | None = '') -> dict[str, list[str]]:
    """Returns parsed information from a Settings instance.

    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        scope (Optional[extensions.ScopeOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'scope' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, list[str]]: keys are names of sections in 'settings' with any 
            matching keys within them and values are a list of matching keys
            from the corresponding sections. 

    """
    kwargs = {
        'terms': terms, 
        'scope': scope, 
        'excise': excise, 
        'divider': divider}
    matches = {}
    for name, section in settings.items():
        if get_keys(settings = section, **kwargs):
            matches[name] = get_keys(settings = section, **kwargs)
    return matches

def get_section_kinds(
    settings: MutableMapping[str, Any],
    terms: tuple[str, ...] | None = None,
    scope: extensions.ScopeOptions | None = 'all',
    excise: bool | None = True,
    divider: str | None = '') -> dict[str, dict[str, str]]:
    """Returns parsed information from a Settings instance.

    Args:
        settings (MutableMapping[str, Any]): configuration data.
        terms (Optional[tuple[str, ...]]): strings to match against entries in a 
            Settings instance. Defaults to None.
        scope (Optional[extensions.ScopeOptions]): how much of the str must be 
            matched. Defaults to 'all'.
        excise (Optional[bool]): whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with 'divider', if applicable.
        divider (Optional[str]): when matching a prefix, suffix, or substring,
            'divider' is the str connection that substring with the remainder of
            the str. If 'scope' is 'all', 'divider' has no effect. Defaults to 
            ''.

    Returns:
        dict[str, dict[str, str]]: keys section names and values have parsed 
            settings keys (possibly modified based on 'excise') and values are 
            the associated terms.

    """
    kwargs = {
        'terms': terms, 
        'scope': scope, 
        'excise': excise, 
        'divider': divider}
    matches = {}
    for name, section in settings.items():
        if get_kinds(settings = section, **kwargs):
            matches[name] = get_kinds(settings = section, **kwargs)
    return matches
