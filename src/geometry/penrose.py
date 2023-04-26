
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
from part import *
from material import *
from section import *
from assembly import *
from interaction import *
from mesh import *
from visualization import *
from connectorBehavior import *
from math import *
from constants import *
from model_generation import make_add_supports
from constants import *
import json
import csv


def log(message):
    print >> sys.__stdout__, message


def main(paths, test, skip_cylinders):
    make_geo_2d(paths, test, skip_cylinders)


def merge(input, output, DELETE=DELETE):
    """fonction qui permet de merge en fonction du nom des instances : celles qui contiennent input"""
    a1 = mdb.models['Model-1'].rootAssembly
    instances = a1.instances.keys()
    instances_list = ()
    for ins in instances:
        if input in ins:
            instances_list = instances_list+(a1.instances[ins],)
    a1.InstanceFromBooleanMerge(name=output, instances=instances_list, originalInstances=DELETE,
                                domain=GEOMETRY)
    return


def make_geo_2d(paths, test, skip_cylinders):
    scale = test['geo_parameters']
    tx, ty, theta = test['trans_rot']

    # * First array horizontally sapce_1 and width
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    connectivity = []
    conbulk = []
    with open(os.path.join(os.path.join(paths[SRC], 'ressources'), 'penrose_beam.csv')) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            connectivity.append([int(r) for r in row])
            conbulk.append(int(row[0]))
            conbulk.append(int(row[1]))
    coordinates = []
    with open(os.path.join(os.path.join(paths[SRC], 'ressources'), 'penrose_nodes.csv')) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            coordinates.append([float(r) for r in row])

    indexes_to_not_consider = []
    for i in range(1, max(conbulk)+1):
        if conbulk.count(i) != 2:
            indexes_to_not_consider.append(conbulk.index(i)//2)

    for i, c in enumerate(connectivity):
        if i not in indexes_to_not_consider:
            s.Line(point1=tuple(coordinates[c[0]-1]),
                   point2=tuple(coordinates[c[1]-1]))

    s.rectangle(point1=(-12.5, -12.5), point2=(12.5, 12.5))
    s.scale(objectList=tuple(gg[1] for gg in g.items()), scaleCenter=(
        0.0, 0.0), scaleValue=scale)
    s.move(vector=(144.0,144.0),objectList=tuple(gg[1] for gg in g.items()))
    p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                   type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-1']
    mdb.saveAs('test.cae')
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['Part-1']
    del mdb.models['Model-1'].sketches['__profile__']
    mdb.saveAs('test.cae')

    mdb.models['Model-1'].rootAssembly.Instance(
        dependent=ON, name='Part-1-1', part=mdb.models['Model-1'].parts['Part-1'])

    # First cut
    print("First cut...")
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(0.0, 0.0), point2=(288.0, 288.0))
    s.rectangle(point1=(-1000.0, -1000.0), point2=(1000.0, 1000.0))
    p = mdb.models['Model-1'].Part(name='cutter_1', dimensionality=TWO_D_PLANAR,
                                   type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['cutter_1']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['cutter_1']
    del mdb.models['Model-1'].sketches['__profile__']

    mdb.models['Model-1'].rootAssembly.Instance(
        dependent=ON, name='cutter_1-1', part=mdb.models['Model-1'].parts['cutter_1'])
    mdb.models['Model-1'].rootAssembly.InstanceFromBooleanCut(cuttingInstances=(
        mdb.models['Model-1'].rootAssembly.instances['cutter_1-1'], ),
        instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'],
        name='cell_square-1', originalInstances=DELETE)

    # * SAVE THE POROSITY
    a = mdb.models['Model-1'].rootAssembly
    area = a.getArea(mdb.models['Model-1'].parts['cell_square-1'].faces)
    porosity = (288*288 - area) / (288*288)
    with open(os.path.join(paths[POROSITY], '_'.join([test['sample_name'], str(test['geo_parameters'])])+'.json'), 'w') as f:
        json.dump(porosity, f, indent=4, separators=(
            ", ", ": "), sort_keys=True)

    s1 = mdb.models['Model-1'].ConstrainedSketch(
        name='__profile__', sheetSize=200.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=STANDALONE)
    s1.CircleByCenterPerimeter(center=(CYL_START_POS, -CYLINDER_CENTER_DIST_EDGE),
                               point1=(CYL_START_POS, -CYLINDER_CENTER_DIST_EDGE+CYLINDER_RADIUS))
    s1.linearPattern(geomList=(g.findAt((CYL_START_POS, -CYLINDER_CENTER_DIST_EDGE+CYLINDER_RADIUS)), ), vertexList=(),
                     number1=NUMBER_OF_CYLINDER_PER_SIDE, spacing1=DIST_BETWEEN_CENTERS, angle1=0.0,
                     number2=2, spacing2=SIDE_LENGTH+2*CYLINDER_CENTER_DIST_EDGE, angle2=90.0)
    s1.CircleByCenterPerimeter(center=(-CYLINDER_CENTER_DIST_EDGE, CYL_START_POS),
                               point1=(-CYLINDER_CENTER_DIST_EDGE, CYL_START_POS+CYLINDER_RADIUS))
    s1.linearPattern(geomList=(g.findAt((-CYLINDER_CENTER_DIST_EDGE, CYL_START_POS+CYLINDER_RADIUS)), ), vertexList=(),
                     number1=2, spacing1=SIDE_LENGTH+2*CYLINDER_CENTER_DIST_EDGE, angle1=0.0, number2=NUMBER_OF_CYLINDER_PER_SIDE, spacing2=DIST_BETWEEN_CENTERS,
                     angle2=90.0)
    p = mdb.models['Model-1'].Part(name='cutter_2', dimensionality=TWO_D_PLANAR,
                                   type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['cutter_2']
    p.BaseShell(sketch=s1)
    s1.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['cutter_2']
    del mdb.models['Model-1'].sketches['__profile__']

    mdb.models['Model-1'].rootAssembly.Instance(
        dependent=ON, name='cutter_2-1', part=mdb.models['Model-1'].parts['cutter_2'])

    log(mdb.models['Model-1'].rootAssembly.instances.keys())
    a1 = mdb.models['Model-1'].rootAssembly
    a1.InstanceFromBooleanCut(name='struct_no_support',
                              instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['cell_square-1-1'],
                              cuttingInstances=(a1.instances['cutter_2-1'], ),
                              originalInstances=DELETE)

    print("Cuts completed")

    # mdb.saveAs(pathName='{}.cae'.format(test['test_id']))
    # exit()

    # .py file adding the support
    mdb.openAcis(os.path.join(paths[SRC], 'ressources', 'support_2d.sat'),
                 scaleFromFile=OFF)
    make_add_supports.add_support_2d(True, skip_cylinders)
