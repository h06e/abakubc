import os
from func import manipulation

# ? Obselette?

campagne_name='campagne_1'
header,campagne=manipulation.read_campagne(campagne_name)
odb_directory=os.path.abspath(os.getcwd())[:-3]+'results/'
theory_directory=os.path.abspath(os.getcwd())[:-3]+'theory_matrix_bank/'
inp_dir=os.path.abspath(os.getcwd())[:-3]+'inp_files/'

current_path=os.path.abspath(os.getcwd())
number_of_gen=manipulation.get_number_of_inp_to_gen(campagne)
if input(f'Proceed the generation of {number_of_gen} generation? (y to proceed)')!='y':
    exit()
counter=0
for test in campagne:
    if test['flag_make_inp']=='True':
        print(f'Already generated :{counter}')
        counter += 1
        manipulation.write_input_test(current_path,test)
        os.system('abaqus_2021 cae noGUI=make_inp.py')
        manipulation.move_inp (test,current_path)
        manipulation.clean_the_repertory()

        if test['sample_name']!='monolithic':
            th_KUBC_file_name=test['sample_name']+'_'+test['geo_parameters'].replace('/','-')+ \
                '_'+test['mat'].replace('/','-')+'_'+test['trans_rot'].replace('/','-')
            print(f'th_KUBC_file_name: {th_KUBC_file_name}')
            if 'KUBC_'+th_KUBC_file_name.replace('.',',')+'.csv' not in os.listdir(theory_directory) and 'KUBC_'+th_KUBC_file_name.replace('.',',')+'.inp' not in os.listdir(inp_dir):
                print('abaqus_2021 cae noGUI=th_gen/make_inp_KUBC_'+test['sample_name']+'.py -- '+test['geo_parameters'].replace('/',' ')+' '+test['mat'].replace('/',' ')+' '+test['trans_rot'].replace('/',' '))
                os.system('abaqus_2021 cae noGUI=th_gen/make_inp_KUBC_'+test['sample_name']+'.py -- '+test['geo_parameters'].replace('/',' ')+' '+test['mat'].replace('/',' ')+' '+test['trans_rot'].replace('/',' '))
                os.system('mv '+'KUBC_'+th_KUBC_file_name.replace('.',',')+'.inp'  +' '+current_path[:-4]+'/inp_files/'+'KUBC_'+th_KUBC_file_name.replace('.',',')+'.inp' )
            th_PBC_file_name=test['sample_name']+'_'+test['geo_parameters'].replace('/','-')+'_'+test['mat'].replace('/','-')
            if 'PBC_'+th_PBC_file_name.replace('.',',')+'.csv' not in os.listdir(theory_directory) and 'PBC_'+th_PBC_file_name.replace('.',',')+'.inp' not in os.listdir(inp_dir):
                print('abaqus_2021 cae noGUI=th_gen/make_inp_PBC_'+test['sample_name']+'.py -- '+test['geo_parameters'].replace('/',' ')+' '+test['mat'].replace('/',' '))
                os.system('abaqus_2021 cae noGUI=th_gen/make_inp_PBC_'+test['sample_name']+'.py -- '+test['geo_parameters'].replace('/',' ')+' '+test['mat'].replace('/',' '))
                os.system('mv '+'PBC_'+th_PBC_file_name.replace('.',',')+'.inp'  +' '+current_path[:-4]+'/inp_files/'+'PBC_'+th_PBC_file_name.replace('.',',')+'.inp' )