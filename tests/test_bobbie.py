"""
test_bobbie: tests Settings class
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
    
    
"""
from __future__ import annotations
import pathlib

import bobbie

dict_settings = {
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

def test_settings():
    ini_settings = bobbie.Settings.create(
        item = pathlib.Path('tests') / 'project_settings.ini')
    assert ini_settings['general']['verbose'] is True
    assert isinstance(ini_settings['tasks']['things_to_do'], list)
    assert ini_settings['files']['test_chunk'] == 500
    assert ini_settings['files']['float_format'] == '%.4f'
    py_settings = bobbie.Settings.create(
        item = pathlib.Path('tests') / 'project_settings.py')
    assert py_settings['general']['verbose'] is True
    assert isinstance(py_settings['tasks']['things_to_do'], list)
    assert py_settings['files']['test_chunk'] == 500
    assert py_settings['files']['float_format'] == '%.4f'
    py_settings = bobbie.Settings.create(
        item = pathlib.Path('tests') / 'project_settings.py')
    assert dict_settings['general']['verbose'] is True
    assert isinstance(dict_settings['tasks']['things_to_do'], list)
    assert dict_settings['files']['test_chunk'] == 500
    assert dict_settings['files']['float_format'] == '%.4f'
    return


if __name__ == '__main__':
    test_settings()
    