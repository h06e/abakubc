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

current_path = os.path.abspath(os.getcwd())
improve_geo=True
skip_cylinders=[[],[],[],[]]

L=20
width=2.0
radius=10.0
tx=0.0
ty=0.0
theta=0.0
# nombre de cellules pour la contstruction avec les arrays (choisir assez grand)
aa=L/tan(pi/3)
bb=L*tan(pi/6)
Nx=int(400/L/2) 
Ny=int(400/(2*(aa+2*bb)))

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
s.rectangle(point1=(0.0, 0.0), point2=(L, -width))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseSolidExtrude(sketch=s, depth=thickness)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
del mdb.models['Model-1'].sketches['__profile__']

s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.CircleByCenterPerimeter(center=(0.0,-radius), point1=(0.0, 0.0))
s1.CircleByCenterPerimeter(center=(0.0,-radius), point1=(0.0, -width))
p = mdb.models['Model-1'].Part(name='Part-2', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-2']
p.BaseSolidExtrude(sketch=s1, depth=20.0)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-2']
del mdb.models['Model-1'].sketches['__profile__']

a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-1']
a1.Instance(name='Part-1-1', part=p, dependent=ON)
p = mdb.models['Model-1'].parts['Part-2']
a1.Instance(name='Part-2-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.InstanceFromBooleanMerge(name='Part-3', instances=(a1.instances['Part-1-1'], 
    a1.instances['Part-2-1'], ), originalInstances=DELETE, domain=GEOMETRY)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('Part-3-1', ), vector=(0.0, radius, 0.0))
a1.RadialInstancePattern(instanceList=('Part-3-1', ), point=(0.0, 0.0, 0.0), 
    axis=(0.0, 0.0, 1.0), number=6, totalAngle=360.0)
a1.InstanceFromBooleanMerge(name='Part-4', instances=(a1.instances['Part-3-1'], 
    a1.instances['Part-3-1-rad-2'], a1.instances['Part-3-1-rad-3'], 
    a1.instances['Part-3-1-rad-4'], a1.instances['Part-3-1-rad-5'], 
    a1.instances['Part-3-1-rad-6'], ), originalInstances=DELETE, 
    domain=GEOMETRY)
a1.rotate(instanceList=('Part-4-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 0.0, 1.0), angle=-180/pi*asin((radius-width/2)/L))
mdb.models['Model-1'].rootAssembly.translate(instanceList=('Part-4-1',), vector=(288.0/2, 288.0/2, 0.0))
#Arrays
print("Array...")
a1 = mdb.models['Model-1'].rootAssembly
a1.LinearInstancePattern(instanceList=('Part-4-1', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1=Nx, number2=1, spacing1=2*L, 
    spacing2=77.1075)
merge('Part-4','cell-5',DELETE)
p = mdb.models['Model-1'].parts['cell-5']
a1.Instance(name='cell-5-2', part=p, dependent=ON)

mdb.models['Model-1'].rootAssembly.translate(instanceList=('cell-5-2',), vector=(L, aa+2*bb, 0.0)) 
merge('cell-5','cell-6',DELETE)
mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0, 
        0.0), direction2=(0.0, 1.0, 0.0), instanceList=('cell-6-1', ), number1=1, 
        number2=Ny, spacing1=L, spacing2=2*(aa+2*bb))
merge('cell-6','cell-7',DELETE)
a1.LinearInstancePattern(instanceList=('cell-7-1', ), direction1=(-1.0, 0.0, 
    0.0), direction2=(0.0, -1.0, 0.0), number1=2, number2=2, spacing1=2*L*Nx, 
    spacing2=Ny*2*(aa+2*bb))
merge('cell-7','cell_infini-1',DELETE)
mdb.models['Model-1'].rootAssembly.features.changeKey(
    fromName='cell_infini-1-1', toName='cell_infini-1')
# Rotation et translation finale
mdb.models['Model-1'].rootAssembly.rotate(angle=theta, axisDirection=(0.0, 0.0, 
    1.0), axisPoint=(144.0, 144.0, 0.0), instanceList=('cell_infini-1', ))
mdb.models['Model-1'].rootAssembly.translate(instanceList=('cell_infini-1',), vector=(tx, ty, 0.0))

#----------------------------------------------------------------------------------------
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

