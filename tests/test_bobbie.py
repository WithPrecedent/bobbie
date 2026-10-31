"""Tests Settings and related classes and functions.

Contents:
    FOLDER: folder with the example settings files.
    example_settings: settings that match every file in the tests folder.
    settings: fixture with a fresh `Settings` copy of `example_settings`.
    verify_settings: checks that a `Settings` matches `example_settings`.
    test_version: tests that the package version is set.
    test_create_from_dict: tests creating `Settings` from a `dict`.
    test_create_with_parameters: tests passing `parameters` to `create`.
    test_create_with_unsupported_source: tests `create` with an invalid source.
    test_load_file: tests loading every supported file type.
    test_toml_keyword_arguments: tests passing kwargs to the `toml` parser.
    test_create_from_str_path: tests loading a file from a `str` path.
    test_create_file_with_parameters: tests passing `parameters` with a file.
    test_unsupported_extension: tests loading a file type with no loader.
    test_extension_without_loader: tests a mapped file type with no loader.
    test_module_without_settings: tests a module with no settings variable.
    test_file_encoding: tests the default and chosen file encodings.
    test_missing_file: tests that every loader raises on a missing file.
    test_ini_percent_sign: tests `ini` values that contain "%".
    test_ini_lists_and_dicts: tests `ini` values that are lists and dicts.
    test_keys_items_values: tests the `dict` views.
    test_item_access: tests getting, setting, deleting, length, and iteration.
    test_add: tests adding new and existing sections.
    test_update_and_plus: tests `update` and the "+" and "+=" operators.
    test_delete: tests deleting present and missing keys.
    test_delete_global_option: tests the global default for `delete`.
    test_get: tests `get` with defaults and `setdefault`.
    test_subset: tests `subset` with `include` and `exclude`.
    test_fromkeys: tests `fromkeys`.
    Target: object to inject settings into.
    test_inject: tests injecting settings into an object.
    test_inject_skips_missing_section: tests `inject` with a missing section.
    test_typify_scalars: tests converting strings to scalars.
    test_typify_lists_and_dicts: tests converting strings to lists and dicts.
    test_split_top_level: tests splitting strings outside brackets and quotes.
    test_iterify: tests wrapping items in iterables.
    test_pathlibify: tests converting paths to `pathlib.Path`.

"""

from __future__ import annotations

import copy
import decimal
import pathlib
from typing import Any

import pytest

import bobbie
from bobbie import options, utilities

FOLDER = pathlib.Path('tests')

example_settings = {
    'general': {
        'verbose': True,
        'seed': 43,
        'conserve_memory': True,
        'parallelize': False,
        'gpu': False},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'analysis_format': 'csv',
        'file_encoding': 'windows-1252',
        'test_data': True,
        'test_chunk': 500,
        'random_test_chunk': True,
        'boolean_out': True,
        'export_results': True},
    'tasks': {
        'things_to_do': ['stop', 'drop', 'roll']}}

""" Fixtures and Helpers """


@pytest.fixture
def settings() -> bobbie.Settings:
    """Returns a `Settings` with a copy of `example_settings`.

    The copy keeps tests that change their `Settings` from changing
    `example_settings`.

    Returns:
        A `Settings` instance with a deep copy of `example_settings`.

    """
    return bobbie.Settings.create(copy.deepcopy(example_settings))


def verify_settings(loaded: bobbie.Settings) -> None:
    """Checks that `loaded` matches `example_settings`.

    Args:
        loaded: `Settings` instance to check.

    """
    assert loaded['general']['verbose'] is True
    assert isinstance(loaded['tasks']['things_to_do'], list)
    assert loaded['files']['test_chunk'] == 500
    assert dict(loaded.contents) == example_settings


""" Creation Tests """


def test_version() -> None:
    """Tests that the package version is set."""
    assert bobbie.__version__ == '0.3.2'


def test_create_from_dict() -> None:
    """Tests creating `Settings` from a `dict` in every supported way."""
    verify_settings(bobbie.Settings.create(example_settings))
    verify_settings(bobbie.Settings.from_dict(example_settings))
    verify_settings(bobbie.Settings(example_settings))


def test_create_with_parameters() -> None:
    """Tests that `parameters` are passed to the `Settings` constructor."""
    loaded = bobbie.Settings.create(
        example_settings, parameters = {'name': 'Project Settings'})
    assert loaded.name == 'Project Settings'
    verify_settings(loaded)


def test_create_with_unsupported_source() -> None:
    """Tests that `create` rejects sources that are not a path or mapping."""
    with pytest.raises(TypeError):
        bobbie.Settings.create(42)
    with pytest.raises(TypeError):
        bobbie.Settings.create([example_settings])


""" File Loading Tests """


@pytest.mark.parametrize(
    ('file_name', 'loader'),
    [
        ('project_settings.ini', 'from_ini'),
        ('project_settings.json', 'from_json'),
        ('project_settings.py', 'from_module'),
        ('project_settings.toml', 'from_toml'),
        ('project_settings.yaml', 'from_yaml')])
def test_load_file(file_name: str, loader: str) -> None:
    """Tests loading each supported file type in every supported way.

    Args:
        file_name: name of the settings file in the tests folder.
        loader: name of the `Settings` class method for the file type.

    """
    file_path = FOLDER / file_name
    verify_settings(bobbie.Settings.create(file_path))
    verify_settings(getattr(bobbie.Settings, loader)(file_path))
    verify_settings(bobbie.Settings.from_file(file_path))


def test_toml_keyword_arguments() -> None:
    """Tests that keyword arguments are passed to the `toml` parser."""
    file_path = FOLDER / 'project_settings.toml'
    loaded = bobbie.Settings.create(file_path, parse_float = decimal.Decimal)
    verify_settings(loaded)


def test_create_from_str_path() -> None:
    """Tests that a `str` path is loaded like a `pathlib.Path`."""
    verify_settings(bobbie.Settings.create('tests/project_settings.yaml'))


def test_create_file_with_parameters() -> None:
    """Tests that `parameters` reach `Settings` when loading a file."""
    file_path = FOLDER / 'project_settings.toml'
    loaded = bobbie.Settings.create(
        file_path,
        parameters = {'name': 'Project Settings'},
        parse_float = decimal.Decimal)
    assert loaded.name == 'Project Settings'
    verify_settings(loaded)
    loaded = bobbie.Settings.from_file(
        file_path, parameters = {'default_factory': dict})
    assert loaded.get('missing') == {}
    with pytest.raises(TypeError):
        bobbie.Settings.create(file_path, parameters = {'color': 'red'})


def test_unsupported_extension(tmp_path: pathlib.Path) -> None:
    """Tests that a file type with no loader raises a `TypeError`.

    Args:
        tmp_path: temporary folder from pytest.

    """
    file_path = tmp_path / 'settings.csv'
    file_path.write_text('a,b\n1,2\n')
    with pytest.raises(TypeError):
        bobbie.Settings.create(file_path)


def test_extension_without_loader(
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests that a mapped file type with no loader raises a `TypeError`.

    Args:
        tmp_path: temporary folder from pytest.
        monkeypatch: pytest fixture for changing the global options.

    """
    monkeypatch.setitem(options._FILE_EXTENSIONS, 'conf', 'conf')
    file_path = tmp_path / 'settings.conf'
    file_path.write_text('general.seed = 43\n')
    with pytest.raises(TypeError, match = 'conf file is not supported'):
        bobbie.Settings.create(file_path)


def test_module_without_settings(tmp_path: pathlib.Path) -> None:
    """Tests that a module with no settings variable raises a clear error.

    Args:
        tmp_path: temporary folder from pytest.

    """
    file_path = tmp_path / 'other.py'
    file_path.write_text('config = {"general": {"seed": 43}}\n')
    with pytest.raises(AttributeError, match = 'no variable named settings'):
        bobbie.Settings.create(file_path)


@pytest.mark.parametrize(
    ('file_name', 'text'),
    [
        ('accents.ini', '[general]\nname = café\n'),
        ('accents.json', '{"general": {"name": "café"}}'),
        ('accents.yaml', 'general:\n    name: café\n')])
def test_file_encoding(
        tmp_path: pathlib.Path,
        file_name: str,
        text: str) -> None:
    """Tests that files are read as UTF-8 unless an encoding is passed.

    Args:
        tmp_path: temporary folder from pytest.
        file_name: name of the settings file to write.
        text: contents of the settings file.

    """
    file_path = tmp_path / file_name
    file_path.write_text(text, encoding = 'utf-8')
    loaded = bobbie.Settings.create(file_path)
    assert loaded['general']['name'] == 'café'
    file_path.write_text(text, encoding = 'cp1252')
    loaded = bobbie.Settings.create(file_path, encoding = 'cp1252')
    assert loaded['general']['name'] == 'café'


@pytest.mark.parametrize(
    ('file_name', 'loader'),
    [
        ('missing.ini', 'from_ini'),
        ('missing.json', 'from_json'),
        ('missing.py', 'from_module'),
        ('missing.toml', 'from_toml'),
        ('missing.yaml', 'from_yaml')])
def test_missing_file(
        tmp_path: pathlib.Path,
        file_name: str,
        loader: str) -> None:
    """Tests that every loader raises a `FileNotFoundError` on a missing file.

    Args:
        tmp_path: temporary folder from pytest.
        file_name: name of a file that does not exist.
        loader: name of the `Settings` class method for the file type.

    """
    file_path = tmp_path / file_name
    with pytest.raises(FileNotFoundError):
        getattr(bobbie.Settings, loader)(file_path)
    with pytest.raises(FileNotFoundError):
        bobbie.Settings.create(file_path)


def test_ini_percent_sign(tmp_path: pathlib.Path) -> None:
    """Tests that `ini` values with "%" are not treated as interpolation.

    Args:
        tmp_path: temporary folder from pytest.

    """
    file_path = tmp_path / 'percent.ini'
    file_path.write_text('[files]\nfloat_format = %.4f\nsteps = a, b\n')
    loaded = bobbie.Settings.create(file_path)
    assert loaded['files']['float_format'] == '%.4f'
    assert loaded['files']['steps'] == ['a', 'b']
    assert list(loaded) == ['files']


def test_ini_lists_and_dicts(tmp_path: pathlib.Path) -> None:
    """Tests that `ini` values in brackets become lists and dicts.

    Args:
        tmp_path: temporary folder from pytest.

    """
    file_path = tmp_path / 'containers.ini'
    file_path.write_text(
        '[tasks]\nsteps = [stop, drop, roll]\nsizes = {small: 1, big: 2}\n')
    loaded = bobbie.Settings.create(file_path)
    assert loaded['tasks']['steps'] == ['stop', 'drop', 'roll']
    assert loaded['tasks']['sizes'] == {'small': 1, 'big': 2}


""" Mapping Tests """


def test_keys_items_values(settings: bobbie.Settings) -> None:
    """Tests that the `dict` views match those of the stored `dict`.

    Args:
        settings: `Settings` fixture.

    """
    assert list(settings.keys()) == ['general', 'files', 'tasks']
    assert list(settings) == list(settings.keys())
    assert dict(settings.items()) == example_settings
    assert list(settings.values()) == list(example_settings.values())


def test_item_access(settings: bobbie.Settings) -> None:
    """Tests getting, setting, and deleting items, length, and iteration.

    Args:
        settings: `Settings` fixture.

    """
    assert len(settings) == 3
    assert 'general' in settings
    settings['extra'] = {'a': 1}
    assert settings['extra'] == {'a': 1}
    assert len(settings) == 4
    del settings['extra']
    assert 'extra' not in settings
    with pytest.raises(KeyError):
        settings['extra']


def test_add(settings: bobbie.Settings) -> None:
    """Tests that `add` merges existing sections and creates new ones.

    Args:
        settings: `Settings` fixture.

    """
    settings.add('general', {'seed': 7, 'workers': 4})
    assert settings['general']['seed'] == 7
    assert settings['general']['workers'] == 4
    assert settings['general']['verbose'] is True
    settings.add('new', {'a': 1})
    assert settings['new'] == {'a': 1}


def test_update_and_plus(settings: bobbie.Settings) -> None:
    """Tests `update` and the "+" and "+=" operators, which all use `add`.

    Args:
        settings: `Settings` fixture.

    """
    result = settings.update({'general': {'seed': 7}, 'new': {'a': 1}})
    assert result is settings
    assert settings['general']['seed'] == 7
    assert settings['general']['gpu'] is False
    combined = settings + {'general': {'seed': 8}, 'other': {'b': 2}}
    assert isinstance(combined, bobbie.Settings)
    assert combined is not settings
    assert combined['general']['seed'] == 8
    assert combined['general']['gpu'] is False
    assert combined['other'] == {'b': 2}
    assert settings['general']['seed'] == 7
    assert 'other' not in settings
    original = settings
    settings += {'other': {'b': 2}}
    assert settings is original
    assert settings['other'] == {'b': 2}


def test_delete(settings: bobbie.Settings) -> None:
    """Tests deleting present and missing keys.

    Args:
        settings: `Settings` fixture.

    """
    settings.delete('tasks')
    assert 'tasks' not in settings
    settings.delete('missing')
    with pytest.raises(KeyError):
        settings.delete('missing', return_error = True)


def test_delete_global_option(
        settings: bobbie.Settings,
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests that `delete` reads the global default when it is called.

    Args:
        settings: `Settings` fixture.
        monkeypatch: pytest fixture for changing the global options.

    """
    monkeypatch.setattr(options, '_ALWAYS_RETURN_ERROR', True)
    with pytest.raises(KeyError):
        settings.delete('missing')
    with pytest.raises(KeyError):
        del settings['missing']
    settings.delete('missing', return_error = False)


def test_get(settings: bobbie.Settings) -> None:
    """Tests `get` with a `default` and with `setdefault`.

    Args:
        settings: `Settings` fixture.

    """
    assert settings.get('general') == example_settings['general']
    assert settings.get('missing', 'fallback') == 'fallback'
    with pytest.raises(KeyError):
        settings.get('missing')
    settings.setdefault(list)
    assert settings.get('missing') == []
    settings.setdefault('constant')
    assert settings.get('missing') == 'constant'


def test_subset(settings: bobbie.Settings) -> None:
    """Tests `subset` with `include`, `exclude`, neither, and `returns`.

    Args:
        settings: `Settings` fixture.

    """
    included = settings.subset(include = 'general')
    assert isinstance(included, bobbie.Settings)
    assert list(included) == ['general']
    excluded = settings.subset(exclude = ['files', 'tasks'])
    assert list(excluded) == ['general']
    both = settings.subset(include = ['general', 'files'], exclude = 'files')
    assert list(both) == ['general']
    excluded['general']['seed'] = 0
    included['general']['seed'] = 0
    assert settings['general']['seed'] == 43
    simple = settings.subset(include = 'tasks', returns = 'simple')
    assert simple == {'tasks': {'things_to_do': ['stop', 'drop', 'roll']}}
    assert not isinstance(simple, bobbie.Settings)
    with pytest.raises(ValueError, match = 'include or exclude'):
        settings.subset()


def test_fromkeys() -> None:
    """Tests that `fromkeys` builds a `Settings` like `dict.fromkeys`."""
    loaded = bobbie.Settings.fromkeys(['a', 'b'], 0, name = 'keys')
    assert isinstance(loaded, bobbie.Settings)
    assert dict(loaded.contents) == {'a': 0, 'b': 0}
    assert loaded.name == 'keys'
    assert dict(bobbie.Settings.fromkeys(('a',)).contents) == {'a': None}


""" Injection Tests """


class Target:
    """Object to inject settings into.

    Attributes:
        seed: attribute with an existing value.
        gpu: attribute with no existing value.

    """

    seed: Any = 1
    gpu: Any = None


def test_inject(settings: bobbie.Settings) -> None:
    """Tests injecting chosen sections, with and without overwriting.

    Args:
        settings: `Settings` fixture.

    """
    target = settings.inject(Target(), sections = 'general')
    assert target.seed == 43
    assert target.gpu is False
    assert not hasattr(target, 'source_format')
    target = settings.inject(Target(), sections = 'general', overwrite = False)
    assert target.seed == 1
    assert target.gpu is False
    target = settings.inject(Target())
    assert target.source_format == 'csv'
    assert target.things_to_do == ['stop', 'drop', 'roll']


def test_inject_skips_missing_section(settings: bobbie.Settings) -> None:
    """Tests that `inject` ignores sections that are not in `contents`.

    Args:
        settings: `Settings` fixture.

    """
    target = settings.inject(Target(), sections = ['missing', 'files'])
    assert target.source_format == 'csv'
    assert target.seed == 1


""" Utility Tests """


@pytest.mark.parametrize(
    ('item', 'expected'),
    [
        ('42', 42),
        ('-3', -3),
        ('2.5', 2.5),
        ('true', True),
        ('Yes', True),
        ('FALSE', False),
        ('no', False),
        ('csv', 'csv'),
        ('', ''),
        (7, 7),
        (None, None)])
def test_typify_scalars(item: Any, expected: Any) -> None:
    """Tests converting strings to scalars and passing other types through.

    Args:
        item: value to convert.
        expected: converted value.

    """
    result = utilities._typify(item)
    assert result == expected
    assert type(result) is type(expected)


def test_typify_lists_and_dicts() -> None:
    """Tests converting strings to lists and dicts, including nested ones."""
    typify = utilities._typify
    assert typify('[x, y, z]') == ['x', 'y', 'z']
    assert typify('[1, 2.5, true]') == [1, 2.5, True]
    assert typify('["a, b", \'c\']') == ['a, b', 'c']
    assert typify("['1']") == ['1']
    assert typify('[]') == []
    assert typify('[x, y,]') == ['x', 'y']
    assert typify('[[1, 2], [3]]') == [[1, 2], [3]]
    assert typify('{a: 1, b: [x, y]}') == {'a': 1, 'b': ['x', 'y']}
    assert typify('{"a": {b: no}}') == {'a': {'b': False}}
    assert typify('{url: "http://x.com"}') == {'url': 'http://x.com'}
    assert typify('{}') == {}
    assert typify('{a, b}') == '{a, b}'
    assert typify('[x, y], z') == [['x', 'y'], 'z']
    assert typify("don't, stop") == ["don't", 'stop']
    assert typify('a,b') == 'a,b'
    assert typify('see (a, b)') == 'see (a, b)'
    assert typify('f(x, y)') == 'f(x, y)'
    assert typify('"a, b"') == '"a, b"'
    assert typify('x, (a, b)') == ['x', '(a, b)']
    assert typify('[x, (a, b)]') == ['x', '(a, b)']


def test_split_top_level() -> None:
    """Tests splitting strings outside of brackets and quotes."""
    split = utilities._split_top_level
    assert split('a, [b, c], {d: e}', ',') == ['a', '[b, c]', '{d: e}']
    assert split('a: b: c', ':', maxsplit = 1) == ['a', 'b: c']
    assert split('"a, b", c', ',') == ['"a, b"', 'c']
    assert split('a), b', ',') == ['a)', 'b']
    assert split('', ',') == []


def test_iterify() -> None:
    """Tests wrapping items in iterables without iterating strings."""
    assert list(utilities._iterify(None)) == []
    assert list(utilities._iterify('abc')) == ['abc']
    assert list(utilities._iterify(b'abc')) == [b'abc']
    assert list(utilities._iterify([1, 2])) == [1, 2]
    assert list(utilities._iterify(5)) == [5]


def test_pathlibify() -> None:
    """Tests converting `str` paths and rejecting other types."""
    path = pathlib.Path('tests')
    assert utilities._pathlibify('tests') == path
    assert utilities._pathlibify(path) is path
    with pytest.raises(TypeError):
        utilities._pathlibify(5)  # type: ignore


if __name__ == '__main__':
    pytest.main([__file__])
