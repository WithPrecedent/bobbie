"""Shared tools for converting and wrapping values.

Contents:
    _PAIR_LENGTH: number of parts in a dict entry and of quotes around a
        quoted string.
    _LIST_SEPARATOR: pattern that separates the items of a list that is not
        in brackets.
    _INLINE_COMMENT: pattern of a comment after a value on a line.
    _SPECIAL_CHARACTERS: characters that require an item in a list or dict
        string to be quoted.

"""

from __future__ import annotations

import pathlib
import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Iterable

# Number of parts in a dict entry (key and value) and quotes around a string.
_PAIR_LENGTH = 2
# A comma followed by whitespace (a space, tab, or line break) separates the
# items of a list that is not in brackets, so a list can span several lines.
_LIST_SEPARATOR = r',\s'
# A "#" with whitespace (or the start of the line) before it and whitespace
# (or the end of the line) after it starts a comment, so a value such as
# "#1f77b4" is kept.
_INLINE_COMMENT = re.compile(r'(?:^|\s)#(?=\s|$).*')
# Characters that split or nest items in a list or dict string.
_SPECIAL_CHARACTERS = frozenset(',:[]{}()\'"')

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
    a comma followed by whitespace (such as a space or a line break) outside
    of brackets and quotes becomes a list. Items in a list or dict are
    converted recursively and may be nested. Quotes around an item in a list
    or dict are removed. If no alternative datatype is found, the item is
    returned in its original form.

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
            elif re.search(_LIST_SEPARATOR, item):
                parts = _split_top_level(item, _LIST_SEPARATOR)
                # A separator that is only inside brackets or quotes (such as
                # '(a, b)') does not split `item`, so it stays a str.
                if parts == [stripped]:
                    return item
                return [_typify(i) for i in parts]
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
    """Splits `item` where `separator` matches, ignoring nested or quoted ones.

    A `separator` inside square brackets, curly braces, parentheses, or quotes
    does not split `item`. A quote only counts if it begins a part, so an
    apostrophe inside a word (such as "don't") does not. Each part has
    surrounding whitespace removed, and empty parts (such as from a trailing
    comma) are dropped.

    Args:
        item: string to split.
        separator: regular expression that matches where to split `item`
            (such as ',' or `_LIST_SEPARATOR`).
        maxsplit: maximum number of splits to make. If it is negative, there
            is no limit. Defaults to -1.

    Returns:
        Parts of `item`.

    """
    pattern = re.compile(separator)
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
                and maxsplit != len(parts)
                and (match := pattern.match(item, index))):
            parts.append(item[start:index])
            index = match.end()
            start = index
            continue
        index += 1
    parts.append(item[start:])
    return [p.strip() for p in parts if p.strip()]


def _stringify(item: Any) -> str:
    """Converts `item` to a string that `_typify` converts back to `item`.

    This is the inverse of `_typify`. A list or tuple becomes a string wrapped
    in square brackets (such as '[x, y, z]') and a dict becomes a string
    wrapped in curly braces (such as '{a: 1, b: 2}'). Items in a list or dict
    are converted with `_stringify_element` and may be nested. A str is
    returned unchanged and any other type is converted with `str`.

    Args:
        item: value to convert to a string.

    Returns:
        String form of `item`.

    """
    if isinstance(item, str):
        return item
    elif isinstance(item, Mapping):
        entries = (
            f'{_stringify_element(k)}: {_stringify_element(v)}'
            for k, v in item.items())
        return '{' + ', '.join(entries) + '}'
    elif isinstance(item, list | tuple):
        return '[' + ', '.join(_stringify_element(i) for i in item) + ']'
    else:
        return str(item)


def _stringify_element(item: Any) -> str:
    """Converts an item in a list or dict to a string.

    This is the inverse of `_typify_element`. A str is wrapped in quotes if
    it is empty, has surrounding whitespace, contains a character in
    `_SPECIAL_CHARACTERS`, or would be converted to another datatype by
    `_typify` (such as '42' or 'true'). Any other type is converted with
    `_stringify`.

    Args:
        item: item in a list or dict to convert to a string.

    Returns:
        String form of `item`.

    """
    if not isinstance(item, str):
        return _stringify(item)
    if (
            item
            and item == item.strip()
            and _SPECIAL_CHARACTERS.isdisjoint(item)
            and _typify(item) == item):
        return item
    quote = '"' if "'" in item else "'"
    return f'{quote}{item}{quote}'


def _strip_inline_comments(item: str) -> str:
    """Removes the comments after values from each line of `item`.

    A comment starts with a "#" that has whitespace (or the start of the line)
    before it and whitespace (or the end of the line) after it, and runs to
    the end of the line. Whitespace left at the end of a line is removed, and
    so is a line that only held a comment.

    Args:
        item: text of a value, which may span several lines.

    Returns:
        `item` without its comments.

    """
    lines = []
    for line in item.split('\n'):
        stripped = _INLINE_COMMENT.sub('', line).rstrip()
        if stripped or not line.strip():
            lines.append(stripped)
    return '\n'.join(lines)
