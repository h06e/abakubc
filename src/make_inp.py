from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import sys
import os
try:
    sys.path.append("src")
except:
    pass
from constants import *
from model_generation import make_assembly, make_corner_cleaner
from geometry import monolithic
from geometry import honey
from geometry import kagome
from geometry import hexachiral
from geometry import rectangle
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
FORCE_GEN=test['debug']

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
        make_corner_cleaner.main_clean_corners(test)
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
while load:
    step_list.append(StepScript('step-{}'.format(index), para_default, load))
    index+=1
    try:
        load=test['load_{}'.format(index)]
    except KeyError:
        load=None

make_assembly.main_assemble_model(test, paths, step_list)
mdb.saveAs(pathName='{}.cae'.format(test['test_id']))

# * Brute force the writing of the input file because Abq sometime return an error
inp_is_written=False
while not inp_is_written:
    try:
        mdb.jobs[test['test_id']].writeInput(consistencyChecking=OFF)  # Write the inp file
    except:
        pass
    else:
        inp_is_written=True