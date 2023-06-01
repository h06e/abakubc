from PIL import Image
from pathlib import Path
import shutil
import numpy as np
import matplotlib.pyplot as plt
import csv
from math import *


class Test():
    def __init__(self, test_parameters: dict, results: dict, campagne: str) -> None:
        self.test_id = test_parameters['test_id']
        self.sample_name = test_parameters['sample_name']
        self.dim = test_parameters['dim']
        self.geo_parameters = test_parameters['geo_parameters']
        self.mesh_size = test_parameters['mesh_size']
        self.thickness = test_parameters['thickness']
        self.trans_rot = test_parameters['trans_rot']
        self.corner_cleaner = test_parameters['corner_cleaner']
        self.mat = test_parameters['mat']
        self.free_rotation = test_parameters['free_rotation']
        self.free_u3 = test_parameters['free_u3']
        self.perfect_panto = test_parameters['perfect_panto']
        self.stiff_panto = test_parameters['stiff_panto']
        self.friction = test_parameters['friction']
        self.clearance = test_parameters['clearance']

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
        self.campagne = campagne
        self.support_links = None

    def get_exportable_dict(self):
        all_dict = {
            'test_id': self.test_id,
            'sample_name': self.sample_name,
            'dim': self.dim,
            'geo_parameters': self.geo_parameters,
            'mesh_size': self.mesh_size,
            'thickness': self.thickness,
            'trans_rot': self.trans_rot,
            'corner_cleaner': self.corner_cleaner,
            'mat': self.mat,
            'free_rotation': self.free_rotation,
            'free_u3': self.free_u3,
            'perfect_panto': self.perfect_panto,
            'stiff_panto': self.stiff_panto,
            'friction': self.friction,
            'clearance': self.clearance,
            'K_field_bc': self.K_field_bc,
            'K_field_dic': self.K_field_dic,
            'K_panto_bc': self.K_panto_bc,
            'K_panto_dic': self.K_panto_dic,
            'K_plane_stress_KUBC': self.K_plane_stress_KUBC,
            'K_plane_stress_PBC': self.K_plane_stress_PBC,
            'K_plane_stress': self.K_plane_stress,
            'global_err': self.global_err,
            'skipped_cyl': self.skipped_cyl,
            'strain_field': self.strain_field,
            'strain_th': self.strain_th,
            'stress_field': self.stress_field,
            'stress_pantos': self.stress_pantos,
            'campagne': self.campagne,
            'support_links': self.support_links
        }
        return all_dict

    def get_number_ms(self) -> int:
        return sum([len(i) for i in self.skipped_cyl])

    def show_geo(self) -> None:
        root = Path('.').absolute().parent
        rgba = Image.open(root/self.campagne/'results' /
                          self.test_id/'geo.png').crop((588, 192, 1331, 935))
        mono = rgba.split()[-1]
        mono = np.array(mono) > 0.01
        image = np.asarray(mono)
        plt.imshow(image, cmap='Greys')
        plt.show()

    def get_geo(self) -> np.ndarray:
        root = Path('.').absolute().parent
        rgba = Image.open(root/self.campagne/'results' /
                          self.test_id/'geo.png').crop((588, 192, 1331, 935))
        mono = rgba.split()[-1]
        mono = np.array(mono) > 0.01
        image = mono*1.0
        return image

    def export_geo(self, destination=Path('.')) -> None:
        root = Path('.')
        shutil.copyfile(root/self.campagne/'results'/self.test_id /
                        'geo.png', destination/f'{self.test_id}.png')

    def get_err(self, err: tuple) -> float:
        return self.global_err[err[0]][err[1]]

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
        return self.global_err[eoi[0]][eoi[1]]

    def get_forces(self) -> tuple:
        """ONLY FOR LIN COMPUTATION"""
        rf = np.zeros((4, 10, 2, 3))
        root = Path('.').absolute().parent
        file = np.loadtxt(root/self.campagne/'results' /
                          self.test_id/'PTBC.csv', delimiter=',')
        extracted_disp_and_force = {
            'COU': [[]]*(10*4*12),
            'TBC': [[]]*(10*4*12)
        }
        with open(root/self.campagne/'results' /
                  self.test_id/'COUP.csv', "r") as f:
            reader = csv.reader(f, delimiter=',')
            first_line = True
            line_number = 0
            for row in reader:
                if first_line:
                    time_step = [float(i) for i in row]
                    first_line = False
                else:
                    extracted_disp_and_force['COU'][line_number -
                                                    1] = [float(i) for i in row]
                line_number += 1
        with open(root/self.campagne/'results' /
                  self.test_id/'PTBC.csv', "r") as f:
            reader = csv.reader(f, delimiter=',')
            first_line = True
            line_number = 0
            for row in reader:
                if first_line:
                    time_step = [float(i) for i in row]
                    first_line = False
                else:
                    extracted_disp_and_force['TBC'][line_number -
                                                    1] = [float(i) for i in row]
                line_number += 1
        return time_step, extracted_disp_and_force


if __name__ == '__main__':
    pass
