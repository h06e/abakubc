from classes import *
from funcData import *
import numpy as np
from math import *
import json
from datetime import date
np.set_printoptions(precision=2)


campagnes = ['campagne_honey','campagne_honey_CC','campagne_honey_UR3_S7','campagne_honey_UR3_S13',
             'campagne_carre','campagne_carre_CC','campagne_carre_UR3_S7','campagne_carre_UR3_S13',
             'campagne_trian','campagne_trian_CC','campagne_trian_UR3_S7','campagne_trian_UR3_S13',
             'campagne_hexac','campagne_hexac_CC','campagne_hexac_UR3_S7','campagne_hexac_UR3_S13']

for campagne in campagnes:
    data=read_data_from_campaigns([campagne])
    data_bulk = get_bulk_data(data)

    exp_dict={'date_of_creation':str(date.today())}
    keys=list(data_bulk.keys())
    for i_k,k in enumerate(keys):
        exp_dict |= {data_bulk[k].test_id:data_bulk[k].get_exportable_dict()}


    with open(f'../database/{campagne}.json', 'w') as f:
        json.dump(exp_dict, f, indent=4, separators=(", ", ": "), sort_keys=True)  # encode dict into JSON

    # # - - - - - - - - -

    # with open('campagne_honey.json', 'r') as f:
    #     data_from_file = json.load(f)

    # print(len(data_from_file.keys()))