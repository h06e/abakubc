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

def main(paths, test, skip_cylinders):
    if test['dim']==3:
        make_geo(paths, test, skip_cylinders)
    else:
        make_geo_2d(paths, test, skip_cylinders)

def make_geo(paths, test, skip_cylinders):

    model = mdb.models['Model-1']
    a1 = model.rootAssembly
    try:
        del a1.features['specimen']
    except:
        pass

    print("First cell...")
    # UNITE CELL
    s = model.ConstrainedSketch(name='__profile__',
                                sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)

    s.rectangle(point1=(0.0, 0.0), point2=(288.0, 288.0))

    p = model.Part(name='cell', dimensionality=THREE_D,
                   type=DEFORMABLE_BODY)
    p = model.parts['cell']
    p.BaseSolidExtrude(sketch=s, depth=test['thickness'])
    s.unsetPrimaryObject()
    p = model.parts['cell']
    del model.sketches['__profile__']

    model.rootAssembly.DatumCsysByDefault(CARTESIAN)
    model.rootAssembly.Instance(
        dependent=ON, name='cell-1', part=model.parts['cell'])

    print("Cylinders cut...")

    s1 = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
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
    p = model.Part(name='cutter_2', dimensionality=THREE_D,
                   type=DEFORMABLE_BODY)
    p = model.parts['cutter_2']
    p.BaseSolidExtrude(sketch=s1, depth=test['thickness'])
    s1.unsetPrimaryObject()
    p = model.parts['cutter_2']
    del model.sketches['__profile__']

    model.rootAssembly.Instance(
        dependent=ON, name='cutter_2-1', part=model.parts['cutter_2'])

    a1 = model.rootAssembly
    a1.InstanceFromBooleanCut(name='specimen',
                              instanceToBeCut=model.rootAssembly.instances['cell-1'],
                              cuttingInstances=(a1.instances['cutter_2-1'], ),
                              originalInstances=SUPPRESS)

    print("Cuts completed")


def make_geo_2d(paths, test, skip_cylinders):

    model = mdb.models['Model-1']
    a1 = model.rootAssembly
    try:
        del a1.features['specimen']
    except:
        pass

    print("First cell...")
    # UNITE CELL
    s = model.ConstrainedSketch(name='__profile__',
                                sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)

    s.rectangle(point1=(0.0, 0.0), point2=(288.0, 288.0))

    p = model.Part(name='cell', dimensionality=TWO_D_PLANAR,
                   type=DEFORMABLE_BODY)
    p = model.parts['cell']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = model.parts['cell']
    del model.sketches['__profile__']

    model.rootAssembly.DatumCsysByDefault(CARTESIAN)
    model.rootAssembly.Instance(
        dependent=ON, name='cell-1', part=model.parts['cell'])

    print("Cylinders cut...")

    s1 = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
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
    p = model.Part(name='cutter_2', dimensionality=TWO_D_PLANAR,
                   type=DEFORMABLE_BODY)
    p = model.parts['cutter_2']
    p.BaseShell(sketch=s1)
    s1.unsetPrimaryObject()
    p = model.parts['cutter_2']
    del model.sketches['__profile__']

    model.rootAssembly.Instance(
        dependent=ON, name='cutter_2-1', part=model.parts['cutter_2'])

    a1 = model.rootAssembly
    a1.InstanceFromBooleanCut(name='specimen',
                              instanceToBeCut=model.rootAssembly.instances['cell-1'],
                              cuttingInstances=(a1.instances['cutter_2-1'], ),
                              originalInstances=SUPPRESS)

    print("Cuts completed")
