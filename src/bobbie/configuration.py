"""Settings for `bobbie`.

Contents:


To Do:


"""
from __future__ import annotations

import dataclasses

_GLOBAL_SECTION: str = 'general'


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
        raise TypeError('namer argument must be a callable')
