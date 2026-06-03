#Nom du programme : LoiDePlanck
 
#Auteurs : François Lévrier, Emmanuel Baudin, Arnaud Raoux et la prépa agreg de Montrouge
#Adresse : Departement de physique de l'Ecole Normale Superieure
#       24 rue Lhomond
#       75005 Paris
#Contact : arnaud.raoux@ens.fr
#
#Année de création : 2016 
#Version : 1.20
 
#Liste des modifications
#v 1.00 : 2016-03-01 Première version complète
#v 1.10 : 2016-05-02 Mise à jour de la mise en page - baudin@lpa.ens.fr
#v 1.20 : 2019-01-09 Remplacement de axisbg dépréciée par facecolor
 
#LICENCE
#Cette oeuvre, création, site ou texte est sous licence Creative Commons Attribution -Pas d'Utilisation Commerciale 4.0 International. Pour accéder à une copie de cette licence,merci de vous rendre à l'adresse suivante http://creativecommons.org/licenses/by-nc/4.0/ ou envoyez un courrier à Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.

#Description : 
#Ce programme représente la loi de Wien du corps noir en fonction de la fréquence du rayonnement
#électromagnétique. Il est possible de modifier la température du corps noir pour observer 
#ses effets. 
#Les lois de Rayleigh-Jeans et de Planck ont aussi été implémentées pour comparaison.
 
#import des bibliothèques python
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons
 
#Definition des constantes physiques
def constant(symbol):
    if (symbol=="c"): return(299792.458)        # Speed of light, in km/s
    elif (symbol=="h"): return(6.6260693e-34)   # Planck constant in J.s
    elif (symbol=="k"): return(1.3806505e-23)   # Boltzmann constant in J/K
    elif (symbol=="e"): return(1.60217653e-19)  # Elementary electrical charge
    elif (symbol=="me"): return(9.1093826e-31)  # Electron mass in kg
    elif (symbol=="mp"): return(1.67262171e-27) # Proton mass in kg
    elif (symbol=="G"): return(6.6742e-11)      # Gravitational constant
    elif (symbol=="Na"): return(6.0221415e23)   # Avogadro's number
    elif (symbol=="mu0"): return(12.566370614e-7)       # Magnetic permeability
    elif (symbol=="epsilon0"): return(8.854187817e-12)  # Electric permittivity
    elif (symbol=="amu"): return(1.66053886e-27)        # Atomic mass unit
    elif (symbol=="nu0_HI"): return(1420.405751)        # Rest frequency of the HI line, in MHz
    elif (symbol=="nu0_CO"): return(115271.203)         # Rest frequency of the CO(1->0) line, in MHz
    elif (symbol=="H0"): return(72)             # Hubble constant, in km/s/Mpc
    else:
        print("Unknown symbol")
        return(0)
 
def Bnu(T,nu): # Fonction de Planck B_nu avec T en K et nu en Hz
    return((2.0*constant("h")*np.power(nu,3.0))/(math.pow(constant("c"),2.0)*1e6*(np.exp((constant("h")*nu)/(constant("k")*T))-1.0)))
 
def Bnu_RJ(T,nu): # Fonction de Planck B_nu dans l'approximation de Rayleigh-Jeans avec T en K en nu en Hz
    return((2.0*constant("k")*T*np.power(nu,2.0))/(math.pow(constant("c"),2.0)*1e6))
 
def Bnu_Wien(T,nu): # Fonction de Planck B_nu dans l'approximation de Wien avec T en K en nu en Hz
    return(((2.0*constant("h")*np.power(nu,3.0))/(math.pow(constant("c"),2.0)*1e6))*(np.exp(-(constant("h")*nu)/(constant("k")*T))))
 
def Blam(T,lam): # Fonction de Planck B_lambda avec T en K en lam (longueur d'onde) en m
    return(((2.0*constant("h")*math.pow(constant("c")*1e3,2.0))/np.power(lam,5.0))*(1.0/(np.exp((constant("h")*constant("c")*1e3)/(constant("k")*T*lam))-1.0)))
 
def Blam_RJ(T,lam): # Fonction de Planck B_lambda dans l'approximation de Rayleigh-Jeans avec T en K en lam (longueur d'onde) en m
    return((2.0*constant("c")*1e3*constant("k")*T)/np.power(lam,4.0))
 
def Blam_Wien(T,lam): # Fonction de Planck B_lambda dans l'approximation de Wien avec T en K en lam (longueur d'onde) en m
    return(((2.0*constant("h")*math.pow(constant("c")*1e3,2.0))/np.power(lam,5.0))*np.exp(-(constant("h")*constant("c")*1e3)/(constant("k")*T*lam)))
 
# Creation de la figure
fig, ax = plt.subplots(figsize=(15,10))
plt.subplots_adjust(left=0.25, bottom=0.25)
 
# Nombre de points
npoints=10000
 
# Limites
nu_min=1e4
nu_max=2e15
T_min=0.1
T_max=10000.0
 
# Creation de l'axe des abscisses
nu = np.logspace(np.log10(nu_min),np.log10(nu_max),num=npoints)
 
# Parametres de la fonction, avec des valeurs par defaut
T0 = 5800 # Temperature en K
 
 
#Ajout des lignes de reperes
plt.plot(7E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0.875,0,1))     # Violet
plt.plot(6.7E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0.357,0,1))   # Indigo
plt.plot(6.0E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0,0,1))   # Bleu
plt.plot(5.8E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0,0.851,1))   # Cyan
plt.plot(5.3E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0.243,1,0))   # Vert
plt.plot(5.1E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0.914,1,0))   # Jaune
plt.plot(4.8E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(1,0.475,0))   # Orange
plt.plot(4.05E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(1,0,0))      # Rouge

# Creation de la fonction à tracer 
bnu=Bnu(T0,nu)
bnuRJ=Bnu_RJ(T0,nu)
bnuW=Bnu_Wien(T0,nu)
 
#Courbe expériementale (ici calculée à partir de Planck)
E, = plt.plot(nu,bnu, lw=2, color='black',visible=True)
# Creation de la trace de la fonction de Planck en fonction de nu. C'est un objet qui est sauvegarde dans 'l'
l, = plt.plot(nu,bnu, lw=2, color='blue',visible=False)
# Idem pour la fonction de Wien
lW, = plt.plot(nu,bnuW, lw=2,color='grey', visible=False)
# Idem pour la fonction de Rayleigh-Jeans
lRJ, = plt.plot(nu,bnuRJ, lw=2, color='grey',visible=False)
 
#Titre de la figure
plt.title('Lois caractéristiques du rayonnement du corps noir')
 
#Commentaires affichés
plt.plot(7E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0.875,0,1))     # Violet
plt.plot(6.7E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0.357,0,1))   # Indigo
plt.plot(6.0E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0,0,1))   # Bleu
plt.plot(5.8E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0,0.851,1))   # Cyan
plt.plot(5.3E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0.243,1,0))   # Vert
plt.plot(5.1E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(0.914,1,0))   # Jaune
plt.plot(4.8E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(1,0.475,0))   # Orange
plt.plot(4.05E14+np.zeros(100),np.linspace(0,10,100),'k', lw=2, color=(1,0,0))      # Rouge

plt.text(-7e14, 5.4e-8, "Violet :  400 nm", color=(0.875,0,1))
plt.text(-7e14, 5e-8, "Indigo :  430 nm", color=(0.357,0,1))
plt.text(-7e14, 4.6e-8, "Bleu : 470 nm", color=(0,0,1))
plt.text(-7e14, 4.2e-8, "Cyan : 500 nm", color=(0,0.851,1))
plt.text(-7e14, 3.8e-8, "Vert :  540 nm", color=(0.243,1,0))
plt.text(-7e14, 3.4e-8, "Jaune : 590 nm", color=(0.914,1,0))
plt.text(-7e14, 3e-8, "Orange : 620 nm", color=(1,0.475,0))
plt.text(-7e14, 2.6e-8, "Rouge :  640 nm", color=(1,0,0))

# Specification des limites des axes (xmin,xmax,ymin,ymax)
plt.ylim(0.0,3*np.max(bnu))
plt.xlim(nu_min,nu_max)
plt.xlabel(r"$\nu$ [$\mathrm{Hz}$]",fontsize=20)
plt.ylabel(r"$B_\nu$ [$\mathrm{W.m^{-2}.Hz^{-1}.sr^{-1}}$]"+"\n",fontsize=20)
for tick in ax.xaxis.get_major_ticks():tick.label.set_fontsize(15) 
for tick in ax.yaxis.get_major_ticks():tick.label.set_fontsize(15) 
#plt.legend(["Planck","Wien","Rayleigh-Jeans"])
 
# Creation des barres de modification de la temperature
axcolor = 'lightgoldenrodyellow'
axT = plt.axes([0.1, 0.11, 0.65, 0.03], facecolor=axcolor)
sT = Slider(axT, 'Temperature [K]', T_min, T_max, valinit=T0) # Remarquer la valeur initiale T0
 
 
# Fonction de mise a jour du graphique
def update(val):
    T = sT.val # On recupere la valeur de la barre sT comme temperature
    E.set_ydata(Bnu(T,nu)) # On met a jour l'objet 'E' avec ces nouvelles valeurs 
    l.set_ydata(Bnu(T,nu)) # On met a jour l'objet 'l' avec ces nouvelles valeurs 
    lW.set_ydata(Bnu_Wien(T,nu)) # On met a jour l'objet 'lW' avec ces nouvelles valeurs 
    lRJ.set_ydata(Bnu_RJ(T,nu)) # On met a jour l'objet 'lRJ' avec ces nouvelles valeurs 
    fig.canvas.draw_idle() # On provoque la mise a jour du graphique, qui n'est pas automatique par defaut
sT.on_changed(update) # lorsque la barre sT est modifiee, on applique la fonction update
 
# Creation du bouton de "reset"
resetax = plt.axes([0.83,0.11, 0.1, 0.04]) 
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')
 
# Definition de la fonction de "reset" (valeurs par defaut)
def reset(event):
    sT.reset() # La methode .reset() appliquee a la barre sfreq lui redonne sa valeur valinit, soit T0
button.on_clicked(reset) # Lorsqu'on clique sur "reset", on applique la fonction reset definie au dessus
 
# Creation du menu de selection des traces a afficher
cax = plt.axes([0.015, 0.63, 0.12, 0.15], facecolor=axcolor)
check = CheckButtons(cax, ('Planck', 'Rayleigh-Jeans', 'Wien'), (False, False, False))
 
# Definition de la fonction qui passe un affichage de visible a invisible
def chooseplot(label):
    if label == 'Planck': l.set_visible(not l.get_visible()) # Si on clique sur le bouton "Planck", la trace 'll passe visible si elle ne l'etait pas, et vice versa
    elif label == 'Wien': lW.set_visible(not lW.get_visible()) # Si on clique sur le bouton "Wien", la trace 'lW' passe visible si elle ne l'etait pas, et vice versa
    elif label == 'Rayleigh-Jeans': lRJ.set_visible(not lRJ.get_visible()) # Si on clique sur le bouton "Rayleigh-Jeans", la trace 'lRJ' passe visible si elle ne l'etait pas, et vice versa
    fig.canvas.draw_idle() # On provoque la mise a jour du graphique, qui n'est pas automatique par defaut
check.on_clicked(chooseplot) # Lorsqu'on coche un de ces boutons, on applique la fonction chooseplot
 
plt.show() # On provoque l'affichage a l'ecran