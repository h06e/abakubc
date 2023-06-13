from math import *
import numpy as np


def norme(k: np.ndarray) -> float:
    return sqrt(np.sum(k**2))


def rotation_voigt(k: np.ndarray, angle: float) -> np.ndarray:
    c, s = cos(angle), sin(angle)
    T = np.array([[c**2, s**2, c*s],
                  [s**2, c**2, -c*s],
                  [-2*s*c, 2*c*s, (c**2-s**2)]])
    return np.dot(np.dot(np.transpose(T), k), T)


def rotation_kelvin(k: np.ndarray, angle: float) -> np.ndarray:
    c, s = cos(angle), sin(angle)
    T = np.array([[c**2, s**2, sqrt(2)*c*s],
                  [s**2, c**2, -sqrt(2)*c*s],
                  [-sqrt(2)*s*c, sqrt(2)*c*s, (c**2-s**2)]])
    return np.dot(np.dot(np.transpose(T), k), T)


def voigt2kelvin(k: np.ndarray) -> np.ndarray:
    a = np.array([[1, 1, sqrt(2)],
                  [1, 1, sqrt(2)],
                  [sqrt(2), sqrt(2), 2]])
    return a*k


def kelvin2voigt(k: np.ndarray) -> np.ndarray:
    a = np.array([[1, 1, sqrt(2)],
                  [1, 1, sqrt(2)],
                  [sqrt(2), sqrt(2), 2]])
    return (1/a)*k


def get_sym_error(k: np.ndarray) -> float:
    """NE PAS CONVERTIR EN KELVIN AVANT
    Prend une matrice en notation de Voigt"""
    k = voigt2kelvin(k)
    k_sym = 0.5*(k+np.transpose(k))
    return 100*norme(k-k_sym)/norme(k)


def get_error_custom(kref: np.ndarray, k2: np.ndarray) -> float:
    kref = voigt2kelvin(kref)
    k2 = voigt2kelvin(k2)
    return 100*norme(k2-kref)/norme(k2)


def get_sym_part(k: list) -> np.ndarray:
    return 0.5*(np.array(k)+np.transpose(np.array(k)))


def get_harmonics(k_voigt: np.ndarray) -> tuple:
    k_kelvin = voigt2kelvin(k_voigt)
    c = k_kelvin/np.array([[1, 1, sqrt(2)],
                           [1, 1, sqrt(2)],
                           [sqrt(2), sqrt(2), 2]])  # Pour avoir les coef cijk

    d = None  # ~ A implémenter si besoin

    a = np.zeros((2, 2))
    a[0, 0] = 1/12 * (c[0, 0] - c[1, 1])
    a[0, 1] = 1/6 * (c[0, 2] + c[1, 2])
    a[1, 0] = a[0, 1]
    a[1, 1] = 1/12 * (c[1, 1] - c[0, 0])

    lambd = 1/8 * (c[0, 0] + c[1, 1] + 3 * (c[0, 1]+c[1, 0]) - 4*c[2, 2])
    mu = 1/8 * (c[0,0]+c[1,1]+4*c[2,2]-c[0,1]-c[1,0])

    return d, a, lambd, mu

def get_invariants (k_voigt:np.ndarray) -> tuple:
    d, a, lambd, mu = get_harmonics(k_voigt)

    I1 = lambd+mu
    J1=mu
    I2 = np.sum(a**2)

    return I1, J1, I2