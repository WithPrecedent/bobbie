"""Example settings stored in a Python module for testing `bobbie`.

Contents:
    settings: example settings loaded by `Settings.from_module`.

"""

from __future__ import annotations

settings = {
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
