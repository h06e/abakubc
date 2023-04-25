import numpy as np
from math import *
import matplotlib.pyplot as plt
import json
import os

def plot_K (K_0,coeff, theory=False):

    K_list = []
    theta_list = np.arange(0, 2*pi, pi/1000)

    for t in theta_list:
        angle = t
        c, s = cos(angle), sin(angle)
        T = np.array([[c**2, s**2, c*s],
                    [s**2, c**2, -c*s],
                    [-2*s*c, 2*c*s, (c**2-s**2)]])
        K = np.dot(np.dot(np.transpose(T), K_0), T)
        K_list.append(K)


    K_list = np.array(K_list)
    
    for c in coeff:
        if theory:
            plt.plot(theta_list, K_list[:, c[0], c[1]],'k--',label=f'$K{c} ref$')
        else:
            plt.plot(theta_list, K_list[:, c[0], c[1]],label=f'$K{c}$')

    plt.grid(True)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))



test_name='Z_test_honey_2'
campagne_name='campagne_test'
with open(f'{campagne_name}/results/{test_name}/final_data.json') as f:
    data = json.load(f)

K_db = np.array(data['K_panto_dic'])
K_PS = np.array(data['K_plane_stress_PBC'])
plt.subplots(subplot_kw={'projection': 'polar'})
plot_K(K_db, ((0,0),(1,1), (0,1), (2,2)) )
plot_K(K_PS, ((0,0),(1,1), (0,1), (2,2)), True )
plt.show()
exit()
# # * Cf equation 2 de vannucci terme avec R0
# res_Re = K_list[:, 0, 0]-2*K_list[:, 1, 0]-4*K_list[:, 2, 2]+K_list[:, 1, 1]
# res_Im = K_list[:, 0, 2]-K_list[:, 1, 2]
# plt.figure()
# plt.plot(theta_list, res_Re, 'r', label='Partie réelle')
# plt.plot(theta_list, res_Im, 'b', label='Partie imaginaire')
# plt.plot(theta_list, K_list[:, 2, 2], 'k', label=r'$K_{33}$')
# plt.legend()
# plt.show()


# ********************************************************

# * Calcul d'un composite 0/45 
# * Dans la base du pli
K_pli_0=np.array([[100,3,0.0], [3,10,0], [0,0,5]])

angle = pi/4
c, s = cos(angle), sin(angle)
T = np.array([[c**2, s**2, c*s],
                [s**2, c**2, -c*s],
                [-2*s*c, 2*c*s, (c**2-s**2)]])
K_pli_45 = np.dot(np.dot(np.transpose(T), K_pli_0), T)

K_empilement=0.5*(K_pli_0+K_pli_45)

K_list = []
theta_list = np.arange(0, 2*pi, pi/1000)

for t in theta_list:
    angle = t
    c, s = cos(angle), sin(angle)
    T = np.array([[c**2, s**2, c*s],
                  [s**2, c**2, -c*s],
                  [-2*s*c, 2*c*s, (c**2-s**2)]])
    K = np.dot(np.dot(np.transpose(T), K_empilement), T)
    K_list.append(K)


K_list = np.array(K_list)
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.plot(theta_list, K_list[:, 0, 0], 'r', label=r'$K_{11}$')
ax.plot(theta_list, K_list[:, 1, 1], 'g', label=r'$K_{22}$')
ax.plot(theta_list, K_list[:, 0, 1], 'b', label=r'$K_{12}$')
ax.plot(theta_list, K_list[:, 2, 2], 'k', label=r'$K_{33}$')

ax.grid(True)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax.set_title("Exemple d'un composite 0/45", va='bottom')
plt.draw()


K_list=K_list
# * Cf equation 2 de vannucci terme avec R0
res_Re = K_list[:, 0, 0]-2*K_list[:, 1, 0]-4*K_list[:, 2, 2]+K_list[:, 1, 1]
res_Im = K_list[:, 0, 2]-K_list[:, 1, 2]
plt.figure()
plt.plot(theta_list, res_Re, 'r', label='Partie réelle')
plt.plot(theta_list, res_Im, 'b', label='Partie imaginaire')
plt.plot(theta_list, K_list[:, 2, 2], 'k', label=r'$K_{33}$')
plt.legend()
plt.show()