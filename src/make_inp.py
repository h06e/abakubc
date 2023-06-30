from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import sys
import os
try:
    sys.path.append("../src")
except:
    pass
from constants import *
from model_generation import make_assembly, make_corner_cleaner
from geometry import monolithic
from geometry import honey
from geometry import kagome
from geometry import hexachiral
from geometry import rectangle
from geometry import losange
from geometry import penrose
from geometry import r0
from geometry import triangle
from geometry import carretrian
from geometry import tetrachiral
from geometry import snubsquare
from geometry import snubsquare2
import time
import csv
from constants import *


def log(message):
    print >> sys.__stdout__, message

test = eval(sys.argv[-2])
for i in test:
    if len(test[i])==0:
        test[i]=None
    else:
        try:
            test[i] = eval(test[i]) if i not in ['sample_name', 'status', 'comment', 'err'] else test[i]
        except NameError:
            pass

paths = eval(sys.argv[-1])

# ! ATTENTION PYTHON 2 !!!!!!!!!
# * For beguging, turn force_gen to True to force the generation of the specimen and not take the one existing in the sample_bank
FORCE_GEN=test['debug'] or test['corner_cleaner'] or test['sample_name'] in ['snubsquare', 'snubsquare2']

Mdb()
session.journalOptions.setValues(
    replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

dim=test['dim']
if dim == 3:
    c_dim=''
else:
    c_dim='2d'
geometry_name=c_dim+'_'.join([str(test[i]) for i in ['sample_name', 'geo_parameters', 'trans_rot', 'thickness', 'corner_cleaner']])

if '{}.sat'.format(geometry_name) not in os.listdir(paths[SAMPLE_BANK_DIR]) or FORCE_GEN:
    skip_cylinders = [[], [], [], []]
    geo_topo_known=True
    try:
        eval(test['sample_name']).main(paths=paths, test=test, skip_cylinders=skip_cylinders)
    except NameError:
        geo_topo_known=False
    if test['corner_cleaner'] :
        make_corner_cleaner.main_clean_corners(paths=paths, test=test)
    if geo_topo_known:
        mdb.models['Model-1'].parts['specimen'].writeAcisFile(os.path.join(paths[SAMPLE_BANK_DIR], '{}.sat'.format(geometry_name)), 24)
        a = mdb.models['Model-1'].rootAssembly
        try:
            a.features['specimen'].suppress()
        except KeyError:
            pass
    with open(os.path.join(paths[SAMPLE_BANK_DIR], '{}_skip_cyl.csv'.format(geometry_name)), "wb") as f:
        writer = csv.writer(f)
        writer.writerows(skip_cylinders)

step_list = []
load=test['load_1']
index=1
""" STEP PARAMETERS"""
s1_initial_inc = 1.0        #Size of the initrial increment. (Better to keep low to allow smooth transition between intermediate steps)
s1_max_inc = 1.0            #Maximum allowable increment size during the simulation (between 0 and 1 )
s1_min_inc = 1.0E-8         #Minimum allowable increment size (smaller numbers can help convergence but also hinder performance)
s1_max_num_inc = 50000      #Maximum number of increments allowed in the step.
s1_NL = OFF if test['perfect_panto'] else ON                #Nlgeom MANDATORY for stiffness, clearance in the pantographs
para_default=[s1_initial_inc,s1_max_inc,s1_min_inc,s1_max_num_inc,s1_NL]
while load:
    step_list.append(StepScript('step-{}'.format(index), para_default, load))
    index+=1
    try:
        load=test['load_{}'.format(index)]
    except KeyError:
        load=None

make_assembly.main_assemble_model(test, paths, step_list)
mdb.jobs[test['test_id']].writeInput(consistencyChecking=OFF)


# mdb.jobs[test['test_id']].submit(consistencyChecking=OFF)
# mdb.jobs[test['test_id']].waitForCompletion()