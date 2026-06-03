# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

plt.close("all")

# Diffraction par une fente

theta=np.linspace(-np.pi/1000,np.pi/1000,1000)
a=0.24e-3
D=1
lambda0=633.e-9
e=2e-3  #Distance iter-fentes

I_fente=(np.sinc(np.pi*a*np.sin(theta)/lambda0))**2

I_young=(np.sinc(np.pi*a*np.sin(theta)/lambda0))**2*(np.cos(np.pi*e*np.sin(theta)/lambda0))**2


N0=20
def I_reseau(theta,N):
    return (np.sinc(np.pi*a*np.sin(theta)/lambda0))**2*((np.sin(int(N)*np.pi*e*np.sin(theta)/lambda0)/np.sin(np.pi*e*np.sin(theta)/lambda0)))**2/(int(N)**2)

fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
plt.plot(theta,I_fente,label="Diffraction par une fente")
plt.plot(theta,I_young,label="Fentes d'Young")
#plt.plot(theta,I_reseau,label="Diffraction par %.f fentes" %(N0))
l, = plt.plot(theta,I_reseau(theta,N0), lw=2, label="Diffraction par %.f fentes" %(N0))

plt.xlabel('Distance d (m)')
plt.ylabel(u"I/I_0")
plt.legend(loc=2)

axcolor = 'lightgoldenrodyellow'
axN = plt.axes([0.25, 0.12, 0.65, 0.03])
ioN = Slider(axN, 'N', 0, 600,valfmt='%0.0f',valinit=N0) # définition de l'intervalle des valeurs de a/epsilon

def update(val):
    N = ioN.val
    l.set_ydata(I_reseau(theta,N))
    fig.canvas.draw_idle()
    
ioN.on_changed(update)

## Definition d'un bouton reset
resetax = plt.axes([0.03, 0.07, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')

def reset(event):
    ioN.reset()
button.on_clicked(reset)

plt.show()
plt.savefig("python_diffraction_fentes.png",dpi=300)