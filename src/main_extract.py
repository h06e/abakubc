from func import manipulation
import os
import glob
from time import sleep
from subprocess import check_call, DEVNULL, STDOUT
from constants import *
import logging
from constants import *

def run_script(script: str, arg: list):
    """Don't add .py to the script name"""
    check_call(['abaqus_2021', 'cae', f'noGUI={script}.py', '--']+arg)

def get_job_name_PBC_KUBC (test):
    """see KUBC and PBC func, job name cannot contain . char (Abq requirement)
    So i convert the . into %. I also remove () and <space>"""
    KUBC_name = 'KUBC_'+'_'.join([str(test[i]) for i in ['sample_name', 'geo_parameters', 'mat', 'trans_rot']]).replace('.', '%')
    for char in ['(', ')', ' ']:
        KUBC_name = KUBC_name.replace(char, '')
    PBC_name = 'PBC_'+'_'.join([str(test[i]) for i in ['sample_name', 'geo_parameters', 'mat']]).replace('.', '%')
    for char in ['(', ')', ' ']:
        PBC_name = PBC_name.replace(char, '')
    return KUBC_name, PBC_name

def proceed_extract_bis(paths, test, th_KUBC_name, th_PBC_name):
    # * Dépouillement du PBC et KUBC th s'il(s) existe(nt)
    if th_KUBC_name:
        logging.info('Extracting and commputing the KUBC')
        run_script(f'src/th_extract/extract_{test["sample_name"]}', [
                   str(test).replace(' ', ''), th_KUBC_name])
    if th_PBC_name:
        logging.info('Extracting and commputing the PBC')
        run_script(f'src/th_extract/extract_{test["sample_name"]}', [
                   str(test).replace(' ', ''), th_PBC_name])
    # * Cas particulier où le pbc ou kubc tournent sur un autre cpu qui n'a pas terminé
    KUBC_name, PBC_name = get_job_name_PBC_KUBC(test)
    if test['sample_name'] in model_with_KUBC_th:
        logging.info(f'Waiting for KUBC th')
        while (f'{KUBC_name}.json' not in os.listdir(paths[THEORY_DIR])):
            sleep(1)
            if f'{KUBC_name}.tmp' not in os.listdir(paths[ROOT]):
                raise FileNotFoundError
    if test['sample_name'] in model_with_PBC_th:
        logging.info(f'Waiting for PUBC th')
        while (f'{PBC_name}.json' not in os.listdir(paths[THEORY_DIR])):
            sleep(1)
            if f'{PBC_name}.tmp' not in os.listdir(paths[ROOT]):
                raise FileNotFoundError
    # * Extraction du fichier principal (du test en lui-meme)
    logging.info('Extracting the main odb')
    run_script(f'src/post_extract', [
        str(test).replace(' ', ''), str(paths).replace(' ', '')])


if __name__ == '__main__':
    pass
