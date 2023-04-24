import numpy as np
import math
from post_compute.post_config import *
import matplotlib.pyplot as plt
from math import *
import sys
try:
    sys.path.append("../src")
except:
    pass
import os
from constants import *
import json

def weighted_avg_and_std(values, weights):
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values-average)**2, weights=weights)
    return average, math.sqrt(variance)

def assign_cylinders(extracted_disp_and_force):
    DOF_FULL=12
    NB_CYL=10
    NB_SIDE=4
    cylinders=[]
    cylinders_names=[]

    for index in range(NB_CYL*NB_SIDE):
        data=extracted_disp_and_force['COU'][index*DOF_FULL:(index+1)*DOF_FULL]
        data_bc=extracted_disp_and_force['TBC'][index*DOF_FULL:(index+1)*DOF_FULL]
        side_number=int(index/(NB_CYL))
        cylinder_number =int(index%NB_CYL)
        if len(data_bc[0])>0:
            if len(data[0])==0:
                c=Cylinder(side_number,cylinder_number,data_bc[6:8],data_bc[11],data_bc[0:2],data_bc[5],None)
            else:
                c=Cylinder(side_number,cylinder_number,data[6:8],data[11],data_bc[0:2],data_bc[5],data_bc[6:8])
            cylinders.append(c)
            cylinders_names.append(c.name)
        else:
            cylinders.append(Cylinder(side_number,cylinder_number,
                                       [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]],
                                         [0.0, 0.0, 0.0, 0.0],
                                         [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]],
                                         [0.0, 0.0, 0.0, 0.0], None))

    cylinders_raw=cylinders[:]
    cylinders=[cylinders[0:10],cylinders[10:20],cylinders[20:30],cylinders[30:40]]
    return cylinders_raw,cylinders

def compute_force(side,direction,sens,step_of_interest,cylinders):
    force=0.0
    for cylinder in cylinders[side]:
        
        if cylinder:
            if sens=='+':
                force-=cylinder.rf[direction-1][step_of_interest]*(cylinder.number+1)/(NB_CYL+1)
            else:
                force-=cylinder.rf[direction-1][step_of_interest]*(NB_CYL-cylinder.number)/(NB_CYL+1)
    return force

def comp_1(A,B):
    A_vec=A.flatten()
    B_vec=B.flatten()
    r=100*sum([abs(a-B_vec[i]) for i,a in enumerate(A_vec)])/max(B_vec)/len(A_vec)
    return r

def ecart_rel_moyen(A,B): #B is ref
    A_vec=A.flatten()
    B_vec=B.flatten()
    r=100*sum([(a-B_vec[i])/B_vec[i] for i,a in enumerate(A_vec)])/len(A_vec)
    return r


def get_strain_from_disp(paths,res_folder, area, step_idx,nodes_coord):
    nodes_in_area=np.genfromtxt(os.path.join(res_folder,'nodes_per_area.csv'),delimiter=',',
                                deletechars='[]',skip_header=area-1, skip_footer=4-area,dtype = 'int')
    U_field=np.loadtxt(os.path.join(res_folder,'U_step-'+str(step_idx)+'.csv'),delimiter=',')
    A=[]
    U=[]
    for node in nodes_in_area[1:-1]:
        A.append([nodes_coord[node,1], 0, nodes_coord[node,2], 1, 0, -nodes_coord[node,2]])
        U.append([U_field[node,0]])
        A.append([0, nodes_coord[node,2], nodes_coord[node,1], 0, 1, nodes_coord[node,1]])
        U.append([U_field[node,1]])
    A=np.array(A)
    U=np.array(U)
    d=np.linalg.lstsq(A,U, rcond=None)
    return d[0],d[1]

def get_stress_average(paths, res_folder, area, step_idx,porosity):
    elements_in_area=np.genfromtxt(os.path.join(res_folder,'elements_per_area.csv'),delimiter=',',
                                deletechars='[]',skip_header=area-1, skip_footer=4-area,dtype = 'int')
    V_field=np.loadtxt(os.path.join(res_folder,'V_step-'+str(step_idx)+'.csv'),delimiter=',')
    V_field=V_field[:,1]
    S_field=np.loadtxt(os.path.join(res_folder,'S_step-'+str(step_idx)+'.csv'),delimiter=',')
    s_values=[]
    v_values=[]
    volume_total=0.0
    for element in elements_in_area[1:-1]:
        s_values.append(S_field[element])
        v_values.append(V_field[element])
        volume_total += v_values[-1]
    s_values=np.array(s_values)*(1-porosity)
    v_values=np.array(v_values)
    average11, std11=weighted_avg_and_std(s_values[:,0], v_values)
    average22, std22=weighted_avg_and_std(s_values[:,1], v_values)
    average12, std12=weighted_avg_and_std(s_values[:,3], v_values)
    min11, max11=np.min(s_values[:,0]),np.max(s_values[:,0])
    min22, max22=np.min(s_values[:,1]),np.max(s_values[:,1])
    min12, max12=np.min(s_values[:,3]),np.max(s_values[:,3])
    averages=[average11, average22, average12]
    stds=[std11,std22,std12]
    mins, maxs = [min11,min22, min12], [max11,max22, max12]
    return averages, stds, mins, maxs


def get_stress_average_whole_sample(root, folder_name, area, step_idx,porosity):
    V_field=np.loadtxt(root+'/results/'+folder_name+'/V_step-'+str(step_idx)+'.csv',delimiter=',')
    V_field=V_field[:,1]
    S_field=np.loadtxt(root+'/results/'+folder_name+'/S_step-'+str(step_idx)+'.csv',delimiter=',')
    s_values=S_field[:]
    v_values=V_field[:]
    s_values=np.array(s_values)*(1-porosity)
    v_values=np.array(v_values)
    average11, std11=weighted_avg_and_std(s_values[:,0], v_values)
    average22, std22=weighted_avg_and_std(s_values[:,1], v_values)
    average12, std12=weighted_avg_and_std(s_values[:,3], v_values)
    min11, max11=np.min(s_values[:,0]),np.max(s_values[:,0])
    min22, max22=np.min(s_values[:,1]),np.max(s_values[:,1])
    min12, max12=np.min(s_values[:,3]),np.max(s_values[:,3])
    averages=[average11, average22, average12]
    stds=[std11,std22,std12]
    mins, maxs = [min11,min22, min12], [max11,max22, max12]
    return averages, stds, mins, maxs

def compute_stiffness_matrix(stress,strain):
    b=np.array([stress[0][0],stress[1][0],stress[2][0],])
    a=np.array([[strain[0][0], strain[0][1], sqrt(2)*strain[0][2]],
                [strain[1][0], strain[1][1], sqrt(2)*strain[1][2]],
                [strain[2][0], strain[2][1], sqrt(2)*strain[2][2]]])
    k1j=np.linalg.solve(a, b)
    # Computation of K2j
    b=np.array([stress[0][1],stress[1][1],stress[2][1],])
    a=np.array([[strain[0][0], strain[0][1], sqrt(2)*strain[0][2]],
                [strain[1][0], strain[1][1], sqrt(2)*strain[1][2]],
                [strain[2][0], strain[2][1], sqrt(2)*strain[2][2]]])
    k2j=np.linalg.solve(a, b)
    # Computation of K3j
    b=np.array([stress[0][2],stress[1][2],stress[2][2],])
    a=1/sqrt(2)*np.array([[strain[0][0], strain[0][1], sqrt(2)*strain[0][2]],
                [strain[1][0], strain[1][1], sqrt(2)*strain[1][2]],
                [strain[2][0], strain[2][1], sqrt(2)*strain[2][2]]])
    k3j=np.linalg.solve(a, b)
    K=np.array([[k1j[0],k1j[1],k1j[2]],
                [k2j[0],k2j[1],k2j[2]],
                [k3j[0],k3j[1],k3j[2]]])

    return K

def get_porosity (test,paths):
    if test['sample_name']=='monolithic':
        return 0.0
    elif test['sample_name']=='honey':
        L, width=test['geo_parameters']
        porosity=((L/2-width/2)/(L/2))**2
        return porosity
    elif test['sample_name']=='rectangle':
        width_1, width_2, space_1, space_2=test['geo_parameters']
        return (space_1-width_1)*(space_2-width_2)/(space_1*space_2)
    else:
        with open(os.path.join(paths[POROSITY],'_'.join([test['sample_name'],str(test['geo_parameters'])])+'.json'),'r') as f:
            p=json.load(f)
            return float(p)


def compute_error(K1,K2):
    s=(K1[0,0]-K2[0,0])**2+(K1[1,1]-K2[1,1])**2+(K1[2,2]-K2[2,2])**2+ \
        ((K1[1,0]-K2[1,0])**2+(K1[0,1]-K2[0,1])**2)+\
        ((K1[2,0]-K2[2,0])**2+(K1[0,2]-K2[0,2])**2)+\
        ((K1[1,2]-K2[1,2])**2+(K1[2,1]-K2[2,1])**2)
    return round(100*sqrt(s)/np.max(K2),2)

def compute_total_deviation_matrix(L):
    deviations=np.empty((len(L),len(L)))
    deviations[:]=np.nan
    for idex_row in range(len(L)):
        for idex_column in range(idex_row,len(L)):
            deviations[idex_row,idex_column]=compute_error(L[idex_column],L[idex_row])
    return deviations

def dev_kii_E (L):
    deviations=np.empty((len(L),len(L)))
    deviations[:]=np.nan
    for idex_row in range(len(L)):
        for idex_column in range(idex_row,len(L)):
            deviations[idex_row,idex_column]=0.5*((L[idex_column][0,0]-L[idex_row][0,0])/L[idex_row][0,0]+
                                                  (L[idex_column][1,1]-L[idex_row][1,1])/L[idex_row][1,1])
    return 100*deviations

def dev_kij (L):
    deviations=np.empty((len(L),len(L)))
    deviations[:]=np.nan
    for idex_row in range(len(L)):
        for idex_column in range(idex_row,len(L)):
            deviations[idex_row,idex_column]=0.5*((L[idex_column][0,1]-L[idex_row][0,1])/L[idex_row][0,1]+
                                                  (L[idex_column][1,0]-L[idex_row][1,0])/L[idex_row][1,0])
    return 100*deviations

def dev_kii_G (L):
    deviations=np.empty((len(L),len(L)))
    deviations[:]=np.nan
    for idex_row in range(len(L)):
        for idex_column in range(idex_row,len(L)):
            deviations[idex_row,idex_column]=(L[idex_column][2,2]-L[idex_row][2,2])/L[idex_row][2,2]
    return 100*deviations

""" def plot_coeff_dev(dev_Ks,labs,title):
    fig, ax = plt.subplots()
    im = ax.imshow(dev_Ks,cmap='bwr',vmin=-np.max([np.nanmax(dev_Ks),-np.nanmin(dev_Ks)]),vmax=np.max([np.nanmax(dev_Ks),-np.nanmin(dev_Ks)]))
    # Show all ticks and label them with the respective list entries
    plt.xticks(np.arange(len(labs)), labels=labs)
    plt.yticks(np.arange(len(labs)), labels=labs)
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")
    # Loop over data dimensions and create text annotations.
    for i in range(len(labs)):
        for j in range(len(labs)):
            text = ax.text(j, i, '{:.2f}'.format(dev_Ks[i, j]) if not np.isnan(dev_Ks[i, j]) else '',
                        ha="center", va="center", color="black")
    ax.set_title(title)
    fig.tight_layout()
    plt.draw() """

def plot_coeff_dev(dev_Ks,labs,title,row,col,ax,borne):
    plt.sca(ax[row, col])
    im = plt.imshow(dev_Ks,cmap='bwr',vmin=-borne,vmax=borne)
    # Show all ticks and label them with the respective list entries
    plt.xticks(np.arange(len(labs)), labels=labs)
    plt.yticks(np.arange(len(labs)), labels=labs)
    # Rotate the tick labels and set their alignment.
    plt.xticks(rotation = 45,ha="right",rotation_mode="anchor")
    # Loop over data dimensions and create text annotations.
    for i in range(len(labs)):
        for j in range(len(labs)):
            text = plt.text(j, i, '{:.2f}'.format(dev_Ks[i, j]) if not np.isnan(dev_Ks[i, j]) else '',
                        ha="center", va="center", color="black")
    plt.title(title)