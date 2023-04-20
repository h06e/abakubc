
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


def merge(input, output):
    a1 = mdb.models['Model-1'].rootAssembly
    instances=a1.instances.keys()
    instances_list=()
    for ins in instances:
        if input in ins:
            instances_list= instances_list+(a1.instances[ins],)
    a1.InstanceFromBooleanMerge(name=output, instances=instances_list, originalInstances=SUPPRESS, 
        domain=GEOMETRY)
    return

def add_support (improve_geometry_maker,skip_cylinders, test):
    print("Adding supports...") 
    model=mdb.models['Model-1']

    if 'support' not in model.parts.keys():
        model.PartFromGeometryFile(combine=False, dimensionality=
            THREE_D, geometryFile=mdb.acis, name='support', type=DEFORMABLE_BODY)
        # Decoupe support bonne epaisseur
        model.ConstrainedSketch(gridSpacing=1.09, name='__profile__', 
            sheetSize=43.68, transform=
            model.parts['support'].MakeSketchTransform(
            sketchPlane=model.parts['support'].faces[1], 
            sketchPlaneSide=SIDE1, 
            sketchUpEdge=model.parts['support'].edges[8], 
            sketchOrientation=RIGHT, origin=(46.0, 3.194106, 55.0)))
        model.parts['support'].projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=model.sketches['__profile__'])
        model.sketches['__profile__'].rectangle(point1=(-14.9875, 7.63)
            , point2=(14.4425, -7.085))
        model.parts['support'].CutExtrude(depth=55-test['thickness'], 
            flipExtrudeDirection=OFF, sketch=
            model.sketches['__profile__'], sketchOrientation=RIGHT, 
            sketchPlane=model.parts['support'].faces[1], 
            sketchPlaneSide=SIDE1, sketchUpEdge=
            model.parts['support'].edges[8])
        del model.sketches['__profile__']

    if improve_geometry_maker==True:
        for n_cote in range(4): # bottom, right, top, left
            print('Side '+str(n_cote+1)+' over 4')
            for n_cylindre in range(10):
                name_cylindre='support_'+str(n_cote)+"_"+str(n_cylindre if n_cote in[0,1] else 9-n_cylindre)
                model.rootAssembly.Instance(dependent=ON, name=
                    name_cylindre, part=model.parts['support'])
                model.rootAssembly.translate(instanceList=(name_cylindre,), 
                    vector=(28*(n_cylindre-1), 0.0, 0.0)) 
                model.rootAssembly.rotate(angle=90*n_cote,
                    axisDirection=(0.0, 0.0, 1.0), 
                    axisPoint=(144.0, 144.0, 0.0), instanceList=(name_cylindre,))
            
                a1 = model.rootAssembly
                try:a1.InstanceFromBooleanCut(name='tmp', 
                    instanceToBeCut=model.rootAssembly.instances['struct_no_support-1'], 
                    cuttingInstances=(a1.instances[name_cylindre], ), 
                    originalInstances=SUPPRESS)
                except:
                    a = model.rootAssembly
                    del a.features[name_cylindre]
                    skip_cylinders[n_cote].append(n_cylindre if n_cote in[0,1] else 9-n_cylindre)
                    print("Skiped (cy,side) : " ,n_cylindre if n_cote in[0,1] else 9-n_cylindre,n_cote)
                else:
                    a = model.rootAssembly
                    a.features['struct_no_support-1'].resume()
                    a.features[name_cylindre].resume()
                    a = model.rootAssembly
                    del a.features['tmp-1']
                    del model.parts['tmp']

    else:
        for n_cote in range(4): # bottom, right, top, left
            for n_cylindre in range(10):
                name_cylindre='support_'+str(n_cote)+"_"+str(n_cylindre)
                if n_cylindre not in skip_cylinders[n_cote]:
                    model.rootAssembly.Instance(dependent=ON, name=
                        name_cylindre, part=model.parts['support'])
                    model.rootAssembly.translate(instanceList=(name_cylindre,), 
                        vector=(28*(n_cylindre-1)*(n_cote in [0,1])+
                                28*(9-n_cylindre-1)*(n_cote in [2,3]), 0.0, 0.0)) 
                    model.rootAssembly.rotate(angle=90*n_cote,
                        axisDirection=(0.0, 0.0, 1.0), 
                        axisPoint=(144.0, 144.0, 0.0), instanceList=(name_cylindre,))


    merge("support_", "couronne_final")

    model.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, 
        instances=(
        model.rootAssembly.instances['couronne_final-1'], 
        model.rootAssembly.instances['struct_no_support-1']), name=
        'specimen', originalInstances=SUPPRESS)
    
    #__main__.skip_cylinders=skip_cylinders
    print('Adding supports completed.')

def add_support_2d (improve_geometry_maker,skip_cylinders):
    print("Adding supports...") 
    model=mdb.models['Model-1']

    if 'support' not in model.parts.keys():
        model.PartFromGeometryFile(combine=False, dimensionality=
            TWO_D_PLANAR, geometryFile=mdb.acis, name='support_2d', type=DEFORMABLE_BODY)

    if improve_geometry_maker==True:
        for n_cote in range(4): # bottom, right, top, left
            print('Side '+str(n_cote+1)+' over 4')
            for n_cylindre in range(10):
                name_cylindre='support_2d_'+str(n_cote)+"_"+str(n_cylindre if n_cote in[0,1] else 9-n_cylindre)
                model.rootAssembly.Instance(dependent=ON, name=
                    name_cylindre, part=model.parts['support_2d'])
                model.rootAssembly.translate(instanceList=(name_cylindre,), 
                    vector=(28*(n_cylindre-1), 0.0, 0.0)) 
                model.rootAssembly.rotate(angle=90*n_cote,
                    axisDirection=(0.0, 0.0, 1.0), 
                    axisPoint=(144.0, 144.0, 0.0), instanceList=(name_cylindre,))
            
                a1 = model.rootAssembly
                try:a1.InstanceFromBooleanCut(name='tmp', 
                    instanceToBeCut=model.rootAssembly.instances['struct_no_support-1'], 
                    cuttingInstances=(a1.instances[name_cylindre], ), 
                    originalInstances=SUPPRESS)
                except:
                    a = model.rootAssembly
                    del a.features[name_cylindre]
                    skip_cylinders[n_cote].append(n_cylindre if n_cote in[0,1] else 9-n_cylindre)
                    print("Skiped (cy,side) : " ,n_cylindre if n_cote in[0,1] else 9-n_cylindre,n_cote)
                else:
                    a = model.rootAssembly
                    a.features['struct_no_support-1'].resume()
                    a.features[name_cylindre].resume()
                    a = model.rootAssembly
                    del a.features['tmp-1']
                    del model.parts['tmp']

    else:
        for n_cote in range(4): # bottom, right, top, left
            for n_cylindre in range(10):
                name_cylindre='support_2d_'+str(n_cote)+"_"+str(n_cylindre)
                if n_cylindre not in skip_cylinders[n_cote]:
                    model.rootAssembly.Instance(dependent=ON, name=
                        name_cylindre, part=model.parts['support_2d'])
                    model.rootAssembly.translate(instanceList=(name_cylindre,), 
                        vector=(28*(n_cylindre-1)*(n_cote in [0,1])+
                                28*(9-n_cylindre-1)*(n_cote in [2,3]), 0.0, 0.0)) 
                    model.rootAssembly.rotate(angle=90*n_cote,
                        axisDirection=(0.0, 0.0, 1.0), 
                        axisPoint=(144.0, 144.0, 0.0), instanceList=(name_cylindre,))


    merge("support_", "couronne_final")

    model.rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, 
        instances=(
        model.rootAssembly.instances['couronne_final-1'], 
        model.rootAssembly.instances['struct_no_support-1']), name=
        'specimen', originalInstances=SUPPRESS)
    
    #__main__.skip_cylinders=skip_cylinders
    print('Adding supports completed.')