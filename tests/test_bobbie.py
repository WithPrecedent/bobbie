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
        'things_to_do': ['stop', 'drop', 'roll']},
    'tasks_parameters': {
        'start': 'when_ready',
        'end': 'when_done'}}

def test_core():
    ini_settings = bobbie.Settings.create(
        pathlib.Path('tests') / 'project_settings.ini')
    assert ini_settings['general']['verbose'] == True
    assert isinstance(ini_settings['tasks']['things_to_do'], list)
    assert ini_settings['files']['test_chunk'] == 500
    # assert ini_settings['files']['float_format'] == '%.4f'
    py_settings = bobbie.Settings.create(
        pathlib.Path('tests') / 'project_settings.py')
    assert py_settings['general']['verbose'] is True
    assert isinstance(py_settings['tasks']['things_to_do'], list)
    assert py_settings['files']['test_chunk'] == 500
    # assert py_settings['files']['float_format'] == '%.4f'
    py_settings = bobbie.Settings.create(
        pathlib.Path('tests') / 'project_settings.py')
    dict_settings = bobbie.Settings.create(example_settings)
    assert dict_settings['general']['verbose'] is True
    assert isinstance(dict_settings['tasks']['things_to_do'], list)
    assert dict_settings['files']['test_chunk'] == 500
    # assert dict_settings['files']['float_format'] == '%.4f'
    return

if __name__ == '__main__':
    test_core()

