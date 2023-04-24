try:
    from abaqus import *
    from abaqusConstants import *
    from caeModules import *
except:
    pass
"""Keys for dicts"""
ROOT='root'
SRC='src'
CAMPAGNE_DIR='campagne_dir'
RES_DIR='res_dir'
ODB_STOCK_DIR='odb_stock_dir'
THEORY_DIR='theory_dir'
SAMPLE_BANK_DIR='sample_bank_dir'
POROSITY='porosity'

"""Machine Inputs"""
NUMBER_OF_CYLINDER_PER_SIDE = 10    #[integer]
CYLINDER_RADIUS = 13.0              #[mm]
DIST_BETWEEN_CENTERS = 28.0         #[mm]
CYLINDER_CENTER_DIST_EDGE = 10.0    #[mm] Distance from the edge of the sample if it was a square
CYL_START_POS = 18.0 # X-Y position of the first reference point on the horizontal edges

"""Mesh control"""
ELEMENT_TYPE = 'wedge'              #Type tetra for tetrahedrons, type wedge for wedges
ELEMENT_ORDER = 'quad'              #Type lin for linear, type quad for quadratic
NE_THICKNESS = 6                    #Number of elements in the thickness :int
MAX_ELEMENT_DIFFERENCE = 10         #Maximum difference size allowed between the smallest and biggest element.
# for monolithic:
ELEMENT_SIZE_CENTER_MONO=7.0       # Number of element in the central part FOR MONOLITHIC ONLY
SIZE_OF_PARTITION = 70.0            # in %

""" STEP PARAMETERS"""
s1_initial_inc = 1.0        #Size of the initrial increment. (Better to keep low to allow smooth transition between intermediate steps)
s1_max_inc = 1.0            #Maximum allowable increment size during the simulation (between 0 and 1 )
s1_min_inc = 1.0E-5         #Minimum allowable increment size (smaller numbers can help convergence but also hinder performance)
s1_max_num_inc = 10000      #Maximum number of increments allowed in the step.
s1_NL = ON                 #Nlgeom MANDATORY for stiffness, clearance in the pantographs
para_default=[s1_initial_inc,s1_max_inc,s1_min_inc,s1_max_num_inc,s1_NL]

"""Other"""
SIDE_LENGTH = 18.0*2 + (NUMBER_OF_CYLINDER_PER_SIDE-1)*DIST_BETWEEN_CENTERS #[mm]
TOL = 0.001 #A tolerance used for the bounding boxes to ensure enclosure of the elements.

class StepScript:
    def __init__(self,step_name,res_parameters,loading):
        self.step_name=step_name
        self.initial_inc = res_parameters[0]
        self.max_inc = res_parameters[1]
        self.min_inc = res_parameters[2]
        self.max_num_inc = res_parameters[3]
        self.NL = res_parameters[4]

        self.Deform_X=loading[0]
        self.Deform_Y=loading[1]
        self.Deform_XY=loading[2]

def log(message):
    print >> sys.__stdout__, message

""" List of geo which need PBC and or KUBC additionnal computation"""
model_with_KUBC_th=['honey', 'rectangle', 'losange']
model_with_PBC_th=['honey', 'rectangle', 'losange']