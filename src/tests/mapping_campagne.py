import os
from math import *

"""
Add a trans_rot mapping
"""

Nx=6
Ny=6
Ntheta=12
theta_max=30

L=28.0*13/10
width=4.0*13/10
aa=L/2/tan(pi/3)
bb=L/2*tan(pi/6)
H=2*(aa+2*bb)

root=os.path.abspath(os.getcwd())[:-3]
f=open(root+'campagne_1.csv','a')
f.write('\n,,,,,,,,,,,,,,,,,,,,,,,\n,,,,,,,,,,,,,,,,,,,,,,,\n')

for idx_theta in range(Ntheta+1):
    for idx_x in range(4):
        for idx_y in range(Ny):

            test_id=f'H{int(L)}_map_{idx_theta}_{idx_x}_{idx_y}'
            theta=round(theta_max*idx_theta/Ntheta,5)
            th=theta/180*pi
            tx_0=L*idx_x/Nx
            ty_0=H*idx_y/Ny
            tx=round(tx_0*cos(th)-ty_0*sin(th),5)
            ty=round(tx_0*sin(th)+ty_0*cos(th),5)
            car=f'{test_id},honey,,{L}/{width},{round(width/5,5)},20.0,{tx}/{ty}/{theta},,,150.0/0.3,True,True,57.74E3/6950.0,0.1/2500/2000.0/0.0/5000.0,0.030/0.004/0.013/0.043,2/0/0,0/2/0,0/0/2,True,False,,,,\n'
            f.write(car)

f.close()
