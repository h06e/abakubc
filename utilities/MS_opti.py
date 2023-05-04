from funcData import *
from classes import *
import numpy as np
import matplotlib.pyplot as plt
from math import *

campagnes = ['campagne_honey']
data = get_bulk_data(read_data_from_campaigns(campagnes))

# test=data[list(data.keys())[0]]
test=data['honey_10_0_5_0']

print(test.skipped_cyl)
print(test.get_MS())
print(test.test_id)
print(get_mean_MS_worse_side(test))
print(get_barycentre(test, True))

#* Error of interest
EOI=(0,3)
function=['get_mean_MS','get_mean_MS_worse_side','get_mean_MS_worse_side_pair',
          'get_mean_MS_worse_corner', 'get_max_MS_consecutive']

plt.figure(figsize=(20,5))
for i, func in enumerate(function):
    err=[]
    criteria=[]
    for _,test in data.items():
        if eval(func)(test) is not None:
            err.append(test.get_err(EOI))
            criteria.append(eval(func)(test))
    plt.subplot(151+i)
    plot_box2(criteria,err, step=0.1, ylabel=f'{func}')
    

plt.tight_layout()
plt.show()