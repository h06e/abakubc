from abaqus import *
from part import *
from material import *
from section import *
from assembly import *
from interaction import *
from mesh import *
from visualization import *
from connectorBehavior import *
from abaqusConstants import *
from math import *
import numpy as np
from caeModules import *
from random import gauss
import csv
from constants import *
from model_generation import make_mono_mesh, make_regular_mesh
from constants import *
from make_job import make_job

if __name__ == '__main__':
    connectorBehavior = None  # Just to fix errors in vsc
    regionToolset = None


def main_assemble_model(test, paths, step_list):
    if test['dim'] == 3:
        assemble_model(test, paths, step_list)
    else:
        assemble_model_2d(test, paths, step_list)


def Create_Step(model, step_name, previous_step, initial_inc, max_inc, min_inc, max_num_inc, NL_ON_OFF):
    mdb.models[model].StaticStep(name=step_name, previous=previous_step,
                                 initialInc=initial_inc, maxInc=max_inc, minInc=min_inc)
    mdb.models[model].steps[step_name].setValues(maxNumInc=max_num_inc)
    mdb.models[model].steps[step_name].setValues(nlgeom=NL_ON_OFF)


def create_element_set(model, part, z1, z2, num, set_name):
    p = mdb.models[model].parts[part]
    n = p.elements
    elements = n.getByBoundingBox(SIDE_LENGTH/2.0 - DIST_BETWEEN_CENTERS * (num+1) - TOL,
                                  SIDE_LENGTH/2.0 - DIST_BETWEEN_CENTERS *
                                  (num+1) - TOL,
                                  z1 - TOL,
                                  SIDE_LENGTH/2.0 + DIST_BETWEEN_CENTERS *
                                  (num+1) + TOL,
                                  SIDE_LENGTH/2.0 + DIST_BETWEEN_CENTERS *
                                  (num+1) + TOL,
                                  z2 + TOL)
    p.Set(elements=elements, name=set_name)


def create_node_set(model, part, z1, z2, num, set_name):
    p = mdb.models[model].parts[part]
    n = p.nodes
    nodes = n.getByBoundingBox(SIDE_LENGTH/2.0 - DIST_BETWEEN_CENTERS * (num+1) - TOL,
                               SIDE_LENGTH/2.0 - DIST_BETWEEN_CENTERS *
                               (num+1) - TOL,
                               z1 - TOL,
                               SIDE_LENGTH/2.0 + DIST_BETWEEN_CENTERS *
                               (num+1) + TOL,
                               SIDE_LENGTH/2.0 + DIST_BETWEEN_CENTERS *
                               (num+1) + TOL,
                               z2 + TOL)
    p.Set(nodes=nodes, name=set_name)


def create_field_output_elements(model, part, step, given_name, applied_set):
    regionDef = mdb.models[model].rootAssembly.allInstances[part].sets[applied_set]
    mdb.models[model].FieldOutputRequest(name=given_name, createStepName=step,
                                         variables=('S', 'E', 'EVOL', 'COORD'), region=regionDef, sectionPoints=DEFAULT,
                                         rebar=EXCLUDE)
    """
    mdb.models['Model-1'].FieldOutputRequest(name=given_name, 
        createStepName=step, variables=('S', 'U', 'EVOL', 'COORD'), 
        region=regionDef, sectionPoints=DEFAULT, position=NODES, rebar=EXCLUDE)
    """


def Create_Field_Output_nodes(model, part, step, given_name, applied_set):
    regionDef = mdb.models[model].rootAssembly.allInstances[part].sets[applied_set]
    mdb.models['Model-1'].FieldOutputRequest(name=given_name,
                                             createStepName=step, variables=(
                                                 'S', 'E', 'U', 'EVOL', 'COORD'),
                                             region=regionDef, sectionPoints=DEFAULT, position=NODES, rebar=EXCLUDE)


def create_connector_section(cs_name, stiffness, prop_connectors, test):
    model = mdb.models['Model-1']
    final_clearance = max(
        min(gauss(test['clearance'][0], test['clearance'][1]), test['clearance'][3]), test['clearance'][2])
    friction_coeff = test['friction'][0]
    final_intern_force = max(
        min(gauss(test['friction'][1], test['friction'][2]), test['friction'][4]), test['friction'][3])
    model.ConnectorSection(name=cs_name,
                           translationalType=RADIAL_THRUST, rotationalType=ROTATION)
    elastic_0 = connectorBehavior.ConnectorElasticity(components=(1, ),
                                                      behavior=NONLINEAR, table=((-10.0*stiffness, -10.0-final_clearance), (0.0, -final_clearance), (0.0, 0.0), (
                                                          0.0, final_clearance), (10.0*stiffness, 10.0+final_clearance)))
    friction_1 = connectorBehavior.ConnectorFriction(useContactForceComponent=ON,
                                                     contactForceStyle=DERIVED_COMPONENT, table=(
                                                         (final_intern_force, ), ),
                                                     frictionModel=USER_CUSTOMIZED, tangentDirection=6)
    model.sections[cs_name].setValues(behaviorOptions=(
        elastic_0, friction_1, ), extrapolation=LINEAR)
    model.sections[cs_name].behaviorOptions[0].ConnectorOptions()
    model.sections[cs_name].behaviorOptions[1].TangentialBehavior(
        table=((friction_coeff, ), ))
    cdct0 = connectorBehavior.CDCTerm(
        intrinsicComponents=(1, 2), table=((1.0, 1.0), ))
    model.sections[cs_name].behaviorOptions[1].DerivedComponent(
        cdcTerms=(cdct0, ))
    model.sections[cs_name].behaviorOptions[1].derivedComponent.cdcTerms[0].ConnectorOptions()
    model.sections[cs_name].behaviorOptions[1].ConnectorOptions()
    prop_connectors.append(
        [cs_name, stiffness, final_clearance, final_intern_force, friction_coeff])


def assemble_model(test, paths, step_list):
    model = mdb.models['Model-1']
    print("Assembly...")

    """
    The cylinders are sorted : by side : BOTTOM, RIGHT, TOP, LEFT
                            by number : 0 -> x or y minimal (it increases going to the right for top and botoom sides and to the top for left aand right sides)

    """
    a = model.rootAssembly
    try:
        a.features['specimen'].suppress()
    except:
        pass

    # Recover the skipped cylinders
    geometry_name = '_'.join([str(test[i]) for i in [
                             'sample_name', 'geo_parameters', 'trans_rot', 'thickness', 'corner_cleaner']])
    skip_cylinders = []
    with open(os.path.join(paths[SAMPLE_BANK_DIR], '{}_skip_cyl.csv'.format(geometry_name)), "r") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            skip_cylinders.append(map(int, row))

    mdb.openAcis(os.path.join(paths[SAMPLE_BANK_DIR], '{}.sat'.format(
        geometry_name)), scaleFromFile=OFF)

    model.PartFromGeometryFile(
        combine=False, dimensionality=THREE_D, geometryFile=mdb.acis,
        name='sample', type=DEFORMABLE_BODY)

    model.Material(name='material-1')
    model.materials['material-1'].Elastic(
        table=((test['mat'][0], test['mat'][1]), ))

    # Creates a section
    # name of the section to be assigned to a body set
    section_name = 'material-1' + '_Section'
    model.HomogeneousSolidSection(
        material='material-1', name=section_name, thickness=None)

    # name of the set that will be created when assigning the section
    body_set_name = 'Sample'
    p = model.parts['sample']
    p.Set(cells=p.cells.getByBoundingBox(-TOL, -TOL, -TOL,
                                         SIDE_LENGTH + TOL, SIDE_LENGTH + TOL, test['thickness']+TOL), name='Sample')

    model.parts['sample'].SectionAssignment(offset=0.0,
                                            offsetField='', offsetType=MIDDLE_SURFACE,
                                            region=model.parts['sample'].sets[body_set_name],
                                            sectionName=section_name, thicknessAssignment=FROM_SECTION)
    # ---------------------------------------------------------------------------------
    # Assembly
    a1 = model.rootAssembly
    p = model.parts['sample']
    a1.Instance(name='sample', part=p, dependent=ON)

    # Step
    step0_name = 'Initial'
    for idx, s in enumerate(step_list):
        Create_Step('Model-1', s.step_name, step0_name if idx == 0 else step_list[idx-1].step_name,
                    s.initial_inc, s.max_inc, s.min_inc, s.max_num_inc, s.NL if test['perfect_panto'] == False else OFF)

    # -------------------------------------------------------------------------------------------------
    # CONNECTOR SECTION

    prop_connectors = []

    datum1 = model.rootAssembly.DatumCsysByDefault(CARTESIAN)
    # ------------------------------------------------------------------------------------------------------------------------------------------
    """This section creates the attachment points necessary for the springs and couplings"""

    Coupling_Pts = []
    for cote in range(4):           # 0 bottom, 1 right, 2 top, 3 left
        # 0 lowest x or y coordinate (goes up for left and right and goes to the right for top and bottom sides)
        for cyl in range(10):
            if cyl not in skip_cylinders[cote]:
                # Make the two points
                coord = (((CYL_START_POS+(cyl*DIST_BETWEEN_CENTERS))if (cote in [0, 2])
                          else -CYLINDER_CENTER_DIST_EDGE+(2*CYLINDER_CENTER_DIST_EDGE+SIDE_LENGTH)*(cote == 1),
                          (CYL_START_POS+(cyl*DIST_BETWEEN_CENTERS)) if (cote in [1, 3])
                          else -CYLINDER_CENTER_DIST_EDGE+(2*CYLINDER_CENTER_DIST_EDGE+SIDE_LENGTH)*(cote == 2), test['thickness']/2.0),)
                Coupling_Pts.append(coord[0])
                point_name = ['B', 'R', 'T', 'L'][cote]+'_'+str(cyl)
                a = model.rootAssembly
                p = model.parts['sample']
                if not test['perfect_panto']:
                    a.AttachmentPoints(
                        name='coupling_'+point_name, points=coord, setName='Cou_'+point_name)
                    connectPt_coord = ((coord[0][0], coord[0][1], 0.0),)
                    a.AttachmentPoints(
                        name='PtBc_'+point_name, points=connectPt_coord, setName='PtBc_'+point_name)
                    # Make the wire
                    a.WirePolyLine(points=((a.vertices.findAt(coordinates=coord[0]),
                                            a.vertices.findAt(coordinates=connectPt_coord[0])), ), mergeType=IMPRINT,
                                   meshable=OFF)

                    # Create connector
                    create_connector_section(
                        'cs_'+point_name, test['stiff_panto'][0] if cote in [0, 2] else test['stiff_panto'][1], prop_connectors, test)
                    # Assign connector section to the wire
                    e1 = a.edges
                    edges1 = e1.findAt(
                        ((coord[0][0], coord[0][1], test['thickness']/3.0), ))
                    a.Set(edges=edges1, name='Wire_'+point_name)
                    region = a.sets['Wire_'+point_name]
                    datum1 = model.rootAssembly.datums[model.rootAssembly.datums.keys()[
                        0]]
                    csa = a.SectionAssignment(
                        sectionName='cs_'+point_name, region=region)

                    a.ConnectorOrientation(
                        region=csa.getSet(), localCsys1=datum1)
                    regionDef = model.rootAssembly.sets['Wire_'+point_name]
                    model.HistoryOutputRequest(name='wire_'+point_name,
                                               createStepName=step_list[0].step_name, variables=('CTF1', 'CTF2', 'CTF3', 'CTM1',
                                                                                                 'CTM2', 'CTM3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)

                    regionDef = model.rootAssembly.sets['PtBc_'+point_name]
                    model.HistoryOutputRequest(name='ptbc_'+point_name,
                                               createStepName=step_list[0].step_name, variables=('U1', 'U2', 'U3', 'UR1', 'UR2',
                                                                                                 'UR3', 'RF1', 'RF2', 'RF3', 'RM1', 'RM2', 'RM3'), region=regionDef,
                                               sectionPoints=DEFAULT, rebar=EXCLUDE)
                    regionDef = model.rootAssembly.sets['Cou_'+point_name]
                    model.HistoryOutputRequest(name='cou_'+point_name,
                                               createStepName=step_list[0].step_name, variables=('U1', 'U2', 'U3', 'UR1', 'UR2', 'UR3',
                                                                                                 'RF1', 'RF2', 'RF3', 'RM1', 'RM2',
                                                                                                 'RM3', 'CTF1', 'CTF2', 'CTF3', 'CTM1', 'CTM2', 'CTM3', 'CP1', 'CP2', 'CP3',
                                                                                                 'CPR1', 'CPR2', 'CPR3', 'CU1', 'CU2', 'CU3', 'CUR1', 'CUR2', 'CUR3'), region=regionDef,
                                               sectionPoints=DEFAULT, rebar=EXCLUDE)

                    region = a.sets['Cou_'+point_name]  # FOR THE COUPLING
                    # Coupling point
                    s1 = a.instances['sample'].faces
                    side1Faces1 = s1.findAt(
                        ((coord[0][0]-(cote == 1)*13+(cote == 3)*13, coord[0][1]+(cote == 0)*13-(cote == 2)*13, test['thickness']/2.0), ))
                    region2 = regionToolset.Region(side1Faces=side1Faces1)
                    model.Coupling(name='coupling_'+point_name, controlPoint=region,
                                   surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
                                   localCsys=None, u1=ON, u2=ON, u3=OFF if test['free_u3'] else ON, ur1=ON, ur2=ON, ur3=ON)
                    # Creating the BC of displacement

                    region = model.rootAssembly.sets['PtBc_'+point_name]
                    model.DisplacementBC(name='dep_'+point_name, createStepName='Initial',
                                         region=region, u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET,
                                         amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

                    for s in step_list:
                        x, y = coord[0][0], coord[0][1]
                        model.boundaryConditions['dep_'+point_name].setValuesInStep(
                            stepName=s.step_name,   u1=s.Deform_X/100.0*(x+CYLINDER_CENTER_DIST_EDGE) +
                            s.Deform_XY/100.0*(y+CYLINDER_CENTER_DIST_EDGE),
                            u2=s.Deform_Y/100.0*(y+CYLINDER_CENTER_DIST_EDGE))

                else:    # ADD_STIFFNESS_CLEARANCE_FRICTION False
                    p.AttachmentPoints(name='PtBc_'+point_name,
                                       points=coord, setName='PtBc_'+point_name)
                    # Creation of the histoiry output
                    regionDef = model.rootAssembly.allInstances['sample'].sets['PtBc_'+point_name]
                    model.HistoryOutputRequest(name='att_'+point_name,
                                               createStepName=step_list[0].step_name, variables=('U1', 'U2', 'U3', 'UR1', 'UR2',
                                                                                                 'UR3', 'RF1', 'RF2', 'RF3', 'RM1', 'RM2', 'RM3'), region=regionDef,
                                               sectionPoints=DEFAULT, rebar=EXCLUDE)
                    # FOR THE COUPLING
                    region = model.rootAssembly.allInstances['sample'].sets['PtBc_'+point_name]

                    # Coupling point
                    s1 = a.instances['sample'].faces
                    side1Faces1 = s1.findAt(
                        ((coord[0][0]-(cote == 1)*13+(cote == 3)*13, coord[0][1]+(cote == 0)*13-(cote == 2)*13, test['thickness']/2.0), ))
                    region2 = regionToolset.Region(side1Faces=side1Faces1)
                    model.Coupling(name='coupling_'+point_name, controlPoint=region,
                                   surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
                                   localCsys=None, u1=ON, u2=ON, u3=OFF if test['free_u3'] else ON, ur1=ON, ur2=ON, ur3=ON)
                    # Creating the BC of displacement

                    region = model.rootAssembly.allInstances['sample'].sets['PtBc_'+point_name]
                    model.DisplacementBC(name='dep_'+point_name, createStepName='Initial',
                                         region=region, u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET if test[
                                             'free_rotation'] else SET,
                                         amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                    for s in step_list:
                        x, y = coord[0][0], coord[0][1]
                        model.boundaryConditions['dep_'+point_name].setValuesInStep(
                            stepName=s.step_name,   u1=s.Deform_X/100.0*(x+CYLINDER_CENTER_DIST_EDGE) +
                            s.Deform_XY/100.0*(y+CYLINDER_CENTER_DIST_EDGE),
                            u2=s.Deform_Y/100.0*(y+CYLINDER_CENTER_DIST_EDGE))

    if not test['perfect_panto']:
        with open(test['test_id']+'_connector_prop.csv', "wb") as f:
            writer = csv.writer(f)
            writer.writerow(['cs_name', 'stiffness', 'clearance', 'friction'])
            writer.writerows(prop_connectors)

    # Create a set for symZ BC
    a = model.rootAssembly
    v1 = a.instances['sample'].vertices
    verts1 = v1.getByBoundingBox(-CYLINDER_CENTER_DIST_EDGE-TOL, -CYLINDER_CENTER_DIST_EDGE-TOL, test['thickness']/2.0-TOL,
                                 SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, test['thickness']/2.0+TOL)
    a.Set(vertices=verts1, name='mid_att')

    if not test['perfect_panto']:
        a = model.rootAssembly
        verts1 = a.vertices.getByBoundingBox(-CYLINDER_CENTER_DIST_EDGE-TOL, -CYLINDER_CENTER_DIST_EDGE-TOL, test['thickness']/2.0-TOL,
                                             SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, test['thickness']/2.0+TOL)
        a.Set(vertices=verts1, name='mid_att')

    # -------------------------------------------------------------
    # SymZ BC
    model.ZsymmBC(name='Sym_Z', createStepName='Initial',
                  region=a.sets['mid_att'], localCsys=None)

    # if ADD_STIFFNESS_CLEARANCE_FRICTION:
    #     verts1 = a.vertices.getByBoundingBox(-CYLINDER_CENTER_DIST_EDGE-TOL, -CYLINDER_CENTER_DIST_EDGE-TOL, -TOL,
    #             SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, +TOL)
    #     a.Set(vertices=verts1, name='connector_head')

    # -------------------------------------------------------------------------
    # MESH
    if test['sample_name'] != 'monolithic':
        make_regular_mesh.mesh_the_part(test)
    else:
        make_mono_mesh.mesh_the_part(test)

    a = model.rootAssembly
    for inst in a.instances.keys():
        if inst != 'sample':
            del a.features[inst]

    model.fieldOutputRequests['F-Output-1'].setValues(variables=('S',
                                                                 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP', 'EVOL'))

    N = 4
    for idx in range(N):
        avg_stress_set_name = 'Avg_Stress_Node_Set_' + str(idx+1)
        create_node_set('Model-1', 'sample', 0.0,
                        test['thickness'], idx, avg_stress_set_name)
        set_name = 'Avg_S_E_nodes' + str(idx+1)
        Create_Field_Output_nodes('Model-1', 'sample',
                                  step_list[0].step_name,
                                  set_name, avg_stress_set_name)
    N = 4
    for idx in range(N):
        avg_stress_set_name = 'Avg_Stress_Element_Set_' + str(idx+1)
        create_element_set('Model-1', 'sample', 0.0,
                           test['thickness'], idx, avg_stress_set_name)
        set_name = 'Avg_S_E_nodes' + str(idx+1)
        create_field_output_elements('Model-1', 'sample',
                                     step_list[0].step_name,
                                     set_name, avg_stress_set_name)

    model.rootAssembly.regenerate()

    mdb.Job(name=test['test_id'], model='Model-1', description='', type=ANALYSIS,
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
            memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
            modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
            scratch=os.getcwd(), resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1,
            numGPUs=0)


def Create_Step_2d(model, step_name, previous_step, initial_inc, max_inc, min_inc, max_num_inc, NL_ON_OFF):
    mdb.models[model].StaticStep(name=step_name, previous=previous_step,
                                 initialInc=initial_inc, maxInc=max_inc, minInc=min_inc)
    mdb.models[model].steps[step_name].setValues(maxNumInc=max_num_inc)
    mdb.models[model].steps[step_name].setValues(nlgeom=NL_ON_OFF)


def create_element_set_2d(model, part, z1, z2, num, set_name):
    p = mdb.models[model].parts[part]
    n = p.elements
    elements = n.getByBoundingBox(SIDE_LENGTH/2.0 - DIST_BETWEEN_CENTERS * (num+1) - TOL,
                                  SIDE_LENGTH/2.0 - DIST_BETWEEN_CENTERS *
                                  (num+1) - TOL,
                                  -0.1,
                                  SIDE_LENGTH/2.0 + DIST_BETWEEN_CENTERS *
                                  (num+1) + TOL,
                                  SIDE_LENGTH/2.0 + DIST_BETWEEN_CENTERS *
                                  (num+1) + TOL, 0.1
                                  )
    p.Set(elements=elements, name=set_name)


def create_node_set_2d(model, part, z1, z2, num, set_name):
    p = mdb.models[model].parts[part]
    n = p.nodes
    nodes = n.getByBoundingBox(SIDE_LENGTH/2.0 - DIST_BETWEEN_CENTERS * (num+1) - TOL,
                               SIDE_LENGTH/2.0 - DIST_BETWEEN_CENTERS *
                               (num+1) - TOL,
                               -0.1,
                               SIDE_LENGTH/2.0 +
                               DIST_BETWEEN_CENTERS * (num+1) + TOL,
                               SIDE_LENGTH/2.0 + DIST_BETWEEN_CENTERS *
                               (num+1) + TOL,
                               0.1
                               )
    p.Set(nodes=nodes, name=set_name)


def create_field_output_elements_2d(model, part, step, given_name, applied_set):
    regionDef = mdb.models[model].rootAssembly.allInstances[part].sets[applied_set]
    mdb.models[model].FieldOutputRequest(name=given_name, createStepName=step,
                                         variables=('S', 'E', 'EVOL', 'COORD'), region=regionDef, sectionPoints=DEFAULT,
                                         rebar=EXCLUDE)
    """
    mdb.models['Model-1'].FieldOutputRequest(name=given_name, 
        createStepName=step, variables=('S', 'U', 'EVOL', 'COORD'), 
        region=regionDef, sectionPoints=DEFAULT, position=NODES, rebar=EXCLUDE)
    """


def Create_Field_Output_nodes_2d(model, part, step, given_name, applied_set):
    regionDef = mdb.models[model].rootAssembly.allInstances[part].sets[applied_set]
    mdb.models['Model-1'].FieldOutputRequest(name=given_name,
                                             createStepName=step, variables=(
                                                 'S', 'E', 'U', 'EVOL', 'COORD'),
                                             region=regionDef, sectionPoints=DEFAULT, position=NODES, rebar=EXCLUDE)


def create_connector_section_2d(cs_name, stiffness, prop_connectors, test):
    model = mdb.models['Model-1']
    final_clearance = max(
        min(gauss(test['clearance'][0], test['clearance'][1]), test['clearance'][3]), test['clearance'][2])
    friction_coeff = test['friction'][0]
    final_intern_force = max(
        min(gauss(test['friction'][1], test['friction'][2]), test['friction'][4]), test['friction'][3])
    model.ConnectorSection(name=cs_name,
                           translationalType=AXIAL, rotationalType=ROTATION)
    elastic_0 = connectorBehavior.ConnectorElasticity(components=(1, ),
                                                      behavior=NONLINEAR, table=((-10.0*stiffness, -10.0-final_clearance), (0.0, -final_clearance), (0.0, 0.0), (
                                                          0.0, final_clearance), (10.0*stiffness, 10.0+final_clearance)))
    friction_1 = connectorBehavior.ConnectorFriction(useContactForceComponent=ON,
                                                     contactForceStyle=DERIVED_COMPONENT, table=(
                                                         (final_intern_force, ), ),
                                                     frictionModel=USER_CUSTOMIZED, tangentDirection=6)
    model.sections[cs_name].setValues(behaviorOptions=(
        elastic_0, friction_1, ), extrapolation=LINEAR)
    model.sections[cs_name].behaviorOptions[0].ConnectorOptions()
    model.sections[cs_name].behaviorOptions[1].TangentialBehavior(
        table=((friction_coeff, ), ))
    cdct0 = connectorBehavior.CDCTerm(
        intrinsicComponents=(1, 2), table=((1.0, 1.0), ))
    model.sections[cs_name].behaviorOptions[1].DerivedComponent(
        cdcTerms=(cdct0, ))
    model.sections[cs_name].behaviorOptions[1].derivedComponent.cdcTerms[0].ConnectorOptions()
    model.sections[cs_name].behaviorOptions[1].ConnectorOptions()
    prop_connectors.append(
        [cs_name, stiffness, final_clearance, final_intern_force, friction_coeff])


def assemble_model_2d(test, paths, step_list):
    model = mdb.models['Model-1']
    print("Assembly...")

    """
    The cylinders or sort : by side : BOTTOM, RIGHT, TOP, LEFT
                            by number : 0 -> x or y minimal (it increases going to the right for top and botoom sides and to the top for left aand right sides)

    """
    if test['sample_name'] in ['snubsquare', 'snubsquare2']:
        mdb.models['Model-1'].parts.changeKey(fromName='specimen', toName='sample')
        mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='specimen-1', 
            toName='sample')

        skip_cylinders = [[],[],[],[]]
    else:
        a = model.rootAssembly
        try:
            a.features['specimen'].suppress()
        except:
            pass

        # Recover the skipped cylinders
        geometry_name = '2d'+'_'.join([str(test[i]) for i in ['sample_name',
                                                            'geo_parameters', 'trans_rot', 'thickness', 'corner_cleaner']])
        skip_cylinders = []
        with open(os.path.join(paths[SAMPLE_BANK_DIR], '{}_skip_cyl.csv'.format(geometry_name)), "r") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                skip_cylinders.append(map(int, row))

        mdb.openAcis(os.path.join(paths[SAMPLE_BANK_DIR], '{}.sat'.format(
            geometry_name)), scaleFromFile=OFF)

        model.PartFromGeometryFile(
            combine=False, dimensionality=TWO_D_PLANAR, geometryFile=mdb.acis,
            name='sample', type=DEFORMABLE_BODY)

        model.Material(name='material-1')
        model.materials['material-1'].Elastic(
            table=((test['mat'][0], test['mat'][1]), ))

        # Creates a section
        # name of the section to be assigned to a body set
        section_name = 'material-1' + '_Section'
        model.HomogeneousSolidSection(
            material='material-1', name=section_name, thickness=test['thickness'])

        # name of the set that will be created when assigning the section
        p = mdb.models['Model-1'].parts['sample']
        f = p.faces
        faces = f.getByBoundingBox(-TOL, -TOL, 0.0,
                                SIDE_LENGTH+TOL, SIDE_LENGTH+TOL, 0.0)
        region = p.Set(faces=faces, name='sample')
        p = mdb.models['Model-1'].parts['sample']
        p.SectionAssignment(region=region, sectionName='material-1_Section',
                            offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',
                            thicknessAssignment=FROM_SECTION)

        # ---------------------------------------------------------------------------------
        # Assembly
        a1 = model.rootAssembly
        p = model.parts['sample']
        a1.Instance(name='sample', part=p, dependent=ON)

    # Step
    step0_name = 'Initial'
    for idx, s in enumerate(step_list):
        Create_Step_2d('Model-1', s.step_name, step0_name if idx == 0 else step_list[idx-1].step_name,
                       s.initial_inc, s.max_inc, s.min_inc, s.max_num_inc, s.NL if test['perfect_panto'] == False else OFF)

    # -------------------------------------------------------------------------------------------------
    # CONNECTOR SECTION

    prop_connectors = []

    datum1 = model.rootAssembly.DatumCsysByDefault(CARTESIAN)
    # ------------------------------------------------------------------------------------------------------------------------------------------
    """This section creates the attachment points necessary for the springs and couplings"""

    Coupling_Pts = []
    for cote in range(4):           # 0 bottom, 1 right, 2 top, 3 left
        # 0 lowest x or y coordinate (goes up for left and right and goes to the right for top and bottom sides)
        for cyl in range(10):
            if cyl not in skip_cylinders[cote]:
                # Make the two points
                coord = (((CYL_START_POS+(cyl*DIST_BETWEEN_CENTERS))if (cote in [0, 2])
                          else -CYLINDER_CENTER_DIST_EDGE+(2*CYLINDER_CENTER_DIST_EDGE+SIDE_LENGTH)*(cote == 1),
                          (CYL_START_POS+(cyl*DIST_BETWEEN_CENTERS)) if (cote in [1, 3])
                          else -CYLINDER_CENTER_DIST_EDGE+(2*CYLINDER_CENTER_DIST_EDGE+SIDE_LENGTH)*(cote == 2), 0.0),)
                Coupling_Pts.append(coord[0])
                point_name = ['B', 'R', 'T', 'L'][cote]+'_'+str(cyl)
                a = model.rootAssembly
                p = model.parts['sample']
                if not test['perfect_panto']:
                    delta = 1e-3
                    a.AttachmentPoints(
                        name='coupling_'+point_name, points=coord, setName='Cou_'+point_name)
                    connectPt_coord = ((coord[0][0]+delta, coord[0][1], 0.0),)
                    a.AttachmentPoints(
                        name='PtBc_'+point_name, points=connectPt_coord, setName='PtBc_'+point_name)
                    # Make the wire
                    a.WirePolyLine(points=((a.vertices.findAt(coordinates=coord[0]),
                                            a.vertices.findAt(coordinates=connectPt_coord[0])), ), mergeType=IMPRINT,
                                   meshable=OFF)

                    # Create connector
                    create_connector_section_2d(
                        'cs_'+point_name, test['stiff_panto'][0] if cote in [0, 2] else test['stiff_panto'][1], prop_connectors, test)
                    # Assign connector section to the wire
                    e1 = a.edges
                    edges1 = e1.findAt(
                        ((coord[0][0]+delta/2.0, coord[0][1], 0.0), ))
                    a.Set(edges=edges1, name='Wire_'+point_name)
                    region = a.sets['Wire_'+point_name]

                    a.SectionAssignment(
                        sectionName='cs_'+point_name, region=region)

                    regionDef = model.rootAssembly.sets['Wire_'+point_name]
                    model.HistoryOutputRequest(name='wire_'+point_name,
                                               createStepName=step_list[0].step_name, variables=('CTF1', 'CTF2', 'CTF3', 'CTM1', 'CTM2', 'CTM3', 'CU1', 'CU2', 'CU3', 'CUR1', 'CUR2', 'CUR3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
                    regionDef = model.rootAssembly.sets['PtBc_'+point_name]
                    model.HistoryOutputRequest(name='ptbc_'+point_name,
                                               createStepName=step_list[0].step_name, variables=('U1', 'U2', 'U3', 'UR1', 'UR2',
                                                                                                 'UR3', 'RF1', 'RF2', 'RF3', 'RM1', 'RM2', 'RM3'), region=regionDef,
                                               sectionPoints=DEFAULT, rebar=EXCLUDE)
                    regionDef = model.rootAssembly.sets['Cou_'+point_name]
                    model.HistoryOutputRequest(name='cou_'+point_name,
                                               createStepName=step_list[0].step_name, variables=('U1', 'U2', 'U3', 'UR1', 'UR2', 'UR3',
                                                                                                 'RF1', 'RF2', 'RF3', 'RM1', 'RM2',
                                                                                                 'RM3'), region=regionDef,
                                               sectionPoints=DEFAULT, rebar=EXCLUDE)

                    a = mdb.models['Model-1'].rootAssembly
                    e1 = a.instances['sample'].edges
                    coord0 = (coord[0][0], coord[0][1], -1)
                    coord1 = (coord[0][0], coord[0][1], 1)
                    edges1 = e1.getByBoundingCylinder(
                        center1=coord0, center2=coord1, radius=13.1)
                    full_box = edges1.getBoundingBox()

                    edges1 = edges1.getByBoundingBox(full_box['low'][0] if cote != 3 else -0.1, full_box['low'][1] if cote != 0 else -0.1, full_box['low'][2],
                                                     full_box['high'][0]if cote != 1 else SIDE_LENGTH+0.1, full_box['high'][1] if cote != 2 else SIDE_LENGTH+0.1, full_box['high'][2])
                    a.Set(edges=edges1, name='coupling_edges_'+point_name)
                    region1 = model.rootAssembly.sets['Cou_'+point_name]
                    region2 = model.rootAssembly.sets['coupling_edges_'+point_name]
                    # mdb.saveAs(pathName='mdb')
                    # exit()
                    mdb.models['Model-1'].Coupling(name='coupling_'+point_name, controlPoint=region1,
                                                   surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
                                                   localCsys=None, u1=ON, u2=ON, ur3=ON)
                    # Creating the BC of displacement

                    region = model.rootAssembly.sets['PtBc_'+point_name]
                    model.DisplacementBC(name='dep_'+point_name, createStepName='Initial',
                                         region=region, u1=SET, u2=SET, ur3=SET,
                                         amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                    for s in step_list:
                        x, y = coord[0][0], coord[0][1]
                        model.boundaryConditions['dep_'+point_name].setValuesInStep(
                            stepName=s.step_name,   u1=s.Deform_X/100.0*(x+CYLINDER_CENTER_DIST_EDGE) +
                            s.Deform_XY/100.0*(y+CYLINDER_CENTER_DIST_EDGE),
                            u2=s.Deform_Y/100.0*(y+CYLINDER_CENTER_DIST_EDGE))

                else:    # ADD_STIFFNESS_CLEARANCE_FRICTION False
                    p.AttachmentPoints(name='PtBc_'+point_name,
                                       points=coord, setName='PtBc_'+point_name)
                    # Creation of the histoiry output
                    regionDef = model.rootAssembly.allInstances['sample'].sets['PtBc_'+point_name]
                    model.HistoryOutputRequest(name='att_'+point_name,
                                               createStepName=step_list[0].step_name, variables=('U1', 'U2', 'U3', 'UR1', 'UR2',
                                                                                                 'UR3', 'RF1', 'RF2', 'RF3', 'RM1', 'RM2', 'RM3'), region=regionDef,
                                               sectionPoints=DEFAULT, rebar=EXCLUDE)
                    # FOR THE COUPLING
                    region = model.rootAssembly.allInstances['sample'].sets['PtBc_'+point_name]

                    # Coupling point
                    a = mdb.models['Model-1'].rootAssembly
                    e1 = a.instances['sample'].edges
                    coord0 = (coord[0][0], coord[0][1], -1)
                    coord1 = (coord[0][0], coord[0][1], 1)
                    edges1 = e1.getByBoundingCylinder(
                        center1=coord0, center2=coord1, radius=13.1)
                    full_box = edges1.getBoundingBox()

                    edges1 = edges1.getByBoundingBox(full_box['low'][0] if cote != 3 else -0.1, full_box['low'][1] if cote != 0 else -0.1, full_box['low'][2],
                                                     full_box['high'][0]if cote != 1 else SIDE_LENGTH+0.1, full_box['high'][1] if cote != 2 else SIDE_LENGTH+0.1, full_box['high'][2])
                    a.Set(edges=edges1, name='coupling_edges_'+point_name)
                    a = mdb.models['Model-1'].rootAssembly
                    region1 = a.instances['sample'].sets['PtBc_'+point_name]
                    a = mdb.models['Model-1'].rootAssembly
                    region2 = a.sets['coupling_edges_'+point_name]
                    mdb.models['Model-1'].Coupling(name='coupling_'+point_name, controlPoint=region1,
                                                   surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC,
                                                   localCsys=None, u1=ON, u2=ON, ur3=ON)
                    # Creating the BC of displacement

                    region = model.rootAssembly.allInstances['sample'].sets['PtBc_'+point_name]
                    model.DisplacementBC(name='dep_'+point_name, createStepName='Initial',
                                         region=region, u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET if test[
                                             'free_rotation'] else SET,
                                         amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                    for s in step_list:
                        x, y = coord[0][0], coord[0][1]
                        model.boundaryConditions['dep_'+point_name].setValuesInStep(
                            stepName=s.step_name,   u1=s.Deform_X/100.0*(x+CYLINDER_CENTER_DIST_EDGE) +
                            s.Deform_XY/100.0*(y+CYLINDER_CENTER_DIST_EDGE),
                            u2=s.Deform_Y/100.0*(y+CYLINDER_CENTER_DIST_EDGE))

    if not test['perfect_panto']:
        with open(test['test_id']+'_connector_prop.csv', "wb") as f:
            writer = csv.writer(f)
            writer.writerow(['cs_name', 'stiffness', 'clearance', 'friction'])
            writer.writerows(prop_connectors)

    # Create a set for symZ BC
    a = model.rootAssembly
    v1 = a.instances['sample'].vertices
    verts1 = v1.getByBoundingBox(-CYLINDER_CENTER_DIST_EDGE-TOL, -CYLINDER_CENTER_DIST_EDGE-TOL,
                                 SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL)
    a.Set(vertices=verts1, name='mid_att')

    if not test['perfect_panto']:
        a = model.rootAssembly
        verts1 = a.vertices.getByBoundingBox(-CYLINDER_CENTER_DIST_EDGE-TOL, -CYLINDER_CENTER_DIST_EDGE-TOL,
                                             SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, test['thickness']/2.0+TOL)
        a.Set(vertices=verts1, name='mid_att')

    # if ADD_STIFFNESS_CLEARANCE_FRICTION:
    #     verts1 = a.vertices.getByBoundingBox(-CYLINDER_CENTER_DIST_EDGE-TOL, -CYLINDER_CENTER_DIST_EDGE-TOL, -TOL,
    #             SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, SIDE_LENGTH+CYLINDER_CENTER_DIST_EDGE+TOL, +TOL)
    #     a.Set(vertices=verts1, name='connector_head')

    # -------------------------------------------------------------------------
    # MESH
    if test['sample_name'] != 'monolithic':
        make_regular_mesh.mesh_the_part_2d(test)
    else:
        make_mono_mesh.mesh_the_part_2d(test)

    a = model.rootAssembly
    for inst in a.instances.keys():
        if inst != 'sample':
            del a.features[inst]

    model.fieldOutputRequests['F-Output-1'].setValues(variables=('S',
                                                                 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP', 'EVOL'))

    N = 4
    for idx in range(N):
        avg_stress_set_name = 'Avg_Stress_Node_Set_' + str(idx+1)
        create_node_set_2d('Model-1', 'sample', 0.0,
                           test['thickness'], idx, avg_stress_set_name)
        set_name = 'Avg_S_E_nodes' + str(idx+1)
        Create_Field_Output_nodes_2d('Model-1', 'sample',
                                     step_list[0].step_name,
                                     set_name, avg_stress_set_name)
    N = 4
    for idx in range(N):
        avg_stress_set_name = 'Avg_Stress_Element_Set_' + str(idx+1)
        create_element_set_2d('Model-1', 'sample', 0.0,
                              test['thickness'], idx, avg_stress_set_name)
        set_name = 'Avg_S_E_nodes' + str(idx+1)
        create_field_output_elements_2d('Model-1', 'sample',
                                        step_list[0].step_name,
                                        set_name, avg_stress_set_name)

    model.rootAssembly.regenerate()

    make_job(mdb, test['test_id'], test, os.getcwd())

    mdb.saveAs(pathName='{}.mdb'.format(test["test_id"]))
    # exit()
