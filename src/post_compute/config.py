import numpy as np

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