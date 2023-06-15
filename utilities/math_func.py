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


# def get_d_harmonic(c: np.ndarray) -> np.ndarray:
#     d = np.zeros((2, 2, 2, 2))
#     c4 = np.zeros((2, 2, 2, 2))
#     c4[0, 0, 0, 0] = c[0, 0]  # C1111
#     c4[1, 1, 1, 1] = c[1, 1]  # C2222
#     c4[0, 0, 1, 1] = c4[1, 1, 0, 0] = c[1, 0] # C1122
#     c4[0, 1, 0, 1] = c4[1, 0, 1, 0] = c4[1, 0, 0, 1] = c4[0, 1, 1, 0] = c[2, 2] # C1212
#     c4[0, 0, 0, 1] = c4[0, 0, 1, 0] = c4[0, 1, 0, 0] = c4[1, 0, 0, 0] = c[0, 2] # C1112
#     c4[1, 1, 1, 0] = c4[1, 1, 0, 1] = c4[1, 0, 1, 1] = c4[0, 1, 1, 1] = c[1, 2] # C2212

#     for i in range(2):
#         for j in range(2):
#             for k in range(2):
#                 for l in range(2):
#                     term_0 = term_1 = term_2 = 0
#                     for p in range(2):
#                         term_0 += ( (i==j)*c4[k,p,i,p] + (k==l)*c4[i,p,j,p] + (i==k)*c4[l,p,j,p] 
#                                    + (l==j)*c4[i,p,k,p] + (i==l)*c4[j,p,k,p] + (j==k)*c4[i,p,l,p])
#                         for q in range(2):
#                             term_1 += c4[p,q,p,q]/12 * ( 5*int(i==j and k==l) - 
#                                                          int(i==k and j==l) - 
#                                                          int(i==l and j==k) )
#                             term_2 += -c4[p,p,q,q]/8 * ( 3*int(i==j and k==l) - 
#                                                          int(i==k and j==l) - 
#                                                          int(i==l and j==k) )

                    
#                     d[i, j, k, l] = c4[i, j, k, l] - 1/6*term_0 + term_1 + term_2

#     return d


# def get_harmonics(k: np.ndarray) -> tuple:
#     c = k/np.array([[1, 1, sqrt(2)],
#                     [1, 1, sqrt(2)],
#                     [sqrt(2), sqrt(2), 2]])
#     d = np.zeros((2, 2, 2, 2))
#     c4 = np.zeros((2, 2, 2, 2))
#     c4[0, 0, 0, 0] = c[0, 0]  # C1111
#     c4[1, 1, 1, 1] = c[1, 1]  # C2222
#     c4[0, 0, 1, 1] = c4[1, 1, 0, 0] = c[1, 0] # C1122
#     c4[0, 1, 0, 1] = c4[1, 0, 1, 0] = c4[1, 0, 0, 1] = c4[0, 1, 1, 0] = c[2, 2] # C1212
#     c4[0, 0, 0, 1] = c4[0, 0, 1, 0] = c4[0, 1, 0, 0] = c4[1, 0, 0, 0] = c[0, 2] # C1112
#     c4[1, 1, 1, 0] = c4[1, 1, 0, 1] = c4[1, 0, 1, 1] = c4[0, 1, 1, 1] = c[1, 2] # C2212

#     for i in range(2):
#         for j in range(2):
#             for k in range(2):
#                 for l in range(2):
#                     term_0 = term_1 = term_2 = 0
#                     for p in range(2):
#                         term_0 += ( (i==j)*c4[k,p,i,p] + (k==l)*c4[i,p,j,p] + (i==k)*c4[l,p,j,p] 
#                                    + (l==j)*c4[i,p,k,p] + (i==l)*c4[j,p,k,p] + (j==k)*c4[i,p,l,p])
#                         for q in range(2):
#                             term_1 += c4[p,q,p,q]/12 * ( 5*int(i==j and k==l) - 
#                                                          int(i==k and j==l) - 
#                                                          int(i==l and j==k) )
#                             term_2 += -c4[p,p,q,q]/8 * ( 3*int(i==j and k==l) - 
#                                                          int(i==k and j==l) - 
#                                                          int(i==l and j==k) )

#                     d[i, j, k, l] = c4[i, j, k, l] - 1/6*term_0 + term_1 + term_2

#     a = np.zeros((2, 2))
#     a[0, 0] = 1/12 * (c[0, 0] - c[1, 1])
#     a[0, 1] = 1/6 * (c[0, 2] + c[1, 2])
#     a[1, 0] = a[0, 1]
#     a[1, 1] = 1/12 * (c[1, 1] - c[0, 0])

#     lambd = 1/8 * (c[0, 0] + c[1, 1] + 3 * (c[0, 1]+c[1, 0]) - 4*c[2, 2])
#     mu = 1/8 * (c[0, 0]+c[1, 1]+4*c[2, 2]-c[0, 1]-c[1, 0])

#     return d, a, lambd, mu


# def get_invariants(k_voigt: np.ndarray) -> tuple:
#     d, a, lambd, mu = get_harmonics(k_voigt)
#     R=np.array([[0,1],[-1,0]])
#     I1 = lambd+mu
#     J1 = mu
#     I2 = np.sum(a**2)
#     J2 = np.sum(d**2)
#     I3 = sum([a[p,q]*d[p,q,r,s]*a[r,s] 
#               for p in range(2)
#               for q in range(2)
#               for r in range(2)
#               for s in range(2)]) # je comprend pas trop ce que numpy fait avec les indices
#     J3 = [R[p,q]*a[q,r]*d[p,r,s,t]*a[s,t] 
#           for p in range(2)
#           for q in range(2)
#           for r in range(2)
#           for s in range(2)
#           for t in range(2)]

#     return I1, J1, I2, J2, I3, J3

def get_invariants(ck: np.ndarray) -> tuple:
    # ck = voigt2kelvin(c_voigt)
    # ck=np.zeros((3,3))
    # if c[0,0]<c[1,1]:
    #     ck[0,0], ck[0,1], ck[0,2] = c[1,1], c[1,0], c[1,2]
    #     ck[1,0], ck[1,1], ck[1,2] = c[0,1], c[0,0], c[0,2]
    #     ck[2,0], ck[2,1], ck[2,2] = c[2,1], c[2,0], c[2,2]
    # else:
    #     ck=c

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


