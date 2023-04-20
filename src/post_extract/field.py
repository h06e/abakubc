import numpy as np
from abaqus import *
from abaqusConstants import *
from caeModules import *
from odbAccess import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import numpy as np

def get_num_int_pt(l):
    number_in_pt=0
    name_init=l[0].elementLabel
    name=name_init
    while name==name_init:
        number_in_pt+=1
        name=l[number_in_pt].elementLabel
    return number_in_pt

def get_field_values(step,odb):
    lastFrame = step.frames[-1]
    try:E_field = lastFrame.fieldOutputs['E'] # replace by 'LE' with nlgeom
    except:E_field = lastFrame.fieldOutputs['LE']
    S_field = lastFrame.fieldOutputs['S']
    EVOL_field = lastFrame.fieldOutputs['EVOL']
    center = odb.rootAssembly.instances['SAMPLE'].elementSets['SAMPLE']
    centerE = E_field.getSubset(region=center)
    centerS = S_field.getSubset(region=center)
    centerEVOL = EVOL_field.getSubset(region=center)
    return centerE.values,centerS.values,centerEVOL.values

def get_field_values_centroid(step,odb):
    lastFrame = step.frames[-1]
    try:E_field = lastFrame.fieldOutputs['E'] # replace by 'LE' with nlgeom
    except:E_field = lastFrame.fieldOutputs['LE']
    S_field = lastFrame.fieldOutputs['S']
    centerE = E_field.getSubset(position=CENTROID)
    centerS = S_field.getSubset(position=CENTROID)
    return centerE.bulkDataBlocks[0].data,centerS.bulkDataBlocks[0].data

def get_field_values_disp_nodal(step,odb):
    lastFrame = step.frames[-1]
    U_field = lastFrame.fieldOutputs['U']
    try:E_field = lastFrame.fieldOutputs['E']
    except:return U_field.bulkDataBlocks[1].data
    else:return U_field.bulkDataBlocks[0].data 

        