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

example_Parsers = {
    'files': bobbie.Parser(
        terms = ('filer', 'files', 'clerk'),
        scope = 'all',
        returns = 'sections',
        excise = False,
        accumulate = False,
        divider = ''),
    'general': bobbie.Parser(
        terms = ('general',),
        scope = 'all',
        returns = 'sections',
        excise = False,
        accumulate = False,
        divider = ''),
    'parameters': bobbie.Parser(
        terms = ('parameters',),
        scope = 'suffix',
        returns = 'sections',
        excise = True,
        accumulate = True,
        divider = '_'),
    'formats': bobbie.Parser(
        terms = ('format',),
        scope = 'suffix',
        returns = 'contents',
        excise = True,
        accumulate = True,
        divider = '_'),
    'kinds': bobbie.Parser(
        terms = ('format', 'chunk', 'out', 'memory'),
        scope = 'suffix',
        returns = 'section_kinds',
        excise = True,
        accumulate = True,
        divider = '_'),
    'format_keys': bobbie.Parser(
        terms = ('format',),
        scope = 'suffix',
        returns = 'section_keys',
        excise = True,
        accumulate = True,
        divider = '_'),
    'key_test': bobbie.Parser(
        terms = ('general', 'files'),
        scope = 'all',
        returns = 'keys',
        excise = False,
        accumulate = True,
        divider = ''),
    'prefix_test': bobbie.Parser(
        terms = ('test', 'final'),
        scope = 'prefix',
        returns = 'section_keys',
        excise = False,
        accumulate = True,
        divider = '_')}

def test_core():
    ini_settings = bobbie.Settings.create(
        pathlib.Path('tests') / 'project_settings.ini')
    assert ini_settings['general']['verbose'] is True
    assert isinstance(ini_settings['tasks']['things_to_do'], list)
    assert ini_settings['files']['test_chunk'] == 500
    assert ini_settings['files']['float_format'] == '%.4f'
    py_settings = bobbie.Settings.create(
        pathlib.Path('tests') / 'project_settings.py')
    assert py_settings['general']['verbose'] is True
    assert isinstance(py_settings['tasks']['things_to_do'], list)
    assert py_settings['files']['test_chunk'] == 500
    assert py_settings['files']['float_format'] == '%.4f'
    py_settings = bobbie.Settings.create(
        pathlib.Path('tests') / 'project_settings.py')
    dict_settings = bobbie.Settings.create(example_settings)
    assert dict_settings['general']['verbose'] is True
    assert isinstance(dict_settings['tasks']['things_to_do'], list)
    assert dict_settings['files']['test_chunk'] == 500
    assert dict_settings['files']['float_format'] == '%.4f'
    return

def test_parsers():
    settings = bobbie.Settings.create(
        example_settings,
        Parsers = example_Parsers)
    assert settings.parameters == {
        'tasks': {
            'start': 'when_ready',
            'end': 'when_done'}}
    assert settings.files == {
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
        'export_results': True}
    assert settings.general == {
        'verbose': True,
        'seed': 43,
        'conserve_memory': False,
        'parallelize': False,
        'gpu': False}
    assert settings.formats == {
        'files': {
            'source': 'csv',
            'interim': 'csv',
            'final': 'csv',
            'analysis': 'csv',
            'float': '%.4f'}}
    assert settings.kinds == {
        'general': {'conserve': 'memory'},
        'files': {
            'source': 'format',
            'interim': 'format',
            'final': 'format',
            'analysis': 'format',
            'float': 'format',
            'test': 'chunk',
            'random_test': 'chunk',
            'boolean': 'out'}}
    assert settings.format_keys == {
        'files': ['source', 'interim', 'final', 'analysis', 'float']}
    assert settings.key_test == ['general', 'files']
    assert settings.prefix_test == {
        'files': ['final_format', 'test_data', 'test_chunk']}
    return

if __name__ == '__main__':
    test_core()
    test_parsers()

