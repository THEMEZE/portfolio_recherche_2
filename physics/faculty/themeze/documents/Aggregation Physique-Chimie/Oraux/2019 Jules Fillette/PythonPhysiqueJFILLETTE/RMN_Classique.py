#-----------------------------------------------------------------------
# Résonnance magnétique nucléaire, interprétation classique
#-----------------------------------------------------------------------
# Renseignements/bugs : Guillaume Dewaele <agreg(at)sci-phy.org>
#-----------------------------------------------------------------------

# Paramètres modifiables

# Coefficient gamma

gamma = 2.675e8 # rad/(s.T)

# Champs magnétiques appliqués

B0 = 1.0 # Tesla
B1 = 0.1 # Tesla

# Bande de fréquence étudiée

Fmin, Fmax = 2e7, 7e7 # Hz

# Durée d'observation

Tmax = 2/Fmin

#-----------------------------------------------------------------------

# Bibliothèques utilisées

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.widgets as mwg
from mpl_toolkits.mplot3d import Axes3D
import scipy.linalg as lin

#-----------------------------------------------------------------------

def Angle(w) :
    return np.arctan2(w/gamma-B0, B1)

def Beff(w) :
    return np.sqrt(((w/gamma)-B0)**2+B1**2)

def VBeff(w) :
    return np.array([B1, 0, (w/gamma)-B0])

def M(B, t) :
    axis = B
    theta = t
    axis = np.asarray(axis)
    axis = axis/np.sqrt(np.dot(axis, axis))
    a = np.cos(theta/2.0)
    b, c, d = -axis*np.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

def Turn(w, t, vbeff, vrot) :
    return M(np.array([0, 0, 1]), w*t).dot(M(vbeff, gamma*t).dot(np.array([0, 0, 1]) ))

def Vect(T, w) :
    vbeff = VBeff(w)
    res = []
    for t in T :
        res.append(Turn(w, t, vbeff, 0))
    
    return np.array(res)

#-----------------------------------------------------------------------

# Détection utilisation hors Pyzo

if '__iep__' not in globals() :
    matplotlib.interactive(False)

# Affichage des résultats

T = np.linspace(0, Tmax, 400)

F = np.linspace(Fmin, Fmax, 400)
W = 2*np.pi*F
    
w = 2*np.pi*42e6
w = gamma/2/np.pi

vect = Vect(T, w)
axTmp = plt.axes([ 0.1, 0.55, 0.4, 0.2 ])
crv, = axTmp.plot(T*1e9, vect[:,2], lw=2)
axTmp.set_ylim(-1, 1)
axTmp.set_title("Composante verticale du moment magnétique")
axTmp.set_xlabel("Temps (ns)")

axTmp = plt.axes([ 0.55, 0.4, 0.35, 0.55 ], projection='3d')
crv3d, = axTmp.plot(*(vect.T), lw=2)
axTmp.set_xlim(-1, 1)
axTmp.set_ylim(-1, 1)
axTmp.set_zlim(-1, 1)
axTmp.set_title("Evolution du moment magnétique")

axTmp = plt.axes([ 0.15, 0.15, 0.7, 0.2 ])
axTmp.fill_between(F/1e6, -np.cos(2*Angle(W)), 1.0+0*F, color='g', alpha=0.3)
axTmp.plot(F/1e6, -np.cos(2*np.arctan2(W/gamma-B0, B1)), color='g', lw=2)
crvmq, = plt.plot([w/2/np.pi/1e6]*2, [-np.cos(2*np.arctan2(w/gamma-B0, B1)), 1], 'g', lw=2)
axTmp.set_xlim(Fmin/1e6, Fmax/1e6)
axTmp.set_title("Amplitude des oscillations verticales")
axTmp.set_xlabel("Fréquence (MHz)")

# Slider

axTmp = plt.axes([0.15, 0.04, 0.7, 0.04])
slider = mwg.Slider(axTmp, '', valmin=Fmin/1e6, valmax=Fmax/1e6, valinit=gamma/(2.0*np.pi)/1e6, color='g', alpha=0.4)

def Update(f) :
    f *= 1e6
    vect = Vect(T, 2*np.pi*f)
    crv.set_data(T*1e9, vect[:,2])
    crvmq.set_data([f/1e6]*2, [-np.cos(2*np.arctan2(f*2*np.pi/gamma-B0, B1)), 1])
    crv3d.set_data(*(vect[:,0:2].T))
    crv3d.set_3d_properties(vect[:,2])
    
slider.on_changed(Update)

slider.set_val(0.9*gamma/(2.0*np.pi)/1e6)

# Détection utilisation hors Pyzo

if '__iep__' not in globals() :
    plt.show()
