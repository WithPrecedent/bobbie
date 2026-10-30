"""Shared tools for converting and wrapping values.

Contents:
    _PAIR_LENGTH: number of parts in a dict entry and of quotes around a
        quoted string.

To Do:


"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Iterable

# Number of parts in a dict entry (key and value) and quotes around a string.
_PAIR_LENGTH = 2

""" Private Functions """


def _iterify(item: Any) -> Iterable[Any]:
    """Returns `item` as an iterable, but does not iterate str types.

    Args:
        item: item to turn into an iterable.

    Returns:
        Iterable of `item`. A `str` or `bytes` type will be stored as a single
            item in an Iterable wrapper, and None becomes an empty iterable.

    """
    if item is None:
        return iter(())
    elif isinstance(item, str | bytes):
        return iter([item])
    else:
        try:
            return iter(cast('Iterable[Any]', item))
        except TypeError:
            return iter((item,))


def _pathlibify(item: str | pathlib.Path) -> pathlib.Path:
    """Converts string `item` to a pathlib.Path object.

    Args:
        item: either a string of a path or a pathlib.Path object.

    Returns:
        pathlib.Path object.

    Raises:
        TypeError: if `item` is neither a str or pathlib.Path type.

    """
    if isinstance(item, str):
        return pathlib.Path(item)
    elif isinstance(item, pathlib.Path):
        return item
    else:
        raise TypeError('item must be str or pathlib.Path type')


def _typify(
        item: str) -> list[Any] | dict[Any, Any] | int | float | bool | str:
    """Converts strings to appropriate, supported datatypes.

    The method converts strings to list, dict, int, float, or bool datatypes
    based upon the content of the string. A string wrapped in square brackets
    (such as '[x, y, z]') becomes a list, a string wrapped in curly braces
    (such as '{a: 1, b: 2}') becomes a dict, and any other string containing
    ', ' becomes a list. Items in a list or dict are converted recursively and
    may be nested. Quotes around an item in a list or dict are removed. If no
    alternative datatype is found, the item is returned in its original form.

    Args:
        item: string to be converted to appropriate datatype.

    Returns:
        Converted item.

    """
    if not isinstance(item, str):
        return item
    try:
        return int(item)
    except ValueError:
        try:
            return float(item)
        except ValueError:
            stripped = item.strip()
            if item.lower() in {'true', 'yes'}:
                return True
            elif item.lower() in {'false', 'no'}:
                return False
            elif stripped.startswith('[') and stripped.endswith(']'):
                return [
                    _typify_element(i)
                    for i in _split_top_level(stripped[1:-1], ',')]
            elif stripped.startswith('{') and stripped.endswith('}'):
                entries = [
                    _split_top_level(e, ':', maxsplit = 1)
                    for e in _split_top_level(stripped[1:-1], ',')]
                if all(len(e) == _PAIR_LENGTH for e in entries):
                    return {
                        _typify_element(k): _typify_element(v)
                        for k, v in entries}
                return item
            elif ', ' in item:
                return [_typify(i) for i in _split_top_level(item, ', ')]
            else:
                return item


def _typify_element(item: str) -> Any:
    """Converts an item from a list or dict string to its datatype.

    Matching single or double quotes around `item` are removed and the
    contents are returned as a str without further conversion. Otherwise,
    `item` is converted with `_typify`.

    Args:
        item: string of one item in a list or dict string.

    Returns:
        Converted item.

    """
    if (
            len(item) >= _PAIR_LENGTH
            and item[0] == item[-1]
            and item[0] in {'"', "'"}):
        return item[1:-1]
    return _typify(item)


def _split_top_level(
        item: str,
        separator: str,
        maxsplit: int = -1) -> list[str]:
    """Splits `item` on `separator`, ignoring nested or quoted separators.

    A `separator` inside square brackets, curly braces, parentheses, or quotes
    does not split `item`. A quote only counts if it begins a part, so an
    apostrophe inside a word (such as "don't") does not. Each part has
    surrounding whitespace removed, and empty parts (such as from a trailing
    comma) are dropped.

    Args:
        item: string to split.
        separator: substring to split `item` on.
        maxsplit: maximum number of splits to make. If it is negative, there
            is no limit. Defaults to -1.

    Returns:
        Parts of `item`.

    """
    parts: list[str] = []
    depth = 0
    quote = None
    start = 0
    index = 0
    while index < len(item):
        character = item[index]
        if quote:
            if character == quote:
                quote = None
        elif character in {'"', "'"} and not item[start:index].strip():
            quote = character
        elif character in '[{(':
            depth += 1
        elif character in ']})':
            depth = max(depth - 1, 0)
        elif (
                depth == 0
                and item.startswith(separator, index)
                and maxsplit != len(parts)):
            parts.append(item[start:index])
            index += len(separator)
            start = index
            continue
        index += 1
    parts.append(item[start:])
    return [p.strip() for p in parts if p.strip()]
