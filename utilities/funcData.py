from pathlib import Path
import json
from time import perf_counter
from classes import *
import csv
import matplotlib.pyplot as plt
from math import *

def read_campagne(file_name) -> tuple[list, list[dict]]:
    ROOT = Path('.').absolute().parent
    tests = {}
    with open(ROOT/f'{file_name}.csv', "r") as f:
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
    ROOT = Path('.').absolute().parent
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


def get_best_test(dict_of_tests: dict[Test], eoi: tuple = (0, 3), number:int=1) -> tuple[str, Test]:
    dic={}
    for _,test in dict_of_tests.items():
        dic |= {test:test.global_err[eoi[0]][eoi[1]]}
    s={k:v for k,v in sorted(dic.items(), key=lambda item: item[1])}
    final=[]
    for t in s:
        final.append(t)
    return final[:number]

def get_worse_test(dict_of_tests: dict[Test], eoi: tuple = (0, 3), number:int=1) -> tuple[str, Test]:
    dic={}
    for _,test in dict_of_tests.items():
        dic |= {test:test.global_err[eoi[0]][eoi[1]]}
    s={k:v for k,v in sorted(dic.items(), key=lambda item: item[1])}
    final=[]
    for t in s:
        final.append(t)
    final.reverse()
    return final[:number]


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
    return np.max(2*np.sum(mat_MS_corner, axis=1))/(np.sum(mat_MS))


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
    return max_con*test.get_number_ms()


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
    plt.figure()
    plt.violinplot(Y_bulk, X_bulk,widths=width,
                   showmeans=False, showmedians=False, showextrema=True)
    plt.plot(X_bulk, y_mean, 'b:')
    plt.xlabel(ylabel)
    plt.ylabel('erreur')
    ax2=plt.twinx()
    ax2.set_ylim(bottom=0, top=1.2*np.max(number_per_x))
    ax2.plot(X_bulk, number_per_x, 'ro')
    ax2.set_ylabel('Number per case', color='r')
    ax2.tick_params(axis='y', colors='red')
    plt.tight_layout()
    plt.show()



# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 


def plot_map_theta_size(data:dict[Test],data_size:tuple, eoi:tuple, angle_max:float, ymax:float, loop=False) -> None:
    """N_theta, N_scale, N_tx, N_ty = data_size"""
    N_theta, N_scale, N_tx, N_ty = data_size
  
    error_per_angle = np.empty((N_theta+1*loop, N_scale, N_tx, N_ty))
    error_per_angle[:] = np.nan
    for test_id, test in data.items():
        scale, angle, idx, idy = tuple(map(int, test_id.split('_')[1:]))
        error_per_angle[angle, scale-7, idx,
                        idy] = test.global_err[eoi[0]][eoi[1]]
        if angle == 0 and loop:
            error_per_angle[-1, scale-7, idx,
                            idy] = test.global_err[eoi[0]][eoi[1]]

    error_per_angle_mean = np.nanmean(error_per_angle, axis=(2, 3))
    error_per_angle_q1 = np.nanquantile(error_per_angle, 0.25, axis=(2, 3))
    error_per_angle_q2 = np.nanquantile(error_per_angle, 0.75, axis=(2, 3))
    error_per_angle_min = np.nanmin(error_per_angle, axis=(2, 3))
    error_per_angle_max = np.nanmax(error_per_angle, axis=(2, 3))

    plt.figure(figsize=(12, 4))
    if loop:
        x = np.linspace(0, N_theta, N_theta+1)-0.5+1/(N_theta)
    else:
        x = np.linspace(0, N_theta-1, N_theta)-0.5+0.5/(N_scale)
    col = ['b', 'g', 'r', 'm', 'k', 'c', 'y']
    leg = [f'{i}/10 scale' for i in range(7, 14)]

    for scale in range(N_scale):
        plt.errorbar(x+scale/N_scale, error_per_angle_mean[:, scale], [error_per_angle_mean[:, scale]-error_per_angle_q1[:, scale], error_per_angle_q2[:, scale] - error_per_angle_mean[:, scale]],
                    fmt=col[scale]+'_', lw=3, ms=1, label=f'{leg[scale]}')
        plt.errorbar(x+scale/N_scale, error_per_angle_mean[:, scale], [error_per_angle_mean[:, scale]-error_per_angle_min[:, scale], error_per_angle_max[:, scale] - error_per_angle_mean[:, scale]],
                    fmt='_'+col[scale], ecolor=col[scale], lw=1, capsize=2)
        for i, m in enumerate(error_per_angle_max[:, scale]):
            if m > ymax:
                plt.text(x[i]+scale/N_scale,
                        ymax*1.02, f'{m:.0f}', ha='center', fontsize=8)

    for i in range(N_theta-1+1*loop):
        plt.axvline(x=i+0.5, color='k', ls='--', lw=1.0)

    plt.ylim((0, ymax))
    plt.xlim((-0.5, N_theta-1+1*loop+0.5))
    if loop:
        plt.xticks(range(N_theta+1), [f'{angle_max/N_theta*i:.1f}°' for i in range(N_theta+1)])
    else:
        plt.xticks(range(N_theta), [f'{angle_max/(N_theta-1)*i:.1f}°' for i in range(N_theta)])
    plt.legend()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel('Angle [°]')
    plt.ylabel(f'Error distribution [%]')
    plt.tight_layout()
    # plt.show()




def plot_coef_matrix_per_angle(data:dict[Test], data_size:tuple, angle_max:float)-> None:
    N_theta, N_scale, N_tx, N_ty = data_size

    data_per_angle = np.empty((N_theta+1, N_tx, N_ty, 3, 3)) # 3x3 stiffness matrix
    data_per_angle[:] = np.nan
    data_per_angle_KUBC = np.empty((N_theta+1, N_tx, N_ty, 3, 3)) # 3x3 stiffness matrix
    data_per_angle_KUBC[:] = np.nan
    for test_id, test in data.items():
        _, angle, idx, idy = tuple(map(int, test_id.split('_')[1:]))
        data_per_angle[angle, idx,
                    idy, :, :] = np.array(test.K_panto_dic)
        data_per_angle_KUBC[angle, idx,
                    idy, :, :] = np.array(test.K_plane_stress_KUBC)
        if angle == 0:  # Periodicite à 30°
            data_per_angle[-1, idx,
                        idy, :, :] = np.array(test.K_panto_dic)
            data_per_angle_KUBC[-1, idx,
                        idy, :, :] = np.array(test.K_plane_stress_KUBC)

    data_per_angle_mean = np.nanmean(data_per_angle, axis=(1, 2))
    data_per_angle_q1 = np.nanquantile(data_per_angle, 0.25, axis=(1, 2))
    data_per_angle_q2 = np.nanquantile(data_per_angle, 0.75, axis=(1, 2))
    data_per_angle_min = np.nanmin(data_per_angle, axis=(1, 2))
    data_per_angle_max = np.nanmax(data_per_angle, axis=(1, 2))

    data_per_angle_KUBC_mean = np.nanmean(data_per_angle_KUBC, axis=(1, 2))
    data_per_angle_KUBC_q1 = np.nanquantile(data_per_angle_KUBC, 0.25, axis=(1, 2))
    data_per_angle_KUBC_q2 = np.nanquantile(data_per_angle_KUBC, 0.75, axis=(1, 2))
    data_per_angle_KUBC_min = np.nanmin(data_per_angle_KUBC, axis=(1, 2))
    data_per_angle_KUBC_max = np.nanmax(data_per_angle_KUBC, axis=(1, 2))


    coefs = ((0, 0), (0, 1), (2, 2))
    leg = ('K11', 'K12', 'K33')
    col = ['b', 'r', 'g', 'm']
    plt.figure(figsize=(5,3))
    x = np.linspace(0, angle_max, N_theta+1)
    for idx, coef in enumerate(coefs):
        plt.errorbar(x-0.25, data_per_angle_mean[:, coef[0], coef[1]], [data_per_angle_mean[:, coef[0], coef[1]]-data_per_angle_q1[:, coef[0], coef[1]], data_per_angle_q2[:, coef[0], coef[1]] - data_per_angle_mean[:, coef[0], coef[1]]],
                    fmt=col[idx]+'_', lw=3, ms=1, label=f'{leg[idx]}')
        plt.errorbar(x-0.25, data_per_angle_mean[:, coef[0], coef[1]], [data_per_angle_mean[:, coef[0], coef[1]]-data_per_angle_min[:, coef[0], coef[1]], data_per_angle_max[:, coef[0], coef[1]] - data_per_angle_mean[:, coef[0], coef[1]]],
                    fmt=col[idx]+'_', ecolor=col[idx], lw=1, capsize=2)
        
        plt.errorbar(x+0.25, data_per_angle_KUBC_mean[:, coef[0], coef[1]], [data_per_angle_KUBC_mean[:, coef[0], coef[1]]-data_per_angle_KUBC_q1[:, coef[0], coef[1]], data_per_angle_KUBC_q2[:, coef[0], coef[1]] - data_per_angle_KUBC_mean[:, coef[0], coef[1]]],
                    fmt='k_', lw=3, ms=1, label=f'{leg[idx]} KUBC')
        plt.errorbar(x+0.25, data_per_angle_KUBC_mean[:, coef[0], coef[1]], [data_per_angle_KUBC_mean[:, coef[0], coef[1]]-data_per_angle_KUBC_min[:, coef[0], coef[1]], data_per_angle_KUBC_max[:, coef[0], coef[1]] - data_per_angle_KUBC_mean[:, coef[0], coef[1]]],
                    fmt='k_', ecolor='k', lw=1, capsize=2)

    xx = np.linspace(0, angle_max, 200)
    K_list = []
    test=data[ next((k for k in data
                        if k.split('_')[2] == '0'), None)]
    K_th = test.K_plane_stress_PBC
    for x in xx:
        angle = x*pi/180
        c, s = cos(angle), sin(angle)
        T = np.array([[c**2, s**2, c*s],
                    [s**2, c**2, -c*s],
                    [-2*s*c, 2*c*s, (c**2-s**2)]])
        K = np.dot(np.dot(np.transpose(T), K_th), T)
        K_list.append(K)
    K_list = np.array(K_list)
    sty = [':', '--', '-.', '-.']
    for idx, coef in enumerate(coefs):
        plt.plot(xx, K_list[:, coef[0], coef[1]],
                'k'+sty[idx], label=f'PBC {leg[idx]}')

    plt.grid()
    plt.legend()
    plt.xlabel('Angle [°]')
    plt.ylabel('Stiffness [MPa]')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()




# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

if __name__ == '__main__':
    data = read_data_from_campaigns(['campagne_test'])
    data = get_bulk_data(data)
    print('Normale termination')
