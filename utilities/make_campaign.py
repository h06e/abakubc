import os
from math import *

# * Get the header from the example
with open('campagne_test.csv', 'r') as f:
    header = f.readline()


def init_write_header(new_campaign_name: str, header: str) -> None:
    with open(new_campaign_name, 'w') as f:
        f.write(header[:-1])


def write_test(new_campaign_name: str, header: str, test: dict) -> None:
    """Write the test into the campagne file"""
    str_test = '\n'
    parameters = header.replace('\n', '').split(';')
    for p in parameters:
        str_test += f'{test[p]};'
    with open(new_campaign_name, 'a') as f:
        f.write(str_test)


# ***************************************************


test = {
    'debug': False,
    'test_id': None,  # TODO
    'sample_name': None, # TODO
    'dim': '',
    'geo_parameters': None,  # TODO
    'mesh_size': None,  # TODO
    'thickness': 30.0,
    'trans_rot': None,  # TODO
    'corner_cleaner': '',
    'mat': '150.0,0.3',
    'free_rotation': True,
    'free_u3': 0.0,
    'perfect_panto': True,
    'stiff_panto': '57740,6950.0',
    'friction': '0.1,2500,2000,0,0.0,5000',
    'clearance': '0.030,0.004,0.013,0.043',
    'load_1': '2,0,0',
    'load_2': '0,2,0',
    'load_3': '0,0,2',
    'flag_make_inp': True,
    'keep_odb': False,
    'status': '',
    'comment': '',
    'err': ''
}

# !##############################################################
# ! NIDA
# new_campaign_name = 'campagnes_vierges/campagne_honey.csv'
# test['sample_name'] = 'honey'
# L, width = 28.0, 4.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = 2*L*cos(pi/6)
# scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# # scale_factors = [1.3]

# nb_of_rotation = 13
# angle_max = 30.0

# # * nb_of_translation=10 mean a 10 by 10 grid. Giving the periodicity.
# # * eg 10 lead to 9*5=45 tests per angle of rotation
# nb_of_translation = 7
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{L*scale:.3f},{width*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for i_angle in range(nb_of_rotation):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'honey_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/(nb_of_translation-1) / 2
#                 ty = length_y * i_ty/(nb_of_translation-1) / 2
#                 angle = angle_max*i_angle/(nb_of_rotation-1)
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)


# test['corner_cleaner']=True
# new_campaign_name = 'campagnes_vierges/campagne_honey_CC.csv'
# test['sample_name'] = 'honey'
# L, width = 28.0, 4.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = 2*L*cos(pi/6)
# # scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# scale_factors = [0.7]

# nb_of_rotation = 13
# angle_max = 30.0

# # * nb_of_translation=10 mean a 10 by 10 grid. Giving the periodicity.
# # * eg 10 lead to 9*5=45 tests per angle of rotation
# nb_of_translation = 7
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{L*scale:.3f},{width*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for i_angle in range(nb_of_rotation):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'honeyCC_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/(nb_of_translation-1) / 2
#                 ty = length_y * i_ty/(nb_of_translation-1) / 2
#                 angle = angle_max*i_angle/(nb_of_rotation-1)
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)

# test['corner_cleaner']=''
# test['free_rotation']=False
# new_campaign_name = 'campagnes_vierges/campagne_honey_UR3.csv'
# test['sample_name'] = 'honey'
# L, width = 28.0, 4.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = 2*L*cos(pi/6)
# # scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# scale_factors = [0.7,1.3]

# nb_of_rotation = 13
# angle_max = 30.0

# # * nb_of_translation=10 mean a 10 by 10 grid. Giving the periodicity.
# # * eg 10 lead to 9*5=45 tests per angle of rotation
# nb_of_translation = 7
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{L*scale:.3f},{width*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for i_angle in range(nb_of_rotation):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'honeyUR3_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/(nb_of_translation-1) / 2
#                 ty = length_y * i_ty/(nb_of_translation-1) / 2
#                 angle = angle_max*i_angle/(nb_of_rotation-1)
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)

# #!##############################################################
# # ! CARRE

# new_campaign_name = 'campagnes_vierges/campagne_carre.csv'
# test['sample_name'] = 'rectangle'
# L, width = 28.0, 4.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = L
# scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# # scale_factors = [1.3]

# nb_of_rotation = 13
# angle_max = 45.0
# nb_of_translation = 7
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{L*scale:.3f},{width*scale:.3f}'
#     test['geo_parameters'] = f'{width*scale:.3f},{2*width*scale:.3f},{L*scale:.3f},{L*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for i_angle in range(nb_of_rotation):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'carre_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/(nb_of_translation-1) / 2
#                 ty = length_y * i_ty/(nb_of_translation-1) / 2
#                 angle = angle_max*i_angle/(nb_of_rotation-1)
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)


# test['corner_cleaner']=True
# new_campaign_name = 'campagnes_vierges/campagne_carre_CC.csv'
# test['sample_name'] = 'rectangle'
# L, width = 28.0, 4.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = L
# # scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# scale_factors = [0.7]

# nb_of_rotation = 13
# angle_max = 45.0
# nb_of_translation = 7
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{L*scale:.3f},{width*scale:.3f}'
#     test['geo_parameters'] = f'{width*scale:.3f},{2*width*scale:.3f},{L*scale:.3f},{L*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for i_angle in range(nb_of_rotation):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'carreCC_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/(nb_of_translation-1) / 2
#                 ty = length_y * i_ty/(nb_of_translation-1) / 2
#                 angle = angle_max*i_angle/(nb_of_rotation-1)
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)


# test['corner_cleaner']=''
# test['free_rotation']=False
# new_campaign_name = 'campagnes_vierges/campagne_carre_UR3.csv'
# test['sample_name'] = 'rectangle'
# L, width = 28.0, 4.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = L
# # scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# scale_factors = [0.7,1.3]

# nb_of_rotation = 13
# angle_max = 45.0
# nb_of_translation = 7
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{L*scale:.3f},{width*scale:.3f}'
#     test['geo_parameters'] = f'{width*scale:.3f},{2*width*scale:.3f},{L*scale:.3f},{L*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for i_angle in range(nb_of_rotation):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'carreUR3_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/(nb_of_translation-1) / 2
#                 ty = length_y * i_ty/(nb_of_translation-1) / 2
#                 angle = angle_max*i_angle/(nb_of_rotation-1)
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)



# #!##############################################################
# # ! losange
# test['sample_name'] = 'losange'
# W, L, ALPHA = 4.0,28.0,45.0
# length_x_default_scale = 2*L*sin(ALPHA*pi/180.0/2.0)
# length_y_default_scale = 2*L*cos(ALPHA*pi/180.0/2.0)
# scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]

# nb_of_rotation = 16
# angle_max = 45.0
# angles = [angle_max*i/nb_of_rotation for i in range(nb_of_rotation)]

# # * nb_of_translation=10 mean a 10 by 10 grid. Giving the periodicity.
# # * eg 10 lead to 9*5=45 tests per angle of rotation
# nb_of_translation = 10
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{W*scale:.3f},{L*scale:.3f},{ALPHA:.1f}'
#     test['mesh_size'] = f'{W*scale/5:.3f}'
#     for ang_i, angle in enumerate(angles):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation//2 + nb_of_translation % 2):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'losa_{int(scale*10)}_{ang_i}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/nb_of_translation
#                 ty = length_y * i_ty/nb_of_translation

#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)

# !##############################################################
# ! TRIANGLE
# test['sample_name'] = 'triangle'
# L, width = 28.0, 4.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = 2*L*tan(pi/6)
# scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# #scale_factors = [1.3]

# nb_of_rotation = 12
# angle_max = 30.0
# angles = [angle_max*i/nb_of_rotation for i in range(nb_of_rotation+1)]

# # * nb_of_translation=10 mean a 10 by 10 grid. Giving the periodicity.
# # * eg 10 lead to 9*5=45 tests per angle of rotation
# nb_of_translation = 10
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{width*scale:.3f},{L*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for ang_i, angle in enumerate(angles):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation//2 + nb_of_translation % 2):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'tria_{int(scale*10)}_{ang_i}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/nb_of_translation
#                 ty = length_y * i_ty/nb_of_translation
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)

new_campaign_name = 'campagnes_vierges/campagne_trian.csv'
test['sample_name'] = 'triangle'
L, width = 28.0, 4.0
length_x_default_scale = 2*L  # * See PBC gen files
length_y_default_scale = 4*L*tan(pi/6.0)
scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# scale_factors = [1.3]

nb_of_rotation = 13
angle_max = 30.0

# * nb_of_translation=10 mean a 10 by 10 grid. Giving the periodicity.
# * eg 10 lead to 9*5=45 tests per angle of rotation
nb_of_translation = 7
# ***************************************************
init_write_header(new_campaign_name, header)

for scale in scale_factors:
    length_x = length_x_default_scale*scale
    length_y = length_y_default_scale*scale
    test['geo_parameters'] = f'{width*scale:.3f},{L*scale:.3f}'
    test['mesh_size'] = f'{width*scale/5:.3f}'
    for i_angle in range(nb_of_rotation):
        for i_tx in range(nb_of_translation):
            for i_ty in range(nb_of_translation):
                # !!!! NOT DOT IN THE NAME
                test['test_id'] = f'tria_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
                tx = length_x * i_tx/(nb_of_translation-1) / 2
                ty = length_y * i_ty/(nb_of_translation-1) / 2
                angle = angle_max*i_angle/(nb_of_rotation-1)
                test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
                write_test(new_campaign_name, header, test)


test['corner_cleaner']=True
new_campaign_name = 'campagnes_vierges/campagne_trian_CC.csv'
test['sample_name'] = 'triangle'
L, width = 28.0, 4.0
length_x_default_scale = 2*L  # * See PBC gen files
length_y_default_scale = 4*L*tan(pi/6.0)
# scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
scale_factors = [0.7]

nb_of_rotation = 13
angle_max = 30.0

# * nb_of_translation=10 mean a 10 by 10 grid. Giving the periodicity.
# * eg 10 lead to 9*5=45 tests per angle of rotation
nb_of_translation = 7
# ***************************************************
init_write_header(new_campaign_name, header)

for scale in scale_factors:
    length_x = length_x_default_scale*scale
    length_y = length_y_default_scale*scale
    test['geo_parameters'] = f'{width*scale:.3f},{L*scale:.3f}'
    test['mesh_size'] = f'{width*scale/5:.3f}'
    for i_angle in range(nb_of_rotation):
        for i_tx in range(nb_of_translation):
            for i_ty in range(nb_of_translation):
                # !!!! NOT DOT IN THE NAME
                test['test_id'] = f'triaCC_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
                tx = length_x * i_tx/(nb_of_translation-1) / 2
                ty = length_y * i_ty/(nb_of_translation-1) / 2
                angle = angle_max*i_angle/(nb_of_rotation-1)
                test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
                write_test(new_campaign_name, header, test)

test['corner_cleaner']=''
test['free_rotation']=False
new_campaign_name = 'campagnes_vierges/campagne_trian_UR3.csv'
test['sample_name'] = 'triangle'
L, width = 28.0, 4.0
length_x_default_scale = 2*L  # * See PBC gen files
length_y_default_scale = 4*L*tan(pi/6.0)
# scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
scale_factors = [0.7,1.3]

nb_of_rotation = 13
angle_max = 30.0

# * nb_of_translation=10 mean a 10 by 10 grid. Giving the periodicity.
# * eg 10 lead to 9*5=45 tests per angle of rotation
nb_of_translation = 7
# ***************************************************
init_write_header(new_campaign_name, header)

for scale in scale_factors:
    length_x = length_x_default_scale*scale
    length_y = length_y_default_scale*scale
    test['geo_parameters'] = f'{width*scale:.3f},{L*scale:.3f}'
    test['mesh_size'] = f'{width*scale/5:.3f}'
    for i_angle in range(nb_of_rotation):
        for i_tx in range(nb_of_translation):
            for i_ty in range(nb_of_translation):
                # !!!! NOT DOT IN THE NAME
                test['test_id'] = f'triaUR3_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
                tx = length_x * i_tx/(nb_of_translation-1) / 2
                ty = length_y * i_ty/(nb_of_translation-1) / 2
                angle = angle_max*i_angle/(nb_of_rotation-1)
                test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
                write_test(new_campaign_name, header, test)

# # !##############################################################
# # ! HEXAC

# new_campaign_name = 'campagnes_vierges/campagne_hexac.csv'
# test['sample_name'] = 'hexachiral'
# L, width, radius = 28.0,4.0,8.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = 2*L*cos(pi/6)
# scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# # scale_factors = [1.3]

# nb_of_rotation = 13
# angle_max = 30.0

# nb_of_translation = 7
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{L*scale:.3f},{width*scale:.3f},{radius*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for i_angle in range(nb_of_rotation):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'hexac_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/(nb_of_translation-1) / 2
#                 ty = length_y * i_ty/(nb_of_translation-1) / 2
#                 angle = angle_max*i_angle/(nb_of_rotation-1)
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)


# test['corner_cleaner']=True
# new_campaign_name = 'campagnes_vierges/campagne_hexac_CC.csv'
# test['sample_name'] = 'hexachiral'
# L, width, radius = 28.0,4.0,8.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = 2*L*cos(pi/6)
# # scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# scale_factors = [0.7]

# nb_of_rotation = 13
# angle_max = 30.0

# nb_of_translation = 7
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{L*scale:.3f},{width*scale:.3f},{radius*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for i_angle in range(nb_of_rotation):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'hexacCC_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/(nb_of_translation-1) / 2
#                 ty = length_y * i_ty/(nb_of_translation-1) / 2
#                 angle = angle_max*i_angle/(nb_of_rotation-1)
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)

# test['corner_cleaner']=''
# test['free_rotation']=False
# new_campaign_name = 'campagnes_vierges/campagne_hexac_UR3.csv'
# test['sample_name'] = 'hexachiral'
# L, width, radius = 28.0,4.0,8.0
# length_x_default_scale = L  # * See PBC gen files
# length_y_default_scale = 2*L*cos(pi/6)
# # scale_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
# scale_factors = [0.7]

# nb_of_rotation = 13
# angle_max = 30.0

# nb_of_translation = 7
# # ***************************************************
# init_write_header(new_campaign_name, header)

# for scale in scale_factors:
#     length_x = length_x_default_scale*scale
#     length_y = length_y_default_scale*scale
#     test['geo_parameters'] = f'{L*scale:.3f},{width*scale:.3f},{radius*scale:.3f}'
#     test['mesh_size'] = f'{width*scale/5:.3f}'
#     for i_angle in range(nb_of_rotation):
#         for i_tx in range(nb_of_translation):
#             for i_ty in range(nb_of_translation):
#                 # !!!! NOT DOT IN THE NAME
#                 test['test_id'] = f'hexacUR3_{int(scale*10)}_{i_angle}_{i_tx}_{i_ty}' # ~ modifier
#                 tx = length_x * i_tx/(nb_of_translation-1) / 2
#                 ty = length_y * i_ty/(nb_of_translation-1) / 2
#                 angle = angle_max*i_angle/(nb_of_rotation-1)
#                 test['trans_rot'] = f'{tx:.3f},{ty:.3f},{angle}'
#                 write_test(new_campaign_name, header, test)
