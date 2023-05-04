import os
import func.manipulation as manipulation
from constants import *
import time
import json
import pandas as pd
from pathlib import Path

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

def update_campagne(campagne_name):
    """Update the campaign csv with the tests which has been completed"""
    results_path=Path(campagne_name)/'results'
    completed_tests=list(results_path.glob('**/final_data.json'))
    header, campagne = manipulation.read_campagne(campagne_name)

    for file in completed_tests:
        data=json.load(open(file,'r'))

        test_name=file.parent.name
        index_test = next((idx for (idx, t) in enumerate(campagne)
                        if t['test_id'] == test_name), None)

        df = pd.read_csv(f'{campagne_name}.csv', delimiter=';')
        if df.loc[index_test, 'flag_make_inp'] == 'True':
            # This line was computed during this run
            df.loc[index_test, 'status'] = 'COMPLETED_'+time.strftime("%m_%d_%H%M")
            df.loc[index_test, 'flag_make_inp'] = 'False'
            df.loc[index_test, 'err'] = str(data['global_err']).replace('[', '').replace(']', '')
            df.to_csv(f'{campagne_name}.csv', index=False, sep=';')