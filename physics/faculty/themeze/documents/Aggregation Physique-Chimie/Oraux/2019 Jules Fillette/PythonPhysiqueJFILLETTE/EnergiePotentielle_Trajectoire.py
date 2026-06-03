#-----------------------------------------------------------------------
# Energie potentielle effective et trajectoires
#
# En l'état, ne fonctionne que pour des problèmes gravitationnels
#-----------------------------------------------------------------------
# Renseignements/bugs : Guillaume Dewaele <agreg(at)sci-phy.org>
#-----------------------------------------------------------------------

# Paramètres modifiables

# Energie potentielle

def Ep(r) :
    return - G*MS*m/r

# Liste des énergies considérées

ListE = [-4.39e8, -3.3e8, -2.2e8, -1.1e8, 0, 1.1e8]

# Masse du mobile (sans effet sur la trajectoire)

m = 1.0

# Moment cinétique

C = m*1.5e11*6.28*1.5e11/(365.25*86400)

# Constante gravitationnelle

G = 6.6742e-11 # SI

# Masse du Soleil

MS = 1.989e30  # kg

# r pour lequel Ueff est minimale

rfond = 1.5e11

# r minimum (pour le tracé de Ep) et maximum

rmin = 0.65e11
rmax = 1.5e12

#-----------------------------------------------------------------------

# Bibliothèques utilisées

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import scipy.integrate as itg
import scipy.optimize as opt

#-----------------------------------------------------------------------

# Energie potentielle effective

def Ueff(r) :
    return Ep(r) + C**2/(2*m*r**2)
    
def GetOrbit(C, E, rmax, Ueff, rfond) :
    assert(E > Ueff(rfond))

    @np.vectorize
    def DerR(r, theta, C, E) :
        if E<Ueff(r) :
            return 0
        d = r**2 * (2/m * (E-Ueff(r)))**0.5 / C
        return d
        
    # Calcul de la trajectoire
    
    TH1 = np.linspace(np.pi/2, np.pi, 1000)
    rini = opt.bisect(lambda r:Ueff(r)-E, rfond/100, rfond)
    
    res = itg.odeint(DerR, [ rfond ], TH1, args=(C, E))
    R1 = res[:,0]

    TH2 = np.linspace(np.pi/2, 0.0, 1000)
    rini = opt.bisect(lambda r:Ueff(r)-E, rfond/100, rfond)
    
    res = itg.odeint(DerR, [ rfond ], TH2, args=(C, E))
    R2 = res[:,0]
    
    R = np.concatenate([R2[::-1], R1])
    TH = np.concatenate([TH2[::-1], TH1])
    
    keep = 0
    while keep < len(R) and R[keep] < rmax*2 :
        keep += 1
    
    TH = TH[:keep]
    R = R[:keep]
    
    R = np.concatenate([R[::-1], R])
    TH = np.concatenate([-TH[::-1], TH])
    
    return R, TH

#-----------------------------------------------------------------------

# Détection utilisation hors Pyzo

if '__iep__' not in globals() :
    matplotlib.interactive(False)

# Affichage des résultats

fig = plt.figure()

ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)

R = np.linspace(rmin, rmax, 200)
ax1.plot(R, Ueff(R), 'k', linewidth=2)
ax2.plot([0], [0], 'ko')

for i, E in enumerate(ListE) :
    R, TH = GetOrbit(C, E, rmax * 2, Ueff, 1.5e11)
    
    ax2.plot(-R*np.cos(TH), R*np.sin(TH), 'brgymc'[i%6]+'-', linewidth=2)
    
    ax1.plot([R[0], R[len(R)//2]], [E, E], 'brgymc'[i%6]+'-', linewidth=2)
ax2.axis("equal")

ax1.set_xlim(0, rmax)
ax1.grid()
ax1.set_title("Energie potentielle effective")
ax1.set_ylabel("Energie (J)")
ax1.set_xlabel("r (m)")

ax2.axis([-0.5e12, 1.5e12, -4e1, 4e1])
ax2.grid()
ax2.set_title("Trajectoires")
ax2.set_ylabel("y (m)")
ax2.set_xlabel("x (m)")

# Détection utilisation hors Pyzo

if '__iep__' not in globals() :
    plt.show()
