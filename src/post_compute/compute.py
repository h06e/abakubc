# import matplotlib.pyplot as plt
# import numpy as np
# import os
# from func import manipulation
# from post_compute import operation
# from post_compute.post_config import *
# import os
# import json

# from post_compute import post_reader


# def proceed_compute(TEST_ID):
#     CAMPAGNE_NAME='campagne_1'

#     header,campagne=manipulation.read_campagne(CAMPAGNE_NAME)
#     root=os.path.abspath(os.getcwd())[:-4]

#     index_test=next( (idx for (idx,t) in enumerate(campagne) if t['test_id']==TEST_ID),None)
#     folder_name=next((f for f in os.listdir(root+'/results/') if (not os.path.isfile(root+'/results/'+f)) and (TEST_ID in f)),None)
#     proceed_full_computation=True
#     if 'final_data.json' in os.listdir(os.path.abspath(os.getcwd())[:-4]+'/results/'+ folder_name+'/'):
#         if input('Froce computation ? (y for yes)')=='y': proceed_full_computation=True
#         else : proceed_full_computation=False
        
#     if proceed_full_computation:
#         test=campagne[index_test]
#         time_step, extracted_disp_and_force = post_reader.read_panto_data(folder_name)
#         thickness=float(test['thickness'])
#         porosity=operation.get_porosity(test)
#         print(f'Porosity of : {porosity}')
#         cylinders_raw,cylinders = operation.assign_cylinders(extracted_disp_and_force)
#         number_of_step=post_reader.get_number_of_step(test)
#         force_panto=[]
#         idx_of_steps=[]
#         for n_step in range(1,number_of_step+1):
#             step_of_interest=time_step.index(n_step)
#             idx_of_steps.append(step_of_interest)
#             force_panto.append({
#             'O_0_x':operation.compute_force(0,1,'-',step_of_interest,cylinders), 
#             'O_0_y':operation.compute_force(0,2,'-',step_of_interest,cylinders), 
#             'O_3_x':operation.compute_force(3,1,'-',step_of_interest,cylinders), 
#             'O_3_y':operation.compute_force(3,2,'-',step_of_interest,cylinders), 

#             'B_0_x':operation.compute_force(0,1,'+',step_of_interest,cylinders), 
#             'B_0_y':operation.compute_force(0,2,'+',step_of_interest,cylinders), 
#             'B_1_x':operation.compute_force(1,1,'-',step_of_interest,cylinders), 
#             'B_1_y':operation.compute_force(1,2,'-',step_of_interest,cylinders), 

#             'C_1_x':operation.compute_force(1,1,'+',step_of_interest,cylinders), 
#             'C_1_y':operation.compute_force(1,2,'+',step_of_interest,cylinders), 
#             'C_2_x':operation.compute_force(2,1,'+',step_of_interest,cylinders), 
#             'C_2_y':operation.compute_force(2,2,'+',step_of_interest,cylinders), 

#             'D_2_x':operation.compute_force(2,1,'-',step_of_interest,cylinders), 
#             'D_2_y':operation.compute_force(2,2,'-',step_of_interest,cylinders), 
#             'D_3_x':operation.compute_force(3,1,'+',step_of_interest,cylinders), 
#             'D_3_y':operation.compute_force(3,2,'+',step_of_interest,cylinders)
#             })

#         #-----------------
#         # Plots Froces in cylinders
#         forces_raw=[]
#         print("Forces in cylinders: Mean, STD, min, max")
#         plt.rcParams.update({'figure.autolayout': True})
#         fig, ax = plt.subplots(figsize=(4,3))
#         for step in range(3):
#             print("step ",step)
#             for cote in range(4):
#                 forces_raw.append([(c.rf[0][idx_of_steps[step]]**2+c.rf[1][idx_of_steps[step]]**2)**0.5 for c in cylinders[cote]])
#                 if cote==2:
#                     line, =ax.plot(range(0,10), forces_raw[-1] , ['r-','b--','g-'][step]+['x','*','x','*'][cote],lw=1.0)
#                     me,=ax.plot([0,9],[np.mean([(c.rf[0][idx_of_steps[step]]**2+c.rf[1][idx_of_steps[step]]**2)**0.5 for c in cylinders[cote]]*2)]*2 , ['r-.','b-.','g-.'][step])
#                     print('{:.2f}    {:.2f}    {:.2f}    {:.2f}'.format(np.mean(forces_raw[-1]),np.std(forces_raw[-1]),np.min(forces_raw[-1]),np.max(forces_raw[-1])))
#                     line.set_label('Step '+str(step+1))
#         ax.set(xlabel='Cylinder index', ylabel='Radial force norm [N]')
#         ax.grid()
#         ax.legend()
#         plt.ylim([0,250])
#         plt.ylim(bottom=0)
#         plt.draw()
#         plt.savefig(os.path.abspath(os.getcwd())[:-4]+'/results/'+ folder_name+'/force.pdf') 
#         plt.savefig(os.path.abspath(os.getcwd())[:-4]+'/results/'+ folder_name+'/force.png')   
#         print('---------------------------------------------')

#         #--------------------------------------------------
#         #Computation of the strain field from the displacement
#         # Resolve A*d=U with epsilon=[e11, e22, e12, MCR1, MCR2, MDRR12]

#         print('computing strain..')
#         nodes_coord=np.loadtxt(root+'/results/'+folder_name+'/node_coord.csv',delimiter=',')
#         area_of_interest=2
#         strain_field=[]
#         residuals=[]
#         for step_idx in range(1,4):
#             d,residual=operation.get_strain_from_disp(root, folder_name, area_of_interest, step_idx,nodes_coord)[:3]
#             strain_field.append([float(d[tmp]) for tmp in range(3)])
#             residuals.append(residual)
#             print(residual)

#         #---------------------------------------------
#         #Computation of the mean stress field
#         print('computing stress...')
#         area_of_interest=2
#         stress_field=[]
#         std_min_max=[]
#         for step_idx in range(1,4):
#             d,std_stress,minimum_stress,maximum_stress=operation.get_stress_average(root, folder_name, area_of_interest, step_idx,porosity)
#             stress_field.append([float(d[tmp]) for tmp in range(3)])
#             std_min_max.append([std_stress,minimum_stress,maximum_stress])
        
#         print(stress_field[0])
#         print(std_min_max[0])

#         #---------------------------------------
#         # Mean stress value according to panthos
#         print('Mean stress computation from the panthos...')
#         stress_pantos=[]
#         for step,force in enumerate(force_panto):
#             m_stress = np.array([[-(force['B_0_x'] + force['C_1_x'] + force['B_1_x'] + force['C_2_x']),
#                             -(force['D_3_x'] + force['D_2_x'] + force['C_2_x'] + force['C_1_x'])],
#                     [-(force['B_0_y'] + force['C_1_y'] + force['B_1_y'] + force['C_2_y']),
#                     -(force['D_3_y'] + force['D_2_y'] + force['C_2_y'] + force['C_1_y'])]])
#             n_stress = m_stress + m_stress.transpose()
#             SIDE_LENGTH=288.0
#             sigma  = 1.0/(2*SIDE_LENGTH*thickness) * (m_stress + m_stress.transpose())
#             stress_pantos.append([sigma[0,0],sigma[1,1],0.5*(sigma[0,1]+sigma[1,0])])

#         #--------------------------------------------
#         # Theoritical strain
#         strain_th=[]
#         for step in range(1,number_of_step+1):
#             strain_th.append([float(test['load_'+str(step)].split('/')[0])/100,
#                             float(test['load_'+str(step)].split('/')[1])/100,
#                             float(test['load_'+str(step)].split('/')[2])/2/100])

#         #--------------------------------------------
#         # Strain-Stress summary
#         print('------------------------------------')
#         print('SUMMARY\Strain:')
#         for step_idx in range(3):
#             print('Step: ',step_idx)
#             print('Theoritical strain:  {:0.3f} {:0.3f} {:0.3f}'.format(100*strain_th[step_idx][0],100*strain_th[step_idx][1],100*strain_th[step_idx][2]))
#             print('Field strain:        {:0.3f} {:0.3f} {:0.3f}'.format(100*strain_field[step_idx][0],100*strain_field[step_idx][1],100*strain_field[step_idx][2]))
#         print('Stress:')
#         for step_idx in range(3):
#             print('Step: ',step_idx)
#             print('Field stress:  {:0.3f} {:0.3f} {:0.3f}'.format(stress_field[step_idx][0],stress_field[step_idx][1],stress_field[step_idx][2]))
#             print('Pantho stress: {:0.3f} {:0.3f} {:0.3f}'.format(stress_pantos[step_idx][0],stress_pantos[step_idx][1],stress_pantos[step_idx][2]))

#         print('------------------------------------')
#         #--------------------------------------------
#         # stiffnesses

#         if test['sample_name']=='monolithic':
#             E=float(test['mat'].split('/')[0])
#             nu=float(test['mat'].split('/')[1])
#             K_plane_stress=np.linalg.inv((np.array([[1/E, -nu/E,0],[-nu/E, 1/E,0],[0,0,(1+nu)/E]])))
#         else:
#             # ! CHANGE HERE YOUR VALUES 
#             # ! ATTENTION
#             # ! ICIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
#             # ! AAAAAARRRRGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG
#             # Honey 28/4 150/0.3
#             K_plane_stress_PBC=np.array([[13.014957777505098, 10.412749877750175, 7.703973072981244e-06],
#                 [10.412749877750175, 13.014897098683347, 2.1595568548962513e-05],
#                 [7.703978377262062e-06, 2.1595571579980123e-05, 2.6021519965811786]])
#             K_plane_stress_KUBC=np.array([[13.536097679609131, 10.387561939380786, 4.201181131722396e-06],
#                 [10.387561939380786, 13.523589240180122, 1.4964061503735975e-05],
#                 [4.201153343024264e-06, 1.4964093262248128e-05, 3.002841973010405]])
#             """ # Honey 25.2/3.6 150/0.3
#             K_plane_stress_PBC=np.array([[13.015357558493202,	10.4128957482614,	7.121717798893703E-06],
#                 [10.4128957482614,	13.015442181449918,	1.4962062743560922E-05],
#                 [7.1217149923959186E-06,	1.4962065550058711E-05,	2.602526491303226]])
#             K_plane_stress_KUBC=np.array([[13.926175199908974,	10.194479388955200,	-0.0000107584905517],
#                 [10.1944793889552,	13.400800728503567,	-0.0000254186492949],
#                 [-1.0758487375820163E-05,	-0.000025418623888,	2.7776862368171598]]) """
#         K_field_dic=operation.compute_stiffness_matrix(stress_field,strain_field)
#         K_panto_dic=operation.compute_stiffness_matrix(stress_pantos,strain_field)
#         K_field_bc=operation.compute_stiffness_matrix(stress_field,strain_th)
#         K_panto_bc=operation.compute_stiffness_matrix(stress_pantos,strain_th)
#         # * SAVING
#         data={
#             'strain_th': strain_th,
#             'strain_field': strain_field,
#             'stress_field': stress_field,
#             'stress_pantos': stress_pantos,
#             'K_field_dic': K_field_dic.tolist(),
#             'K_panto_dic': K_panto_dic.tolist(),
#             'K_field_bc': K_field_bc.tolist(),
#             'K_panto_bc': K_panto_bc.tolist()
#         }
#         if test['sample_name']=='monolithic':data['K_plane_stress']=K_plane_stress.tolist();mono_sample=True
#         else:
#             mono_sample=False
#             data['K_plane_stress_PBC']=K_plane_stress_PBC.tolist()
#             data['K_plane_stress_KUBC']=K_plane_stress_KUBC.tolist()
#         with open(os.path.abspath(os.getcwd())[:-4]+'/results/'+ folder_name+'/final_data.json', "w") as fp:
#             json.dump(data, fp, indent=4, separators=(", ", ": "), sort_keys=True)  # encode dict into JSON

#     else:
#         K_plane_stress=0.0
#         with open(os.path.abspath(os.getcwd())[:-4]+'/results/'+ folder_name+'/final_data.json', "r") as fp:
#             # Load the dictionary from the file
#             data = json.load(fp)
#         locals().update(data)
#         if K_plane_stress: mono_sample=True
#         else :mono_sample=False

#     if mono_sample:
#         mono_sample=True
#         K_plane_stress=np.array(K_plane_stress)
#         print('K_plane_stress\n',K_plane_stress)
#     else:
#         K_plane_stress_PBC=np.array(K_plane_stress_PBC)
#         K_plane_stress_KUBC=np.array(K_plane_stress_KUBC)
#         print('K_plane_stress_PBC\n',K_plane_stress_PBC)
#         print('K_plane_stress_KUBC\n',K_plane_stress_KUBC)
#     K_field_dic=np.array(K_field_dic)
#     K_panto_dic=np.array(K_panto_dic)
#     print('K_field_dic\n',K_field_dic)
#     print('K_panto_dic\n',K_panto_dic)

#     if mono_sample:
#         Ks=[K_plane_stress,K_field_dic,K_panto_dic]
#     else:
#         Ks=[K_plane_stress_PBC,K_plane_stress_KUBC,K_field_dic,K_panto_dic]

#     global_deviation=operation.compute_total_deviation_matrix(Ks)
#     print('Deviation %')
#     print(global_deviation)

#     dev_Kii_E=operation.dev_kii_E(Ks)
#     dev_kij=operation.dev_kij(Ks)
#     dev_kii_G=operation.dev_kii_G(Ks)

#     #--------------------------------------------
#     # Plots
#     if mono_sample: labs=[r'Th.P$\sigma$','Field','Panto']
#     else: labs=['Th. PBC','Th. KUBC','Field','Panto']

#     borne=np.max([np.nanmax([dev_Kii_E,dev_kij,dev_kii_G]),-np.nanmin([dev_Kii_E,dev_kij,dev_kii_G])])
#     borneG=np.max([np.nanmax(global_deviation),-np.nanmin(global_deviation)])

#     fig, ax = plt.subplots(figsize=(3, 3))
#     im = plt.imshow(global_deviation,cmap='OrRd')
#     plt.xticks(np.arange(len(labs)), labels=labs)
#     plt.yticks(np.arange(len(labs)), labels=labs)
#     plt.xticks(rotation = 45,ha="right",rotation_mode="anchor")
#     # plt.setp(ax, rotation=45, ha="right",
#     #          rotation_mode="anchor")
#     # Loop over data dimensions and create text annotations.
#     for i in range(len(labs)):
#         for j in range(len(labs)):
#             text = plt.text(j, i, '{:.2f}'.format(global_deviation[i, j]) if not np.isnan(global_deviation[i, j]) else '',
#                         ha="center", va="center", color="black")
#     plt.title("Err. Glob.")
#     fig.tight_layout()
#     plt.savefig(os.path.abspath(os.getcwd())[:-4]+'/results/'+ folder_name+'/error_'+TEST_ID+'.pdf')  
#     plt.savefig(os.path.abspath(os.getcwd())[:-4]+'/results/'+ folder_name+'/error_'+TEST_ID+'.png',dpi=300)  
#     # plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)


# if __name__=="__main__":
#     exit()