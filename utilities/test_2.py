import matplotlib.pyplot as plt
import numpy as np
from math import *
from classes import *
from funcData import *

np.set_printoptions(precision=2)

campagnes=['campagne_honey','campagne_honey_CC']

data=read_data_from_database(campagnes)
print(data.keys())
data_bulk = get_bulk_data(data)

print(data_bulk['honey_9_7_5_2'].campagne)

data_bulk['honey_9_7_5_2'].show_geo()