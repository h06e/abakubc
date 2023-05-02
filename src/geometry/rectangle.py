
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

def log(message):
    print >> sys.__stdout__, message

def main(paths, test, skip_cylinders):
    make_geo_2d(paths, test, skip_cylinders)


def merge(input, output,DELETE=DELETE): 
    """fonction qui permet de merge en fonction du nom des instances : celles qui contiennent input"""
    a1 = mdb.models['Model-1'].rootAssembly
    instances=a1.instances.keys()
    instances_list=()
    for ins in instances:
        if input in ins:
            instances_list= instances_list+(a1.instances[ins],)
    a1.InstanceFromBooleanMerge(name=output, instances=instances_list, originalInstances=DELETE, 
        domain=GEOMETRY)
    return


def make_geo_2d(paths, test, skip_cylinders):
    width_1, width_2, space_1, space_2=test['geo_parameters']
    tx, ty, theta=test['trans_rot']
    angle=90.0
    Ny=int(488.0/space_2)
    Nx=int(488.0/space_1)
    
    # * First array horizontally sapce_1 and width_1
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=( 144+-width_1/2.0,144+-288.0), point2=(144+width_1/2.0, 144+288.0))
    p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-1']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['Part-1']
    del mdb.models['Model-1'].sketches['__profile__']

    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name=
        'Part-1', part=mdb.models['Model-1'].parts['Part-1'])

    mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
        0.0), direction2=(0.0, 1.0, 0.0), instanceList=('Part-1', ), number1=Nx, 
        number2=1, spacing1=space_1, spacing2=1.0)
    mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(-1.0, 0.0, 
        0.0), direction2=(0.0, 1.0, 0.0), instanceList=('Part-1', ), number1=Nx, 
        number2=1, spacing1=space_1, spacing2=1.0)

    
    merge('Part-1', 'Part-2', DELETE)

    # * Second array horizontally sapce_2 and width_2
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(144+-width_2/2.0,144+-288.0), point2=(144+width_2/2.0, 144+288.0))
    p = mdb.models['Model-1'].Part(name='Part-3', dimensionality=TWO_D_PLANAR, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-3']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['Part-3']
    del mdb.models['Model-1'].sketches['__profile__']

    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name=
        'Part-3', part=mdb.models['Model-1'].parts['Part-3'])

    mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
        0.0), direction2=(0.0, 1.0, 0.0), instanceList=('Part-3', ), number1=Ny, 
        number2=1, spacing1=space_2, spacing2=1.0)
    mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(-1.0, 0.0, 
        0.0), direction2=(0.0, 1.0, 0.0), instanceList=('Part-3', ), number1=Ny, 
        number2=1, spacing1=space_2, spacing2=1.0)
    
    merge('Part-3', 'Part-4')
    
    mdb.models['Model-1'].rootAssembly.rotate(angle=angle, axisDirection=(0.0, 0.0, 
        1.0), axisPoint=(144.0, 144.0, 0.0), instanceList=('Part-4-1', ))
    
    a = mdb.models['Model-1'].rootAssembly

    mdb.models['Model-1'].rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, 
        instances=(mdb.models['Model-1'].rootAssembly.instances['Part-4-1'], 
        mdb.models['Model-1'].rootAssembly.instances['Part-2-1']), name='Primary', 
        originalInstances=DELETE)
    
    mdb.models['Model-1'].rootAssembly.translate(instanceList=('Primary-1',), vector=(tx, ty, 0.0))
    mdb.models['Model-1'].rootAssembly.rotate(angle=theta, axisDirection=(0.0, 0.0, 
        1.0), axisPoint=(144.0, 144.0, 0.0), instanceList=('Primary-1', ))

    
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
    
    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name=
        'cutter_1-1', part=mdb.models['Model-1'].parts['cutter_1'])
    mdb.models['Model-1'].rootAssembly.InstanceFromBooleanCut(cuttingInstances=(
        mdb.models['Model-1'].rootAssembly.instances['cutter_1-1'], ), 
        instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Primary-1'], 
        name='cell_square-1', originalInstances=DELETE)

    s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
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

    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name=
        'cutter_2-1', part=mdb.models['Model-1'].parts['cutter_2'])

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
    mdb.openAcis(os.path.join(paths[SRC],'ressources', 'support_2d.sat'), 
        scaleFromFile=OFF)
    make_add_supports.add_support_2d(True,skip_cylinders)