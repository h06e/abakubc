
from abaqus import *
from abaqusConstants import *
from caeModules import *
from odbAccess import *
import os
import numpy as np
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
from math import sqrt
import sys
from math import tan,pi
import json


def log(message):
    print >> sys.__stdout__, message

test = eval(sys.argv[-2])
for i in test:
    if len(test[i])==0:
        test[i]=None
    else:
        try:
            test[i] = eval(test[i]) if i!='sample_name' else test[i]
        except NameError:
            pass


file_name=sys.argv[-1]
log(['file_name', file_name])
#Conditions d'experience
e11=0.02
e22=0.02
e12=0.02 # Gamma12
eps12=e12/2

L=test['geo_parameters'][0]
log(['OOOOOOOOOOOOOOOOOOOOO',file_name])

if file_name.split('_')[0]=='KUBC':
    area=288*288
else:
    aa=L/2/tan(pi/3)
    bb=L/2*tan(pi/6)
    area=2*(aa+2*bb)*L

#-------------
current_path=os.path.abspath(os.getcwd())
odb = session.openOdb(name='{}.odb'.format(file_name))
session.viewports['Viewport: 1'].setValues(displayedObject=odb)
xyList = xyPlot.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=((
    'RF', NODAL, ((COMPONENT, 'RF1'), (COMPONENT, 'RF2'), )), ), nodeSets=("REFMACRO1", "REFMACRO2", ))

fx=np.array(xyList[0].data)/area
fy=np.array(xyList[2].data)/area
fxy=np.array(xyList[1].data)/area
p=np.array([[fx[1][1],fx[3][1],fx[5][1]],
           [fy[1][1],fy[3][1],fy[5][1]],
           [fxy[1][1],fxy[3][1],fxy[5][1]]])*area
#log(p)
K=np.array([[fx[1][1]/e11,fx[3][1]/e22,fx[5][1]/eps12/sqrt(2)],
           [fy[1][1]/e11,fy[3][1]/e22,fy[5][1]/eps12/sqrt(2)],
           [fxy[1][1]/e11*sqrt(2),fxy[3][1]/e22*sqrt(2),fxy[5][1]/eps12]])
np.set_printoptions(precision=5,suppress=True,floatmode='fixed')
log(K)

K=K.tolist()
with open('theory_matrix_bank/{}.json'.format(file_name), 'w') as f:
    json.dump(K, f, indent=4, separators=(", ", ": "), sort_keys=True)

