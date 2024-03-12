"""Additional functionality for Settings class.

Contents:
    Parser: a descriptor for parseing `Settings` data.
    Parsers: a `dict`-like class to store `Parser` instances.
    View: a mixin for `Settings` that can dynamically add parsers to it.

To Do:

"""
from __future__ import annotations

import dataclasses
from collections.abc import Hashable, MutableMapping, Sequence
from typing import Any, Literal

from . import parsers, utilities

_ScopeOptions = Literal['all', 'prefix', 'suffix']
_ReturnsOptions = Literal[
    'contents',
    'keys',
    'kinds',
    'sections',
    'section_keys',
    'section_kinds']


@dataclasses.dataclass
class Parser(object):
    """A descriptor which extracts information from a `Settings` instance.

    Args:
        terms: strings to match against entries in a `Settings` instance.
        scope: how much of the `str `must be matched. Defaults to `all`.'
        returns: the kind of data that should be returned after parsing.
            Defaults to `section`.
        excise: whether to remove the matching terms from keys in the return
            item. Defaults to _MISSING, which means the global setting will be
            used.
        accumulate: whether to return all matching items (True) or just the
            first (False). Defaults to _MISSING, which means the global setting
            will be used.
        divider: when matching a prefix, suffix, or substring,
            `divider` is the str connection that substring with the remainder of
            the str. If `scope` is `all`, `divider` has no effect. Defaults to
            ''.

    """

    terms: tuple[str, ...]
    scope: _ScopeOptions = 'all'
    returns: _ReturnsOptions = 'sections'
    excise: bool = True
    accumulate: bool = True
    divider: str = ''

    """ Dunder Methods """

    def __get__(self, instance: object, kind: type[Any] | None = None) -> Any:
        """Getter for use as a descriptor.

        Args:
            instance: the object which has a Parser instance as a descriptor.
            kind: class of `instance`.

        Returns:
            Any: stored value(s).

        """
        try:
            settings = instance.settings
        except AttributeError:
            settings = instance
        return parsers.parse(settings = settings, parse = self)

    def __set__(self, instance: object, value: Any) -> None:
        """Setter for use as a descriptor.

        Args:
            instance: the object which has a Parser instance as a descriptor.
            value: the value to assign when accessed.

        """
        try:
            settings = instance.settings
        except AttributeError:
            settings = instance
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

    def __set_name__(self, owner: type[Any], name: str) -> None:
        """Stores the attribute name in `owner` of the Parser descriptor.

        Args:
            owner: the class which has a Parser instance as a descriptor.
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


@dataclasses.dataclass
class View(object):
    """A mixin for `Settings`, adding `Parser` descriptors."""

    @classmethod
    def add_parsers(cls, parsers: str | Sequence[str]) -> None:
        """add_parsers _summary_

        Args:
            parsers: _description_

        Returns:
            _description_

        """
        for name in utilities._iterify(parsers):
            parser = Parsers[name]
            setattr(cls, name, parser())
