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


# * * * * * * * * * * * * * * * * * * * * *
# * Graph with error per angle and per size

N_theta, N_scale, N_tx, N_ty = (12, 7, 10, 5)
EOI = (0, 3)

error_per_angle = np.empty((N_theta+1, N_scale, N_tx, N_ty))
error_per_angle[:] = np.nan
for test_id, test in data.items():
    scale, angle, idx, idy = tuple(map(int, test_id.split('_')[1:]))
    error_per_angle[angle, scale-7, idx,
                    idy] = test.global_err[EOI[0]][EOI[1]]
    if angle == 0:
        error_per_angle[-1, scale-7, idx,
                        idy] = test.global_err[EOI[0]][EOI[1]]

error_per_angle_mean = np.nanmean(error_per_angle, axis=(2, 3))
error_per_angle_q1 = np.nanquantile(error_per_angle, 0.25, axis=(2, 3))
error_per_angle_q2 = np.nanquantile(error_per_angle, 0.75, axis=(2, 3))
error_per_angle_min = np.nanmin(error_per_angle, axis=(2, 3))
error_per_angle_max = np.nanmax(error_per_angle, axis=(2, 3))

plt.figure(figsize=(12, 4))
x = np.linspace(0, N_theta, N_theta+1)-0.5+1/N_theta
col = ['b', 'g', 'r', 'm', 'k', 'c', 'y']
leg = [f'{i}/10 scale' for i in range(7, 14)]

for scale in range(N_scale):
    plt.errorbar(x+scale/N_scale, error_per_angle_mean[:, scale], [error_per_angle_mean[:, scale]-error_per_angle_q1[:, scale], error_per_angle_q2[:, scale] - error_per_angle_mean[:, scale]],
                 fmt=col[scale]+'_', lw=3, ms=1, label=f'{leg[scale]}')
    plt.errorbar(x+scale/N_scale, error_per_angle_mean[:, scale], [error_per_angle_mean[:, scale]-error_per_angle_min[:, scale], error_per_angle_max[:, scale] - error_per_angle_mean[:, scale]],
                 fmt='_'+col[scale], ecolor=col[scale], lw=1, capsize=2)
    for i, m in enumerate(error_per_angle_max[:, scale]):
        if m > 30.0:
            plt.text(x[i]+scale/N_scale,
                     30.0, f'{m:.0f}', ha='center', fontsize=8)

for i in range(12):
    plt.axvline(x=i+0.5, color='k', ls='--', lw=1.0)

plt.ylim((0, 30))
plt.xlim((-0.5, 12.5))
plt.xticks(range(13), [f'{2.5*i}°' for i in range(13)])
plt.legend()
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xlabel('Angle [°]')
plt.ylabel(f'Error distribution [%]')
plt.tight_layout()
plt.draw()

# ******* Return the best test *****************
best_test_key, best_test = get_best_test(data, (0, 3))
print(
    f'The best test was achieved with the {best_test_key} leading to an error of {best_test.global_err[0][3]}')


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# * Plot les coef des matrices de rigité de l'echelle 7/10 comparé au KUBC et PBC tourné matriciellement

small_scale_test = get_tests_by_test_id(data, index=1, target='7')

data_per_angle = np.empty((N_theta+1, N_tx, N_ty, 3, 3))
data_per_angle[:] = np.nan
data_per_angle_KUBC = np.empty((N_theta+1, N_tx, N_ty, 3, 3))
data_per_angle_KUBC[:] = np.nan
for test_id, test in small_scale_test.items():
    _, angle, idx, idy = tuple(map(int, test_id.split('_')[1:]))
    data_per_angle[angle, idx,
                   idy, :, :] = np.array(test.K_panto_dic)
    data_per_angle_KUBC[angle, idx,
                   idy, :, :] = np.array(test.K_plane_stress_KUBC)
    if angle == 0:  # Periodicite à 30°
        data_per_angle[-1, idx,
                       idy, :, :] = np.array(test.K_panto_dic)
        data_per_angle_KUBC[-1, idx,
                       idy, :, :] = np.array(test.K_plane_stress_KUBC)

data_per_angle_mean = np.nanmean(data_per_angle, axis=(1, 2))
data_per_angle_q1 = np.nanquantile(data_per_angle, 0.25, axis=(1, 2))
data_per_angle_q2 = np.nanquantile(data_per_angle, 0.75, axis=(1, 2))
data_per_angle_min = np.nanmin(data_per_angle, axis=(1, 2))
data_per_angle_max = np.nanmax(data_per_angle, axis=(1, 2))

data_per_angle_KUBC_mean = np.nanmean(data_per_angle_KUBC, axis=(1, 2))
data_per_angle_KUBC_q1 = np.nanquantile(data_per_angle_KUBC, 0.25, axis=(1, 2))
data_per_angle_KUBC_q2 = np.nanquantile(data_per_angle_KUBC, 0.75, axis=(1, 2))
data_per_angle_KUBC_min = np.nanmin(data_per_angle_KUBC, axis=(1, 2))
data_per_angle_KUBC_max = np.nanmax(data_per_angle_KUBC, axis=(1, 2))


theorique = test.K_plane_stress_PBC

coefs = ((0, 0), (0, 1), (2, 2))
leg = ('K11', 'K12', 'K33')
col = ['b', 'r', 'g', 'm']
plt.figure()
x = np.linspace(0, 30, N_theta+1)
for idx, coef in enumerate(coefs):
    plt.errorbar(x, data_per_angle_mean[:, coef[0], coef[1]], [data_per_angle_mean[:, coef[0], coef[1]]-data_per_angle_q1[:, coef[0], coef[1]], data_per_angle_q2[:, coef[0], coef[1]] - data_per_angle_mean[:, coef[0], coef[1]]],
                 fmt=col[idx]+'_', lw=3, ms=1, label=f'{leg[idx]}')
    plt.errorbar(x, data_per_angle_mean[:, coef[0], coef[1]], [data_per_angle_mean[:, coef[0], coef[1]]-data_per_angle_min[:, coef[0], coef[1]], data_per_angle_max[:, coef[0], coef[1]] - data_per_angle_mean[:, coef[0], coef[1]]],
                 fmt=col[idx]+'_', ecolor=col[idx], lw=1, capsize=2)
    
    plt.errorbar(x+0.5, data_per_angle_KUBC_mean[:, coef[0], coef[1]], [data_per_angle_KUBC_mean[:, coef[0], coef[1]]-data_per_angle_KUBC_q1[:, coef[0], coef[1]], data_per_angle_KUBC_q2[:, coef[0], coef[1]] - data_per_angle_KUBC_mean[:, coef[0], coef[1]]],
                 fmt='k_', lw=3, ms=1, label=f'{leg[idx]} KUBC')
    plt.errorbar(x+0.5, data_per_angle_KUBC_mean[:, coef[0], coef[1]], [data_per_angle_KUBC_mean[:, coef[0], coef[1]]-data_per_angle_KUBC_min[:, coef[0], coef[1]], data_per_angle_KUBC_max[:, coef[0], coef[1]] - data_per_angle_KUBC_mean[:, coef[0], coef[1]]],
                 fmt='k_', ecolor='k', lw=1, capsize=2)

xx = np.linspace(0, 30, 200)
K_list = []
K_th = test.K_plane_stress_PBC
for x in xx:
    angle = x*pi/180
    c, s = cos(angle), sin(angle)
    T = np.array([[c**2, s**2, c*s],
                  [s**2, c**2, -c*s],
                  [-2*s*c, 2*c*s, (c**2-s**2)]])
    K = np.dot(np.dot(np.transpose(T), K_th), T)
    K_list.append(K)
K_list = np.array(K_list)
sty = [':', '--', ':', '-.']
for idx, coef in enumerate(coefs):
    plt.plot(xx, K_list[:, coef[0], coef[1]],
             'k'+sty[idx], label=f'PBC {leg[idx]}')

plt.grid()
plt.legend()
plt.xlabel('Angle [°]')
plt.ylabel('Stiffness [MPa]')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()

plt.show()

# * * * * * * * * * * * * * * * * * * * * * * * * * *
