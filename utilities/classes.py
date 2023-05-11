from PIL import Image
from pathlib import Path
import shutil
import numpy as np
import matplotlib.pyplot as plt
import csv

class Info:
    def __init__(self, test) -> None:
        self.test_id = test['test_id']
        self.sample_name = test['sample_name']
        self.dim = test['dim']
        self.geo_parameters = test['geo_parameters']
        self.mesh_size = test['mesh_size']
        self.thickness = test['thickness']
        self.trans_rot = test['trans_rot']
        self.corner_cleaner = test['corner_cleaner']
        self.mat = test['mat']
        self.free_rotation = test['free_rotation']
        self.free_u3 = test['free_u3']
        self.perfect_panto = test['perfect_panto']
        self.stiff_panto = test['stiff_panto']
        self.friction = test['friction']
        self.clearance = test['clearance']
        


class Test(Info):
    def __init__(self, test_parameters: dict, results: dict, campagne: str) -> None:
        super().__init__(test_parameters)
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
        self.support_links=None

    def get_number_ms(self) -> int:
        return sum([len(i) for i in self.skipped_cyl])

    def show_geo(self) -> None:
        root = Path('.').absolute().parent
        rgba = Image.open(root/self.campagne/'results' /
                         self.test_id/'geo.png').crop((588, 192, 1331, 935))
        mono= rgba.split()[-1]
        mono=np.array(mono)>0.01
        image = np.asarray(mono)
        plt.imshow(image, cmap='Greys')
        plt.show()
    
    def get_geo(self) -> np.ndarray:
        root = Path('.').absolute().parent
        rgba = Image.open(root/self.campagne/'results' /
                         self.test_id/'geo.png').crop((588, 192, 1331, 935))
        mono= rgba.split()[-1]
        mono=np.array(mono)>0.01
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

    def get_error(self, eoi:tuple)->float:
        return self.global_err[eoi[0]][eoi[1]]

    def get_forces(self)->tuple:
        """ONLY FOR LIN COMPUTATION"""
        rf=np.zeros((4,10,2,3))
        root = Path('.').absolute().parent
        file = np.loadtxt(root/self.campagne/'results' /
                         self.test_id/'PTBC.csv', delimiter=',')
        extracted_disp_and_force={
        'COU':[[]]*(10*4*12),
        'TBC':[[]]*(10*4*12)
        }
        with open(root/self.campagne/'results' /
                         self.test_id/'COUP.csv', "r") as f:
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
        with open(root/self.campagne/'results' /
                         self.test_id/'PTBC.csv', "r") as f:
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
        return time_step,extracted_disp_and_force

if __name__ == '__main__':
    pass
