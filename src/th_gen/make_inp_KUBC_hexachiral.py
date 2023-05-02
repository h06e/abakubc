from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
from math import *
import sys
import os
try:
    sys.path.append("../src")
except:
    pass
from constants import *
import th_gen.homogeneBoundary as homogeneBoundary
from make_job import make_job

def log(message):
    print >> sys.__stdout__, message

# ? lauch abq with $ env LC_ALL="en_US.UTF8" abaqus cae

def merge(input, output, DELETE=DELETE):
    a1 = mdb.models['Model-1'].rootAssembly
    instances = a1.instances.keys()
    instances_list = ()
    for ins in instances:
        if input in ins:
            instances_list = instances_list+(a1.instances[ins],)
    a1.InstanceFromBooleanMerge(name=output, instances=instances_list, originalInstances=DELETE,
                                domain=GEOMETRY)
    
test = eval(sys.argv[-2])
for i in test:
    if len(test[i]) == 0:
        test[i] = None
    else:
        try:
            test[i] = eval(test[i]) if i != 'sample_name' else test[i]
        except NameError:
            pass

paths = eval(sys.argv[-1])

Mdb()
tol = 0.01

# Mat
E, nu = test['mat']        # DE base, E_air=0.0001 et nu_air=0.3

L, width, radius = test['geo_parameters']
tx, ty, theta = test['trans_rot']

# nombre de cellules pour la contstruction avec les arrays (choisir assez grand)
aa = L/2.0/tan(pi/3.0)
bb = L/2.0*tan(pi/6)
Nx = int(400/(L/2.0)/2)
Ny = int(400/(2*(aa+2*bb)))
# Construction de la piece
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                            sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=(L/2.0, -width))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
del mdb.models['Model-1'].sketches['__profile__']

s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                sheetSize=200.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.CircleByCenterPerimeter(center=(0.0, -radius), point1=(0.0, 0.0))
s1.CircleByCenterPerimeter(center=(0.0, -radius), point1=(0.0, -width))
p = mdb.models['Model-1'].Part(name='Part-2', dimensionality=TWO_D_PLANAR,
                                type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-2']
p.BaseShell(sketch=s1)
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
            axisDirection=(0.0, 0.0, 1.0), angle=-180/pi*asin((radius-width/2)/(L/2.0)))
mdb.models['Model-1'].rootAssembly.translate(
    instanceList=('Part-4-1',), vector=(288.0/2, 288.0/2, 0.0))
# Arrays
print("Array...")
a1 = mdb.models['Model-1'].rootAssembly
a1.LinearInstancePattern(instanceList=('Part-4-1', ), direction1=(1.0, 0.0,
                                                                    0.0), direction2=(0.0, 1.0, 0.0), number1=Nx, number2=1, spacing1=L,
                            spacing2=77.1075)
merge('Part-4', 'cell-5', DELETE)
p = mdb.models['Model-1'].parts['cell-5']
a1.Instance(name='cell-5-2', part=p, dependent=ON)

mdb.models['Model-1'].rootAssembly.translate(
    instanceList=('cell-5-2',), vector=(L/2.0, aa+2*bb, 0.0))
merge('cell-5', 'cell-6', DELETE)
mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(1.0, 0.0,
                                                                        0.0), direction2=(0.0, 1.0, 0.0), instanceList=('cell-6-1', ), number1=1,
                                                            number2=Ny, spacing1=L/2.0, spacing2=2*(aa+2*bb))
merge('cell-6', 'cell-7', DELETE)
a1.LinearInstancePattern(instanceList=('cell-7-1', ), direction1=(-1.0, 0.0,
                                                                    0.0), direction2=(0.0, -1.0, 0.0), number1=2, number2=2, spacing1=L*Nx,
                            spacing2=Ny*2*(aa+2*bb))
merge('cell-7', 'cell_infini-1', DELETE)
mdb.models['Model-1'].rootAssembly.features.changeKey(
    fromName='cell_infini-1-1', toName='cell_infini-1')
# Rotation et translation finale
mdb.models['Model-1'].rootAssembly.translate(
    instanceList=('cell_infini-1',), vector=(tx, ty, 0.0))
mdb.models['Model-1'].rootAssembly.rotate(angle=theta, axisDirection=(0.0, 0.0,
                                                                        1.0), axisPoint=(144.0, 144.0, 0.0), instanceList=('cell_infini-1', ))

# First cut
print("First cut...")
s = mdb.models['Model-1'].ConstrainedSketch(
    name='__profile__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=(288.0, 288.0))
s.rectangle(point1=(-1000, -1000), point2=(288.0+1000, 288.0+1000))
p = mdb.models['Model-1'].Part(name='cutter_1', dimensionality=TWO_D_PLANAR,
                                type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['cutter_1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['cutter_1']
del mdb.models['Model-1'].sketches['__profile__']

mdb.models['Model-1'].rootAssembly.Instance(
    dependent=ON, name='cutter_1-1', part=mdb.models['Model-1'].parts['cutter_1'])
a1 = mdb.models['Model-1'].rootAssembly
a1.InstanceFromBooleanCut(name='cell_square',
                            instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['cell_infini-1'],
                            cuttingInstances=(a1.instances['cutter_1-1'], ),
                            originalInstances=DELETE)


mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((E, nu), ))

mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1',
                                              material='Material-1', thickness=None)


p = mdb.models['Model-1'].parts['cell_square']
f = p.faces
faces = f.getByBoundingBox(-tol, -tol, -tol, 288+tol, 288+tol, tol)
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['cell_square']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
                    offsetType=MIDDLE_SURFACE, offsetField='',
                    thicknessAssignment=FROM_SECTION)


a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['cell_square']
a.Instance(name='cell_square-1', part=p, dependent=ON)

mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
mdb.models['Model-1'].StaticStep(name='Step-2', previous='Step-1')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-2')
mdb.models['Model-1'].StaticStep(name='Step-3', previous='Step-2')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-3')

p = mdb.models['Model-1'].parts['cell_square']
p.seedPart(size=test['mesh_size'], deviationFactor=0.1, minSizeFactor=0.1)


elemType1 = mesh.ElemType(elemCode=CPS8R, elemLibrary=STANDARD)
elemType2 = mesh.ElemType(elemCode=CPS6M, elemLibrary=STANDARD,
                          secondOrderAccuracy=OFF, distortionControl=DEFAULT)
p = mdb.models['Model-1'].parts['cell_square']
f = p.faces
faces = f.getByBoundingBox(-tol, -tol, -tol, 288+tol, 288+tol, tol)
pickedRegions = (faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
p = mdb.models['Model-1'].parts['cell_square']
f = p.faces
pickedRegions = f.getByBoundingBox(-tol, -tol, -tol, 288+tol, 288+tol, tol)
p.setMeshControls(regions=pickedRegions, elemShape=TRI)
p = mdb.models['Model-1'].parts['cell_square']
p.generateMesh()
p = mdb.models['Model-1'].parts['cell_square']
p.regenerate()
a = mdb.models['Model-1'].rootAssembly
a.regenerate()

a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(0.0, -10.0, 0.0))
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(0.0, -20.0, 0.0))

sys.path.insert(8,
                r'/u/valmalette/abaqus_plugins/homtools0.9/Contraints_generation/Materials')
homogeneBoundary = homogeneBoundary.HomogeneBoundary()
homogeneBoundary.__init__()
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
pickedRP1 = r1.findAt((0, -10.0, 0.0),)
homogeneBoundary.setRefpoint1(RP1=pickedRP1)
a = mdb.models['Model-1'].rootAssembly
r11 = a.referencePoints
pickedRP2 = r11.findAt((0, -20.0, 0.0),)
homogeneBoundary.setRefpoint2(RP2=pickedRP2)

a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['cell_square-1'].edges
v1 = a.instances['cell_square-1'].vertices

a.Set(edges=e1.getByBoundingBox(-tol, -tol, -tol, 288+tol, +tol, tol) +
      e1.getByBoundingBox(-tol, -tol, -tol, tol, 288+tol, tol) +
      e1.getByBoundingBox(288-tol, -tol, -tol, 288+tol, 288+tol, tol) +
      e1.getByBoundingBox(-tol, 288-tol, -tol, 288+tol, 288+tol, tol), name='Set-edges')
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)

homogeneBoundary.setGroup1(set1=e1.getByBoundingBox(-tol, -tol, -tol, 288+tol, +tol, tol) +
                           e1.getByBoundingBox(-tol, -tol, -tol, tol, 288+tol, tol) +
                           e1.getByBoundingBox(288-tol, -tol, -tol, 288+tol, 288+tol, tol) +
                           e1.getByBoundingBox(-tol, 288-tol, -tol, 288+tol, 288+tol, tol))
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
homogeneBoundary.Effective(is_smallstrain=True, dim=2)

a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1 = (r1.findAt((0, -10.0, 0.0),), )
region = a.Set(referencePoints=refPoints1, name='Set-2295')

mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                     region=region, u1=0.02, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                     distributionType=UNIFORM, fieldName='', localCsys=None)
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1 = (r1.findAt((0, -20.0, 0.0),), )
region = a.Set(referencePoints=refPoints1, name='Set-2296')
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                     region=region, u1=0.0, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                     distributionType=UNIFORM, fieldName='', localCsys=None)

mdb.models['Model-1'].boundaryConditions['BC-1'].setValuesInStep(
    stepName='Step-2', u1=0.0, u2=0.02)
mdb.models['Model-1'].boundaryConditions['BC-1'].setValuesInStep(
    stepName='Step-3', u2=0.0)
mdb.models['Model-1'].boundaryConditions['BC-2'].setValuesInStep(
    stepName='Step-3', u1=0.02)

job_name ='KUBC_'+'_'.join([str(test[i]) for i in ['sample_name', 'geo_parameters', 'mat', 'trans_rot']]).replace('.', '%')
for char in ['(', ')', ' ']:
    job_name = job_name.replace(char, '')
    
make_job(mdb, job_name, test, os.getcwd())
mdb.jobs[job_name].writeInput(consistencyChecking=OFF)