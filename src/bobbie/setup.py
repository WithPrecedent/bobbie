"""Settings, constants, and global types for `bobbie`.

Contents:


To Do:


"""
from __future__ import annotations

import dataclasses
from collections.abc import Hashable, MutableMapping
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    from collections.abc import Callable

from . import utilities

""" Types """

GenericDict: TypeAlias = MutableMapping[Hashable, Any]

""" Global Variables """

_CREATOR_METHOD: Callable[[str], str] = lambda x: f'from_{x}'
_FILE_EXTENSIONS: dict[str, str] = {
    'env': 'env',
    'ini': 'ini',
    'json': 'json',
    'toml': 'toml',
    'py': 'module',
    'xml': 'xml',
    'yaml': 'yaml',
    'yml': 'yaml'}
_INFER_TYPES: dict[str, bool] = {
    'env': True,
    'ini': True,
    'json': True,
    'toml': False,
    'module': False,
    'xml': True,
    'yaml': False}
_LOAD_FUNCTION: Callable[[str], str] = lambda x: f'{x}_to_dict'
_MODULE_SETTINGS_ATTRIBUTE: str = 'settings'
_OVERWRITE_ATTRIBUTES: bool = True
_RECURSIVE_SETTINGS: bool = True
_TYPER: Callable[[Any], Any] = utilities._typify

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
