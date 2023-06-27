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
        self.force_panto = results['force_panto']
        self.cyl_out = results['cyl_out']

    def get_exportable_dict(self):
        full_dict = {}
        for key in [k for k in dir(self) if not k.startswith('__')]:
            if type(eval(f'self.{key}')) != type(self.get_exportable_dict):
                full_dict[key] = eval(f'self.{key}')
        return full_dict
    

    def get_number_ms(self) -> int:
        return sum([len(i) for i in self.skipped_cyl])
    

    def show_geo(self):
        root = Path('.').absolute().parent
        rgba = Image.open(root/self.campagne/'results' /
                            self.test_id/'geo.png').crop((588, 192, 1331, 935))
        rgba.save('tmp.png',compress_level=9)
        mono = rgba.split()[-1]
        mono = np.array(mono) > 0.01
        plt.figure(figsize=(3,3))
        plt.imshow(np.asarray(mono), cmap='Greys')
        plt.axis('off')
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



if __name__ == '__main__':
    pass
