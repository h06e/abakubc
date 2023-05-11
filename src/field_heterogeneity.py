import matplotlib.pyplot as plt
import numpy as np
import os
from func import manipulation
from post_compute import operation
from constants import *
import os


TEST_ID='mono_3D_mesh_2'
CAMPAGNE_NAME='campagne_mono'

header,campagne=manipulation.read_campagne(CAMPAGNE_NAME)
root=os.path.abspath(os.getcwd())[:-4]

index_test=next( (idx for (idx,t) in enumerate(campagne) if t['test_id']==TEST_ID),None)
folder_name=next((f for f in os.listdir(root+'/results/') if (not os.path.isfile(root+'/results/'+f)) and (TEST_ID in f)),None)

test=campagne[index_test]
porosity=operation.get_porosity(test)

step_of_interest=1
means=[]
stds=[]
mins=[]
maxs=[]
coeff_of_interest=0
for area in range(1,6):
    print(f'area : {area}')
    if area != 5:
        d,std_stress,minimum_stress,maximum_stress=operation.get_stress_average(root, folder_name, area, step_of_interest,porosity)
    else:
        d,std_stress,minimum_stress,maximum_stress=operation.get_stress_average_whole_sample(root, folder_name, area, step_of_interest,porosity)

    means.append(float(d[coeff_of_interest])) #s11
    stds.append(std_stress[coeff_of_interest])
    mins.append(minimum_stress[coeff_of_interest])
    maxs.append(maximum_stress[coeff_of_interest])
print(f'Valeurs moyennes : \n{means}')

fig, ax1 = plt.subplots(figsize=(5,3.5))
col=['b','g','r','m','k']
for area in range(5):
    ax1.errorbar([area],[means[area]],[[means[area]-mins[area]],[maxs[area]-means[area]]],fmt='_'+col[area],ecolor=col[area],lw=1,capsize=2)
    ax1.errorbar([area],[means[area]],stds[area],fmt='_'+col[area],lw=3,ms=15)

my_xticks = [r'$2p\times2p$',r'$4p\times4p$',r'$6p\times6p$',r'$8p\times8p$',f'whole\nspecimen']
plt.ylabel(r'$Local stress \sigma_{xx}$ [MPa]')
plt.xlabel('Area')
plt.xticks(np.arange(5), my_xticks)

plt.text(4-0.1,maxs[4],'max',horizontalalignment='right',verticalalignment='top')
plt.text(4-0.1,mins[4],'min',horizontalalignment='right',verticalalignment='bottom')
plt.text(4-0.1,means[4],f'mean\n('+r'$\pm$ std)',horizontalalignment='right',verticalalignment='center')


fig.tight_layout()
plt.grid()
ax2=fig.add_axes([0.3, 0.6, 0.3, 0.3])
plt.xticks(np.arange(3), my_xticks[:3])
plt.xticks(rotation = 20,ha="right",rotation_mode="anchor")
for area in range(3):
    ax2.errorbar([area],[means[area]],[[means[area]-mins[area]],[maxs[area]-means[area]]],fmt='_'+col[area],ecolor=col[area],lw=1,capsize=2)
    ax2.errorbar([area],[means[area]],stds[area],fmt='_'+col[area],lw=3,ms=15)


plt.savefig('tests/stress_per_area.pdf') 
plt.savefig('tests/stress_per_area.png',dpi=300) 
plt.show()

