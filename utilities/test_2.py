import matplotlib.pyplot as plt
import numpy as np
from math import *
from classes import *
from funcData import *

np.set_printoptions(precision=2)

campagnes = ['campagne_honey','campagne_honey_CC','campagne_honey_UR3_S7','campagne_honey_UR3_S13',
             'campagne_carre','campagne_carre_CC','campagne_carre_UR3_S7','campagne_carre_UR3_S13',
             'campagne_trian','campagne_trian_CC','campagne_trian_UR3_S7','campagne_trian_UR3_S13',
             'campagne_hexac','campagne_hexac_CC','campagne_hexac_UR3_S7','campagne_hexac_UR3_S13']

data=read_data_from_database(campagnes)
print(data.keys())
data_bulk = get_bulk_data(data)

print(data_bulk['honey_9_7_5_2'].campagne)

data_bulk['honey_9_7_5_2'].show_geo()