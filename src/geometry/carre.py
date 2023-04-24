
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



# fonction qui permet de merge en fonction du nom des instances : celles qui contiennent input
def merge(input, output,DELETE): 
    a1 = mdb.models['Model-1'].rootAssembly
    instances=a1.instances.keys()
    instances_list=()
    for ins in instances:
        if input in ins:
            instances_list= instances_list+(a1.instances[ins],)
    a1.InstanceFromBooleanMerge(name=output, instances=instances_list, originalInstances=DELETE, 
        domain=GEOMETRY)
    return


def make_geo (current_path,skip_cylinders,improve_geo):
    
    L=geo_parameters[0]
    width=geo_parameters[1]
    tx=trans_rot[0]
    ty=trans_rot[1]
    theta=trans_rot[2]
    # nombre de cellules pour la contstruction avec les arrays (choisir assez grand)
    N=int(400/L)
    # Sup
    try:
        a1 = mdb.models['Model-1'].rootAssembly
        del a1.features['specimen']
    except: 
        pass

    print("First cell...")
    ################ UNITE CELL
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)

    # Heart

    pt1=(-225, width/2)
    pt2=(-225, -width/2)
    pt3=(255, -width/2)
    pt4=(255, width/2)

    s.Line(point1=pt1, point2=pt2)
    s.Line(point1=pt2, point2=pt3)
    s.Line(point1=pt3, point2=pt4)
    s.Line(point1=pt4, point2=pt1)

    # End Heart

    p = mdb.models['Model-1'].Part(name='cell', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['cell']
    p.BaseSolidExtrude(sketch=s, depth=thickness)
    s.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['cell']
    del mdb.models['Model-1'].sketches['__profile__']


    ################## ARRAY Modification
    print("Array...")
    mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='cell-1', part=
        mdb.models['Model-1'].parts['cell'])
    mdb.models['Model-1'].rootAssembly.translate(instanceList=('cell-1',), vector=(288.0/2, 288.0/2, 0.0))
    # A cette ligne, la cellule unitaire seule est centree

    # Construction du specimen avec les merges les plus petits possibles (avec des arrays successifs)
    mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
        0.0), direction2=(0.0, 1.0, 0.0), instanceList=('cell-1', ), number1=1, 
        number2=N, spacing1=1.0, spacing2=L)
    merge('cell-1','cell-2',DELETE)

    mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
        0.0), direction2=(0.0, -1.0, 0.0), instanceList=('cell-2-1', ), number1=1, 
        number2=2, spacing1=1.0, spacing2=L*N)
    merge('cell-2','cell-3',DELETE)

    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='cell-4', part=
        mdb.models['Model-1'].parts['cell-3'])
    mdb.models['Model-1'].rootAssembly.rotate(angle=90, axisDirection=(0.0, 0.0, 
        1.0), axisPoint=(144.0, 144.0, 0.0), instanceList=('cell-4', ))



    a=mdb.models['Model-1'].rootAssembly
    a.InstanceFromBooleanMerge(name='cell_infini-1', instances=(a.instances['cell-4'], 
        a.instances['cell-3-1'], ),   originalInstances=DELETE, domain=GEOMETRY)
    mdb.models['Model-1'].rootAssembly.features.changeKey(
        fromName='cell_infini-1-1', toName='cell_infini-1')

    # Rotation et translation finale
    mdb.models['Model-1'].rootAssembly.rotate(angle=theta, axisDirection=(0.0, 0.0, 
        1.0), axisPoint=(144.0, 144.0, 0.0), instanceList=('cell_infini-1', ))
    mdb.models['Model-1'].rootAssembly.translate(instanceList=('cell_infini-1',), vector=(tx, ty, 0.0))


    # First cut
    print("First cut...")
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(0.0, 0.0), point2=(288.0, 288.0))
    s.rectangle(point1=(-1000, -1000), point2=(288.0+1000, 288.0+1000))
    p = mdb.models['Model-1'].Part(name='cutter_1', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['cutter_1']
    p.BaseSolidExtrude(sketch=s, depth=thickness)
    s.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['cutter_1']
    del mdb.models['Model-1'].sketches['__profile__']

    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name=
        'cutter_1-1', part=mdb.models['Model-1'].parts['cutter_1'])
    a1 = mdb.models['Model-1'].rootAssembly
    a1.InstanceFromBooleanCut(name='cell_square', 
        instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['cell_infini-1'], 
        cuttingInstances=(a1.instances['cutter_1-1'], ), 
        originalInstances=DELETE)

    # Second cut
    print("Second cut...")

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
    p = mdb.models['Model-1'].Part(name='cutter_2', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['cutter_2']
    p.BaseSolidExtrude(sketch=s1, depth=thickness)
    s1.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['cutter_2']
    del mdb.models['Model-1'].sketches['__profile__']

    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name=
        'cutter_2-1', part=mdb.models['Model-1'].parts['cutter_2'])
    
    #mdb.saveAs(pathName='/ul/valmalette/Documents/abakubc_V1.0/src/test')
    
    a1 = mdb.models['Model-1'].rootAssembly
    a1.InstanceFromBooleanCut(name='struct_no_support', 
        instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['cell_square-1'], 
        cuttingInstances=(a1.instances['cutter_2-1'], ), 
        originalInstances=DELETE)

    print("Cuts completed")

    # .py file adding the support
    mdb.openAcis(current_path+'/ressources/support.sat', 
        scaleFromFile=OFF)
    make_add_supports.add_support(improve_geo,skip_cylinders)