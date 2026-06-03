#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 15:05:37 2018

@author: alexandre
"""

## Importation des bibliotheques
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from numpy import pi

## Construction manuelle du signal carre et creation de la fenetre

a0=1            # Amplitude en V
T0=2            # periode effective du signal en s
f0=1/T0         # frequence du signal (inverse de la periode effective)

fig, ax = plt.subplots()
plt.subplots_adjust(left=0.2, bottom=0.2)         # dimensions du graphique

# definition de la fonction creneau
def creneau(x):
    reste = x%T0
    if (reste<T0/2):
        res = a0
    else:
        res = -a0
    return res
creneau_vec = np.vectorize(creneau)

t = np.arange(-1*T0, 2*T0, 0.001)    # temps allant de -2 s à 4s par pas de 0.01s (sur trois periodes)
plt.plot(t,creneau_vec(t),'b')

# Creation de la courbe initiale (avec la serie de Fourier à un terme)
def f0(x,N):
    S0 = 0
    for n in np.arange(0,N+1,1):                        # n va varier de 0 à N0 par pas de 1 (attention la borne max est N0+1 car il exclu la borne max
        Cn0 = (4/pi)*(np.sin((2*n+1)*2*pi*x/T0))/(2*n+1)
        S0 = S0 + Cn0
    return S0


N0=0                                                # initialisation à 1 le nombre de composantes de la serie de Fourier
l, = plt.plot(t, f0(t,N0), lw=1, color='red')         # courbe à tracer i en fonction de omega
plt.axis([-1*T0, 2*T0, -1.5*a0, 1.5*a0])                     # limite des axes (xmin,xmax,ymin,ymax)
plt.xlabel("temps (s)")                     # titre de l'axe des abscisses
plt.ylabel("Amplitude du signal (V)")                               # titre de l'axe des ordonnees
plt.title("Serie de Fourier d'un signal carre") 
plt.grid(True)                                          # quadrille le graphique


## Ajout des barres de changement de valeur des variables initiales
axcolor = 'lightgoldenrodyellow'                            # couleur des barres
axN = plt.axes([0.25, 0.02, 0.65, 0.03])    # localisation de la barre pour N
ioN = Slider(axN,"nbre d'harmoniques",0,100,valinit=N0,valfmt='%0.0f')

## Definition de la fonction qui permet de reinitialiser les valeurs initiales par celle choisie à la barre
def update(val):
    N = ioN.val                                             # prend la valeur de la barre pour N
    l.set_ydata(f0(t,N))    # ressort le nouveau profil de resonance
    fig.canvas.draw_idle()                                  # redessine la courbe
ioN.on_changed(update)                                      # affiche à côte de la barre la valeur de N


## Definition d'un bouton reset
resetax = plt.axes([0.03, 0.07, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

def reset(event):
    ioN.reset()
button.on_clicked(reset)