"""Settings, constants, and global types for `bobbie`.

Contents:


To Do:


"""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import MutableMapping

""" Global Variables """

_ACCUMULATE_MATCHES: bool = True
_EXCISE_MATCHES: bool = True
_FILE_EXTENSIONS: dict[str, str] = {
    'env': 'env',
    'ini': 'ini',
    'json': 'json',
    'toml': 'toml',
    'py': 'module',
    'xml': 'xml',
    'yaml': 'yaml',
    'yml': 'yml'}
_GENERAL_SECTION: str | None = 'general'
_INFER_TYPES: bool = True
_INJECT_GLOBAL: bool = True
_INTERNAL_STORAGE: type[MutableMapping] = dict
_RAISE_ERROR: bool = True
_RECURSIVE_SETTINGS: bool = True


""" Missing Argument Sentinel Class and Instance """

@dataclasses.dataclass
class _MISSING_VALUE(object):  # noqa: N801
    """Sentinel object for a missing data or parameter.

    This follows the same pattern as the `_MISSING_TYPE` class in the builtin
    dataclasses library.
    https://github.com/python/cpython/blob/3.10/Lib/dataclasses.py#L182-L186

    Because None is sometimes a valid argument or data option, this class
    provides an alternative that does not create the confusion that a default of
    None can sometimes lead to.

    """

    pass  # noqa: PIE790


# _MISSING, instance of MISSING_VALUE, should be used for missing values as an
# alternative to None. This provides a fuller repr and traceback.
_MISSING = _MISSING_VALUE()

""" Functions for Changing Global Variables """

def set_global_section(name: str) -> None:
    """Sets the `Settings` section for global settings to `name`.

    Args:
        name: name of section where global settings are stored.

    Raises:
        TypeError: if 'name' is not a `str`.

    """
    if isinstance(name, str):
        globals()['_GLOBAL_SECTION'] = name
    else:
        raise TypeError('name argument must be a str')

def set_nested_settings(nest: bool) -> None:
    """Sets the `Settings` section for global settings to `name`.

    Args:
        nest: whether Settings should automatically create nested instances of
            itself (True) or use ordinary `dict` types (False).

    Raises:
        TypeError: if 'nest' is not a `bool`.

    """
    if isinstance(nest, bool):
        globals()['_NESTED_SETTINGS'] = bool
    else:
        raise TypeError('nest argument must be a boolean')
