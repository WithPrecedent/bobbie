"""Shared tools

Contents:


To Do:


"""
from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


def _drop_prefix_from_str(item: str, /, prefix: str, divider: str = '') -> str:
    """Drops `prefix` from `item` with `divider` in between.

    Args:
        item (str): item to be modified.
        prefix (str): prefix to be added to `item`.
        divider (str): str to add between `item` and `prefix`. Defaults to '',
            which means no divider will be added.

    Returns:
        str: modified str.

    """
    prefix = ''.join([prefix, divider])
    return item[len(prefix):] if item.startswith(prefix) else item

def _drop_suffix_from_str(item: str, /, suffix: str, divider: str = '') -> str:
    """Drops `suffix` from `item` with `divider` in between.

    Args:
        item (str): item to be modified.
        suffix (str): suffix to be added to 'item'.

    Returns:
        str: modified str.

    """
    suffix = ''.join([suffix, divider])
    return item.removesuffix(suffix) if item.endswith(suffix) else item

def _iterify(item: Any) -> Iterable:
    """Returns `item` as an iterable, but does not iterate str types.

    Args:
        item (Any): item to turn into an iterable

    Returns:
        Iterable: of `item`. A str type will be stored as a single item in an
            Iterable wrapper.

    """
    if item is None:
        return iter(())
    elif isinstance(item, (str, bytes)):
        return iter([item])
    else:
        try:
            return iter(item)
        except TypeError:
            return iter((item,))

def _pathlibify(item: str | pathlib.Path) -> pathlib.Path:
    """Converts string `path` to pathlib.Path object.

    Args:
        item: either a string of a path or a pathlib.Path object.

    Raises:
        TypeError if `path` is neither a str or pathlib.Path type.

    Returns:
        pathlib.Path object.

    """
    if isinstance(item, str):
        return pathlib.Path(item)
    elif isinstance(item, pathlib.Path):
        return item
    else:
        raise TypeError('item must be str or pathlib.Path type')


def _typify(item: str) -> list[Any] | int | float | bool | str:
    """Converts stings to appropriate, supported datatypes.

    The method converts strings to list (if ', ' is present), int, float,
    or bool datatypes based upon the content of the string. If no
    alternative datatype is found, the item is returned in its original
    form.

    Args:
        item (str): string to be converted to appropriate datatype.

    Returns:
        list[Any] | int | float | bool | str: converted item.

    """
    if not isinstance(item, str):
        return item
    try:
        return int(item)
    except ValueError:
        try:
            return float(item)
        except ValueError:
            if item.lower() in {'true', 'yes'}:
                return True
            elif item.lower() in {'false', 'no'}:
                return False
            elif ', ' in item:
                item = item.split(', ')
                return [_typify(i) for i in item]
            else:
                return item
