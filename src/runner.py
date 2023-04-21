from multiprocessing import Pool
import time
from func import func
import sys
from subprocess import check_call
import os
from constants import *
import glob
import main_extract
import main_compute
import shutil
import logging
from constants import *
from random import random


def remove_files(path: str, types_to_remove: list[str] = []) -> None:
    """Remove files by type """
    for file in os.listdir(path):
        if (file.split('.')[-1] in types_to_remove) and os.path.isfile(os.path.join(path, file)):
            os.remove(os.path.join(path, file))


def get_job_name_PBC_KUBC(test):
    """see KUBC and PBC func, job name cannot contain . char (Abq requirement)
    So i convert the . into %. I also remove () and <space>"""
    KUBC_name = 'KUBC_'+'_'.join([str(test[i]) for i in ['sample_name',
                                                         'geo_parameters', 'mat', 'trans_rot']]).replace('.', '%')
    for char in ['(', ')', ' ']:
        KUBC_name = KUBC_name.replace(char, '')
    PBC_name = 'PBC_' + \
        '_'.join([str(test[i]) for i in ['sample_name',
                                         'geo_parameters', 'mat']]).replace('.', '%')
    for char in ['(', ')', ' ']:
        PBC_name = PBC_name.replace(char, '')
    return KUBC_name, PBC_name


def run_script(script: str, arg: list):
    """Don't add .py to the script name"""
    logging.debug(' '.join(['abaqus_2021', 'cae', f'noGUI={script}.py', '--']+[f'"{i}"' for i in arg]))
    check_call(['abaqus_2021', 'cae', f'noGUI={script}.py', '--']+arg)


def sumbit_job(job_list: list[str], scratch: str, number_of_cpu=1):
    for job in job_list:
        if job:
            logging.info(f'Submitting the job {job}')
            try:
                logging.debug(' '.join(['abaqus_2021', 'interactive', f'job={job}', f'cpus={number_of_cpu}', f'scratch={scratch}']))
                check_call(['abaqus_2021', 'interactive',
                            f'job={job}', f'cpus={number_of_cpu}', f'scratch={scratch}'])
            except:
                logging.warning(f'{job} couldn\'t be completed on the first attempt')
                submit_job_custom(job,number_of_cpu,scratch)


def submit_job_custom(job,number_of_cpu,scratch):
    """Sometimes, the computation failed. remove other files related to the test can help"""
    for file in os.listdir(paths[ROOT]):
        if (job in file) and file.split('.')[-1]!='inp':
            try:
                os.remove(file)
            except:
                pass
    check_call(['abaqus_2021', 'interactive',
                            f'job={job}', f'cpus={number_of_cpu}', f'scratch={scratch}'])

def init_log(open_in_vsc=False):
    i = 1
    # * if not this random delay, multiple cpu can write into the same log
    time.sleep(random())
    while f'{i:03.0f}_log.log' in os.listdir(os.getcwd()):
        i += 1
    logging.basicConfig(filename=f'{i:03.0f}_log.log', encoding='utf-8', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s', filemode='w')
    logging.info('Initialization...')
    if open_in_vsc:
        check_call(['code', '-r', f'{i:03.0f}_log.log'])

def remove_files_during_run(test, paths, KUBC_name=None, PBC_name=None):
    for file in os.listdir(paths[ROOT]):
        if test['test_id'] in file or               \
                'abaqus.rpy' in file or             \
                (KUBC_name and KUBC_name in file) or\
                (PBC_name and PBC_name in file):
            try:
                os.remove(file)
            except:
                pass

def move_file_duto_error (test, paths, KUBC_name=None, PBC_name=None):
    try: 
        os.mkdir(test['test_id'])
    except:
        pass

    for file in os.listdir(paths[ROOT]):
        if test['test_id'] in file or         \
                (KUBC_name and KUBC_name in file) or\
                (PBC_name and PBC_name in file):
            try:
                shutil.move(file, os.path.join(test['test_id'],file))
            except:
                pass

# * -------------------------------------------

def run_test(test):
    init_log(open_in_vsc=True)
    logging.info(f'START: model {test["test_id"]}')
    # * generate the main inp (the actual test)
    try:
        run_script('src/make_inp',
                   [str(test).replace(' ', ''), str(paths).replace(' ', '')])
    except Exception as e:
        logging.error('Error while generating the main test')
        move_file_duto_error (test, paths)
        return 1
    # * generate the inp of KUBC and PBC id needed
    KUBC_name, PBC_name = get_job_name_PBC_KUBC(test)
    if test['sample_name'] in model_with_KUBC_th and\
        f'{KUBC_name}.json' not in os.listdir(paths[THEORY_DIR]) and \
            f'{KUBC_name}.tmp' not in os.listdir(paths[ROOT]):
        open(f'{KUBC_name}.tmp', 'w').close()
        logging.info('GEN of the KUBC')
        try:
            run_script(f'src/th_gen/make_inp_KUBC_{test["sample_name"]}', [
                str(test).replace(' ', ''), str(paths).replace(' ', '')])
        except Exception as e:
            logging.error('Error while generating the KUBC')
            move_file_duto_error (test, paths, KUBC_name)
            return 2
    else:
        KUBC_name = None
    if test['sample_name'] in model_with_PBC_th and \
        f'{PBC_name}.json' not in os.listdir(paths[THEORY_DIR]) and \
            f'{PBC_name}.tmp' not in os.listdir(paths[ROOT]):
        open(f'{PBC_name}.tmp', 'w').close()
        logging.info('GEN of the PBC')
        try:
            run_script(f'src/th_gen/make_inp_PBC_{test["sample_name"]}', [
                str(test).replace(' ', ''), str(paths).replace(' ', '')])
        except Exception as e:
            logging.error('Error while generating the PBC')
            move_file_duto_error (test, paths, KUBC_name, PBC_name)
            return 3
    else:
        PBC_name = None

    # * submit the computation when needed
    job_list = [test['test_id']]
    if KUBC_name:
        job_list.append(KUBC_name)
    if PBC_name:
        job_list.append(PBC_name)
    try:
        sumbit_job(job_list=job_list, scratch=paths[ROOT])
    except Exception as e:
        logging.error('Error while submiting the job')
        move_file_duto_error (test, paths, KUBC_name, PBC_name)
        return 4
    # * Extracting the data
    try:
        main_extract.proceed_extract_bis(paths, test, KUBC_name, PBC_name)
    except Exception as e:
        logging.error('Error while extracting the data')
        remove_files_during_run(test, paths, KUBC_name, PBC_name)
        return 5
    # * Computing the result
    main_compute.proceed_computation(paths, test)
    try:
        pass
    except Exception as e:
        logging.error('Error while the computation')
        remove_files_during_run(test, paths, KUBC_name, PBC_name)
        return 6
    # * Deal with the odbs
    if test['keep_odb']:
        if PBC_name:
            shutil.move(f'{PBC_name}.odb', os.path.join(
                paths[ODB_STOCK_DIR], f'{PBC_name}.odb'))
        if KUBC_name:
            shutil.move(f'{KUBC_name}.odb', os.path.join(
                paths[ODB_STOCK_DIR], f'{KUBC_name}.odb'))
        shutil.move(f'{test["test_id"]}.odb', os.path.join(
            paths[ODB_STOCK_DIR], f'{test["test_id"]}.odb'))
    # * Remove files
    remove_files_during_run(test, paths, KUBC_name, PBC_name)
    logging.info(f'test {test["test_id"]} COMPLETED')
    return 0


# *******************************************
# *                 Main                    *
# *******************************************

# * reset the folder
# ! DEBUG MODE
DEBUG=True
if DEBUG:
    for file in os.listdir(os.getcwd()):
        if not os.path.isfile(file) and file not in ['utilities', 'src', '.git']:
            shutil.rmtree(file)
time.sleep(2)

N_TASK = int(sys.argv[-2])
campagne_name = sys.argv[-1]
paths, tests_to_run = func.init_campagne(campagne_name)
remove_files(paths[ROOT], types_to_remove=['lck', 'tmp'])

with Pool(processes=N_TASK-1) as pool:
    results = pool.imap_unordered(run_test, tests_to_run)
    for r in results:
        print(f'Status: {r}')

# * Remove eventual folder created by abq
list_of_campaign=[]
for file in os.listdir(os.getcwd()):
    if file.split('.')[-1]=='csv':
        list_of_campaign.append(file.split('.')[:-1][0])

print(f'{list_of_campaign=}')
for file in os.listdir(os.getcwd()):
    if not os.path.isfile(file) and file not in list_of_campaign+['utilities', 'src', '.git', 'theory_matrix_bank', 'porosity', 'sample_bank']:
        shutil.rmtree(file)

# * Essaye d'envoyer une notification de bureau
try:
    import notify2
    notify2.init('Computation')
    n = notify2.Notification(f'{campagne_name}', 'Calcul terminé')
    n.show()
except:
    pass
