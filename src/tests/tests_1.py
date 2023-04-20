import matplotlib.pyplot as plt
import numpy as np

""" means=np.array([0.21058610055590618,0.21046708958276225,0.2102853119227517,0.21020146383814173])
stds=np.array([0.00011508158292594744,0.00027809859113104337,0.0006457321390692652,0.0029065411371402413])
mins=np.array([0.21005766,0.20847206,0.20723689,-0.00040794315])
maxs=np.array([0.21070209,0.2116267,0.2118811,0.6144226])

fig, ax1 = plt.subplots(figsize=(5,3))
ax1.errorbar(np.arange(4),means,stds,fmt='ok',lw=2)
ax1.errorbar(np.arange(4),means,[means-mins,maxs-means],fmt='.k',ecolor='gray',lw=1,capsize=2)
my_xticks = [r'Area 1','Area 2','Area 3','Area 4']
plt.ylabel(r'$\sigma_{xx}$ [MPa]')
plt.xticks(np.arange(4), my_xticks)
fig.tight_layout()
plt.show()
plt.savefig('tests/stress_per_area.pdf') 
plt.savefig('tests/stress_per_area.png') 
 """

means=np.array([0.21058610055590618,0.21046708958276225,0.2102853119227517])
stds=np.array([0.00011508158292594744,0.00027809859113104337,0.0006457321390692652])
mins=np.array([0.21005766,0.20847206,0.20723689])
maxs=np.array([0.21070209,0.2116267,0.2118811])

fig, ax1 = plt.subplots(figsize=(4,3))
ax1.errorbar(np.arange(3),means,[means-mins,maxs-means],fmt='.k',ecolor='gray',lw=1,capsize=2)
ax1.errorbar(np.arange(3),means,stds,fmt='ok',lw=2)
my_xticks = [r'$2p\times2p$',r'$4p\times4p$',r'$8p\times8p$']
plt.ylabel(r'$\sigma_{xx}$ [MPa]')

plt.xticks(np.arange(3), my_xticks)
fig.tight_layout()
plt.savefig('tests/stress_per_area.pdf') 
plt.savefig('tests/stress_per_area.png') 
plt.draw()


angle=[0,5,10,15,20,25]
err_petit=[2.55,2.37,1.85,3.59,1.84,2.44]
err_grand=[1.71,8.91,1.32,2.34,1.20,8.72]

plt.figure(figsize=(5,4))
plt.plot(angle,err_petit,'b-o',label='Motif 25.2/3.6')
plt.plot(angle,err_grand,'r-^',label='Motif 28/4.0')

plt.xlabel('Rotation [°]')
plt.ylabel('Err. Glob. [%]')
plt.grid()
plt.legend()
plt.tight_layout()
plt.savefig('tests/rotation_effect.pdf') 
plt.savefig('tests/rotation_effect.png') 
plt.draw()


tran_petit=[0,3.6,7.2,10.8,14.4,18,21.8]
err_petit=[2.55,2.54,3.11,3.74,3.74,3.11,2.56]
trans_grand=[0,4,8,12,16,20,24]
err_grand=[1.71,1.79,2.65,2.57,3.28,2.13,1.74]

plt.figure(figsize=(5,4))
plt.plot(tran_petit,err_petit,'b-o',label='Motif 25.2/3.6')
plt.plot(trans_grand,err_grand,'r-^',label='Motif 28/4.0')

plt.xlabel('Translation [mm]')
plt.ylabel('Err. Glob. [%]')
plt.grid()
plt.legend()
plt.tight_layout()
plt.savefig('tests/translation_effect.pdf') 
plt.savefig('tests/translation_effect.png') 
plt.draw()
plt.show()