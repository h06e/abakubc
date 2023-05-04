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
import csv

def log(message):
    print >> sys.__stdout__, message

def merge(input, output, keepIntersections=OFF):
    """fonction qui permet de merge en fonction du nom des instances : celles qui contiennent input"""
    a1 = mdb.models['Model-1'].rootAssembly
    instances = a1.instances.keys()
    instances_list = ()
    for ins in instances:
        if input in ins:
            instances_list = instances_list+(a1.instances[ins],)
    a1.InstanceFromBooleanMerge(name=output, instances=instances_list, originalInstances=DELETE,
                                domain=GEOMETRY,keepIntersections=keepIntersections)


# ? lauch abq with $ env LC_ALL="en_US.UTF8" abaqus cae

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

# Geo
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
s.move(vector=(144.0, 144.0), objectList=tuple(gg[1] for gg in g.items()))
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

mdb.models['Model-1'].rootAssembly.translate(
    instanceList=('Part-1-1',), vector=(tx, ty, 0.0))
mdb.models['Model-1'].rootAssembly.rotate(angle=theta, axisDirection=(0.0, 0.0,
                                                                        1.0), axisPoint=(144.0, 144.0, 0.0), instanceList=('Part-1-1', ))

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

mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((E, nu), ))

mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1',
                                              material='Material-1', thickness=None)


p = mdb.models['Model-1'].parts['cell_square-1']
f = p.faces
faces = f.getByBoundingBox(-tol, -tol, -tol, 288+tol, 288+tol, tol)
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['cell_square-1']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
                    offsetType=MIDDLE_SURFACE, offsetField='',
                    thicknessAssignment=FROM_SECTION)


a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['cell_square-1']
a.Instance(name='cell_square-1-1', part=p, dependent=ON)

mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
mdb.models['Model-1'].StaticStep(name='Step-2', previous='Step-1')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-2')
mdb.models['Model-1'].StaticStep(name='Step-3', previous='Step-2')
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-3')

p = mdb.models['Model-1'].parts['cell_square-1']
p.seedPart(size=test['mesh_size'], deviationFactor=0.1, minSizeFactor=0.1)


elemType1 = mesh.ElemType(elemCode=CPS8R, elemLibrary=STANDARD)
elemType2 = mesh.ElemType(elemCode=CPS6M, elemLibrary=STANDARD,
                          secondOrderAccuracy=OFF, distortionControl=DEFAULT)
p = mdb.models['Model-1'].parts['cell_square-1']
f = p.faces
faces = f.getByBoundingBox(-tol, -tol, -tol, 288+tol, 288+tol, tol)
pickedRegions = (faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
p = mdb.models['Model-1'].parts['cell_square-1']
f = p.faces
pickedRegions = f.getByBoundingBox(-tol, -tol, -tol, 288+tol, 288+tol, tol)
p.setMeshControls(regions=pickedRegions, elemShape=TRI)
p = mdb.models['Model-1'].parts['cell_square-1']
p.generateMesh()
p = mdb.models['Model-1'].parts['cell_square-1']
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
e1 = a.instances['cell_square-1-1'].edges
v1 = a.instances['cell_square-1-1'].vertices

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

