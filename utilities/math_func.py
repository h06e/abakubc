from math import *
import numpy as np


def norme(k: np.ndarray) -> float:
    return sqrt(np.sum(k**2))


def rotation_voigt(k: np.ndarray, angle: float) -> np.ndarray:
    c, s = cos(angle), sin(angle)
    T = np.array([[c**2, s**2, c*s],
                  [s**2, c**2, -c*s],
                  [-2*s*c, 2*c*s, (c**2-s**2)]])
    return np.matmul(np.matmul(np.transpose(T), k), T)


def rotation_kelvin(k: np.ndarray, angle: float) -> np.ndarray:
    c, s = cos(angle), sin(angle)
    T = np.array([[c**2, s**2, sqrt(2)*c*s],
                  [s**2, c**2, -sqrt(2)*c*s],
                  [-sqrt(2)*s*c, sqrt(2)*c*s, (c**2-s**2)]])
    return np.matmul(np.matmul(np.transpose(T), k), T)


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


def get_invariants(ck: np.ndarray) -> tuple:

    a1 = 0.5 * (ck[0,0]-ck[1,1])
    K = 0.5 * (ck[0,0]+ck[0,1]-a1)
    d1 = -0.25 * (2*ck[0,1]+ck[2,2]-2*K)
    G=K-d1-ck[0,1]
    a2=1/sqrt(2) * (ck[0,2]+ck[1,2])
    d2=1/2/sqrt(2) * (ck[0,2]-ck[1,2])

    R=np.array([[0,1],[-1,0]])

    a_mat = np.array([[a1, a2],[a2, -a1]])
    d_mat = np.zeros((2,2,2,2))
    d_mat[0,0,0,0]=d_mat[1,1,1,1]=d1
    d_mat[0,0,1,1]=d_mat[0,1,0,1]=d_mat[1,0,0,1]=d_mat[1,0,1,0]=d_mat[0,1,1,0]=d_mat[1,1,0,0]=-d1
    d_mat[0,0,0,1]=d_mat[0,0,1,0]=d_mat[0,1,0,0]=d_mat[1,0,0,0]=d2
    d_mat[1,1,1,0]=d_mat[1,1,0,1]=d_mat[1,0,1,1]=d_mat[0,1,1,1]=-d2
    
    I2 = np.sum(a_mat**2)
    J2 = np.sum(d_mat**2)
    I3 = sum([a_mat[p,q]*d_mat[p,q,r,s]*a_mat[r,s] 
              for p in range(2)
              for q in range(2)
              for r in range(2)
              for s in range(2)])
    J3 = sum([R[p,q]*a_mat[q,r]*d_mat[p,r,s,t]*a_mat[s,t] 
          for p in range(2)
          for q in range(2)
          for r in range(2)
          for s in range(2)
          for t in range(2)])
    return K,G, I2, J2, I3, J3


