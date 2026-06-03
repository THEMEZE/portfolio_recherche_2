#!/usr/bin/python
# # -*- coding: utf_8 -*-


import numpy as np
import matplotlib.pyplot as plt
import os
from mpl_toolkits.mplot3d import Axes3D # pour la 3D
from pylab import *
from  scipy  import *
from  scipy.integrate  import  odeint
from math import*


#--------------------------------------------------------------------
#                       Oscillateur amorti
#                       xpp+(w0/Q)xp+(w0^2)x=0
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# Description
# routine amorti.py
# function amort(y,t,Q,w0)
#     arguments: y: solution, t:temps d'intégration, Q,w0: variables du problème.
# commentaires:
# On résoud numériquement l'équa. diff. de l'oscillateur amorti pour plusieurs valeurs du facteur de qualité (boucle sur i avec i le nombre de Q testés différents.
# La résolution numérique des équations différentielles donne un tableau où les lignes correspondent au temps, la premiere colone  à la solution pour la variable y[0]=x et la deuxième colone à la solution pour la variable y[1]=v
#--------------------------------------------------------------------

#--------------------------------------------------------------------
#       Obtention des solutions
#--------------------------------------------------------------------

# -------------------------------------------------------------------
# Definition de l'equa. diff.

# Definition des deux équa diff du premier ordre
# dxdt = v
# dvdt = -wo/Q*v - w0^2*x
def fluide(y, t, Q, w0):
    x, v = y                            # Vecteur variable
    dvdt = -w0/Q*v-w0**2*x              # Equa. diff. 2
    dydt = [v,dvdt]                     # Vecteur solution
    return dydt                         

# -------------------------------------------------------------------
# Definition des constantes du problème et des CI

# Constantes du problème
w0 = 6
Q=[0.3,5] # On calcule pour différents facteurs de qualité



# Paramètre d'intégration: vecteur temps
start = 0                       # debut
end = 10                        # fin
numsteps = 1500                  # nombre de pas d'integration
t = linspace(start,end,numsteps)

# Conditions initiales
x0=9
v0=0
# Tableau des CI
CI=array([x0,v0])

# -------------------------------------------------------------------
# Initialisation du tableau des solutions
# Autant de solutions que de Q différents
X=np.zeros((numsteps, len(Q)))
V=np.zeros((numsteps, len(Q)))


#--------------------------------------------------------------------
# Boucle de résolution
for i in range(len(Q)): 
 sol=odeint(fluide,CI,t,args=(Q[i], w0))    
        
 # récupération de la solution
 X[:,i]=sol[:,0]
 V[:,i]=sol[:,1]


#--------------------------------------------------------------------
#       Tracé des solutions
#--------------------------------------------------------------------


# Evolution temporelle
plt.figure(figsize=(10, 7))
plt.suptitle('Oscillateur amorti par frottement fluide  ' + r'$\ddot{x} + \frac{\omega_0}{Q}\dot{x} + \omega_0^2 x = 0$',fontsize=22)
plt.subplot(1,2,1)
plot(t, X[:, 0], '-', ms=6,label=r'$Q=0.3$')
plot(t, X[:, 1], '-', ms=6,label=r'$Q=5$')
plot(t,x0*np.exp(-t*w0/(2*Q[1])),linestyle='--',color='orange',alpha=0.7)
plot(t,-x0*np.exp(-t*w0/(2*Q[1])),linestyle='--',color='orange',alpha=0.7)
#plt.axis((-0.25,0.25,-0.25,0.25))
title('Evolution temporelle',fontsize=16)
xlabel(r'$t$', fontsize=20)
ylabel(r'$x$', rotation=0, fontsize=20)
legend(fontsize=20)
grid(True)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
xlim(0,10)
# Portrait de phase
plt.subplot(1,2,2)
plot(X[:, 0], V[:, 0]/w0, '-', ms=6,label=u"$Q=0.3$")
plot(X[:, 1], V[:, 1]/w0, '-', ms=6,label=u"$Q=5$")
plt.axis((-1,1,-1,1))
title('Portrait de phase',fontsize=16)
xlabel(r'$x$', fontsize=20)
ylabel(r'$\frac{\dot{x}}{\omega_0}$', fontsize=20, rotation=0)
axis('equal')
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
legend(fontsize=20,loc='upper right')
plt.axis((-12,12,-12,12))
grid(True)
#plt.savefig('amorti_fluide.png')
plt.show()
