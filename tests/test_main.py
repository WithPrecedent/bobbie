"""Main file for unit tests.

Tests created using sourcery.ai.

"""

from __future__ import annotations

import pytest
import pathlib
from bobbie.core import Settings, _validate_source
from collections.abc import MutableMapping

# Test IDs for parametrization
HAPPY_PATH_ID = "happy_path"
EDGE_CASE_ID = "edge_case"
ERROR_CASE_ID = "error_case"

# Happy path tests with various realistic test values
@pytest.mark.parametrize("test_id, source, parameters, parsers, kwargs, expected", [
    (HAPPY_PATH_ID, {"key": "value"}, None, None, {}, {"key": "value"}),
    (HAPPY_PATH_ID, pathlib.Path("/path/to/settings.ini"), None, None, {}, Settings.from_ini),
    # Add more test cases with different file types and realistic values
], ids=lambda test_id: test_id)
def test_create_settings_happy_path(test_id, source, parameters, parsers, kwargs, expected):
    # Act
    settings = Settings.create(source, parameters, parsers, **kwargs)

    # Assert
    assert isinstance(settings, Settings)
    if isinstance(expected, MutableMapping):
        assert settings.contents == expected
    else:
        assert isinstance(settings, expected)

# Edge cases
@pytest.mark.parametrize("test_id, source, parameters, parsers, kwargs, expected", [
    (EDGE_CASE_ID, {}, None, None, {}, {}),
    # Add more edge cases as needed
], ids=lambda test_id: test_id)
def test_create_settings_edge_cases(test_id, source, parameters, parsers, kwargs, expected):
    # Act
    settings = Settings.create(source, parameters, parsers, **kwargs)

    # Assert
    assert settings.contents == expected

# Error cases
@pytest.mark.parametrize("test_id, source, parameters, parsers, kwargs, exception", [
    (ERROR_CASE_ID, None, None, None, {}, TypeError),
    (ERROR_CASE_ID, 123, None, None, {}, TypeError),
    # Add more error cases as needed
], ids=lambda test_id: test_id)
def test_create_settings_error_cases(test_id, source, parameters, parsers, kwargs, exception):
    # Act / Assert
    with pytest.raises(exception):
        Settings.create(source, parameters, parsers, **kwargs)

# Test _validate_source function
@pytest.mark.parametrize("test_id, source, kind, exception", [
    (HAPPY_PATH_ID, "string", str, None),
    (HAPPY_PATH_ID, pathlib.Path("/path/to/file"), pathlib.Path, None),
    (ERROR_CASE_ID, 123, str, TypeError),
    # Add more test cases for different types and expected outcomes
], ids=lambda test_id: test_id)
def test_validate_source(test_id, source, kind, exception):
    if exception:
        # Act / Assert
        with pytest.raises(exception):
            _validate_source(source, kind)
    else:
        # Act
        result = _validate_source(source, kind)

        # Assert
        assert result == source

# Note: Additional tests should be created for each method in the Settings class
# to achieve 100% line and branch coverage. This includes testing methods like
# from_dict, from_path, add, delete, inject, items, keys, subset, values, and
# all dunder methods. Each method should be tested with a variety of inputs to
# cover all branches and lines of code.

