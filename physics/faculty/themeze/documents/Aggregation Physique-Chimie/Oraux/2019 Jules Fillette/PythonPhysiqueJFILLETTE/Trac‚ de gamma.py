# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 14:59:47 2019

@author: jules.fillette
"""

import numpy as np
import matplotlib.pyplot as plt

gamma = []
x = np.linspace(0,0.99,100)
y = np.linspace(1.10,1.10,100)

gamma = 1/np.sqrt(1-x**2)
    
plt.plot(x,gamma,x,y)
plt.axis([0, 1, 0.9, 7])
plt.xlabel('vitesse (en unités de c)')
plt.ylabel('$\gamma = 1/\sqrt{1-(v/c)^2}}$')
plt.title('$\gamma$ en fonction de $v/c$')
plt.grid(axis='both')