"""Tests Settings and related classes and functions."""

from __future__ import annotations
import pathlib

import pytest

import bobbie

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

def verify_settings(settings: bobbie.Settings) -> None:
    assert settings['general']['verbose'] == True
    assert isinstance(settings['tasks']['things_to_do'], list)
    assert settings['files']['test_chunk'] == 500
    assert dict(settings.contents) == dict(example_settings)
    return

def test_dict() -> None:
    settings = bobbie.Settings.create(example_settings)
    verify_settings(settings)
    settings = bobbie.Settings.from_dict(example_settings)
    verify_settings(settings)
    settings = bobbie.Settings(example_settings) # type: ignore
    verify_settings(settings)
    return

def test_ini() -> None:
    file_path = pathlib.Path('tests') / 'project_settings.ini'
    settings = bobbie.Settings.create(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_ini(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_file(file_path)
    verify_settings(settings)
    return

def test_json() -> None:
    file_path = pathlib.Path('tests') / 'project_settings.json'
    settings = bobbie.Settings.create(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_json(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_file(file_path)
    verify_settings(settings)
    return

def test_py() -> None:
    file_path = pathlib.Path('tests') / 'project_settings.py'
    settings = bobbie.Settings.create(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_module(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_file(file_path)
    verify_settings(settings)
    return

def test_toml() -> None:
    file_path = pathlib.Path('tests') / 'project_settings.toml'
    settings = bobbie.Settings.create(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_toml(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_file(file_path)
    verify_settings(settings)
    return

def test_yaml() -> None:
    file_path = pathlib.Path('tests') / 'project_settings.yaml'
    settings = bobbie.Settings.create(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_yaml(file_path)
    verify_settings(settings)
    settings = bobbie.Settings.from_file(file_path)
    verify_settings(settings)
    return

def test_ini_percent_sign(tmp_path: pathlib.Path) -> None:
    file_path = tmp_path / 'percent.ini'
    file_path.write_text('[files]\nfloat_format = %.4f\nsteps = a, b\n')
    settings = bobbie.Settings.create(file_path)
    assert settings['files']['float_format'] == '%.4f'
    assert settings['files']['steps'] == ['a', 'b']
    assert list(settings) == ['files']

def test_ini_missing_file(tmp_path: pathlib.Path) -> None:
    with pytest.raises(FileNotFoundError):
        bobbie.Settings.from_ini(tmp_path / 'missing.ini')
    with pytest.raises(FileNotFoundError):
        bobbie.Settings.create(tmp_path / 'missing.ini')

def test_keys_items_values() -> None:
    settings = bobbie.Settings.create(example_settings)
    assert list(settings.keys()) == ['general', 'files', 'tasks']
    assert list(settings) == list(settings.keys())
    assert dict(settings.items()) == example_settings
    assert list(settings.values()) == list(example_settings.values())

def test_inject() -> None:
    class Target:
        seed = 1
        gpu = None

    settings = bobbie.Settings.create(example_settings)
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

if __name__ == '__main__':
    test_ini()
    test_dict()
    test_json()
    test_py()
    test_toml()
    test_yaml()
    test_inject()
