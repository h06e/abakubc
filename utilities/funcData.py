from pathlib import Path
import json
from time import perf_counter
from classes import *
import csv
import matplotlib.pyplot as plt
from math import *

def read_campagne(file_name) -> tuple[list, list[dict]]:
    tests = {}
    with open(f'{file_name}.csv', "r") as f:
        reader = csv.reader(f, delimiter=';',)
        header = next(reader)
        for row in reader:
            test_line = {}
            for idx, parameter in enumerate(row):
                test_line[header[idx]] = parameter
            tests[test_line['test_id']] = test_line
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
                data[campagne][test.parent.name] = Test(
                    tests_info[test.parent.name], json.load(f), campagne)
    t_end = perf_counter()
    print(f'Lecture des données réalisée en {t_end-t_start :.5f}s')
    return data


def get_bulk_data(data: dict[dict[Test]]) -> dict[str, Test]:
    """Allow to get bulk data (suppress the campagne name stage)"""
    data_bulk = {}
    for c in data:
        data_bulk |= data[c]
    return data_bulk


def get_best_test(list_of_tests: dict[Test], error_type: tuple = (0, 1)) -> tuple[str, Test]:
    best_test = None
    best_error = 1e8
    for key, test in list_of_tests.items():
        if test.global_err[error_type[0]][error_type[1]] < best_error:
            best_test = (key, test)
            best_error = test.global_err[error_type[0]][error_type[1]]
    return best_test


def get_tests_by_test_id(data, index: int, target: str) -> dict[Test]:
    """ return a dict of test based on the test_id with _ split"""
    new_dict = {}
    for key in data:
        if key.split('_')[index] == target:
            new_dict |= {key: data[key]}
    return new_dict


def get_vect_of_support(cote, cyl) -> np.ndarray:
    if cote in [1, 3]:
        x = 0.55 if cote == 1 else -0.55
        y = cyl/10 - 0.45
    else:
        x = cyl/10 - 0.45
        y = 0.55 if cote == 2 else -0.55
    # print(f'{cote=} {cyl=}')
    # print(f'{[x, y]=}')
    return np.array([x, y])

# ***** Missing supports *****


def get_mean_MS(test: Test) -> float:
    mat_MS = test.get_MS()
    return np.mean(mat_MS)


def get_mean_MS_worse_side(test: Test) -> float:
    mat_MS = test.get_MS()
    return np.max(np.mean(mat_MS, axis=1))


def get_mean_MS_worse_side_pair(test: Test) -> float:
    mat_MS = test.get_MS()
    nb_per_side = np.mean(mat_MS, axis=1)
    return max([nb_per_side[0]+nb_per_side[2], nb_per_side[1]+nb_per_side[3]])


def get_mean_MS_worse_corner(test: Test) -> float:
    mat_MS = test.get_MS()
    mat_MS_corner = test.get_MS_corner()
    return np.max(np.mean(mat_MS_corner, axis=1))


def get_max_MS_consecutive(test: Test) -> float:
    mat_MS = test.get_MS()
    mat_MS = np.array([mat_MS[0, :], mat_MS[1, :], np.flip(
        mat_MS[2, :]), np.flip(mat_MS[3, :])])
    max_con = 0
    current_con = 0
    for i in range(40):
        if mat_MS[(i//4) % 4, i % 10] == 0.0 and i > 40:
            max_con = max([max_con, current_con])
            break
        elif mat_MS[(i//4) % 4, i % 10] == 1.0:
            current_con += 1
        else:
            if current_con != 0.0:
                max_con = max([max_con, current_con])
                current_con = 0
    return max_con


def get_barycentre(test: Test, full_vect=False) -> float:
    skip_cyl = test.skipped_cyl
    barycentre = np.array([0.0, 0.0])
    for i_c,cote in enumerate(skip_cyl):
        for cyl in cote:
            barycentre = barycentre+get_vect_of_support(i_c, cyl)
    r=(barycentre[0]**2 + barycentre[1]**2)**0.5
    theta=atan(barycentre[1]/barycentre[0])
    if full_vect:
        return barycentre,r
    if r!=0.0 and test.get_number_ms()!=0:
        return r
    else:
        return None
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


def plot_box(X, Y):
    X_sorted, Y_sorted = (list(t) for t in zip(*sorted(zip(X, Y))))
    X_bulk, Y_bulk = [], []
    old = None
    for x, y in zip(X_sorted, Y_sorted):
        if x == old:
            Y_bulk[-1].append(y)
        else:
            X_bulk.append(x)
            Y_bulk.append([y])
            print(old)
            old = x
    y_mean = []
    y_q1 = []
    y_q2 = []
    y_min = []
    y_max = []
    for y in Y_bulk:
        y_mean.append(np.mean(np.array(y)))
        y_q1.append(np.quantile(np.array(y), 0.25))
        y_q2.append(np.quantile(np.array(y), 0.75))
        y_min.append(np.min(np.array(y)))
        y_max.append(np.max(np.array(y)))
    y_mean = np.array(y_mean)
    y_q1 = np.array(y_q1)
    y_q2 = np.array(y_q2)
    y_min = np.array(y_min)
    y_max = np.array(y_max)
    plt.errorbar(X_bulk, y_mean,
                 [y_mean-y_q1,
                  y_q2 - y_mean],
                 fmt='b_', lw=3, ms=1, label='[min - Q1 - mean - Q3 - max]')
    plt.errorbar(X_bulk, y_mean,
                 [y_mean-y_min, y_max - y_mean],
                 fmt='b_', ecolor='b', lw=1, capsize=2)
    plt.plot(X_bulk, y_mean, 'b:')

def plot_box2(X, Y, step:float=0.01, width:float=0.2, ylabel:str=''):
    X_sorted, Y_sorted = (list(t) for t in zip(*sorted(zip(X, Y))))
    old = X_sorted[0]
    X_bulk, Y_bulk, number_per_x= [old], [[]], []
    counter=0
    for x, y in zip(X_sorted, Y_sorted):
        if x<old+step:
            Y_bulk[-1].append(y)
            counter+=1
            continue
        number_per_x.append(counter)
        X_bulk.append(x)
        Y_bulk.append([y])
        old = x
        counter=0
    number_per_x.append(counter)
    y_mean = []
    for y in Y_bulk:
        y_mean.append(np.mean(np.array(y)))
    y_mean = np.array(y_mean)

    plt.violinplot(Y_bulk, X_bulk,widths=width,
                   showmeans=False, showmedians=False, showextrema=False)
    plt.plot(X_bulk, y_mean, 'b:')
    plt.xlabel(f'critère {ylabel}')
    plt.ylabel('erreur')
    ax2=plt.twinx()
    ax2.set_ylim(bottom=0, top=1.2*np.max(number_per_x))
    ax2.plot(X_bulk, number_per_x, 'ro')
    ax2.set_ylabel('Number per case', color='r')
    ax2.tick_params(axis='y', colors='red')

if __name__ == '__main__':
    data = read_data_from_campaigns(['campagne_test'])
    data = get_bulk_data(data)
    print('Normale termination')
