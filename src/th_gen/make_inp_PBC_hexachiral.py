import sys
try:
    sys.path.append("../src")
except:
    pass
import th_gen.periodicBoundary as periodicBoundary
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
from math import *
import json
from constants import *


def log(message):
    print >> sys.__stdout__, message


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
            test[i] = eval(test[i]) if i not in ['sample_name',
                                                 'status', 'comment', 'err'] else test[i]
        except NameError:
            pass

paths = eval(sys.argv[-1])

Mdb()
tol = 0.01

# Mat
E, nu = test['mat']        # DE base, E_air=0.0001 et nu_air=0.3

# Geo
L, width, radius = test['geo_parameters']

# nombre de cellules pour la contstruction avec les arrays (choisir assez grand)
aa = L/2.0/tan(pi/3.0)
bb = L/2.0*tan(pi/6.0)

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


# Arrays
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-4']
a1.Instance(name='Part-4-2', part=p, dependent=ON)
a1.Instance(name='Part-4-3', part=p, dependent=ON)
a1.Instance(name='Part-4-4', part=p, dependent=ON)
a1.Instance(name='Part-4-5', part=p, dependent=ON)
a1.Instance(name='Part-4-6', part=p, dependent=ON)
a1.Instance(name='Part-4-7', part=p, dependent=ON)
a1.rotate(instanceList=('Part-4-1', 'Part-4-2', 'Part-4-3', 'Part-4-4', 'Part-4-5', 'Part-4-6', 'Part-4-7', ),
          axisPoint=(0.0, 0.0, 0.0),          axisDirection=(0.0, 0.0, 1.0), angle=-180/pi*asin((radius-width/2)/(L/2.0)))

a1.translate(instanceList=('Part-4-2', ), vector=(L, 0.0, 0.0))
a1.translate(instanceList=('Part-4-3', ), vector=(L/2.0, L*cos(pi/6.0), 0.0))
a1.translate(instanceList=('Part-4-4', ), vector=(-L/2.0, L*cos(pi/6.0), 0.0))
a1.translate(instanceList=('Part-4-5', ), vector=(-L, 0.0, 0.0))
a1.translate(instanceList=('Part-4-6', ), vector=(L/2.0, -L*cos(pi/6.0), 0.0))
a1.translate(instanceList=('Part-4-7', ), vector=(-L/2.0, -L*cos(pi/6.0), 0.0))

a1.InstanceFromBooleanMerge(name='Part-5', instances=(a1.instances['Part-4-1'],
                                                      a1.instances['Part-4-2'], a1.instances['Part-4-3'],
                                                      a1.instances['Part-4-4'], a1.instances['Part-4-5'],
                                                      a1.instances['Part-4-6'], a1.instances['Part-4-7'], ),
                            originalInstances=DELETE,
                            domain=GEOMETRY)

# ----------------------------------------------------------------------------------------
# First cut
print("First cut...")
s = mdb.models['Model-1'].ConstrainedSketch(
    name='__profile__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(-L/2.0, -L*cos(pi/6.0)), point2=(L/2.0, L*cos(pi/6.0)))
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
a1.InstanceFromBooleanCut(name='cell',
                          instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Part-5-1'],
                          cuttingInstances=(a1.instances['cutter_1-1'], ),
                          originalInstances=DELETE)

# * SAVE THE POROSITY
a = mdb.models['Model-1'].rootAssembly
area = a.getArea(mdb.models['Model-1'].parts['cell'].faces)
area_frame = L*2*L*cos(pi/6.0)
porosity = (area_frame - area) / area_frame
with open(os.path.join(paths[POROSITY], '_'.join([test['sample_name'], str(test['geo_parameters'])])+'.json'), 'w') as f:
    json.dump(porosity, f, indent=4, separators=(", ", ": "), sort_keys=True)

mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((E, nu), ))

mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1',
                                              material='Material-1', thickness=None)

p = mdb.models['Model-1'].parts['cell']
f = p.faces
faces = f.getByBoundingBox(-L/2.0-tol, -L*cos(pi/6.0) -
                           tol, -tol, L/2.0+tol, L*cos(pi/6.0)+tol, tol)
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['cell']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
                    offsetType=MIDDLE_SURFACE, offsetField='',
                    thicknessAssignment=FROM_SECTION)


p = mdb.models['Model-1'].parts['cell']
p.seedPart(size=0.1, deviationFactor=0.1, minSizeFactor=0.1)
elemType1 = mesh.ElemType(elemCode=CPS8R, elemLibrary=STANDARD)
elemType2 = mesh.ElemType(elemCode=CPS6M, elemLibrary=STANDARD,
                          secondOrderAccuracy=OFF, distortionControl=DEFAULT)
p = mdb.models['Model-1'].parts['cell']
f = p.faces
faces = f.getByBoundingBox(-L/2.0-tol, -L*cos(pi/6.0) -
                           tol, -tol, L/2.0+tol, L*cos(pi/6.0)+tol, tol)
pickedRegions = (faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
p = mdb.models['Model-1'].parts['cell']
f = p.faces
pickedRegions = f.getByBoundingBox(-L/2.0-tol, -L*cos(pi/6.0) -
                                   tol, -tol, L/2.0+tol, L*cos(pi/6.0)+tol, tol)
p.setMeshControls(regions=pickedRegions, elemShape=TRI)
p = mdb.models['Model-1'].parts['cell']
p.generateMesh()
p = mdb.models['Model-1'].parts['cell']
p.regenerate()
a = mdb.models['Model-1'].rootAssembly
a.regenerate()

a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['cell']
a.Instance(name='cell-1', part=p, dependent=ON)

a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(0.0, -50.0, 0.0))
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(0.0, -60.0, 0.0))


periodicBoundary = periodicBoundary.PeriodicBoundary()
periodicBoundary.__init__()

a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
pickedRP1 = r1.findAt((0, -50.0, 0.0),)
periodicBoundary.setRefpoint1(RP1=pickedRP1)
a = mdb.models['Model-1'].rootAssembly
r11 = a.referencePoints
pickedRP2 = r11.findAt((0, -60.0, 0.0),)
periodicBoundary.setRefpoint2(RP2=pickedRP2)
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['cell-1'].edges
pickedSet1 = e1.getByBoundingBox(-tol-L/2.0, -tol -
                                 L*cos(pi/6.0), -tol, tol+L/2.0, -L*cos(pi/6.0)+tol, tol)
periodicBoundary.setGroup1(set1=pickedSet1)
a = mdb.models['Model-1'].rootAssembly
e21 = a.instances['cell-1'].edges
pickedSet2 = e1.getByBoundingBox(-tol-L/2.0, -tol +
                                 L*cos(pi/6.0), -tol, tol+L/2.0, +L*cos(pi/6.0)+tol, tol)
periodicBoundary.setGroup2(set2=pickedSet2)
periodicBoundary.Periodic(is_smallstrain=True, dim=2,
                          Vx=0, Vy=2*L*cos(pi/6.0), Vz=0)

periodicBoundary.__init__()
periodicBoundary.setRefpoint1(RP1=pickedRP1)
periodicBoundary.setRefpoint2(RP2=pickedRP2)
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['cell-1'].edges
pickedSet1 = e1.getByBoundingBox(-tol-L/2.0, -tol -
                                 L*cos(pi/6.0), -tol, tol-L/2.0, L*cos(pi/6.0)+tol, tol)
periodicBoundary.setGroup1(set1=pickedSet1)
a = mdb.models['Model-1'].rootAssembly
e21 = a.instances['cell-1'].edges
pickedSet2 = e1.getByBoundingBox(-tol+L/2.0, -tol -
                                 L*cos(pi/6.0), -tol, tol+L/2.0, L*cos(pi/6.0)+tol, tol)
periodicBoundary.setGroup2(set2=pickedSet2)
periodicBoundary.Periodic(is_smallstrain=True, dim=2, Vx=L, Vy=0, Vz=0)

mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
mdb.models['Model-1'].StaticStep(name='Step-2', previous='Step-1')
mdb.models['Model-1'].StaticStep(name='Step-3', previous='Step-2')

a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1 = (pickedRP1, )
region = a.Set(referencePoints=refPoints1, name='Set-REF_PT_1')
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                     region=region, u1=0.02, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                     distributionType=UNIFORM, fieldName='', localCsys=None)
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1 = (pickedRP2, )
region = a.Set(referencePoints=refPoints1, name='Set-REF_PT_2')
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                     region=region, u1=0.0, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                     distributionType=UNIFORM, fieldName='', localCsys=None)
mdb.models['Model-1'].boundaryConditions['BC-1'].setValuesInStep(
    stepName='Step-2', u1=0.0, u2=0.02)
mdb.models['Model-1'].boundaryConditions['BC-1'].setValuesInStep(
    stepName='Step-3', u2=0.0)
mdb.models['Model-1'].boundaryConditions['BC-2'].setValuesInStep(
    stepName='Step-3', u1=0.02)


job_name = 'PBC_'+'_'.join([str(test[i])
                            for i in ['sample_name', 'geo_parameters', 'mat']]).replace('.', '%')
for char in ['(', ')', ' ']:
    job_name = job_name.replace(char, '')

mdb.Job(name=job_name, model='Model-1', description='', type=ANALYSIS,
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
        scratch=os.getcwd(), resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1,
        numGPUs=0)

# # * Brute force the writing of the input file because Abq sometime return an error
# inp_is_written=False
# while not inp_is_written:
#     try:
#         mdb.jobs[job_name].writeInput(consistencyChecking=OFF)  # Write the inp file
#     except:
#         pass
#     else:
#         inp_is_written=True

mdb.jobs[job_name].submit(consistencyChecking=OFF)
mdb.jobs[job_name].waitForCompletion()
