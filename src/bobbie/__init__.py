"""Flexible, easy python project configuration"""

from __future__ import annotations

__version__ = '0.1.5'

__author__: str = 'Corey Rayburn Yung'


from .core import Settings
from .extensions import Parser, Parsers
from .filters import match, match_all, match_prefix, match_suffix
from .parsers import (
    get_contents,
    get_keys,
    get_kinds,
    get_section_keys,
    get_section_kinds,
    get_sections,
    parse,
)

__all__: list[str] = [
    "Settings",
    "Parser",
    "Parsers",
    "match",
    "match_all",
    "match_prefix",
    "match_suffix",
    "get_contents",
    "get_keys",
    "get_kinds",
    "get_section_keys",
    "get_section_kinds",
    "get_sections",
    "parse"]


