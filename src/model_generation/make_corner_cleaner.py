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


def clean_corners(test):
    model=mdb.models['Model-1']

    print('Corner cleaner...')
    s = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.Line(point1=(0.0, 0.0), point2=(0.0, 7.5))
    if test['corner_cleaner']=='ADV_SHEAR':
        ptc=(35.0,35.0)
        s.Line(point1=(0.0, 7.5), point2=(7.5/2-2, -(7.5/2-2)+7.5))
        p=s.Line(point1=(7.5/2-2, -(7.5/2-2)+7.5), point2=ptc)
        pp=s.Line(point1=ptc, point2=(7.5/2+2, -(7.5/2+2)+7.5))
        s.Line(point1=(7.5/2+2, -(7.5/2+2)+7.5), point2=(7.5, 0.0))
        s.FilletByRadius(radius=2.0, curve1=p, nearPoint1=(7.5/2-2, -(7.5/2-2)+7.5), curve2=pp, 
        nearPoint2=(7.5/2+2, -(7.5/2+2)+7.5))
    else:s.Line(point1=(0.0, 7.5), point2=(7.5, 0.0))
    s.Line(point1=(7.5, 0.0), point2=(0.0, 0.0))
    p = model.Part(name='corner_cleaner', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = model.parts['corner_cleaner']
    p.BaseSolidExtrude(sketch=s, depth=test['thickness'])
    s.unsetPrimaryObject()
    p = model.parts['corner_cleaner']
    del model.sketches['__profile__']

    s = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.Line(point1=(0.0, 7.45), point2=(0.0, 7.5))
    s.Line(point1=(0.0, 7.5), point2=(7.5, 0.0))
    s.Line(point1=(7.5, 0.0), point2=(7.45, 0.0))
    s.Line(point1=(7.45, 0.0), point2=(0.0, 7.45))
    p = model.Part(name='corner_checker', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = model.parts['corner_checker']
    p.BaseSolidExtrude(sketch=s, depth=test['thickness'])
    s.unsetPrimaryObject()
    p = model.parts['corner_checker']
    del model.sketches['__profile__']

    try:model.rootAssembly.features.changeKey(fromName='specimen'+'-1',toName='specimen')
    except:pass

    for corner in range(1,5):
        a = model.rootAssembly
        p = model.parts['corner_cleaner']
        a.Instance(name='corner_cleaner-'+str(corner), part=p, dependent=ON)
        a.rotate(instanceList=('corner_cleaner-'+str(corner), ), axisPoint=(144.0, 144.0, 0.0), 
            axisDirection=(0.0, 0.0, 1.0), angle=90.0*(corner-1))
        a1 = model.rootAssembly
        if True: # ? test['force_clean']
            try:
                a1.InstanceFromBooleanCut(name='specimen', 
                    instanceToBeCut=model.rootAssembly.instances['specimen'], 
                    cuttingInstances=(a1.instances['corner_cleaner-'+str(corner)], ), 
                    originalInstances=DELETE)
            except: del a1.features['corner_cleaner-'+str(corner)]
            else:
                model.rootAssembly.features.changeKey(fromName='specimen'+'-1',toName='specimen')
        else:
            a = model.rootAssembly
            pp=model.parts['corner_checker']
            a.Instance(name='corner_checker-'+str(corner), part=pp, dependent=ON)
            a.rotate(instanceList=('corner_checker-'+str(corner), ), axisPoint=(144.0, 144.0, 0.0), 
            axisDirection=(0.0, 0.0, 1.0), angle=90.0*(corner-1))
            try:a1.InstanceFromBooleanCut(name='tmp', 
                    instanceToBeCut=model.rootAssembly.instances['specimen'], 
                    cuttingInstances=(a1.instances['corner_checker-'+str(corner)], ), 
                    originalInstances=DELETE)
            except:
                a1.InstanceFromBooleanCut(name='specimen', 
                    instanceToBeCut=model.rootAssembly.instances['specimen'], 
                    cuttingInstances=(a1.instances['corner_cleaner-'+str(corner)], ), 
                    originalInstances=DELETE)
                
            else:
                try:model.rootAssembly.features.changeKey(fromName='specimen'+'-1',toName='specimen')
                except:pass
                a1.features['specimen'].resume()
                del a1.features['tmp-1']
            del a1.features['corner_checker-'+str(corner)]
            del a1.features['corner_cleaner-'+str(corner)]
    
    print('Corner cleaner completed.')



def clean_corners_2d(test):
    model=mdb.models['Model-1']

    print('Corner cleaner...')
    s = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.Line(point1=(0.0, 0.0), point2=(0.0, 7.5))
    if test['corner_cleaner']=='ADV_SHEAR':
        ptc=(35.0,35.0)
        s.Line(point1=(0.0, 7.5), point2=(7.5/2-2, -(7.5/2-2)+7.5))
        p=s.Line(point1=(7.5/2-2, -(7.5/2-2)+7.5), point2=ptc)
        pp=s.Line(point1=ptc, point2=(7.5/2+2, -(7.5/2+2)+7.5))
        s.Line(point1=(7.5/2+2, -(7.5/2+2)+7.5), point2=(7.5, 0.0))
        s.FilletByRadius(radius=2.0, curve1=p, nearPoint1=(7.5/2-2, -(7.5/2-2)+7.5), curve2=pp, 
        nearPoint2=(7.5/2+2, -(7.5/2+2)+7.5))
    else:s.Line(point1=(0.0, 7.5), point2=(7.5, 0.0))
    s.Line(point1=(7.5, 0.0), point2=(0.0, 0.0))
    p = model.Part(name='corner_cleaner', dimensionality=TWO_D_PLANAR, 
        type=DEFORMABLE_BODY)
    p = model.parts['corner_cleaner']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = model.parts['corner_cleaner']
    del model.sketches['__profile__']

    s = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.Line(point1=(0.0, 7.45), point2=(0.0, 7.5))
    s.Line(point1=(0.0, 7.5), point2=(7.5, 0.0))
    s.Line(point1=(7.5, 0.0), point2=(7.45, 0.0))
    s.Line(point1=(7.45, 0.0), point2=(0.0, 7.45))
    p = model.Part(name='corner_checker', dimensionality=TWO_D_PLANAR, 
        type=DEFORMABLE_BODY)
    p = model.parts['corner_checker']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = model.parts['corner_checker']
    del model.sketches['__profile__']

    try:model.rootAssembly.features.changeKey(fromName='specimen'+'-1',toName='specimen')
    except:pass

    for corner in range(1,5):
        a = model.rootAssembly
        p = model.parts['corner_cleaner']
        a.Instance(name='corner_cleaner-'+str(corner), part=p, dependent=ON)
        a.rotate(instanceList=('corner_cleaner-'+str(corner), ), axisPoint=(144.0, 144.0, 0.0), 
            axisDirection=(0.0, 0.0, 1.0), angle=90.0*(corner-1))
        a1 = model.rootAssembly
        if True: # ? test['force_clean']
            try:
                a1.InstanceFromBooleanCut(name='specimen', 
                    instanceToBeCut=model.rootAssembly.instances['specimen'], 
                    cuttingInstances=(a1.instances['corner_cleaner-'+str(corner)], ), 
                    originalInstances=DELETE)
            except: del a1.features['corner_cleaner-'+str(corner)]
            else:
                model.rootAssembly.features.changeKey(fromName='specimen'+'-1',toName='specimen')
        else:
            a = model.rootAssembly
            pp=model.parts['corner_checker']
            a.Instance(name='corner_checker-'+str(corner), part=pp, dependent=ON)
            a.rotate(instanceList=('corner_checker-'+str(corner), ), axisPoint=(144.0, 144.0, 0.0), 
            axisDirection=(0.0, 0.0, 1.0), angle=90.0*(corner-1))
            try:a1.InstanceFromBooleanCut(name='tmp', 
                    instanceToBeCut=model.rootAssembly.instances['specimen'], 
                    cuttingInstances=(a1.instances['corner_checker-'+str(corner)], ), 
                    originalInstances=DELETE)
            except:
                a1.InstanceFromBooleanCut(name='specimen', 
                    instanceToBeCut=model.rootAssembly.instances['specimen'], 
                    cuttingInstances=(a1.instances['corner_cleaner-'+str(corner)], ), 
                    originalInstances=DELETE)
                
            else:
                try:model.rootAssembly.features.changeKey(fromName='specimen'+'-1',toName='specimen')
                except:pass
                a1.features['specimen'].resume()
                del a1.features['tmp-1']
            del a1.features['corner_checker-'+str(corner)]
            del a1.features['corner_cleaner-'+str(corner)]
    
    print('Corner cleaner completed.')