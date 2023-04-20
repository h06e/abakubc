from func import manipulation
import os

true_list=['1','True','true','oui','Oui']
false_list=['0','False','false','non','N','']

campagne_name='campagne_1'
header,campagne=manipulation.read_campagne(campagne_name)
path=os.path.abspath(os.getcwd())+'/'

for test in campagne:
    if test['sample_name']not in ['monolithic','honey']:
        if test['sample_name']+str(test['geo_parameters'])+str(test['thickness'])+'.sat' not in os.listdir('sample_bank/'):
            print('The geometry is not supported. See /src/geometry and sample_bank/\nTermination: Consistency Error test {}.'.format(test['test_id']))
            exit()
    elif test['corner_cleaner'] not in ['','STD','ADV_SHEAR']:
        print('The cutter is unknown.\nTermination: Consistency Error test {}.'.format(test['test_id']))
        exit()
    elif test['force_clean'] not in true_list+false_list:
        print('force_clean parameter should 1 or 0.\nTermination: Consistency Error test {}.'.format(test['test_id']))
        exit()
    elif test['free_rotation'] not in true_list+false_list:
        print('free_rotation parameter should 1 or 0.\nTermination: Consistency Error test {}.'.format(test['test_id']))
        exit()
    elif test['perfect_panto'] not in true_list+false_list:
        print('perfect_panto parameter should 1 or 0.\nTermination: Consistency Error test {}.'.format(test['test_id']))
        exit()
    elif test['flag_make_inp'] not in true_list+false_list:
        print('flag_make_inp parameter should 1 or 0.\nTermination: Consistency Error test {}.'.format(test['test_id']))
        exit()

                                
