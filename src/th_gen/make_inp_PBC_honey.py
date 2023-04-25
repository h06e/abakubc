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


test = eval(sys.argv[-2])
for i in test:
    if len(test[i]) == 0:
        test[i] = None
    else:
        try:
            test[i] = eval(test[i]) if i not in ['sample_name', 'status', 'comment', 'err'] else test[i]
        except NameError:
            pass

paths = eval(sys.argv[-1])

Mdb()
tol = 0.01

# Mat
E, nu = test['mat']        # DE base, E_air=0.0001 et nu_air=0.3

# Geo
L , width = test['geo_parameters']


#------------------------------------------------
# nombre de cellules pour la contstruction avec les arrays (choisir assez grand)
aa=L/2/tan(pi/3)
bb=L/2*tan(pi/6)

#Construction de la piece
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(-L/2, -(aa+2*bb)), point2=(L/2, (aa+2*bb)))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']



session.viewports['Viewport: 1'].setValues(displayedObject=None)
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=814.58, gridSpacing=20.36)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)

pt1=(0.0, aa+bb)
pt2=(-L/2, bb)
pt3=(-L/2,-bb)
pt4=(0.0, -aa-bb)
pt5=(L/2, -bb)
pt6=(L/2, bb)
s.Line(point1=pt1, point2=pt2)
s.Line(point1=pt2, point2=pt3)
s.Line(point1=pt3, point2=pt4)
s.Line(point1=pt4, point2=pt5)
s.Line(point1=pt5, point2=pt6)
s.Line(point1=pt6, point2=pt1)
s.offset(distance=width/2, objectList=(g[6], g[7], g[8], g[9], g[10], g[11]), 
    side=RIGHT)
s.delete(objectList=(g[6], g[11], g[10], g[9], g[8], g[7]))
s.move(vector=(-L, -(aa+2*bb)), objectList=(g[12], g[13], g[14], g[15], g[16], g[17]))
s.copyMove(vector=(L/2, (aa+2*bb)), objectList=(g[12], g[13], g[14], g[15], g[16], g[17]))
s.linearPattern(geomList=(g[12], g[13], g[14], g[15], g[16], g[17]), vertexList=(
    ), number1=2, spacing1=L, angle1=0.0, number2=2, spacing2=2*(aa+2*bb), 
    angle2=90.0)
s.linearPattern(geomList=(g[18], g[19], g[20], g[21], g[22], g[23]), vertexList=(
    ), number1=2, spacing1=L, angle1=0.0, number2=2, spacing2=2*(aa+2*bb), 
    angle2=90.0)

p = mdb.models['Model-1'].parts['Part-1']
p.Cut(sketch=s)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# * SAVE THE POROSITY
a = mdb.models['Model-1'].rootAssembly
area=a.getArea(mdb.models['Model-1'].parts['Part-1'].faces)
area_frame=L*2*(aa+2*bb)
porosity = (area_frame - area) / area_frame
with open(os.path.join(paths[POROSITY],'_'.join([test['sample_name'],str(test['geo_parameters'])])+'.json'),'w') as f:
    json.dump(porosity,f, indent=4, separators=(", ", ": "), sort_keys=True)

mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((E, nu), ))

mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', 
    material='Material-1', thickness=None)

p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getByBoundingBox(-L/2-tol, -(aa+2*bb)-tol,-tol,L/2+tol, (aa+2*bb)+tol,tol)
region = p.Set(faces=faces, name='Set-1')
p = mdb.models['Model-1'].parts['Part-1']
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)


p = mdb.models['Model-1'].parts['Part-1']
p.seedPart(size=0.1, deviationFactor=0.1, minSizeFactor=0.1)
elemType1 = mesh.ElemType(elemCode=CPS8R, elemLibrary=STANDARD)
elemType2 = mesh.ElemType(elemCode=CPS6M, elemLibrary=STANDARD, 
    secondOrderAccuracy=OFF, distortionControl=DEFAULT)
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getByBoundingBox(-L/2-tol, -(aa+2*bb)-tol,-tol,L/2+tol, (aa+2*bb)+tol,tol)
pickedRegions =(faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedRegions = f.getByBoundingBox(-L/2-tol, -(aa+2*bb)-tol,-tol,L/2+tol, (aa+2*bb)+tol,tol)
p.setMeshControls(regions=pickedRegions, elemShape=TRI)
p = mdb.models['Model-1'].parts['Part-1']
p.generateMesh()
p = mdb.models['Model-1'].parts['Part-1']
p.regenerate()
a = mdb.models['Model-1'].rootAssembly
a.regenerate()

a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=ON)

a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(0.0, -50.0, 0.0))
a = mdb.models['Model-1'].rootAssembly
a.ReferencePoint(point=(0.0, -60.0, 0.0))


periodicBoundary=periodicBoundary.PeriodicBoundary()
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
e1 = a.instances['Part-1-1'].edges
pickedSet1 = e1.getByBoundingBox(-tol-L/2,-tol-(aa+2*bb),-tol,tol+L/2,-(aa+2*bb)+tol,tol)
periodicBoundary.setGroup1(set1=pickedSet1)
a = mdb.models['Model-1'].rootAssembly
e21 = a.instances['Part-1-1'].edges
pickedSet2 = e1.getByBoundingBox(-tol-L/2,-tol+(aa+2*bb),-tol,tol+L/2,+(aa+2*bb)+tol,tol)
periodicBoundary.setGroup2(set2=pickedSet2)
periodicBoundary.Periodic(is_smallstrain=True, dim=2, Vx=0, Vy=2*(aa+2*bb), Vz=0)

periodicBoundary.__init__()
periodicBoundary.setRefpoint1(RP1=pickedRP1)
periodicBoundary.setRefpoint2(RP2=pickedRP2)
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
pickedSet1 =e1.getByBoundingBox(-tol-L/2,-tol-(aa+2*bb),-tol,tol-L/2,(aa+2*bb)+tol,tol)
periodicBoundary.setGroup1(set1=pickedSet1)
a = mdb.models['Model-1'].rootAssembly
e21 = a.instances['Part-1-1'].edges
pickedSet2 =e1.getByBoundingBox(-tol+L/2,-tol-(aa+2*bb),-tol,tol+L/2,(aa+2*bb)+tol,tol)
periodicBoundary.setGroup2(set2=pickedSet2)
periodicBoundary.Periodic(is_smallstrain=True, dim=2, Vx=L, Vy=0, Vz=0)

mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
mdb.models['Model-1'].StaticStep(name='Step-2', previous='Step-1')
mdb.models['Model-1'].StaticStep(name='Step-3', previous='Step-2')

a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1=(pickedRP1, )
region = a.Set(referencePoints=refPoints1, name='Set-REF_PT_1')
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1', 
    region=region, u1=0.02, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
    distributionType=UNIFORM, fieldName='', localCsys=None)
a = mdb.models['Model-1'].rootAssembly
r1 = a.referencePoints
refPoints1=(pickedRP2, )
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




job_name = 'PBC_'+'_'.join([str(test[i]) for i in ['sample_name', 'geo_parameters', 'mat']]).replace('.', '%')
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

