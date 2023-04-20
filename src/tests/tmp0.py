import numpy as np
from math import sqrt
import json


def compute_error(K1, K2):
    K1 = np.array(K1)
    K2 = np.array(K2)
    s = (K1[0, 0]-K2[0, 0])**2+(K1[1, 1]-K2[1, 1])**2+(K1[2, 2]-K2[2, 2])**2 + \
        ((K1[1, 0]-K2[1, 0])**2+(K1[0, 1]-K2[0, 1])**2) +\
        ((K1[2, 0]-K2[2, 0])**2+(K1[0, 2]-K2[0, 2])**2) +\
        ((K1[1, 2]-K2[1, 2])**2+(K1[2, 1]-K2[2, 1])**2)
    return round(100*sqrt(s)/np.max(K2),1)


np.set_printoptions(precision=2,suppress=True,floatmode='fixed')

""" tests = ['MONO_1', 'MONO_2_free_u3', 'MONO_2D_1_gros', 'MONO_2D_1_fin']
data = {}
for test in tests:
    with open(f'../results/{test}/final_data.json', 'r') as f:
        d = json.load(f)
        data[test] = d

print('# Err inter-model')
print('K_field_dic')
print('3D - 3D U3 libre     ',compute_error(data['MONO_1']['K_field_dic'],
                    data['MONO_2_free_u3']['K_field_dic']))
print('3D U3 libre - 2D     ', compute_error(data['MONO_2_free_u3']
                    ['K_field_dic'], data['MONO_2D_1_gros']['K_field_dic']))
print('K_panto_dic')
print('3D - 3D U3 libre     ',compute_error(data['MONO_1']['K_panto_dic'],
                    data['MONO_2_free_u3']['K_panto_dic']))
print('3D U3 libre - 2D     ',compute_error(data['MONO_2_free_u3']
                    ['K_panto_dic'], data['MONO_2D_1_gros']['K_panto_dic']))

print()
print('# Erreur intra model : K_panto_dic - K_plane_stress')

print('3D                   ',compute_error(data['MONO_1']['K_panto_dic'],
                    data['MONO_1']['K_plane_stress']))
print('3D U3 libre          ', compute_error(data['MONO_2_free_u3']['K_panto_dic'],
                    data['MONO_2_free_u3']['K_plane_stress']))
print('2D                   ',compute_error(data['MONO_2D_1_gros']['K_panto_dic'],
                    data['MONO_2D_1_gros']['K_plane_stress']))
print('2D fin               ',compute_error(data['MONO_2D_1_fin']['K_panto_dic'],
                    data['MONO_2D_1_fin']['K_plane_stress']))
print('Matrices K_panto_dic ')


print('3D\n',np.array(data['MONO_1']['K_panto_dic']))
print('3D U3 libre\n',np.array(data['MONO_2_free_u3']['K_panto_dic']))
print('2D\n',np.array(data['MONO_2D_1_gros']['K_panto_dic']))
print('2D fin\n',np.array(data['MONO_2D_1_fin']['K_panto_dic']))    
 """

###############################


tests = ['HONEY_1', 'HONEY_2D_1_gros','HONEY_2D_1_fin']
data = {}
for test in tests:
    with open(f'../results/{test}/final_data.json', 'r') as f:
        d = json.load(f)
        data[test] = d

print('2D fin\n',np.array(data['HONEY_2D_1_fin']['K_panto_dic']))
print('2D moyen\n',np.array(data['HONEY_2D_1_gros']['K_panto_dic']))
print()
print('Soit une erreur de       ',compute_error(data['HONEY_2D_1_fin']['K_panto_dic'],
                    data['HONEY_2D_1_gros']['K_panto_dic']))