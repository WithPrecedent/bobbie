"""Flexible, easy python project configuration.

Contents:
    Settings: loads and stores configuration settings with easy-to-use parser
        and viewers for accessing those settings.

"""

from __future__ import annotations

__version__ = '0.3.2'

__author__: str = 'Corey Rayburn Yung'


from .base import Settings

__all__: list[str] = ['Settings']
