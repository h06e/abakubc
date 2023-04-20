import matplotlib.pyplot as plt
import numpy as np
import csv
import os

###############################################################
FILE_NAME='monolithic_1_02-22-1011'
THICKNESS=30.0
###############################################################

extracted_disp_and_force={
    'COU':[[]]*(10*4*12),
    'TBC':[[]]*(10*4*12)
}

with open(os.path.abspath(os.getcwd())+'/post_output/COUP_'+FILE_NAME+'.csv', "r") as f:
    reader = csv.reader(f,delimiter=',')
    first_line=True
    line_number=0
    for row in reader:
        if first_line:
            time_step=[float(i) for i in row]
            first_line=False
        else:
            extracted_disp_and_force['COU'][line_number-1]=[float(i) for i in row]
        line_number+=1

with open(os.path.abspath(os.getcwd())+'/post_output/PTBC_'+FILE_NAME+'.csv', "r") as f:
    reader = csv.reader(f,delimiter=',')
    first_line=True
    line_number=0
    for row in reader:
        if first_line:
            time_step=[float(i) for i in row]
            first_line=False
        else:
            extracted_disp_and_force['TBC'][line_number-1]=[float(i) for i in row]
        line_number+=1

class Cylinder:
    def __init__(self,side,number,u,ur,rf,rm,u_bc):
        self.name=str(side)+'_'+str(number)
        self.side=side
        self.number=number
        self.u=u
        self.ur=ur
        self.rf=rf
        self.rm=rm
        if u_bc!=None:
            self.shift=np.array(u)-np.array(u_bc)
        else:
            self.shift=[0,0]


DOF_FULL=12
NB_CYL=10
NB_SIDE=4
cylinders=[]
cylinders_names=[]

print('time_step : ',time_step)
step_of_interest=time_step.index(2.0)
print('step_of_interest',step_of_interest)

for index in range(NB_CYL*NB_SIDE):
    data=extracted_disp_and_force['COU'][index*DOF_FULL:(index+1)*DOF_FULL]
    data_bc=extracted_disp_and_force['TBC'][index*DOF_FULL:(index+1)*DOF_FULL]

    side_number=int(index/(NB_CYL))
    cylinder_number =int(index%NB_CYL)

    if len(data_bc[0])>0:
        if len(data[0])==0:
            c=Cylinder(side_number,cylinder_number,data_bc[6:8],data_bc[11],data_bc[0:2],data_bc[5],None)
            print(side_number,cylinder_number,data_bc[6:8],data_bc[11],data_bc[0:2],data_bc[5],None)
        else:
            c=Cylinder(side_number,cylinder_number,data[6:8],data[11],data_bc[0:2],data_bc[5],data_bc[6:8])
        cylinders.append(c)
        cylinders_names.append(c.name)
    else:
        cylinders.append(None)

cylinders_raw=cylinders[:]
cylinders=[cylinders[0:9],cylinders[10:19],cylinders[20:29],cylinders[30:39]]


def compute_force(side,direction,sens):
    force=0.0
    for cylinder in cylinders[side]:
        
        if cylinder:
            if sens=='+':
                force-=cylinder.rf[direction-1][step_of_interest]*(cylinder.number+1)/(NB_CYL+1)
            else:
                force-=cylinder.rf[direction-1][step_of_interest]*(NB_CYL-cylinder.number)/(NB_CYL+1)
    return force


force_panto={
    'O_0_x':compute_force(0,1,'-'), 
    'O_0_y':compute_force(0,2,'-'), 
    'O_3_x':compute_force(3,1,'-'), 
    'O_3_y':compute_force(3,2,'-'), 

    'B_0_x':compute_force(0,1,'+'), 
    'B_0_y':compute_force(0,2,'+'), 
    'B_1_x':compute_force(1,1,'-'), 
    'B_1_y':compute_force(1,2,'-'), 

    'C_1_x':compute_force(1,1,'+'), 
    'C_1_y':compute_force(1,2,'+'), 
    'C_2_x':compute_force(2,1,'+'), 
    'C_2_y':compute_force(2,2,'+'), 

    'D_2_x':compute_force(2,1,'-'), 
    'D_2_y':compute_force(2,2,'-'), 
    'D_3_x':compute_force(3,1,'+'), 
    'D_3_y':compute_force(3,2,'+')
}

m_stress = np.array([[-(force_panto['B_0_x'] + force_panto['C_1_x'] + force_panto['B_1_x'] + force_panto['C_2_x']),
                       -(force_panto['D_3_x'] + force_panto['D_2_x'] + force_panto['C_2_x'] + force_panto['C_1_x'])],
            [-(force_panto['B_0_y'] + force_panto['C_1_y'] + force_panto['B_1_y'] + force_panto['C_2_y']),
              -(force_panto['D_3_y'] + force_panto['D_2_y'] + force_panto['C_2_y'] + force_panto['C_1_y'])]])

n_stress = m_stress + m_stress.transpose()
SIDE_LENGTH=288.0
sigma  = 1.0/(2*SIDE_LENGTH*THICKNESS) * (m_stress + m_stress.transpose())
print(sigma)
