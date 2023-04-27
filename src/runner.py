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
    if KUBC_name:
        os.remove(f'{KUBC_name}.tmp')
    if PBC_name:
        os.remove(f'{PBC_name}.tmp')
    if True: # ? test['debug'] not in ['True', True]
        print('netoyage')
        shutil.rmtree(test['test_id'])
    
# * -------------------------------------------

def run_test(test):
    init_log()
    logging.info(f'START: model {test["test_id"]}')
    # * generate the main inp (the actual test)
    logging.info('Gen of the main test')
    try:
        check_call(['./sub_run_main.sh', test['test_id'], 'make_inp', str(test).replace(' ', ''), str(paths).replace(' ', '')])
    except:
        return 1
    jobs_list=[test['test_id']]
    # * generate the inp of KUBC and PBC id needed
    KUBC_name, PBC_name = get_job_name_PBC_KUBC(test)
    if test['sample_name'] in model_with_KUBC_th and\
        f'{KUBC_name}.json' not in os.listdir(paths[THEORY_DIR]) and \
            f'{KUBC_name}.tmp' not in os.listdir(paths[ROOT]):
        open(f'{KUBC_name}.tmp', 'w').close()
        logging.info('Gen of the KUBC')
        try:
            check_call(['./sub_run_main.sh', test['test_id'], f'th_gen/make_inp_KUBC_{test["sample_name"]}', 
                        str(test).replace(' ', ''), str(paths).replace(' ', '')])
            jobs_list.append(KUBC_name)
        except Exception as e:
            logging.error('Error while generating the KUBC')
            remove_files_during_run(test, paths, KUBC_name, PBC_name)
            return 2
    else:
        KUBC_name = None
    if test['sample_name'] in model_with_PBC_th and \
        f'{PBC_name}.json' not in os.listdir(paths[THEORY_DIR]) and \
            f'{PBC_name}.tmp' not in os.listdir(paths[ROOT]):
        open(f'{PBC_name}.tmp', 'w').close()
        logging.info('Gen of the PBC')
        try:
            logging.debug(['./sub_run_main.sh', test['test_id'], f'th_gen/make_inp_PBC_{test["sample_name"]}', 
                        str(test).replace(' ', ''), str(paths).replace(' ', '')])
            check_call(['./sub_run_main.sh', test['test_id'], f'th_gen/make_inp_PBC_{test["sample_name"]}', 
                        str(test).replace(' ', ''), str(paths).replace(' ', '')])
            jobs_list.append(PBC_name)
        except Exception as e:
            logging.error('Error while generating the PBC')
            remove_files_during_run(test, paths, KUBC_name, PBC_name)
            return 3
    else:
        PBC_name = None
    # * Submit inps
    try:
        logging.info('Submission of the inp')
        check_call(['./sub_run_job.sh']+jobs_list)
    except:
        pass

    # * Extracting the data
    logging.info('Extracting the data')
    try:
        main_extract.proceed_extract_bis(paths, test, KUBC_name, PBC_name)
    except Exception as e:
        logging.error('Error while extracting the data')
        remove_files_during_run(test, paths, KUBC_name, PBC_name)
        return 5
    # * Computing the result
    logging.info('Computing the data')
    try:
        main_compute.proceed_computation(paths, test)
    except Exception as e:
        logging.error('Error while the computation')
        #remove_files_during_run(test, paths, KUBC_name, PBC_name)
        return 6
    # * Deal with the odbs
    if test['keep_odb']:
        if PBC_name:
            shutil.move(os.path.join(test['test_id'],f'{PBC_name}.odb'), os.path.join(
                paths[ODB_STOCK_DIR], f'{PBC_name}.odb'))
        if KUBC_name:
            shutil.move(os.path.join(test['test_id'],f'{KUBC_name}.odb'), os.path.join(
                paths[ODB_STOCK_DIR], f'{KUBC_name}.odb'))
        shutil.move(os.path.join(test['test_id'],f'{test["test_id"]}.odb'), os.path.join(
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
DEBUG=False
if DEBUG:
    for file in os.listdir(os.getcwd()):
        if not os.path.isfile(file) and file not in ['utilities', 'src', '.git']:
            shutil.rmtree(file)
    time.sleep(1)

N_TASK = int(sys.argv[-2])
campagne_name = sys.argv[-1]
paths, tests_to_run = func.init_campagne(campagne_name)
remove_files(paths[ROOT], types_to_remove=['lck', 'tmp'])

with Pool(processes=N_TASK-1) as pool:
    results = pool.imap_unordered(run_test, tests_to_run)
    for r in results:
        print(f'Status: {r}')


# * Essaye d'envoyer une notification de bureau
try:
    import notify2
    notify2.init('Computation')
    n = notify2.Notification(f'{campagne_name}', 'Calcul terminé')
    n.show()
except:
    pass
