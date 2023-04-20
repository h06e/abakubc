import os
import func.manipulation as manipulation
from constants import *


def get_tests_to_compute(campagne):
    tests_to_run = []
    for test in campagne:
        if test['flag_make_inp'] == 'True':
            tests_to_run.append(test)
    return tests_to_run


def init_campagne(campagne_name):
    header, campagne = manipulation.read_campagne(campagne_name)
    root=os.path.abspath(os.getcwd())
    campagne_folder= os.path.join(root, campagne_name)
    paths={
        ROOT: root,
        SRC: os.path.join(root, 'src'),
        CAMPAGNE_DIR: campagne_folder,
        RES_DIR: os.path.join(root, campagne_name, 'results'),
        ODB_STOCK_DIR: os.path.join(root, campagne_name, 'odb'),
        THEORY_DIR: os.path.join(root, 'theory_matrix_bank'),
        SAMPLE_BANK_DIR: os.path.join(root, 'sample_bank'),
        POROSITY: os.path.join(root, 'porosity')
    }
    for key in paths:
        try: 
            os.mkdir(paths[key])
        except:
            pass

    return paths, get_tests_to_compute(campagne)
