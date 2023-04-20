
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


# ------------------------------------------------------------------------------------------------------------------------------------------

"""This section is associated to the mesh controls"""


def Mesh_Element_Geometry(model, part, geometry, test):
    p = mdb.models[model].parts[part]
    p.setMeshControls(elemShape=geometry[0], regions=p.cells.getByBoundingBox(
        -TOL, -TOL, -TOL, SIDE_LENGTH + TOL, SIDE_LENGTH + TOL, test['thickness'] + TOL), technique=geometry[1])


def Mesh_Element_Order(model, part, order, test):
    p = mdb.models[model].parts[part]
    p.setElementType(elemTypes=(ElemType(elemCode=order[0], elemLibrary=STANDARD),
                                ElemType(
                                    elemCode=order[1], elemLibrary=STANDARD),
                                ElemType(elemCode=order[2], elemLibrary=STANDARD)),
                     regions=(p.cells.getByBoundingBox(-TOL, -TOL, -TOL, SIDE_LENGTH + TOL, SIDE_LENGTH + TOL, test['thickness'] + TOL), ))


def mesh_the_part(test):

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
    # Seeding for the whole piece (thickness in particular)
    mdb.models['Model-1'].parts['sample'].seedEdgeByNumber(
        constraint=FINER, edges=mdb.models['Model-1'].parts['sample'].edges.getByBoundingBox(-TOL, -TOL, -TOL, SIDE_LENGTH + TOL, SIDE_LENGTH + TOL, test['thickness'] + TOL), number=NE_THICKNESS)

    # Seeding of the front and back faces
    mdb.models['Model-1'].parts['sample'].seedEdgeBySize(constraint=FINER, deviationFactor=0.1,
                                                         edges=mdb.models['Model-1'].parts['sample'].edges.getByBoundingBox(-TOL, -TOL, -TOL, SIDE_LENGTH+TOL, SIDE_LENGTH+TOL, TOL) +
                                                         mdb.models['Model-1'].parts['sample'].edges.getByBoundingBox(-TOL, -TOL, test['thickness'] - TOL, SIDE_LENGTH+TOL, SIDE_LENGTH+TOL, test['thickness'] + TOL), size=test['mesh_size'])

    mdb.models['Model-1'].parts['sample'].generateMesh()
    mdb.models['Model-1'].rootAssembly.regenerate()


def mesh_the_part_2d(test):

    p = mdb.models['Model-1'].parts['sample']
    f = p.faces
    pickedRegions = f.getByBoundingBox(-TOL, -TOL,
                                       0.0, SIDE_LENGTH+TOL, SIDE_LENGTH+TOL, 0.0)
    p.setMeshControls(regions=pickedRegions, elemShape=TRI)
    elemType1 = mesh.ElemType(elemCode=CPS8R, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=CPS6M, elemLibrary=STANDARD,
                              secondOrderAccuracy=OFF, distortionControl=DEFAULT)
    p = mdb.models['Model-1'].parts['sample']
    f = p.faces
    faces = f.getByBoundingBox(-TOL, -TOL, 0.0,
                               SIDE_LENGTH+TOL, SIDE_LENGTH+TOL, 0.0)
    pickedRegions = (faces, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
    p = mdb.models['Model-1'].parts['sample']
    p.seedPart(size=test['mesh_size'], deviationFactor=0.1, minSizeFactor=0.1)
    p = mdb.models['Model-1'].parts['sample']
    p.generateMesh()
