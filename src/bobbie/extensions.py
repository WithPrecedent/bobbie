"""Additional functionality for Settings class.

Contents:
    Parser: a descriptor for parseing `Settings` data.
    Parsers: a `dict`-like class to store `Parser` instances. It
        can be passed as an argument to `Settings` to automatically add `Parser`
        instances as attributes to `Settings`.

To Do:

"""
from __future__ import annotations

import dataclasses
from collections.abc import Hashable, MutableMapping
from typing import Any, Literal

from . import parses

""" Limited option types for static type checkers """

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
    """A descriptor which supports a different parse of `Settings` data.

    Args:
        terms: strings to match against entries in a
            `Settings` instance.
        scope: how much of the str must be scopeed.
            Defaults to `all`.
        returns: the type of data that should be 
            returned after parsing. Defaults to `section`.
        excise: whether to remove the matching terms from keys
            in the return item. Defaults to True, meaning the terms will be 
            excised from keys along with `divider`, if applicable.
        accumulate: whether to return all matching items (True)
            or just the first (False). Defaults to True.
        divider: when matching a prefix, suffix, or substring,
            `divider` is the str connection that substring with the remainder of
            the str. If `scope` is `all`, `divider` has no effect. Defaults to 
            ''.

    """

    terms: tuple[str, ...]
    scope: ScopeOptions = 'all'
    returns: ReturnsOptions = 'sections'
    excise: bool = True
    accumulate: bool = True
    divider: str = ''

    """ Dunder Methods """

    def __get__(self, obj: object, objtype: type[Any] | None = None) -> Any:
        """Getter for use as a descriptor.

        Args:
            obj: the object which has a Parser instance as a descriptor.
            objtype: object connected to this descriptor.

        Returns:
            Any: stored value(s).

        """
        try:
            settings = obj.settings
        except AttributeError:
            settings = obj
        return parses.parse(settings = settings, parse = self)

    def __set__(self, obj: object, value: Any) -> None:
        """Setter for use as a descriptor.

        Args:
            obj: the object which has a Parser instance as a 
                descriptor.
            value: the value to assign when accessed.

        """
        try:
            settings = obj.settings
        except AttributeError:
            settings = obj
        keys = parses.get_keys(
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

    def __set_name__(self, owner: type[Any], name: str) -> None:
        """Stores the attribute name in `owner` of the Parser descriptor.

        Args:
            owner: the class which has a Parser instance as a 
                descriptor.
            name: the str name of the descriptor.

        """
        self.name = name
        return


@dataclasses.dataclass
class Parsers(MutableMapping):
    """Rules for parsing a Settings instance.

    Args:
        contents: a `dict` for storing configuration options. Defaults to en
            empty `dict`.
        default_factory: default value to return when the `get` method is used. 
            Defaults to an empty dict.

    """

    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Any | None = dict

    """ Instance Methods """

    def validate(self) -> None:
        """Validates types in `contents`.

        Raises:
            TypeError: if not all keys are Hashable or all values are not Parser
                instances.

        """
        if not all(isinstance(k, Hashable) for k in self.contents):
            raise TypeError('All keys in Parsers must be Hashable')
        if not all(isinstance(v, Parser) for v in self.contents.values()):
            raise TypeError('All values in Parsers must be Parser instances')
        return
