from PIL import Image
from pathlib import Path
import shutil
import numpy as np
import matplotlib.pyplot as plt
import csv
from math import *
from math_func import *
import json
import base64

class Test():
    def __init__(self, results: dict, campagne: str) -> None:
        self.test_id = results['test']['test_id']
        self.sample_name = results['test']['sample_name']
        self.dim = results['test']['dim']
        self.geo_parameters = results['test']['geo_parameters']
        self.mesh_size = results['test']['mesh_size']
        self.thickness = results['test']['thickness']
        self.trans_rot = results['test']['trans_rot']
        self.corner_cleaner = results['test']['corner_cleaner']
        self.mat = results['test']['mat']
        self.free_rotation = results['test']['free_rotation']
        self.free_u3 = results['test']['free_u3']
        self.perfect_panto = results['test']['perfect_panto']
        self.stiff_panto = results['test']['stiff_panto']
        self.friction = results['test']['friction']
        self.clearance = results['test']['clearance']

        self.K_field_bc = results['K_field_bc']
        self.K_field_dic = results['K_field_dic']
        self.K_panto_bc = results['K_panto_bc']
        self.K_panto_dic = results['K_panto_dic']
        self.K_plane_stress_KUBC = results['K_plane_stress_KUBC'] if 'K_plane_stress_KUBC' in results.keys(
        ) else None
        self.K_plane_stress_PBC = results['K_plane_stress_PBC'] if 'K_plane_stress_PBC' in results.keys(
        ) else None
        self.K_plane_stress = results['K_plane_stress'] if 'K_plane_stress' in results.keys(
        ) else None
        self.global_err = results['global_err']
        self.skipped_cyl = results['skipped_cyl']
        self.strain_field = results['strain_field']
        self.strain_th = results['strain_th']
        self.stress_field = results['stress_field']
        self.stress_pantos = results['stress_pantos']
        self.force_panto = results['force_panto'] if 'force_panto' in results.keys(
        ) else None
        self.cyl_out = results['cyl_out'] if 'cyl_out' in results.keys(
        ) else None
        self.campagne = campagne
        self.support_links = None
        self.force_panto :list[dict]= results['force_panto']
        self.cyl_out = results['cyl_out']

    def get_exportable_dict(self):
        full_dict = {}
        for key in [k for k in dir(self) if not k.startswith('__')]:
            if type(eval(f'self.{key}')) != type(self.get_exportable_dict):
                full_dict[key] = eval(f'self.{key}')
        return full_dict
    

    def get_number_ms(self) -> int:
        return sum([len(i) for i in self.skipped_cyl])
    

    def show_geo(self, show=True, cmap='Greys', new=True):
        root = Path('.').absolute().parent
        rgba = Image.open(root/self.campagne/'results' /
                            self.test_id/'geo.png').crop((588, 192, 1331, 935))
        rgba.save('tmp.png',compress_level=9)
        mono = rgba.split()[-1]
        mono = np.array(mono) > 0.01
        if new:
            plt.figure(figsize=(3,3))
        plt.imshow(np.asarray(mono), cmap=cmap, extent =[0.05,0.95,0.05,0.95], alpha=0.2)
        plt.axis('off')
        if show:
            plt.show()
        return 
    

    def get_MS(self) -> np.ndarray:
        m = np.zeros((4, 10))
        for i_cote, cote in enumerate(self.skipped_cyl):
            for support in cote:
                m[i_cote, support] = 1.0
        return m

    def get_MS_corner(self) -> np.ndarray:
        """return the m matrix [corner, idex_support] the coef is in [0,0.5,1.0]"""
        m_MS = self.get_MS()
        m = np.zeros((4, 5))
        for corner in range(4):
            m[corner] = 0.5*(np.flip(m_MS[corner, 5:]) +
                             m_MS[(corner+1) % 4, :5])
        return m

    def get_error(self, eoi: tuple) -> float:
        """Erreur avec notation de Kelvin"""
        if self.K_plane_stress:
            k_list=[self.K_plane_stress,self.K_field_dic,self.K_panto_dic]
        else:
            k_list=[self.K_plane_stress_PBC,self.K_plane_stress_KUBC,self.K_field_dic,self.K_panto_dic]
        a=voigt2kelvin(np.array(k_list[eoi[0]]))
        b=voigt2kelvin(np.array(k_list[eoi[1]]))
        return 100*norme(b-a)/norme(a)

    def show_eff_corner(self, step=0,scale_fac=3,eoi=(0,3)) -> None:
        ec=0.05
        def draw_machine():
            plt.plot([ec, 1-ec],[0,0],'b-')
            plt.plot([ec, 1-ec],[1,1],'b-')
            plt.plot([0, 0],[ec,1-ec],'b-')
            plt.plot([1, 1],[ec,1-ec],'b-')
            plt.text(0.1,0.1,'O', va='center', ha='center')
            plt.text(0.9,0.1,'B', va='center', ha='center')
            plt.text(0.1,0.9,'D', va='center', ha='center')
            plt.text(0.9,0.9,'C', va='center', ha='center')
            plt.text(0.5,0.1,'3', va='center', ha='center')
            plt.text(0.9,0.5,'2', va='center', ha='center')
            plt.text(0.5,0.9,'4', va='center', ha='center')
            plt.text(0.1,0.5,'1', va='center', ha='center')

        def draw_all_vec(scale=1):
            for k,i in self.force_panto[step].items():
                corner, edge, component = k.split('_')
                if edge == '1':
                    x0=-ec
                elif corner in ['O', 'D']:
                    x0=ec
                elif edge == '2':
                    x0=1+ec
                else:
                    x0=1-ec

                if edge == '3':
                    y0=-ec
                elif corner in ['O', 'B']:
                    y0=ec
                elif edge == '4':
                    y0=1+ec
                else:
                    y0=1-ec
                if component=='x':
                    plt.plot([x0,x0+i/scale],[y0,y0])
                    plt.text(x0+i/scale,y0,f'{i:.0f}')
                else:
                    plt.plot([x0,x0],[y0,y0+i/scale])
                    plt.text(x0,y0+i/scale,f'{i:.0f}')

        scale=scale_fac*max([i for _,i in self.force_panto[step].items()])
        plt.figure(figsize=(5,5))
        self.show_geo(show=False, new=False)
        draw_machine()
        draw_all_vec(scale)
        plt.text(0.5,0.5,f'Err. PBC/Panto.\n{self.get_error(eoi):.1f}\n{self.get_coef_dev()}',
                  va='center',ha='center', fontsize=10)
        plt.axis('equal')
        plt.show()
    
    def get_coef_dev(self, rot=False):
        if self.sample_name == 'monolithique':
            k_ref=np.array(self.K_plane_stress)
        else:
            k_ref=np.array(self.K_plane_stress_PBC)
        k_machine=np.array(self.K_panto_dic)
        if rot:
            k_ref=rotation_voigt(k_ref,-self.trans_rot[2])
            k_machine=rotation_voigt(k_machine,-self.trans_rot[2])

        string = f'     PBC    KUBC\n'
        for i,j in [(0,0),(0,1),(2,2)]:
            string += f'K{i+1}{j+1} {k_ref[i,j]:.1f}  {k_machine[i,j]:.1f} ({(k_machine[i,j]-k_ref[i,j])*100/k_ref[i,j]:+.0f}%)\n'

        return string

if __name__ == '__main__':
    pass
