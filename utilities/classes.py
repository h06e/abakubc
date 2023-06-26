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
    def __init__(self, test_parameters: dict, results: dict, campagne: str, line_img=None) -> None:
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
        # self.global_err = results['global_err']
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

        self.line_img = line_img # C'est pour acceder a l'image dans le .iii

    def get_exportable_dict(self):
        full_dict = {}
        for key in [k for k in dir(self) if not k.startswith('__')]:
            if type(eval(f'self.{key}')) != type(self.get_exportable_dict):
                full_dict[key] = eval(f'self.{key}')
        return full_dict
    
    def get_exportable_dict_with_img(self):
        """the png geo is stored in binary string in the dict"""
        full_dict = {}
        for key in [k for k in dir(self) if not k.startswith('__')]:
            full_dict[key] = eval(f'self.{key}')
        
        img = self.get_img_file()
        img.save('tmp.png',compress_level=9)
        with open('tmp.png','br') as img_file:
            conv_img=img_file.readlines()
        full_dict['img_geo_bin']=[base64.b64decode(i) for i in conv_img]
        return full_dict

    def get_number_ms(self) -> int:
        return sum([len(i) for i in self.skipped_cyl])

    def show_geo(self) -> None:
        ROOT = Path('.').absolute().parent
        if self.line_img:
            print(self.line_img)
            with open(ROOT/'database'/f'{self.campagne}.iii', 'br') as f:
                for _ in range(self.line_img):
                    next(f)
                file=[f.readline()]
                line=None
                while line != b'\x89PNG\r\n':
                    line=f.readline()
                    file.append(line)
                with open('tmp.png', 'bw') as img_file:
                    img_file.writelines(file[:-2])
                rgba = Image.open('tmp.png')
        else:
            rgba = Image.open(ROOT/self.campagne/'results' /
                            self.test_id/'geo.png').crop((588, 192, 1331, 935))
        mono = rgba.split()[-1]
        mono = np.array(mono) > 0.01
        image = np.asarray(mono)
        plt.figure(figsize=(3,3))
        plt.imshow(image, cmap='Greys')
        plt.axis('off')
        return
        

    def get_img_binfile(self):
        root = Path('.').absolute().parent
        rgba = Image.open(root/self.campagne/'results' /
                          self.test_id/'geo.png').crop((588, 192, 1331, 935))
        rgba.save('tmp.png',compress_level=9)
        with open('tmp.png','br') as img_file:
            conv_img=img_file.readlines()
        return conv_img


    # def export_geo(self, destination) -> None:
    #     root = Path('.').absolute().parent
    #     shutil.copyfile(root/self.campagne/'results'/self.test_id /
    #                     'geo.png', f'{destination}/{self.test_id}.png')

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
