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

def get_error_custom (kref:list, k2:list)-> float:
    kref=voigt2kelvin(np.array(kref))
    k2=voigt2kelvin(np.array(k2))
    return 100*norme(k2-kref)/norme(k2)