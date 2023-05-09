from multiprocessing import Pool
import time
from func import func
import sys
from subprocess import check_call
import os
from constants import *
import main_extract
import main_compute
import shutil
import logging
from constants import *
from random import random
from pathlib import Path
import pandas as pd
from func import manipulation
import json

campagne_name = 'campagne_test'
paths, tests_to_run = func.init_campagne(campagne_name)

def update_campagne(campagne_name):
    """Update the campaign csv with the tests which has been completed"""
    results_path=Path(campagne_name)/'results'
    completed_tests=list(results_path.glob('**/final_data.json'))
    header, campagne = manipulation.read_campagne(campagne_name)
    print(completed_tests)
    for file in completed_tests:
        data=json.load(open(file,'r'))

        test_name=file.parent.name
        index_test = next((idx for (idx, t) in enumerate(campagne)
                        if t['test_id'] == test_name), None)

        df = pd.read_csv(f'{campagne_name}.csv', delimiter=';')
        print(df.loc[index_test, 'flag_make_inp'])
        if df.loc[index_test, 'flag_make_inp'] in [True, 'True']:
            # This line was computed during this run
            df.loc[index_test, 'status'] = 'COMPLETED_'+time.strftime("%m_%d_%H%M")
            df.loc[index_test, 'flag_make_inp'] = 'False'
            df.loc[index_test, 'err'] = str(data['global_err']).replace('[', '').replace(']', '')
            df.to_csv(f'{campagne_name}.csv', index=False, sep=';')

update_campagne(campagne_name)