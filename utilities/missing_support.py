from funcData import *
from classes import *
import numpy as np
import matplotlib.pyplot as plt
from math import *
"""
The aim is here to study the effect of missing cylinders on the results
Only basics plots are made to find preliminary tendences.

This will likely motivate a further study with a minimizing algorithm
"""


# * Importing the data from the campaign.
campagnes = ['campagne_honey']
data = get_bulk_data(read_data_from_campaigns(campagnes))


index_error = (0, 3)

# * * * * * * * * * * * * * * * * * * * * * * * * *
# * Erreur en fonction du nombre de support absent
x_scatter, y_scatter = [], []
for test_id, test in data.items():
    err = test.global_err[index_error[0]][index_error[1]]
    number_missing_support = sum([len(i) for i in test.skipped_cyl])
    x_scatter.append(number_missing_support)
    y_scatter.append(err)

X_sorted, Y_sorted = (list(t) for t in zip(*sorted(zip(x_scatter, y_scatter))))
X_bulk, Y_bulk = [], []
old = None
for x, y in zip(X_sorted, Y_sorted):
    if x == old:
        Y_bulk[-1].append(y)
    else:
        X_bulk.append(x)
        Y_bulk.append([y])
        old = x

y_mean = []
y_q1 = []
y_q2 = []
y_min = []
y_max = []
for y in Y_bulk:
    y_mean.append(np.mean(np.array(y)))
    y_q1.append(np.quantile(np.array(y), 0.25))
    y_q2.append(np.quantile(np.array(y), 0.75))
    y_min.append(np.min(np.array(y)))
    y_max.append(np.max(np.array(y)))
y_mean = np.array(y_mean)
y_q1 = np.array(y_q1)
y_q2 = np.array(y_q2)
y_min = np.array(y_min)
y_max = np.array(y_max)
plt.figure()
plt.errorbar(X_bulk, y_mean,
             [y_mean-y_q1,
              y_q2 - y_mean],
             fmt='b_', lw=3, ms=1, label='[min - Q1 - mean - Q3 - max]')
plt.errorbar(X_bulk, y_mean,
             [y_mean-y_min, y_max - y_mean],
             fmt='b_', ecolor='b', lw=1, capsize=2)

fit = np.polyfit(x_scatter, y_scatter, 1)
plt.plot([0.0, max(x_scatter)], [fit[1], fit[1]+fit[0]
                                 * max(x_scatter)], 'k:', label='linear fit')

plt.ylabel('Error PBC - Panto+DIC')
plt.xlabel('Number of missing supports')
plt.legend(loc='upper center')
plt.twinx()
plt.plot(X_bulk, [len(b) for b in Y_bulk], 'r')
plt.ylabel('Number of tests', color='r')
plt.xticks(range(21))
plt.tight_layout()
plt.draw()

# * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# * Erreur en fonction de la position du support manquant

x_scatter, y_scatter = range(5), [[],[],[],[],[]]
for test_id, test in data.items():
    err = test.global_err[index_error[0]][index_error[1]]
    missing_support = []
    for cote in test.skipped_cyl:
        for i in cote:
            ii = i if i <= 4 else 9-i
            if ii not in missing_support:
                missing_support.append(ii)
                y_scatter[ii].append(err)

y_mean = []
y_q1 = []
y_q2 = []
y_min = []
y_max = []
for y in y_scatter:
    y_mean.append(np.mean(np.array(y)))
    y_q1.append(np.quantile(np.array(y), 0.25))
    y_q2.append(np.quantile(np.array(y), 0.75))
    y_min.append(np.min(np.array(y)))
    y_max.append(np.max(np.array(y)))
y_mean = np.array(y_mean)
y_q1 = np.array(y_q1)
y_q2 = np.array(y_q2)
y_min = np.array(y_min)
y_max = np.array(y_max)
plt.figure()
plt.plot(x_scatter, y_mean, 'b:')
plt.errorbar(x_scatter, y_mean,
             [y_mean-y_q1,
              y_q2 - y_mean],
             fmt='b_', lw=3, ms=1, label='[min - Q1 - mean - Q3 - max]')
plt.errorbar(x_scatter, y_mean,
             [y_mean-y_min, y_max - y_mean],
             fmt='b_', ecolor='b', lw=1, capsize=2)

plt.ylim((-1,14))
plt.xticks(range(5))
plt.xlabel('Index of the cylinder')
plt.ylabel('Error [%]')
plt.twinx()
plt.plot(x_scatter, [len(b) for b in y_scatter], 'r')
plt.ylabel('Number of test', color='r')

plt.tight_layout()
plt.show()

# *************************************************

