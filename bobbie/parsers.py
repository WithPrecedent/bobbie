"""
parsers: base class for configuring projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Contents:
    Settings (camina.Dictionary, ashford.SourceFactory): stores configuration 
        settings after either loading them from disk or by the passed arguments.

ToDo:
       
       
"""
from __future__ import annotations
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
import configparser
import contextlib
import dataclasses
import importlib
import importlib.util
import pathlib
from typing import Any, ClassVar, Optional, Type, Union

import ashford
import camina

from . import core


