import os
import sys
import glob
from time import sleep, time
from func import manipulation, func
import main_auto_compute
import main_extract
import shutil
import time
from tests import module_test
from subprocess import check_call, DEVNULL, STDOUT

# * Recommended vsc extensions : better comments, log file highlighter


def pylog(message):
    date = time.strftime("%y-%m-%d %H:%M:%S")
    car = date+' '+__file__.split('/')[-1]+' '+message
    root = os.path.abspath(os.getcwd())[:-3]
    log_file = open(root+'log.log', 'a')
    log_file.write(car+'\n')
    log_file.close()
    return


def pylog_line():
    root = os.path.abspath(os.getcwd())[:-3]
    log_file = open(root+'log.log', 'a')
    log_file.write('---------------------------------------------\n')
    log_file.close()
    return


def execute(command):
    pylog('COMMAND $ '+command)
    check_call(command.split(' '))
    return


def remove_files(path: str, types_to_remove: list[str] = [], types_to_keep: list[str] = []) -> None:
    for file in os.listdir(path):
        if (file.split('.')[-1] in types_to_remove or file.split('.')[-1] not in types_to_keep) and os.path.isfile(path+file):
            os.remove(path+file)


N_CPU = 2
REMOVE_FILES = True  # Remove file which are not odb, inp or py
campagne_name = 'campagne_1'


header, campagne = manipulation.read_campagne(campagne_name)
root = os.path.abspath(os.getcwd())[:-3]
odb_directory = os.path.abspath(os.getcwd())[:-3]+'results/'
odb_stockage = os.path.abspath(os.getcwd())[:-3]+'odb/'
theory_directory = os.path.abspath(os.getcwd())[:-3]+'theory_matrix_bank/'
inp_dir = os.path.abspath(os.getcwd())[:-3]+'inp_files/'

current_path = os.path.abspath(os.getcwd())
inp_path = current_path[:-3]+'inp_files/'
log_file = open(root+'log.log', 'w')
log_file.close()

for file in os.listdir():
    if file.split('.')[-1] not in ['py', 'slurm']:
        if os.path.isfile(file):
            os.remove(file)

number_of_gen = manipulation.get_number_of_inp_to_gen(campagne)
pylog(f'{number_of_gen} will be computed')
number_of_err = 0

for test in campagne:
    if test['flag_make_inp'] == 'True':
        test_id = test['test_id']
        pylog_line()
        pylog(f' INFO TEST : {test_id}')
        manipulation.write_input_test(current_path, test)
        if test['dim'] in ['2', '2.0', '']:
            try:
                pylog(f' INFO Generation 2D')
                execute('abaqus_2021 cae noGUI=make_inp_2d.py')
            except:
                pylog('ERROR Generation impossible')
                number_of_err += 1
                manipulation.clean_the_repertory()
                continue
        else:
            try:
                pylog(f' INFO Generation 3D')
                execute('abaqus_2021 cae noGUI=make_inp.py')
            except:
                pylog('ERROR Generation impossible')
                number_of_err += 1
                manipulation.clean_the_repertory()
                continue
        #manipulation.move_inp (test,current_path)
        manipulation.clean_the_repertory()

        if test['sample_name'] != 'monolithic':
            th_KUBC_file_name = test['sample_name']+'_'+test['geo_parameters'].replace('/', '-') + \
                '_'+test['mat'].replace('/', '-')+'_' + \
                test['trans_rot'].replace('/', '-')
            if 'KUBC_'+th_KUBC_file_name.replace('.', ',')+'.csv' not in os.listdir(theory_directory):
                execute('abaqus_2021 cae noGUI=th_gen/make_inp_KUBC_'+test['sample_name']+'.py -- '+test['geo_parameters'].replace(
                    '/', ' ')+' '+test['mat'].replace('/', ' ')+' '+test['trans_rot'].replace('/', ' '))
            th_PBC_file_name = test['sample_name']+'_'+test['geo_parameters'].replace(
                '/', '-')+'_'+test['mat'].replace('/', '-')
            if 'PBC_'+th_PBC_file_name.replace('.', ',')+'.csv' not in os.listdir(theory_directory):
                execute('abaqus_2021 cae noGUI=th_gen/make_inp_PBC_' +
                        test['sample_name']+'.py -- '+test['geo_parameters'].replace('/', ' ')+' '+test['mat'].replace('/', ' '))

        pylog('INFO Submiting the job(s)')
        inps = glob.glob('*.inp')

        for inp in inps:
            execute('abaqus_2021 job=' +
                    inp[:-4]+' cpus='+str(N_CPU)+' scratch='+current_path)
            sleep(1)
            while glob.glob('*.lck') != []:
                sleep(5)
            pylog('INFO '+inp+' COMPLETED!')

        sleep(2)
        for file in os.listdir():
            if file.split('.')[-1] not in ['odb', 'py', 'slurm']:
                if os.path.isfile(file):
                    os.remove(file)

        pylog('INFO Moving the odb to resutls/')
        for file in os.listdir():
            if file.split('.')[-1] == 'odb':
                shutil.move(file, odb_directory+file.split('/')[-1])

        pylog('INFO Extracting data')
        try:
            main_extract.proceed_extract(campagne_name)
        except:
            pylog('ERROR extraction impossible')
            number_of_err += 1
            if test['keep_odb'] == 'False':
                pylog('INFO deleting the odb(s)')  # to '+odb_stockage)
                remove_files(['odb'], odb_directory)
            else:
                pylog('INFO moving the odb(s) to the storing folder')
                for file in os.listdir(odb_directory):
                    if file.split('.')[-1] == 'odb':
                        shutil.move(odb_directory+file,
                                    odb_stockage+file.split('/')[-1])
            continue
        pylog('INFO Computing data')
        try:
            main_auto_compute.proceed_compute(campagne_name)
        except:
            pylog('ERROR computation impossible')
            remove_files(['odb'], odb_directory)
            number_of_err += 1
            continue
        if test['keep_odb'] == 'False':
            pylog('INFO deleting the odb(s)')  # to '+odb_stockage)
            remove_files(['odb'], odb_directory)
            for file in os.listdir(odb_directory+test_id):
                if 'step' in file or 'node' in file:
                    os.remove(odb_directory+test_id+'/'+file)
        else:
            pylog('INFO moving the odb(s) to the storing folder')
            for file in os.listdir(odb_directory):
                if file.split('.')[-1] == 'odb':
                    shutil.move(odb_directory+file,
                                odb_stockage+file.split('/')[-1])


pylog_line()
pylog_line()
pylog('INFO full_runner.py TERMINATION')
if number_of_err != 0:
    pylog(f'INO {number_of_err} ERROR s occured. Keep calm and retry ^^')
else:
    pylog('INFO No error detected ;)')
exit()
