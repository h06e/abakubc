from pathlib import Path
import json
from time import perf_counter
from classes import *
import csv


def read_campagne(file_name) -> tuple[list,list[dict]]:
    tests = {}
    with open(f'{file_name}.csv', "r") as f:
        reader = csv.reader(f, delimiter=';',)
        header = next(reader)
        for row in reader:
            test_line = {}
            for idx, parameter in enumerate(row):
                test_line[header[idx]] = parameter
            tests[test_line['test_id']]=test_line
    return header, tests


def read_data_from_campaigns(campagnes: list) -> dict[dict[Test]]:
    """Read and save of the tests in the campaign list campagne
    Return a dict organized as data[campagne_name][test_id][XX]"""
    ROOT = Path('.')
    data = {}
    t_start = perf_counter()
    for campagne in campagnes:
        data[campagne] = {}
        _, tests_info = read_campagne(campagne)
        tests = list((ROOT/campagne/'results').glob('**/final_data.json'))
        for test in tests:
            with open(test) as f:
                data[campagne][test.parent.name] = Test(tests_info[test.parent.name], json.load(f), campagne)
    t_end = perf_counter()
    print(f'Lecture des données réalisée en {t_end-t_start :.5f}s')
    return data


def get_bulk_data(data: dict[dict[Test]]) -> dict[str,Test]:
    """Allow to get bulk data (suppress the campagne name stage)"""
    data_bulk = {}
    for c in data:
        data_bulk |= data[c]
    return data_bulk




if __name__ == '__main__':
    data = read_data_from_campaigns(['campagne_test'])
    data = get_bulk_data(data)
    print('Normale termination')
