
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


def Mesh_Element_Geometry(model, part, geometry, test):
    p = mdb.models[model].parts[part]
    p.setMeshControls(elemShape=geometry[0], regions=
    p.cells.getByBoundingBox(-TOL, -TOL , -TOL, SIDE_LENGTH + TOL, SIDE_LENGTH + TOL, test['thickness'] + TOL), technique=geometry[1])

def Mesh_Element_Order(model, part, order, test):
    p = mdb.models[model].parts[part]
    p.setElementType(elemTypes=(ElemType(elemCode=order[0], elemLibrary=STANDARD), 
                                ElemType(elemCode=order[1], elemLibrary=STANDARD), 
                                ElemType(elemCode=order[2], elemLibrary=STANDARD)), 
    regions=(p.cells.getByBoundingBox(-TOL, -TOL , -TOL, SIDE_LENGTH + TOL, SIDE_LENGTH + TOL, test['thickness'] + TOL), ))


def mesh_the_part (test):
    #--------------------------------------------
    """Partitioning"""
    model=mdb.models['Model-1']
    p = model.parts['sample']
    p.DatumAxisByPrincipalAxis(principalAxis=ZAXIS)

    p = model.parts['sample']
    f1, e1, d2 = p.faces, p.edges, p.datums
    t = p.MakeSketchTransform(sketchPlane=f1.findAt(coordinates=(144.0, 
        144.0, 0.0)), sketchUpEdge=e1.findAt(coordinates=(288.0, 118.846688, 
        0.0)), sketchPlaneSide=SIDE1, origin=(144.0, 144.0, 0.0))
    s1 = model.ConstrainedSketch(name='__profile__', 
        sheetSize=814.58, gridSpacing=20.36, transform=t)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=SUPERIMPOSE)
    p = model.parts['sample']
    p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
    s1.rectangle(point1=(-144*SIZE_OF_PARTITION/100, -144*SIZE_OF_PARTITION/100), 
                point2=(144*SIZE_OF_PARTITION/100, 144*SIZE_OF_PARTITION/100))
    p = model.parts['sample']
    f = p.faces
    pickedFaces = f.findAt(((144.0, 144.0, 0.0), ))
    e, d1 = p.edges, p.datums
    p.PartitionFaceBySketch(sketchUpEdge=e.findAt(coordinates=(288.0, 118.846688, 
        0.0)), faces=pickedFaces, sketch=s1)
    s1.unsetPrimaryObject()
    del model.sketches['__profile__']
    p = model.parts['sample']
    c = p.cells
    pickedCells = c.findAt(((144.0, 144.0, 0.0), ))
    e, d1 = p.edges, p.datums
    pickedEdges = e.findAt(((144-144*SIZE_OF_PARTITION/100, 144.0, 0.0), ), ((144.0, 144.0-144*SIZE_OF_PARTITION/100, 0.0), ), 
                        ((144+144*SIZE_OF_PARTITION/100, 144, 0.0), ), ((144, 144+144*SIZE_OF_PARTITION/100, 0.0), ))
    p.PartitionCellByExtrudeEdge(line=p.datums[p.datums.keys()[0]], cells=pickedCells, edges=pickedEdges, 
        sense=FORWARD)

    #------------------------------------------------------------------------------------------------------------------------------------------

    """This section is associated to the mesh controls"""

    tetra = [TET, FREE]
    wedge = [WEDGE, SWEEP]
    quadratic = [C3D20R, C3D15, C3D10]
    linear = [C3D8R, C3D6, C3D4]


    if ELEMENT_TYPE == 'tetra':
        Mesh_Element_Geometry('Model-1', 'sample', tetra, test)
    elif ELEMENT_TYPE == 'wedge':
        Mesh_Element_Geometry('Model-1', 'sample', wedge, test)

    if ELEMENT_ORDER == 'quad':
        Mesh_Element_Order('Model-1', 'sample', quadratic, test)
    elif ELEMENT_ORDER == 'lin':
        Mesh_Element_Order('Model-1', 'sample', linear, test)
    
    """Seeding of edges in the model"""
    #Seeding for the whole piece (thickness in particular)
    model.parts['sample'].seedEdgeByNumber(
        constraint=FINER, edges=
        model.parts['sample'].edges.getByBoundingBox(-TOL, -TOL, -TOL, SIDE_LENGTH + TOL, SIDE_LENGTH + TOL, test['thickness'] + TOL), number = NE_THICKNESS)

    #Seeding of the front and back faces     
    model.parts['sample'].seedEdgeBySize(constraint=FINER, deviationFactor=0.1, 
        edges = model.parts['sample'].edges.getByBoundingBox(-TOL, -TOL, -TOL, SIDE_LENGTH+TOL, SIDE_LENGTH+TOL, TOL) + 
        model.parts['sample'].edges.getByBoundingBox(-TOL, -TOL, test['thickness'] - TOL, SIDE_LENGTH+TOL, SIDE_LENGTH+TOL, test['thickness'] + TOL), size=test['mesh_size'][0])

    model.parts['sample'].seedEdgeBySize(constraint=FINER, deviationFactor=0.1, 
        edges = model.parts['sample'].edges.getByBoundingBox(144-144*SIZE_OF_PARTITION/100-TOL, 144-144*SIZE_OF_PARTITION/100-TOL, -TOL, 
                                                                            144+144*SIZE_OF_PARTITION/100+TOL, 144+144*SIZE_OF_PARTITION/100+TOL, +TOL)
            + model.parts['sample'].edges.getByBoundingBox(144-144*SIZE_OF_PARTITION/100-TOL, 144-144*SIZE_OF_PARTITION/100-TOL, test['thickness']-TOL, 
                                                                            144+144*SIZE_OF_PARTITION/100+TOL, 144+144*SIZE_OF_PARTITION/100+TOL, test['thickness']+TOL)
                                                                            , size=test['mesh_size'][1])


    model.parts['sample'].generateMesh()
    model.rootAssembly.regenerate()

    

def mesh_the_part_2d (test):
    #--------------------------------------------
    """Partitioning"""
    model=mdb.models['Model-1']
    p = model.parts['sample']
    p.DatumAxisByPrincipalAxis(principalAxis=ZAXIS)

    p = model.parts['sample']
    f1, e1, d2 = p.faces, p.edges, p.datums
    t = p.MakeSketchTransform(sketchPlane=f1.findAt(coordinates=(144.0, 
        144.0, 0.0)), sketchUpEdge=e1.findAt(coordinates=(288.0, 118.846688, 
        0.0)), sketchPlaneSide=SIDE1, origin=(144.0, 144.0, 0.0))
    s1 = model.ConstrainedSketch(name='__profile__', 
        sheetSize=814.58, gridSpacing=20.36, transform=t)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=SUPERIMPOSE)
    p = model.parts['sample']
    p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
    s1.rectangle(point1=(-144*SIZE_OF_PARTITION/100, -144*SIZE_OF_PARTITION/100), 
                point2=(144*SIZE_OF_PARTITION/100, 144*SIZE_OF_PARTITION/100))
    p = model.parts['sample']
    f = p.faces
    pickedFaces = f.findAt(((144.0, 144.0, 0.0), ))
    e, d1 = p.edges, p.datums
    p.PartitionFaceBySketch(sketchUpEdge=e.findAt(coordinates=(288.0, 118.846688, 
        0.0)), faces=pickedFaces, sketch=s1)
    s1.unsetPrimaryObject()
    del model.sketches['__profile__']
    p = model.parts['sample']
    c = p.cells
    pickedCells = c.findAt(((144.0, 144.0, 0.0), ))
    e, d1 = p.edges, p.datums
    pickedEdges = e.findAt(((144-144*SIZE_OF_PARTITION/100, 144.0, 0.0), ), ((144.0, 144.0-144*SIZE_OF_PARTITION/100, 0.0), ), 
                        ((144+144*SIZE_OF_PARTITION/100, 144, 0.0), ), ((144, 144+144*SIZE_OF_PARTITION/100, 0.0), ))
    # mdb.saveAs(pathName='mdb')
    # exit()

    p = mdb.models['Model-1'].parts['sample']
    f = p.faces
    pickedRegions = f.getByBoundingBox(-TOL,-TOL,0.0,SIDE_LENGTH+TOL,SIDE_LENGTH+TOL,0.0)
    p.setMeshControls(regions=pickedRegions, elemShape=TRI)
    elemType1 = mesh.ElemType(elemCode=CPS8R, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=CPS6M, elemLibrary=STANDARD, 
        secondOrderAccuracy=OFF, distortionControl=DEFAULT)
    p = mdb.models['Model-1'].parts['sample']
    f = p.faces
    faces = f.getByBoundingBox(-TOL,-TOL,0.0,SIDE_LENGTH+TOL,SIDE_LENGTH+TOL,0.0)
    pickedRegions =(faces, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))

    #Seeding of the front and back faces     
    model.parts['sample'].seedEdgeBySize(constraint=FINER, deviationFactor=0.1, 
        edges = model.parts['sample'].edges.getByBoundingBox(-TOL, -TOL, -TOL, SIDE_LENGTH+TOL, SIDE_LENGTH+TOL, TOL) + 
        model.parts['sample'].edges.getByBoundingBox(-TOL, -TOL, test['thickness'] - TOL, SIDE_LENGTH+TOL, SIDE_LENGTH+TOL, test['thickness'] + TOL), size=test['mesh_size'][0])

    model.parts['sample'].seedEdgeBySize(constraint=FINER, deviationFactor=0.1, 
        edges = model.parts['sample'].edges.getByBoundingBox(144-144*SIZE_OF_PARTITION/100-TOL, 144-144*SIZE_OF_PARTITION/100-TOL, -TOL, 
                                                                            144+144*SIZE_OF_PARTITION/100+TOL, 144+144*SIZE_OF_PARTITION/100+TOL, +TOL)
            + model.parts['sample'].edges.getByBoundingBox(144-144*SIZE_OF_PARTITION/100-TOL, 144-144*SIZE_OF_PARTITION/100-TOL, test['thickness']-TOL, 
                                                                            144+144*SIZE_OF_PARTITION/100+TOL, 144+144*SIZE_OF_PARTITION/100+TOL, test['thickness']+TOL)
                                                                            , size=test['mesh_size'][1])


    model.parts['sample'].generateMesh()
    model.rootAssembly.regenerate()