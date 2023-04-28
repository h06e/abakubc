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
from make_job import make_job

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
scale = test['geo_parameters']
L=20.0

acis = mdb.openAcis(
    os.path.join(paths[SRC], 'ressources', 'r0_cell.sat'), 
    scaleFromFile=OFF)
mdb.models['Model-1'].PartFromGeometryFile(name='Part-1', geometryFile=acis, 
    combine=False, dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY, 
    scale=scale)
p = mdb.models['Model-1'].parts['Part-1']


# * SAVE THE POROSITY
a = mdb.models['Model-1'].rootAssembly
area=a.getArea(mdb.models['Model-1'].parts['Part-1'].faces)
area_frame=(L*scale)**2
porosity = (area_frame - area) / area_frame
with open(os.path.join(paths[POROSITY],'_'.join([test['sample_name'],str(test['geo_parameters'])])+'.json'),'w') as f:
    json.dump(porosity,f, indent=4, separators=(", ", ": "), sort_keys=True)

mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((E, nu), ))

mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', 
    material='Material-1', thickness=None)

p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
faces = f.getByBoundingBox(-tol, -tol,-tol,L*scale+tol, L*scale+tol,tol)
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
faces = f.getByBoundingBox(-tol, -tol,-tol,L*scale+tol, L*scale+tol,tol)
pickedRegions =(faces, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
p = mdb.models['Model-1'].parts['Part-1']
f = p.faces
pickedRegions = f.getByBoundingBox(-tol, -tol,-tol,L*scale+tol, L*scale+tol,tol)
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
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('Part-1-1', ), vector=(-L*scale/2.0, -L*scale/2.0, 0.0))

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
pickedSet1 = e1.getByBoundingBox(-tol-L*scale/2.0,-tol-L*scale/2.0,-tol,tol+(L*scale/2.0),-L*scale/2.0+tol,tol)
periodicBoundary.setGroup1(set1=pickedSet1)
a = mdb.models['Model-1'].rootAssembly
e21 = a.instances['Part-1-1'].edges
pickedSet2 = e1.getByBoundingBox(-tol-L*scale/2.0,-tol+L*scale/2.0,-tol,tol+(L*scale/2.0),+L*scale/2.0+tol,tol)
periodicBoundary.setGroup2(set2=pickedSet2)
periodicBoundary.Periodic(is_smallstrain=True, dim=2, Vx=0, Vy=L*scale, Vz=0)

periodicBoundary.__init__()
periodicBoundary.setRefpoint1(RP1=pickedRP1)
periodicBoundary.setRefpoint2(RP2=pickedRP2)
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
pickedSet1 =e1.getByBoundingBox(-tol-(L*scale/2.0),-tol-L*scale/2.0,-tol,tol-(L*scale/2.0),L*scale/2.0+tol,tol)
periodicBoundary.setGroup1(set1=pickedSet1)
a = mdb.models['Model-1'].rootAssembly
e21 = a.instances['Part-1-1'].edges
pickedSet2 =e21.getByBoundingBox(-tol+(L*scale/2.0),-tol-L*scale/2.0,-tol,tol+(L*scale/2.0),L*scale/2.0+tol,tol)
periodicBoundary.setGroup2(set2=pickedSet2)
periodicBoundary.Periodic(is_smallstrain=True, dim=2, Vx=L*scale, Vy=0, Vz=0)

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


mdb.saveAs('pbc.cae')


job_name = 'PBC_'+'_'.join([str(test[i]) for i in ['sample_name', 'geo_parameters', 'mat']]).replace('.', '%')
for char in ['(', ')', ' ']:
    job_name = job_name.replace(char, '')

make_job(mdb, job_name, test, os.getcwd())
mdb.jobs[job_name].writeInput(consistencyChecking=OFF)
