# -*- coding: mbcs -*-
from abaqus import *
from abaqusConstants import *
from caeModules import *
from odbAccess import *
import sys
try:
    sys.path.append("../src")
except:
    pass
import os
import time
import csv
from numpy import nan
import numpy as np
from post_extract import field, attachment_point
from constants import *
import json

def log(message):
    print >> sys.__stdout__, message



test = eval(sys.argv[-2])
for i in test:
    if len(test[i]) == 0:
        test[i] = None
    else:
        try:
            test[i] = eval(test[i]) if i not in ['sample_name', 'status', 'comment', 'err'] else test[i]
        except NameError:
            pass

paths = eval(sys.argv[-1])


res_folder = os.path.join(paths[RES_DIR], test['test_id'])
try:
    os.mkdir(res_folder)
except:
    pass

odb = session.openOdb(name='{}.odb'.format(test['test_id']))


# Get the name of the part (DON'T WORK IF MORE THAN ONE PART)
instances = odb.rootAssembly.instances.items()
if len(instances) > 2:
    print("More than two instances have been detected. The script cannot handle this.")
    exit()
for item in instances:
    if item[0] != 'ASSEMBLY':
        PART_NAME2 = item[0]

file_pathName = os.path.abspath(os.getcwd())+'/'

cylinder_output_filename = os.path.join(res_folder, 'cyldata.json')


# ------------------------------------------------------------------------------------------------------------------------------------------
"""Displacement of the speciment (with rotation !!) and the force in each cylinder"""
# Commente le 16 juin. 
# DOF = 12
# N_CY = 10  # number of cylinder per side
# time_step = []
# extracted_disp_and_force = {
#     'COU': [[]]*(10*4*12),
#     'TBC': [[]]*(10*4*12)
# }

# flag_first_step = False
# for idx_step, step_name in enumerate(odb.steps.keys()):
#     history_region_keys = odb.steps[step_name].historyRegions.keys()
#     flag_step = False
#     for hist in history_region_keys:
#         region_type = hist.split(' ')[0]
#         if region_type == 'Node':
#             description = odb.steps[step_name].historyRegions[hist].description
#             side = description.split('_')[1]
#             cylinder_number = description.split('_')[2]
#             type_of_point = description.split(' ')[-1][-7:-4]
#             output = odb.steps[step_name].historyRegions[hist].historyOutputs
#             dep, time_over_step = attachment_point.clean_out(output)
#             index = attachment_point.compute_index(side, cylinder_number)
#             attachment_point.add_data(
#                 dep, index, type_of_point, extracted_disp_and_force, flag_first_step)
#             if not flag_step:
#                 time_step = time_step + \
#                     list(np.array(time_over_step)+idx_step)[1*flag_first_step:]
#                 flag_step = True
#     flag_first_step = True

# attachment_point.save_into_csv(
#     report1_name, extracted_disp_and_force['COU'], time_step)
# attachment_point.save_into_csv(
#     report2_name, extracted_disp_and_force['TBC'], time_step)


def get_name_point(description):
    type_of_point = description.split(' ')[-1][-7:-4]
    point_name = type_of_point + '_' + "_".join(description.split("_")[1:])
    return point_name

def get_dict_for_the_point (history_output):
    data={}
    for component in history_output.keys():
        data[component] = history_output[component].data[-1][1] # Le dernier du step, [1] pour prendre la valeur ([0] contient le temps)
    return data

out_cylinder_step=[]

for idx_step, step_name in enumerate(odb.steps.keys()):
    extracted_disp_and_force={}
    for hist_region in odb.steps[step_name].historyRegions.keys():
        if hist_region.split(' ')[0] != 'Node':
            continue
        point_name = get_name_point(odb.steps[step_name].historyRegions[hist_region].description) # de 'Output at instance SAMPLE node 8737 region PTBC_T_6' a 'TBC_T_6'
        extracted_disp_and_force[point_name] = get_dict_for_the_point(odb.steps[step_name].historyRegions[hist_region].historyOutputs).copy()
        print(point_name)
    out_cylinder_step.append(extracted_disp_and_force.copy())

with open(cylinder_output_filename, 'w') as f:
    json.dump(out_cylinder_step, f)

# -----------------------------------------------------------------------------------
# Take pictures
log('Taking the pictures')


def take_3_stress_pic(idx_step, step_name,res_folder):

    session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
        deformationScaling=UNIFORM, uniformScaleFactor=1)

    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
        variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(COMPONENT,
                                                                         'S11'), )
    session.viewports[session.currentViewportName].odbDisplay.setFrame(
        step=step_name, frame=1000000)

    session.printToFile(
        fileName=os.path.join(res_folder,'s'+str(idx_step)+'_s11'), format=PNG,
        canvasObjects=(session.viewports['Viewport: 1'], ))
    session.viewports[session.currentViewportName].odbDisplay.setFrame(
        step=step_name, frame=100000)
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
        variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(COMPONENT,
                                                                         'S22'), )
    session.viewports[session.currentViewportName].odbDisplay.setFrame(
        step=step_name, frame=10000)
    session.printToFile(
        fileName=os.path.join(res_folder,'s'+str(idx_step)+'_s22'), format=PNG,
        canvasObjects=(session.viewports['Viewport: 1'], ))
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
        variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(COMPONENT,
                                                                         'S12'), )
    session.viewports[session.currentViewportName].odbDisplay.setFrame(
        step=step_name, frame=100000)
    session.printToFile(
        fileName=os.path.join(res_folder,'s'+str(idx_step)+'_s12'), format=PNG,
        canvasObjects=(session.viewports['Viewport: 1'], ))


session.viewports[session.currentViewportName].odbDisplay.setFrame(
    step=step_name, frame=0)
session.viewports['Viewport: 1'].setValues(displayedObject=odb)
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
    visibleEdges=FREE)
session.viewports['Viewport: 1'].view.setProjection(projection=PARALLEL)
session.viewports['Viewport: 1'].view.setValues(cameraPosition=(152.271,
                                                                144, 1500), cameraUpVector=(0, 1, 0))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(
    plotState=CONTOURS_ON_DEF)
session.pngOptions.setValues(imageSize=(1920, 1080))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    UNDEFORMED, ))
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
    state=OFF, title=OFF)

session.printToFile(
    fileName=os.path.join(res_folder,'geo'), format=PNG,
    canvasObjects=(session.viewports['Viewport: 1'], ))
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))

# ? Uncomment to take one pic at each step
# for idx_step, step_name in enumerate(odb.steps.keys()):
#     log(step_name)

#     take_3_stress_pic(idx_step, step_name,res_folder)

# -----------------------------------------------------------------------------------
# EXTRACT THE FIELD


number_of_nodes = len(odb.rootAssembly.instances['SAMPLE'].nodes)

log('Extracting connectivity for each element...')
elements_connectivity = []


step = odb.steps['step-1']
lastFrame = step.frames[0]
for elt in odb.rootAssembly.instances['SAMPLE'].elements:
    elements_connectivity.append([elt.label-1]+list(elt.connectivity))

np.savetxt(os.path.join(res_folder,'connectivity.csv'),
           np.array(elements_connectivity), delimiter=", ", fmt='% s')


log('Extracting volume for each element...')

for j, step in odb.steps.items():
    elements_volume = []
    lastFrame = step.frames[0]
    EVOL_field = lastFrame.fieldOutputs['EVOL'].values
    for elt in odb.rootAssembly.instances['SAMPLE'].elements:
        elements_volume.append([elt.label-1, EVOL_field[elt.label-1].data])
    np.savetxt(os.path.join(res_folder,'V_'+str(j)+'.csv'),
               np.array(elements_volume), delimiter=", ", fmt='% s')

log('Extracting area nodes...')
nd_area = [[], [], [], []]
for idx_area in range(1, 5):
    area = odb.rootAssembly.instances['SAMPLE'].nodeSets['AVG_STRESS_NODE_SET_'+str(
        idx_area)]
    for nd in area.nodes:
        nd_area[idx_area-1].append(nd.label)
np.savetxt(os.path.join(res_folder,'nodes_per_area.csv'),
           np.array(nd_area), delimiter=", ", fmt='% s')

log('Extracting area elements...')
el_area = [[], [], [], []]
for idx_area in range(1, 5):
    area = odb.rootAssembly.instances['SAMPLE'].elementSets['AVG_STRESS_ELEMENT_SET_'+str(
        idx_area)]
    for el in area.elements:
        el_area[idx_area-1].append(el.label)
np.savetxt(os.path.join(res_folder,'elements_per_area.csv'),
           np.array(el_area), delimiter=", ", fmt='% s')

log('Extracting node coordinates...')
node_coord = []
for node in odb.rootAssembly.instances['SAMPLE'].nodes:
    node_coord.append([node.label]+list(node.coordinates))
np.savetxt(os.path.join(res_folder,'node_coord.csv'),
           np.array(node_coord), delimiter=", ", fmt='% s')


log('Extracting disp at each node...')
for j, step in odb.steps.items():
    d_values = field.get_field_values_disp_nodal(step, odb)
    np.savetxt(os.path.join(res_folder,'U_'+str(j)+'.csv'),
               np.array(d_values), delimiter=", ", fmt='% s')
    s_values = field.get_field_values_centroid(step, odb)
    np.savetxt(os.path.join(res_folder,'S_'+str(j)+'.csv'),
               s_values, delimiter=", ", fmt='% s')
