import matplotlib.pyplot as plt
from math import *
import numpy as np

# Paramètre de la gauss
mu = 2500
sigma = 2000
tronq_min = 0
tronq_max = 5000

# Nombre de points
N=1000
x = np.arange(tronq_min,tronq_max,(tronq_max-tronq_min)/N)
y=1/(sqrt(2/pi)*sigma)*np.exp(-(x-mu)**2/(2*sigma**2))
plt.plot(x,y,'r-')
plt.fill_between(x, y, 0, color='blue', alpha=.5)
plt.show()

# \frac{1}{\sqrt{2\pi}\cdot s}e ^ {\frac{-\left(x-m\right) ^ {2}}{2s ^ {2}}}
