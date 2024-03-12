"""Supported file format data."""

from __future__ import annotations

import configparser
import contextlib
import copy
import dataclasses
import importlib
import importlib.util
import pathlib
import sys
from collections.abc import (
    Callable,
    Hashable,
    Mapping,
    MutableMapping,
    Sequence,
)
from typing import TYPE_CHECKING, Any


@dataclasses.dataclass
class FileFormat:
    """File format information, loader, and saver.

    Args:
        name : the format name which should match the key when a FileFormat
            instance is stored. 'name' is required so that the automatic
            registration of all FileFormat instances works properly and to
            enable better use by classes that need consistent `str` names for
            file formats.
        module: name of module where the relevant loader and
            saver are located. If 'module' is None, nagata will first look to
            see if 'loader' or 'saver' is attached to the FileFormat instance
            and then check for a function in the 'transfer' module. Defaults to
            None.
        extensions: str file extension(s)
            associated with the format. If more than one is listed, the first
            one is used for saving new files and all will be used for loading.
            Defaults to None.
        loader: if a str, it is the name of the
            loading method in 'module' to use, name of attribute of the loading
            method on the FileFormat instance, or the name of a method in the
            'transfer' module of nagata. Otherwise, it should be a function for
            loading.
        saver: if a str, it is the name of the
            saving method in 'module' to use, name of attribute of the saving
            method on the FileFormat instance, or the name of a method in the
            'transfer' module of nagata. Otherwise, it should be a function for
            saving.


    """

    name: str
    module: str
    extensions: Sequence[str]
    loader: str
