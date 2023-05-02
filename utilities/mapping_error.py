from funcData import *
from classes import *
import numpy as np
import matplotlib.pyplot as plt
"""
The aim is here to study the effect of missing cylinders on the results
Only basics plots are made to find preliminary tendences.

This will likely motivate a further study with a minimizing algorithm
"""


# * Importing the data from the campaign.
campagnes = ['campagne_honey_2']
data = get_bulk_data(read_data_from_campaigns(campagnes))

# for t in data:
#     data[t].export_geo(Path('./tmp'))

error_type = (0,3)
d=np.zeros((11,11))
for test_id, test in data.items():
    scale ,angle, idx, idy = tuple(map(int, test_id.split('_')[1:]))
    d[idx,idy]=test.global_err[error_type[0]][error_type[1]] 

d[10,:]=d[0,:]
d[:,10]=d[:,0]

a=d-(np.flip(np.flip(d,1),0))

plt.figure()
plt.imshow(a)
plt.colorbar()
plt.show()

# error_type = (0,3)
# error_per_angle = np.empty((12,7,10,5))
# error_per_angle[:]=np.nan
# for test_id, test in data.items():
#     scale ,angle, idx, idy = tuple(map(int, test_id.split('_')[1:]))
#     error_per_angle[angle,scale-7,idx,idy]=test.global_err[error_type[0]][error_type[1]]


