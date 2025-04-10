"""Tests Settings and related classes and functions."""

from __future__ import annotations
import pathlib

import bobbie

example_settings = {
    'general': {
        'verbose': True,
        'seed': 43,
        'conserve_memory': False,
        'parallelize': False,
        'gpu': False},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'analysis_format': 'csv',
        'file_encoding': 'windows-1252',
        'float_format': '%.4f',
        'test_data': True,
        'test_chunk': 500,
        'random_test_chunk': True,
        'boolean_out': True,
        'export_results': True},
    'tasks': {
        'things_to_do': ['stop', 'drop', 'roll']}}

def test_settings(settings: bobbie.Settings) -> None:
    assert settings['general']['verbose'] == True
    assert isinstance(settings['tasks']['things_to_do'], list)
    assert settings['files']['test_chunk'] == 500
    assert settings.contents == example_settings
    return

def test_dict() -> None:
    settings = bobbie.Settings.create(example_settings)
    test_settings(settings)
    settings = bobbie.Settings.from_dict(example_settings)
    test_settings(settings)
    settings = bobbie.Settings(example_settings)
    test_settings(settings)
    return

def test_ini() -> None:
    file_path = pathlib.Path('tests') / 'project_settings.ini'
    settings = bobbie.Settings.create(file_path)
    test_settings(settings)
    settings = bobbie.Settings.from_ini(file_path)
    test_settings(settings)
    settings = bobbie.Settings.from_file(file_path)
    test_settings(settings)
    return

def test_py() -> None:
    file_path = pathlib.Path('tests') / 'project_settings.py'
    settings = bobbie.Settings.create(file_path)
    test_settings(settings)
    settings = bobbie.Settings.from_py(file_path)
    test_settings(settings)
    settings = bobbie.Settings.from_file(file_path)
    test_settings(settings)
    return

def test_toml() -> None:
    file_path = pathlib.Path('tests') / 'project_settings.toml'
    settings = bobbie.Settings.create(file_path)
    test_settings(settings)
    settings = bobbie.Settings.from_toml(file_path)
    test_settings(settings)
    settings = bobbie.Settings.from_file(file_path)
    test_settings(settings)
    return

def test_yaml() -> None:
    file_path = pathlib.Path('tests') / 'project_settings.yaml'
    settings = bobbie.Settings.create(file_path)
    test_settings(settings)
    settings = bobbie.Settings.from_yaml(file_path)
    test_settings(settings)
    settings = bobbie.Settings.from_file(file_path)
    test_settings(settings)
    return

if __name__ == '__main__':
    test_ini()
    test_dict()
    test_py()
    test_yaml()

