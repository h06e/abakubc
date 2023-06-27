import sys

try:
    sys.path.append("../src")
except:
    pass
from post_compute import post_reader
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import os
from func import manipulation
from post_compute import operation
from post_compute.post_config import *
import os
import matplotlib.cbook as cbook
import json
from math import sqrt, cos, sin, pi
from constants import *
import time



def get_job_name_PBC_KUBC(test):
    """see KUBC and PBC func, job name cannot contain . char (Abq requirement)
    So i convert the . into %. I also remove () and <space>"""
    t = test.copy()

    KUBC_name ='KUBC_'+'_'.join([str(t[i]) for i in ['sample_name', 'geo_parameters', 'mat', 'trans_rot']]).replace('.', '%')
    for char in ['(', ')', ' ']:
        KUBC_name = KUBC_name.replace(char, '')
    PBC_name = 'PBC_' + \
        '_'.join([str(t[i]) for i in ['sample_name',
                                         'geo_parameters', 'mat']]).replace('.', '%')
    for char in ['(', ')', ' ']:
        PBC_name = PBC_name.replace(char, '')
    return KUBC_name, PBC_name


def proceed_computation(paths, test):

    for i in test:
        if len(test[i]) == 0:
            test[i] = None
        else:
            try:
                test[i] = eval(test[i]) if i not in [
                    'sample_name', 'status', 'comment', 'err'] else test[i]
            except NameError:
                pass

    res_folder = os.path.join(paths[RES_DIR], test['test_id'])
    print(res_folder)
    porosity = operation.get_porosity(test, paths)
    number_of_step = post_reader.get_number_of_step(test)

    # time_step, extracted_disp_and_force = post_reader.read_panto_data(
    #     res_folder)
    # thickness = test['thickness'] if test['thickness'] != 0 else 1.0
    # cylinders_raw, cylinders = operation.assign_cylinders(
    #     extracted_disp_and_force)
    # force_panto = []
    # idx_of_steps = []
    # for n_step in range(1, number_of_step+1):
    #     step_of_interest = time_step.index(n_step)
    #     idx_of_steps.append(step_of_interest)
    #     force_panto.append({
    #         'O_0_x': operation.compute_force(0, 1, '-', step_of_interest, cylinders),
    #         'O_0_y': operation.compute_force(0, 2, '-', step_of_interest, cylinders),
    #         'O_3_x': operation.compute_force(3, 1, '-', step_of_interest, cylinders),
    #         'O_3_y': operation.compute_force(3, 2, '-', step_of_interest, cylinders),

    #         'B_0_x': operation.compute_force(0, 1, '+', step_of_interest, cylinders),
    #         'B_0_y': operation.compute_force(0, 2, '+', step_of_interest, cylinders),
    #         'B_1_x': operation.compute_force(1, 1, '-', step_of_interest, cylinders),
    #         'B_1_y': operation.compute_force(1, 2, '-', step_of_interest, cylinders),

    #         'C_1_x': operation.compute_force(1, 1, '+', step_of_interest, cylinders),
    #         'C_1_y': operation.compute_force(1, 2, '+', step_of_interest, cylinders),
    #         'C_2_x': operation.compute_force(2, 1, '+', step_of_interest, cylinders),
    #         'C_2_y': operation.compute_force(2, 2, '+', step_of_interest, cylinders),

    #         'D_2_x': operation.compute_force(2, 1, '-', step_of_interest, cylinders),
    #         'D_2_y': operation.compute_force(2, 2, '-', step_of_interest, cylinders),
    #         'D_3_x': operation.compute_force(3, 1, '+', step_of_interest, cylinders),
    #         'D_3_y': operation.compute_force(3, 2, '+', step_of_interest, cylinders)
    #     })

    with open(os.path.join(res_folder, 'cyldata.json'),'r') as f:
        cyl_data = json.load(f) # ! NOTATION VALMALETTE 

    force_panto=[]
    for step in cyl_data: # clen(cyl_data) = nombre de step
        force_panto.append({
            'O_1_x': operation.compute_force2(dat = step, cote= 3, composante= 'RF1' ,sens = '-'),
            'O_1_y': operation.compute_force2(dat = step, cote= 3, composante= 'RF2' ,sens = '-'),
            'O_3_x': operation.compute_force2(dat = step, cote= 0, composante= 'RF1' ,sens = '-'),
            'O_3_y': operation.compute_force2(dat = step, cote= 0, composante= 'RF2' ,sens = '-'),
            'B_3_x': operation.compute_force2(dat = step, cote= 0, composante= 'RF1' ,sens = '+'),
            'B_3_y': operation.compute_force2(dat = step, cote= 0, composante= 'RF2' ,sens = '+'),
            'B_2_x': operation.compute_force2(dat = step, cote= 1, composante= 'RF1' ,sens = '-'),
            'B_2_y': operation.compute_force2(dat = step, cote= 1, composante= 'RF2' ,sens = '-'),
            'C_2_x': operation.compute_force2(dat = step, cote= 1, composante= 'RF1' ,sens = '+'),
            'C_2_y': operation.compute_force2(dat = step, cote= 1, composante= 'RF2' ,sens = '+'),
            'C_4_x': operation.compute_force2(dat = step, cote= 2, composante= 'RF1' ,sens = '+'),
            'C_4_y': operation.compute_force2(dat = step, cote= 2, composante= 'RF2' ,sens = '+'),
            'D_4_x': operation.compute_force2(dat = step, cote= 2, composante= 'RF1' ,sens = '-'),
            'D_4_y': operation.compute_force2(dat = step, cote= 2, composante= 'RF2' ,sens = '-'),
            'D_1_x': operation.compute_force2(dat = step, cote= 3, composante= 'RF1' ,sens = '+'),
            'D_1_y': operation.compute_force2(dat = step, cote= 3, composante= 'RF2' ,sens = '+')
        }) # ! NOTATION DASSONVILLE


    # --------------------------------------------------
    # Computation of the strain field from the displacement
    # Resolve A*d=U with epsilon=[e11, e22, e12, MCR1, MCR2, MDRR12]
    nodes_coord = np.loadtxt(os.path.join(
        res_folder, 'node_coord.csv'), delimiter=',')
    area_of_interest = 4 # 4
    strain_field = []
    residuals = []
    for step_idx in range(1, 4):
        d, residual = operation.get_strain_from_disp(
            paths, res_folder, area_of_interest, step_idx, nodes_coord)[:3]
        strain_field.append([float(d[tmp]) for tmp in range(3)])
        residuals.append(residual)

    # ---------------------------------------------
    # Computation of the mean stress field
    print('computing stress...')
    area_of_interest = 4 # 4
    stress_field = []
    std_min_max = []
    for step_idx in range(1, 4):
        d, std_stress, minimum_stress, maximum_stress = operation.get_stress_average(
            paths, res_folder, area_of_interest, step_idx, porosity)
        stress_field.append([float(d[tmp]) for tmp in range(3)])
        std_min_max.append([std_stress, minimum_stress, maximum_stress])

    print(stress_field[0])
    print(std_min_max[0])

    # ---------------------------------------
    # Mean stress value according to panthos
    print('Mean stress computation from the panthos...')
    stress_pantos = []
    for force in force_panto:
        s11 = 0.5*(sum([force[k] for k in ['C_4_x', 'C_2_x', 'B_2_x', 'B_3_x']])-sum([force[k] for k in ['D_4_x', 'D_1_x', 'O_1_x', 'O_3_x']]))
        s22 = 0.5*(sum([force[k] for k in ['C_2_y', 'C_4_y', 'D_4_y', 'D_1_y']])-sum([force[k] for k in ['B_2_y', 'B_3_y', 'O_3_y', 'O_1_y']]))

        s12 = sum([force[k] for k in ['C_4_x', 'C_2_x', 'D_4_x', 'D_1_x']])-sum([force[k] for k in ['B_2_x', 'B_3_x', 'O_3_x', 'O_1_x']]) 
        s12+= sum([force[k] for k in ['C_4_y', 'C_2_y', 'B_2_y', 'B_3_y']])-sum([force[k] for k in ['D_1_y', 'D_4_y', 'O_3_y', 'O_1_y']])
        s12 = s12/4

        SIDE_LENGTH = 288.0
        sigma = 1.0/(SIDE_LENGTH*test['thickness'])
        stress_pantos.append([s11/(SIDE_LENGTH*test['thickness']),
                              s22/(SIDE_LENGTH*test['thickness']),
                              s12/(SIDE_LENGTH*test['thickness'])])

    # --------------------------------------------
    # Theoritical strain
    print('Theoritical strain')
    strain_th = []
    for step in range(1, number_of_step+1):
        strain_th.append([test['load_'+str(step)][0]/100,
                          test['load_'+str(step)][1]/100,
                          test['load_'+str(step)][2]/2/100])

    # --------------------------------------------
    # stiffnesses
    print('Stiffnesses')
    K_field_dic = operation.compute_stiffness_matrix(
        stress_field, strain_field)
    K_panto_dic = operation.compute_stiffness_matrix(
        stress_pantos, strain_field)
    K_field_bc = operation.compute_stiffness_matrix(stress_field, strain_th)
    K_panto_bc = operation.compute_stiffness_matrix(stress_pantos, strain_th)

    # * SAVING (start only)
    data = {
        'test' : test,
        'strain_th': strain_th,
        'strain_field': strain_field,
        'stress_field': stress_field,
        'stress_pantos': stress_pantos,
        'K_field_dic': K_field_dic.tolist(),
        'K_panto_dic': K_panto_dic.tolist(),
        'K_field_bc': K_field_bc.tolist(),
        'K_panto_bc': K_panto_bc.tolist(),
        'stress_pantos': stress_pantos,
        'stress_field': stress_field,
        'strain_field': strain_field,
        'strain_th': strain_th,
        'cyl_out': cyl_data,
        'force_panto': force_panto
    }

    # * Ajout des matrices theorique et construction de la matrice d'erreur DANS l'ordre
    # * Plane stress, PBC, KUBC, K_field_dic, K_panto_dic
    Ks = []

    if test['sample_name'] == 'monolithic':
        E = test['mat'][0]
        nu = test['mat'][1]
        K_plane_stress = np.linalg.inv(
            (np.array([[1/E, -nu/E, 0], [-nu/E, 1/E, 0], [0, 0, 2*(1+nu)/E]])))
        data['K_plane_stress'] = K_plane_stress.tolist()
        Ks.append(K_plane_stress)

    KUBC_name, PBC_name = get_job_name_PBC_KUBC(test)
    if test['sample_name'] in model_with_PBC_th:
        with open(os.path.join(paths[THEORY_DIR], f'{PBC_name}.json')) as f:
            K_plane_stress_PBC = json.load(f)
            K_plane_stress_PBC = np.array(K_plane_stress_PBC)
            # * Rotation de la matrice
            angle = test['trans_rot'][2]*pi/180
            c, s = cos(angle), sin(angle)
            T = np.array([[c**2, s**2, c*s],
                          [s**2, c**2, -c*s],
                          [-2*s*c, 2*c*s, (c**2-s**2)]])
            K_plane_stress_PBC = np.dot(
                np.dot(np.transpose(T), K_plane_stress_PBC), T)
            data['K_plane_stress_PBC'] = K_plane_stress_PBC.tolist()
            Ks.append(K_plane_stress_PBC)
    if test['sample_name'] in model_with_KUBC_th:
        with open(os.path.join(paths[THEORY_DIR], f'{KUBC_name}.json')) as f:
            K_plane_stress_KUBC = json.load(f)
            data['K_plane_stress_KUBC'] = K_plane_stress_KUBC
            Ks.append(np.array(K_plane_stress_KUBC))

    Ks.append(K_field_dic)
    Ks.append(K_panto_dic)

    global_deviation = operation.compute_total_deviation_matrix(Ks)
    data['global_err'] = global_deviation.tolist()

    # * Add the skiped cylinder in final_data.json

    dim = test['dim']
    if dim == 3:
        c_dim = ''
    else:
        c_dim = '2d'
    geometry_name = c_dim+'_'.join([str(test[i]) for i in ['sample_name',
                                                           'geo_parameters', 'trans_rot', 'thickness', 'corner_cleaner']])
    skip_cylinders = []
    with open(os.path.join(paths[SAMPLE_BANK_DIR], '{}_skip_cyl.csv'.format(geometry_name)), "r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            skip_cylinders.append([int(i) for i in row])
    data['skipped_cyl'] = skip_cylinders

    with open(os.path.join(res_folder, 'final_data.json'), "w") as fp:
        # json.dump(data, fp, indent=4, separators=(", ", ": "),
        #           sort_keys=True)  # encode dict into JSON
        json.dump(data, fp)

    # * update de la campagne
    # ? used to update the campagne but was removed because of several error during multiprocesses
    # ? Please refer to the logs
    """ while 'campagne.lck' in os.listdir():
        time.sleep(0.2)
    f=open('campagne.lck','w')
    f.close()
    campagne_name = paths[RES_DIR].split('/')[-2]
    header, campagne = manipulation.read_campagne(campagne_name)
    index_test = next((idx for (idx, t) in enumerate(campagne)
                       if t['test_id'] == test['test_id']), None)

    df = pd.read_csv(f'{campagne_name}.csv', delimiter=';')
    df.loc[index_test, 'status'] = 'COMPLETED_'+time.strftime("%m_%d_%H%M")
    if not test['debug']:
        df.loc[index_test, 'flag_make_inp'] = 'False'
    df.loc[index_test, 'err'] = str(
        global_deviation.tolist()).replace('[', '').replace(']', '')
    df.to_csv(f'{campagne_name}.csv', index=False, sep=';')
    os.remove('campagne.lck') """

    if not test['debug']:
        for file in os.listdir(res_folder):
            if 'step' in file or 'node' in file or 'elements' in file or 'connectivity' in file or 'cyldata' in file:
                os.remove(os.path.join(res_folder, file))
