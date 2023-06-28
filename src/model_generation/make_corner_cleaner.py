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

def main_clean_corners(paths,test):
    if test['dim']==3:
        clean_corners(paths, test)
    else:
        clean_corners_2d(paths, test)

def clean_corners(paths, test):
    model=mdb.models['Model-1']

    print('Corner cleaner...')
    s = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.Line(point1=(0.0, 0.0), point2=(0.0, 7.5))
    if True: # ? test['corner_cleaner']=='ADV_SHEAR'
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
        try:
            a1.InstanceFromBooleanCut(name='specimen', 
                instanceToBeCut=model.rootAssembly.instances['specimen'], 
                cuttingInstances=(a1.instances['corner_cleaner-'+str(corner)], ), 
                originalInstances=DELETE)
        except: del a1.features['corner_cleaner-'+str(corner)]
        else:
            model.rootAssembly.features.changeKey(fromName='specimen'+'-1',toName='specimen')

    
    print('Corner cleaner completed.')



def clean_corners_2d(paths, test):

    if test['corner_cleaner'] in [True,'full']:
        acis = mdb.openAcis(
        os.path.join(os.path.join(paths[SRC], 'ressources'), 'cc_sketch.sat'), 
        scaleFromFile=OFF)
    elif test['corner_cleaner'] == 'corner':
        acis = mdb.openAcis(
        os.path.join(os.path.join(paths[SRC], 'ressources'), 'cc_sketch_corner_only.sat'), 
        scaleFromFile=OFF)
    else:
        raise KeyError

    mdb.models['Model-1'].ConstrainedSketchFromGeometryFile(name='cc_sketch', 
        geometryFile=acis)
        

    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
        sheetSize=814.58, gridSpacing=20.36)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=SUPERIMPOSE)
    p = mdb.models['Model-1'].parts['specimen']
    s.sketchOptions.setValues(gridOrigin=(144.0, 144.0))
    s.retrieveSketch(sketch=mdb.models['Model-1'].sketches['cc_sketch'])
    s.move(vector=(144.0,144.0), objectList = tuple((g[k] for k in g.keys())))

    p = mdb.models['Model-1'].parts['specimen']
    p.Cut(sketch=s)
    s.unsetPrimaryObject()
    del mdb.models['Model-1'].sketches['__profile__']