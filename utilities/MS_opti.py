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
          'get_mean_MS_worse_corner', 'get_max_MS_consecutive', 'get_barycentre']

plt.figure(figsize=(20,5))
for i, func in enumerate(function):
    data_raw=[]
    data_fit=[]
    for test_id,test in data.items():
        if eval(func)(test) is not None:
            data_raw.append(test.get_err(EOI))
            data_fit.append(eval(func)(test))

    plt.subplot(161+i)
    if func in ['get_barycentre']:
        plt.scatter(data_fit,data_raw,0.3)
    else:
        plot_box(data_fit,data_raw)
    plt.xlabel(f'critère {func}')
    plt.ylabel('erreur')

plt.tight_layout()
plt.show()