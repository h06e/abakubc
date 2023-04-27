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
from constants import *
import json
from make_job import make_job

def log(message):
    print >> sys.__stdout__, message


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
width, length, angle = test['geo_parameters']

lx=2*length*sin(angle*pi/180.0/2.0)
ly=2*length*cos(angle*pi/180.0/2.0)


# ------------------------------------------------
# nombre de cellules pour la contstruction avec les arrays (choisir assez grand)



# Construction de la piece
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                            sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
l1 = s.Line(point1=(0.0, ly/2.0),
            point2=(-lx/2.0, 0.0))
l2 = s.Line(point1=(-lx/2.0, 0.0),
            point2=(0.0, -ly/2.0))
l3 = s.Line(point1=(0.0, -ly/2.0),
            point2=(lx/2.0, 0.0))
l4 = s.Line(point1=(lx/2.0, 0.0),
            point2=(0.0, ly/2.0))
s.offset(distance=width/2.0, objectList=(l1, l2, l3, l4), side=RIGHT)
s.offset(distance=width/2.0, objectList=(l1, l2, l3, l4), side=LEFT)
s.setAsConstruction(objectList=(l1, l2, l3, l4))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                               type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']

s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=150.93, gridSpacing=3.77)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Part-1']
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
s1.rectangle(point1=(-lx/2.0, -ly/2.0), point2=(lx/2.0, ly/2.0))
s1.rectangle(point1=(-1000, -1000), point2=(1000, 1000))
p = mdb.models['Model-1'].parts['Part-1']
p.Cut(sketch=s1)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# * SAVE THE POROSITY
a = mdb.models['Model-1'].rootAssembly
area=a.getArea(mdb.models['Model-1'].parts['Part-1'].faces)
area_frame=lx*ly
porosity = (area_frame - area) / area_frame
with open(os.path.join(paths[POROSITY],'_'.join([test['sample_name'],str(test['geo_parameters'])])+'.json'),'w') as f:
    json.dump(porosity,f, indent=4, separators=(", ", ": "), sort_keys=True)

mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((E, nu), ))

mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1',
                                              material='Material-1', thickness=None)

p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getByBoundingBox(-1000, -1000, -tol, 1000, 1000, tol)
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
faces = f.getByBoundingBox(-lx/2-tol, -ly/2.0-tol,-tol,lx/2.0+tol, ly/2.0+tol,tol)
pickedRegions =(faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedRegions = f.getByBoundingBox(-lx/2-tol, -ly/2.0-tol,-tol,lx/2.0+tol, ly/2.0+tol,tol)
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
pickedSet1 = e1.getByBoundingBox(-tol-lx/2.0,-tol-ly/2.0,-tol,tol+lx/2,-ly/2.0+tol,tol)
periodicBoundary.setGroup1(set1=pickedSet1)
a = mdb.models['Model-1'].rootAssembly
e21 = a.instances['Part-1-1'].edges
pickedSet2 = e1.getByBoundingBox(-tol-lx/2.0,-tol+ly/2.0,-tol,tol+lx/2.0,+ly/2.0+tol,tol)
periodicBoundary.setGroup2(set2=pickedSet2)
periodicBoundary.Periodic(is_smallstrain=True, dim=2, Vx=0, Vy=ly, Vz=0)

periodicBoundary.__init__()
periodicBoundary.setRefpoint1(RP1=pickedRP1)
periodicBoundary.setRefpoint2(RP2=pickedRP2)
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
pickedSet1 =e1.getByBoundingBox(-tol-lx/2.0,-tol-ly/2.0,-tol,tol-lx/2.0,ly/2.0+tol,tol)
periodicBoundary.setGroup1(set1=pickedSet1)
a = mdb.models['Model-1'].rootAssembly
e21 = a.instances['Part-1-1'].edges
pickedSet2 =e1.getByBoundingBox(-tol+lx/2.0,-tol-ly/2.0,-tol,tol+lx/2.0,ly/2.0+tol,tol)
periodicBoundary.setGroup2(set2=pickedSet2)
periodicBoundary.Periodic(is_smallstrain=True, dim=2, Vx=lx, Vy=0, Vz=0)

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

make_job(mdb, job_name, test, os.getcwd())
mdb.jobs[job_name].writeInput(consistencyChecking=OFF)