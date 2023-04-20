import csv
import os
from time import strftime
import pandas as pd
import time

def read_campagne(file_name):
    tests=[]
    with open(f'{file_name}.csv', "r") as f:
        reader = csv.reader(f,delimiter=';',)
        header=next(reader)
        for row in reader:
            test_line={}
            for idx,parameter in enumerate(row):
                test_line[header[idx]]=parameter
            tests.append(test_line)
    return header,tests

def get_number_of_inp_to_gen(campagne):
    total=0
    true_list=['1','True','true','oui','Oui']
    for test in campagne:
        if test['flag_make_inp']in true_list:
            total+=1
    return total

def move_inp (test,path):
    true_list=['1','True','true','oui','Oui']
    os.system('mv '+test['test_id']+'.inp'  +' '+path[:-4]+'/inp_files/'+test['test_id']+'.inp' )
    if test['perfect_panto'] in true_list:
        try: os.remove(path[:-4]+'inp_files/'+test['test_id']+'_connector_prop.csv')
        except:pass
    else:
        os.system('mv '+test['test_id']+'_connector_prop.csv'  +' '+path[:-4]+'/inp_files/'+test['test_id']+'_connector_prop.csv' )

def clean_the_repertory():
    for file in os.listdir():
        if file.split('.')[-1] not in ['inp','sat','py','csv','cae','slurm']:
            if os.path.isfile(file):
                os.remove(file)
    return

