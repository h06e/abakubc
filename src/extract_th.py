
from abaqus import *
from abaqusConstants import *
from caeModules import *
from odbAccess import *
import sys
import os
import numpy as np
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
from math import sqrt
import sys
from math import tan, pi
import json
from math import *
from constants import *
from post_compute import operation

def log(message):
    print >> sys.__stdout__, message


test = eval(sys.argv[-3])
for i in test:
    if len(test[i]) == 0:
        test[i] = None
    else:
        try:
            test[i] = eval(test[i]) if i not in ['sample_name',
                                                 'status', 'comment', 'err'] else test[i]
        except NameError:
            pass

paths = eval(sys.argv[-2])
file_name = sys.argv[-1]
log(['file_name', file_name])
# Conditions d'experience
e11 = 0.02
e22 = 0.02
e12 = 0.02  # Gamma12
eps12 = e12/2




if file_name.split('_')[0] == 'KUBC':
    area = 288*288
else: # Give the total area of the PBC sample
    if test['sample_name'] == 'honey':
        L, width = test['geo_parameters']
        aa = L/2/tan(pi/3)
        bb = L/2*tan(pi/6)
        area = 2*(aa+2*bb)*L
    elif test['sample_name'] == 'rectangle':
        width_1, width_2, space_1, space_2 = test['geo_parameters']
        area = space_1*space_2
    elif test['sample_name'] == 'losange':
        width, length, angle = test['geo_parameters']
        lx = 2*length*sin(angle*pi/180.0/2.0)
        ly = 2*length*cos(angle*pi/180.0/2.0)
        area = lx*ly
    elif test['sample_name'] == 'hexachiral':
        L, width, radius = test['geo_parameters']
        area = L*2*L*cos(pi/6.0)
    elif test['sample_name'] == 'r0':
        scale = test['geo_parameters']
        area = (20.0*scale)**2
    elif test['sample_name'] == 'triangle':
        width, space =test['geo_parameters']
        area= 2*space*2*space*tan(pi/6.0)
    elif test['sample_name'] == 'carretrian':
        width, space =test['geo_parameters']
        area = space**2
    elif test['sample_name'] == 'tetrachiral' :
        L, width, radius = test['geo_parameters']
        area=L**2
    elif test['sample_name'] in ['snubsquare', 'snubsquare2']:
        L =test['geo_parameters']
        LC=L*cos(30.0*pi/180.0)
        LS=L*sin(30.0*pi/180.0)
        area=(LS+LC)**2
    else:
        raise ValueError

# -------------
current_path = os.path.abspath(os.getcwd())
odb = session.openOdb(name='{}.odb'.format(file_name))
session.viewports['Viewport: 1'].setValues(displayedObject=odb)
xyList = xyPlot.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=((
    'RF', NODAL, ((COMPONENT, 'RF1'), (COMPONENT, 'RF2'), )), ), nodeSets=("REFMACRO1", "REFMACRO2", ))

fx = np.array(xyList[0].data)/area
fy = np.array(xyList[2].data)/area
fxy = np.array(xyList[1].data)/area
p = np.array([[fx[1][1], fx[3][1], fx[5][1]],
              [fy[1][1], fy[3][1], fy[5][1]],
              [fxy[1][1], fxy[3][1], fxy[5][1]]])*area
# log(p)
K = np.array([[fx[1][1]/e11, fx[3][1]/e22, fx[5][1]/(2*eps12)],
              [fy[1][1]/e11, fy[3][1]/e22, fy[5][1]/(2*eps12)],
              [fxy[1][1]/e11, fxy[3][1]/e22, fxy[5][1]/(2*eps12)]])
np.set_printoptions(precision=5, suppress=True, floatmode='fixed')


K = K.tolist()
with open('../theory_matrix_bank/{}.json'.format(file_name), 'w') as f:
    json.dump(K, f, indent=4, separators=(", ", ": "), sort_keys=True)

# * Alternativ method to compute stiffness matrix without the CROUTE of the border

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
        
def get_field_values_centroid(step,odb):
    lastFrame = step.frames[-1]
    S_field = lastFrame.fieldOutputs['S']
    centerS = S_field.getSubset(position=CENTROID)
    return centerS.bulkDataBlocks[0].data

def get_stress_average(elmts, porosity, stress_elements, volume_elements):
    s_values=[]
    v_values=[]
    for element in elmts:
        s_values.append(stress_elements[element.label-1])
        v_values.append(volume_elements[element.label-1])
    s_values=np.array(s_values)*(1-porosity)
    v_values=np.array(v_values)
    average11=np.average(s_values[:,0], weights=v_values[:,0])
    average22=np.average(s_values[:,1], weights=v_values[:,0])
    average12=np.average(s_values[:,3], weights=v_values[:,0])
    return [average11, average22, average12]

def get_strain_from_disp(nds, U_field):
    A=[]
    U=[]
    for node in nds:
        A.append([node.coordinates[0], 0, node.coordinates[1], 1, 0, -node.coordinates[1]])
        U.append([U_field[node.label-1,0]])
        A.append([0, node.coordinates[1], node.coordinates[0], 0, 1, node.coordinates[0]])
        U.append([U_field[node.label-1,1]])
    A=np.array(A)
    U=np.array(U)
    d=np.linalg.lstsq(A,U) # d=np.linalg.lstsq(A,U, rcond=None)
    return d[0]

def compute_stress(odb, area_of_interest, porosity):
    stress_field = []
    if area_of_interest == 0:
        elmts = odb.rootAssembly.instances['SAMPLE'].elementSets['SAMPLE'].elements
    else:
        elmts= odb.rootAssembly.instances['SAMPLE'].elementSets['AVG_STRESS_ELEMENT_SET_'+str(area_of_interest)].elements
    for j, step in odb.steps.items():
        stress_elements = get_field_values_centroid(step,odb)
        volume_elements = step.frames[-1].fieldOutputs['EVOL'].bulkDataBlocks[0].data
        mean_stresses = get_stress_average(elmts, porosity, stress_elements, volume_elements)
        stress_field.append([float(i) for i in mean_stresses])
    return stress_field

# * Deformation moyenne
def compute_strain(odb, area_of_interest):
    strain_field = []
    if area_of_interest == 0:
        nds = odb.rootAssembly.instances['SAMPLE'].nodeSets['SAMPLE'].nodes
    else:
        nds=odb.rootAssembly.instances['SAMPLE'].nodeSets['AVG_STRESS_NODE_SET_'+str(area_of_interest)].nodes
    for j, step in odb.steps.items():
        U_field  = step.frames[-1].fieldOutputs['U'].bulkDataBlocks[0].data
        strain = get_strain_from_disp(nds, U_field)
        strain_field.append([float(i) for i in strain[:3]])
    return strain_field


porosity = get_porosity(test, paths)
mean_stress = compute_stress(odb, porosity),
mean_strain = compute_strain(odb)

K_CROUTE = operation.compute_stiffness_matrix(mean_stress, mean_strain)

with open('../theory_matrix_bank/{}.json'.format(file_name), 'w') as f:
    json.dump({'KUBC':K, 'KUBC_NO_CROUTE':K_CROUTE}, f, indent=4, separators=(", ", ": "), sort_keys=True)
