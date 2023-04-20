import os
import csv

def read_panto_data(res_folder):
    extracted_disp_and_force={
    'COU':[[]]*(10*4*12),
    'TBC':[[]]*(10*4*12)
    }
    with open(os.path.join(res_folder,'COUP.csv'), "r") as f:
        reader = csv.reader(f,delimiter=',')
        first_line=True
        line_number=0
        for row in reader:
            if first_line:
                time_step=[float(i) for i in row]
                first_line=False
            else:
                extracted_disp_and_force['COU'][line_number-1]=[float(i) for i in row]
            line_number+=1
    with open(os.path.join(res_folder,'PTBC.csv'), "r") as f:
        reader = csv.reader(f,delimiter=',')
        first_line=True
        line_number=0
        for row in reader:
            if first_line:
                time_step=[float(i) for i in row]
                first_line=False
            else:
                extracted_disp_and_force['TBC'][line_number-1]=[float(i) for i in row]
            line_number+=1
    return time_step,extracted_disp_and_force

def get_number_of_step(test):
    if test['load_2']==None:
        return 1
    elif test['load_3']==None:
        return 2
    else : return 3