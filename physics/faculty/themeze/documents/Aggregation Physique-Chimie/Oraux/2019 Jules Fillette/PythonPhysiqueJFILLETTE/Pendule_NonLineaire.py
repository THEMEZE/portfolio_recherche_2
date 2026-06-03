# coding: utf-8

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate
from scipy.fftpack import fft

# Ce script trace l'évolution temporelle, le portrait de phase et la FFT d'un oscillateur 1D.
# Auteurs: Aurélien Pascal, Alexandre Morlet

# Discrétisation du temps------------------------

nombre_pas = 20000
t_final = 300
t = np.linspace(0,t_final,num=nombre_pas)

#Système d'équations à résoudre-----------------

def sys(y,t):
    """
    La fonction sys renvoie une liste contenant
    la dérivée de x et celle de x'
    Pour l'oscillateur harmonique le retour est donc [x',-x]
    """
    x, xprime = y

    #changer la ligne suivante pour un oscillateur different

    #return [xprime, -x] #oscillateur harmonique
    #return [xprime, -x-0.1*xprime] #oscillateur harmonique amorti
    return [xprime, -np.sin(x)] #pendule simple non amorti
    #return [xprime, -np.sin(x)-0.1*xprime] #pendule simple amorti
    #return [xprime, (0.2-x**2)*xprime -x] #oscillateur de Van der Pol

    omega = 2*np.pi #pulsation d'excitation
    omega0 = 1.5*omega #pulsation propre
    beta = omega0/4 #coefficient d'amortissement
    excitation = 1.09
    #return [xprime, -2*(beta)*xprime -(omega0**2)*np.sin(x) + excitation*(omega0**2)*np.cos(omega*t)] #Pendule amorti et forcé



#Liste de conditions initiales-------------------

"""
Les conditions initiales sont sous la forme [x(0),x'(0)]
y0 est un tableau contenant autant de conditions
initiales qu'il y a de portraits de phase à tracer.
Exemple : pour 3 courbes, y0 = [[10,0],[10,2],[8,5]]
"""

# Cas 'normal'
y0 = [[-np.pi/4.0,0], [-np.pi/2,0.0],[-np.pi/2,1.0]]
# Van der Pol
#y0 = [[0.001,0], [np.pi/2, 0.7]]

#Integration par le solveur odeint---------------------------------

#solution contient une liste de matrices, une pour chaque condition initiale y0
#chaque matrice contient (x,x'); le tableau t contient le temps

solution = []
for ci in y0:
    solution.append(scipy.integrate.odeint(sys,ci,t))

#Affichage---------------------------------------------
f, ax = plt.subplots(1,3) # ax[n] est la figure n

## Tracé de la solution en temps
for sol in solution:
    ax[0].plot(t[0000:2000],sol[0000:2000,0])
ax[0].set_xlabel("Temps")
ax[0].set_ylabel("Position")
ax[0].set_title('Evolution temporelle du systeme')


## Tracé du portrait de phase
for sol in solution: # tracé du portrait de phase
    ax[1].plot(sol[:,0],sol[:,1])
ax[1].set_xlabel("Position")
ax[1].set_ylabel("Vitesse")
ax[1].axis('equal')
ax[1].grid()
ax[1].set_title("Portrait de phase")


## Tracé de la FFT

xf = np.linspace(0.0, nombre_pas/(2.*t_final), nombre_pas//2) # abscisse pour la FFT
for sol in solution:
    yf=fft(sol[:,0])
    ax[2].plot(xf,2.0/nombre_pas * np.abs(yf[0:nombre_pas//2]))

ax[2].set_xlim((0,0.5))
ax[2].set_xlabel('Frequence')
ax[2].set_title('Spectre')

plt.show()
