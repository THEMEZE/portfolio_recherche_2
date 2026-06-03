# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 11:20:35 2018

@author: juliu
"""

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import os
from pylab import *
from scipy import *
from scipy.integrate  import  odeint
from math import *


"""Paramètre d'intégration: vecteur temps"""
# Ce sera le même pour les deux oscillateurs

start = 0.                       # debut
end = 10.                        # fin
numsteps = 1000
t = linspace(start,end,numsteps)

#%% OSCILLATEUR AMORTI PAR FROTTEMENT SOLIDE


""" Paramètres du problème """
wS0=np.pi # rad/s
f=0.65
a=9.81*f/wS0**2

""" Définition des deux équa diff du premier ordre pour le frottement solide """
# dxdt = v
# dvdt = - w0^2*x -eps*w0^2*a
def solide(y, t):
    x, v = y                                    # Vecteur variable
    dvdt = -(wS0**2)*x-(wS0**2)*a*sign(v)         # Equa. diff. 2
    if abs(x) < a and abs(v) < 1e-8:
        dydt = [0,0]
    else:
        dydt = [v,dvdt]                         # Vecteur solution
    return dydt 


""" Conditions initiales """
xS0=[3,8]
vS0=[0,0]
CI=array([xS0,vS0])

""" Initialisation du tableau des solutions """
XS=np.zeros((numsteps,len(xS0)))
VS=np.zeros((numsteps,len(xS0)))


""" Résolution """
for i in range(len(xS0)) :
    sol=odeint(solide,CI[:,i],t)    
    XS[:,i]=sol[:,0]
    VS[:,i]=sol[:,1]


#%% OSCILLATEUR AMORTI PAR FROTTEMENT FLUIDE

"""Constantes du problème"""
wF0 = np.pi
Q=[0.3,5]

"""Definition des deux équa diff du premier ordre"""
# dxdt = v
# dvdt = -wo/Q*v - w0^2*x
def fluide(y, t, Q, w0):
    x, v = y                            # Vecteur variable
    dvdt = -w0/Q*v-w0**2*x              # Equa. diff. 2
    dydt = [v,dvdt]                     # Vecteur solution
    return dydt                         

""" Conditions initiales """
xF0=8
vF0=0
CI=array([xF0,vF0])

""" Initialisation du tableau des solutions """
# Autant de solutions que de Q différents
XF=np.zeros((numsteps, len(Q)))
VF=np.zeros((numsteps, len(Q)))


""" Boucle de résolution """
for i in range(len(Q)): 
    sol=odeint(fluide,CI,t,args=(Q[i], wF0))    
    XF[:,i]=sol[:,0]
    VF[:,i]=sol[:,1]


#%% Tracé

#""" Evolutions temporelles """

plt.figure(figsize=(10, 7))
plt.suptitle("Evolution temporelle d'oscillateurs amortis", fontsize=22)
# Frottement fluide
plt.subplot(1,2,1)
title('Frottement fluide  ' + r'$\ddot{x} + \frac{\omega_0}{Q}\dot{x} + \omega_0^2 x = 0$',fontsize=18)
plot(t, XF[:, 0], '-', label=r'$Q=0.3$', color='C9')
plot(t, XF[:, 1], '-', label=r'$Q=5$', color='C1')
plot(t,xF0*np.exp(-t*wF0/(2*Q[1])),linestyle='--',color='orange',alpha=0.7)
plot(t,-xF0*np.exp(-t*wF0/(2*Q[1])),linestyle='--',color='orange',alpha=0.7)
xlabel(r'$t$', fontsize=18)
ylabel(r'$x$', rotation=0, fontsize=18)
legend(fontsize=18)
plt.grid()
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
xlim(0,10)

#Frottement solide
plt.subplot(1,2,2)
for i in range(len(xS0)):
    plot(t, XS[:,i], label=r'$x_0=${}'.format(round(xS0[i],2)))
t_env=linspace(0,8*2*pi/(4*a*wS0),3) # tracé de l'enveloppe
plt.plot(t_env,8-4*a*t_env*wS0/(2*pi),linestyle='--',color='orange',alpha=0.5)
plt.plot(t_env,-8+4*a*t_env*wS0/(2*pi),linestyle='--',color='orange',alpha=0.5)
xlabel(r'$t$', fontsize=18)
ylabel(r'$x$', fontsize=18,rotation=0)
legend(fontsize=18)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
xlim(0,10)
plt.fill_between(t,-a,a,alpha=0.2,color='C2')
title('Frottement solide  ' + r'$\ddot{x} + \omega_0^2 x = \varepsilon \omega_0^2 a$',fontsize=18)
plt.grid()
plt.show()


#""" Portraits de phase """
#
#plt.figure(figsize=(10, 7))
#plt.suptitle("Portraits de phase d'oscillateurs amortis", fontsize=22)
## Frottement fluide
#plt.subplot(1,2,1)
#title('Frottement fluide  ' + r'$\ddot{x} + \frac{\omega_0}{Q}\dot{x} + \omega_0^2 x = 0$',fontsize=18)
#plot(XF[:, 0], VF[:, 0]/wF0, '-', label=u"$Q=0.3$", color='C9')
#plot(XF[:, 1], VF[:, 1]/wF0, '-', label=u"$Q=5$", color='C1')
#xlabel(r'$x$', fontsize=20)
#ylabel(r'$\frac{\dot{x}}{\omega_0}$', fontsize=20, rotation=0)
#axes=plt.gca()
#axes.add_artist(matplotlib.patches.Circle((xF0, 0), 0.2, color = 'C9'))
#axes.add_artist(matplotlib.patches.Circle((xF0, 0), 0.2, color = 'C1'))
#axes.axis('equal')
#plt.xticks(fontsize=20)
#plt.yticks(fontsize=20)
#legend(fontsize=18,loc='upper right')
#plt.grid()
#plt.xlim(-10,10)
#
## Frottement solide
#plt.subplot(1,2,2)
#title('Frottement solide  ' + r'$\ddot{x} + \omega_0^2 x = \varepsilon \omega_0^2 a$',fontsize=18)
#for i in range(len(xS0)) :
#    plot(XS[:,i], VS[:,i]/wS0, label=r'$x_0=${}'.format(round(xS0[i],2)))
#axes=plt.gca()
#plt.fill_between([-a,a],-12,12,alpha=0.2,color='C2')
#axes.add_artist(matplotlib.patches.Circle((xS0[0], 0), 0.2, color = 'C0'))
#axes.add_artist(matplotlib.patches.Circle((xS0[1], 0), 0.2, color = 'C1'))
#plt.xticks(fontsize=20)
#plt.yticks(fontsize=20)
#xlabel(r'$x$', fontsize=20)
#ylabel(r'$\frac{\dot{x}}{\omega_0}$', fontsize=20, rotation=0)
#legend(fontsize=18)
#plt.axis((-10,10,-10,10))
#plt.grid()
##plt.savefig('LP1_amorti_phase.png',transparent=True,dpi=100)
#plt.show()
