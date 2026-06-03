#!/usr/bin/python
# # -*- coding: utf_8 -*-



#--------------------------------------------------------------------
#                       Oscillateur amorti
#                       xpp+(w0^2)x=-fg*signe(xp)
#--------------------------------------------------------------------

#Ce programme permet de tracer les trajectoires de phase de l'oscillateur 
#amorti par frottement solide pour deux (ou plus) valeurs d'élongation initale
#(la vitesse initiale est nulle), avec mise en évidence du segment attracteur.
#Il permet également de tracer l'évolution temporelle de l'élongation et
#ainsi de mettre en évidence la décroissance linéaire de l'amplitude des oscillations.


from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
from pylab import *
from scipy import *
from scipy.integrate  import  odeint
from math import *


#paramètres du problème
w0=3 # rad/s
f=0.65
a=9.81*f/w0**2
print(a)

# Definition des deux équa diff du premier ordre
# dxdt = v
# dvdt = - w0^2*x -eps*w0^2*a
def solide(y, t):
    x, v = y                                # Vecteur variable
    dvdt = -(w0**2)*x-(w0**2)*a*sign(v)        # Equa. diff. 2
    if abs(x) < a and abs(v) < 1e-8:
        dydt = [0,0]
    else:
        dydt = [v,dvdt]                         # Vecteur solution
    return dydt 

# Paramètre d'intégration: vecteur temps
start = 0.                       # debut
end = 10.                        # fin
numsteps = 1000
t = np.linspace(start,end,numsteps)


# Conditions initiales
x0=[2,9]
v0=[0,0]
CI=np.array([x0,v0])

# Initialisation du tableau des solutions
X=np.zeros((numsteps,len(x0)))
V=np.zeros((numsteps,len(x0)))


# Résolution
for i in range(len(x0)) :
    print('0')
    sol=odeint(solide,CI[:,i],t)    
    X[:,i]=sol[:,0]
    V[:,i]=sol[:,1]


#--------------------------------------------------------------------
#       Tracé 
#--------------------------------------------------------------------

plt.figure(figsize=(10, 7))
plt.suptitle('Oscillateur amorti  ' + r'$\ddot{x} + \omega_0^2 x = \varepsilon \omega_0^2 a$',fontsize=22)
# Evolution temporelle
plt.subplot(1,2,1)
title('Evolution temporelle',fontsize=16)
for i in range(len(x0)):
    plot(t, X[:,i], label=r'$x_0=${}'.format(round(x0[i],2)))
t_env=linspace(0,9*2*pi/(4*a*w0),3)
plt.plot(t_env,9-4*a*t_env*w0/(2*pi),linestyle='--',color='orange',alpha=0.5)
plt.plot(t_env,-9+4*a*t_env*w0/(2*pi),linestyle='--',color='orange',alpha=0.5)
xlabel(r'$t$', fontsize=16)
ylabel(r'$x$', fontsize=16,rotation=0)
legend(fontsize=18)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
xlim(0,10)
plt.fill_between(t,-a,a,alpha=0.2,color='C2')
plt.grid()
# Portrait de phase
plt.subplot(1,2,2)
title('Portrait de phase',fontsize=16)
for i in range(len(x0)) :
    plot(X[:,i], V[:,i]/w0, label=r'$x_0=${}'.format(round(x0[i],2)))
axes=plt.gca()
plt.fill_between([-a,a],-12,12,alpha=0.2,color='C2')
plt.annotate(r'$M_0$',xy=(x0[0],0), xytext=(x0[0],0.5),color='C0',fontsize=20)
plt.annotate(r'$M_0$',xy=(x0[1],0), xytext=(x0[1],0.5),color='C1',fontsize=20)
axes.add_artist(matplotlib.patches.Circle((x0[0], 0), 0.2, color = 'C0'))
axes.add_artist(matplotlib.patches.Circle((x0[1], 0), 0.2, color = 'C1'))
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
xlabel(r'$x$', fontsize=20)
ylabel(r'$\frac{\dot{x}}{\omega_0}$', fontsize=20, rotation=0)
legend(fontsize=18)
plt.grid()
plt.axis((-12,12,-12,12))
#plt.savefig('amorti_solide.png')
plt.show()
