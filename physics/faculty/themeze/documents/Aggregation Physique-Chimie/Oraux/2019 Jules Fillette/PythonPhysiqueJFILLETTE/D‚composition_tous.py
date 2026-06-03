#-----------------------------------------------------------------------
# Analyse spectrale d'un signal quelconque
#
# Utiliser la barre inférieure pour sélectionner le nombre d'harmoniques
#-----------------------------------------------------------------------
# Renseignements/bugs : Guillaume Dewaele <agreg(at)sci-phy.org>
#-----------------------------------------------------------------------

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons


# Paramètres modifiables

# Nombre d'harmoniques considérées

max_harm = 40

# Bibliothèque de fonctions

@np.vectorize
def triangle(t) :
    return -0.25+t if t<0.5 else 0.75-t

@np.vectorize
def scie(t) :
    return -0.25+t if t<0.75 else t-1.25

@np.vectorize
def creneau(t) :
    return -0.5 + (1.0 if 0.1<=t<0.6 else 0.0)

@np.vectorize
def bruitblanc(t) :
    np.random.seed(int(t*1000000))
    return np.random.random()-0.5

# Choix de la fonction

foo = triangle

#-----------------------------------------------------------------------

# Bibliothèques utilisées

import numpy as np
import numpy.fft as fft
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.widgets as mwg

#-----------------------------------------------------------------------

# Détection utilisation hors Pyzo

if '__iep__' not in globals() :
    matplotlib.interactive(False)

# Calcul du spectre

N = 8192
T = np.linspace(0.0, 1.0, N)
Y = foo(T)
Yp = fft.fft(Y)

# Tracés

Tr = np.linspace(0.0, 2.0, 2*N)
Ampl = 20*np.log10(np.abs(Yp[:max_harm]))

# Signal

axTmp = plt.axes([0.11, 0.6, 0.78, 0.32])
axTmp.plot(Tr, np.concatenate([Y, Y]), "k--")
partial, = axTmp.plot(Tr, np.concatenate([Y, Y]), "b")
axTmp.set_xlim([0, 2])
axTmp.set_ylim([ min(Y) - (max(Y)-min(Y))*0.3, max(Y) + (max(Y)-min(Y))*0.3 ])
axTmp.set_title("signal")
axTmp.set_ylabel("amplitude")
axTmp.set_xlabel("temps (t/T0)")

# Spectre

axTmp = plt.axes([0.11, 0.15, 0.78, 0.32])
axTmp.bar(np.arange(max_harm)-0.5, Ampl, color="white")
rects = axTmp.bar(np.arange(max_harm)-0.5, Ampl, color="blue")
axTmp.set_xlim([0, max_harm])
axTmp.set_ylim([0, np.max(Ampl)*1.1])
axTmp.set_title("spectre")
axTmp.set_ylabel("amplitude (dB)")
axTmp.set_xlabel("fréquences (f/f0)")

# Slider

axTmp = plt.axes([0.11, 0.035, 0.78, 0.035])
slider = mwg.Slider(axTmp, '', valmin=0, valmax=max_harm, valinit=max_harm)

def Update(i) :
    PartialY = np.real(fft.ifft(Yp * np.fromfunction(lambda j : j<=i, (len(Yp),))))
    partial.set_data(Tr, 2*np.concatenate([PartialY, PartialY]))
    for j, rect in enumerate(rects) :
        rect.set_height(0 if j>i else Ampl[j])

slider.on_changed(Update)

Update(max_harm)

# Détection utilisation hors Pyzo

if '__iep__' not in globals() :
    plt.show()
    