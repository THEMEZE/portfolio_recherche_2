# -*- coding: utf-8 -*-
"""
Auteur : ENS de Lyon promotion de 2017-2018

Adapté du code de Frédéric Legrand : http://www.f-legrand.fr/scidoc/docimg/sciphys/elecmag/paquet/paquet.html

License Creative Commons 3.0 CC-BY-NC-SA

Ce programme commence par définir un paquet d'onde comme la somme de fonctions sinusoïdales.
Il permet de visualiser l'effet de différentes relations de dispersion sur la propagation de ces paquets d'onde.
Les différentes relations de dispersion utilisées sont :
    - vide : k = w/c
    - milieu à coupure (plasma) : k = sqrt(w^2-w_c^2)/c
    - milieu transparent (indice optique) : k = (w/c)*(1+B*w^2)
    - onde d'une particule non relativiste libre k = sqrt(2*m*w/h_barre)
    
Le programme prend c = 1, m = 1, h_barre = 1. Les valeurs prises sont adimmensionnées.

Le programme permet de tracer : 
    - le suivi d'un paquet d'onde pour observer son glissement de phase et son étalement
    ATTENTION : si la simulation dure trop longtemps on verra les interférences entre le paquet d'onde suivi et les paquets voisins
    - la propagation de plusieurs paquets d'onde dans le milieu dispersif


Les paramètres se changent à partir de la ligne 127.


"""



import numpy
import math
from scipy.signal import get_window
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Onde:
    def __init__(self,suivi=True,dispersion='vide',coupure=0.0,coeff=1.0):
        """
            : param suivi : suivi du paquet d'onde a la vitesse de groupe
            : param dispersion : relation de dispersion
            : param coupure : frequence de coupure pour la relation de dispersion 'coupure'
            : param coeff : coefficient pour la relation de dipsersion 'optique'
        """
        self.freq = [1.0,3.0,5.0]
        self.amp = [1.0,0.5,0.2]
        self.phase = [0.0,0.0,0.0]
        self.nf = len(self.freq)
        if suivi:
            self.suivi = 1.0
        else:
            self.suivi = 0.0
        self.coupure = coupure
        self.coeff = coeff
        self.wc2 = (2*math.pi*coupure)**2
        self.a = 1.0
        
        if dispersion=='vide':
            self.k = self.k_vide
            self.vg = self.vg_vide
            
        elif dispersion=='coupure':
            self.k = self.k_coupure
            self.vg = self.vg_coupure
            
        elif dispersion=='optique':
            self.k = self.k_optique
            self.vg = self.vg_optique
            
        elif dispersion=='debroglie':
            self.k = self.k_debroglie
            self.vg = self.vg_debroglie
            
    def k_vide(self,w):
        return w
    def vg_vide(self,w):
        return 1.0
    
    def k_coupure(self,w):
        return math.sqrt(w*w-self.wc2)
    def vg_coupure(self,w):
        return math.sqrt(1-self.wc2/(w*w))
        
    def k_optique(self,w):
        return w*(1.0+self.coeff*w*w)
    def vg_optique(self,w):
        return 1.0/(1.0+3*self.coeff*w*w)
        
    def k_debroglie(self,w):
        return math.sqrt(w)
    def vg_debroglie(self,w):
        return 2.0*math.sqrt(w)
            
    def paquet(self,f,P,window="hamming"):
        """
            Creation d'un paquet d'onde
            : param f : frequence centrale
            : param P : 2P+1 = nombre de frequences
            : param window : fenetrage
        """
        M = int(2*P+1)
        self.a = 2*math.pi*f/self.k(2*math.pi*f)
        self.freq = numpy.zeros(M)
        self.amp = numpy.zeros(M)
        self.phase = numpy.zeros(M)
        self.nf = M
        self.vgroupe = self.vg(2*math.pi*f)/self.a
        for n in range(M):
            self.freq[n] = f-P+n
            self.amp[n] = 1.0
            self.phase[n] = 0.0
        self.amp = get_window(window,M)
            
    def echantillons(self,xmin,xmax,t,N):
        """
            calcul de N echantillons de l'onde reelle sur l'intervalle [xmin,xmax] a l'instant t
        """
        x = numpy.linspace(xmin,xmax,N)
        y = numpy.zeros(x.size)
        for i in range(self.nf):
            w = 2*math.pi*self.freq[i]            
            k = self.k(w)*self.a
            phi = k*x+(k*self.vgroupe*self.suivi-w)*t+self.phase[i]
            y += self.amp[i]*numpy.cos(phi)
        return (x,y)
            
    def echantillons_proba(self,xmin,xmax,t,N):
        """
            calcul de N echantillons de la densite de probabilite sur l'intervalle [xmin,xmax] a l'instant t
        """
        x = numpy.linspace(xmin,xmax,N)
        yr = numpy.zeros(x.size)
        yi = numpy.zeros(x.size)
        for i in range(self.nf):
            w = 2*math.pi*self.freq[i]            
            k = self.k(w)*self.a
            phi = k*x+(k*self.vgroupe*self.suivi-w)*t+self.phase[i]
            yr += self.amp[i]*numpy.cos(phi)
            yi += self.amp[i]*numpy.sin(phi)
        return (x,numpy.absolute(yr+1j*yi))



########################################################################################################################################
#######################################                                                    #############################################
#######################################             DEFINITION DES PARAMETRES              #############################################
#######################################                                                    #############################################
########################################################################################################################################

#choix de la frequence centrale du paquet d'onde

frequence=100


#choix de la relation de dispersion :
#  'vide' : propagation d'une onde électromagnétique dans le vide
#  'coupure' : relation de dispersion de type Klein-Gordon, choix de la fréquence de coupure avec le paramètre f_c
#  'optique' : relation de dispersion de Cauchy (dispersion dans un diélectrique, (par exemple le verre)), choix du coefficient B de n^2 = A + B/(lambda^2)
#  'debroglie' : relation de dispersion de l'équation de Schrödinger pour une propagation dans le vide (une vitesse de simulation de 0.4)

disp="coupure"
f_c=40
coefficient=0.1


#choix de la vitesse de simulation (par défaut 1.0)

vitesse = 1.0


#choix du tracé de :
#    False => l'amplitude de la fonction d'onde/du champ électrique
#    True => la densité de probabilité/de l'amplitude du vecteur de Poynting

intensite = False


########################################################################################################################################
#######################################                                                    #############################################
#######################################        Tracé des animations de dispersion          #############################################
#######################################                                                    #############################################
########################################################################################################################################

onde = Onde(suivi=True,dispersion=disp,coupure=f_c,coeff=coefficient*10**(-6))
onde2 = Onde(suivi=False,dispersion=disp,coupure=f_c,coeff=coefficient*10**(-6))


onde.paquet(frequence,20,window='hamming') 
onde2.paquet(frequence,20,window='hamming') 


temps = 0.0
dt = 0.005*vitesse
N = 5000
xmin = -0.35
xmax = 0.35

xmin2 = 0.
xmax2 = 4.0


if not intensite :

    (x,y) = onde.echantillons(xmin,xmax,temps,N)
    (x2,y2) = onde2.echantillons(xmin2,xmax2,temps,N)
    
    fig, ((ax1, ax2)) = plt.subplots(2, 1)
    line, = ax1.plot(x,y)
    ax1.grid()
    ax1.set_xlabel("Distance au centre du paquet d'onde (1)",fontsize=18)
    ax1.set_ylabel("Amplitude (1)",fontsize=18)
    
    line2, = ax2.plot(x2,y2)
    ax2.grid()
    ax2.set_xlabel("Distance dans le milieu dispersif (1)",fontsize=18)
    ax2.set_ylabel("Amplitude (1)",fontsize=18)
    
    
    def animate(i):
        global temps,xmin,xmax,N
        temps += dt
        (x,y) = onde.echantillons(xmin,xmax,temps,N)
        line.set_xdata(x)
        line.set_ydata(y)
        return line,
    
    def animate2(i):
        global temps,xmin,xmax,N
        temps += dt
        (x2,y2) = onde2.echantillons(xmin2,xmax2,temps,N)
        line2.set_xdata(x2)
        line2.set_ydata(y2)
        return line,line2
    
    ani = animation.FuncAnimation(fig,animate,1000,interval=40),animation.FuncAnimation(fig,animate2,1000,interval=40)
    
else :

    (x,y) = onde.echantillons_proba(xmin,xmax,temps,N)
    (x2,y2) = onde2.echantillons_proba(xmin2,xmax2,temps,N)
    
    fig, ((ax1, ax2)) = plt.subplots(2, 1)
    line, = ax1.plot(x,y)
    ax1.grid()
    ax1.set_xlabel("Distance au centre du paquet d'onde (1)",fontsize=18)
    ax1.set_ylabel("Amplitude (1)",fontsize=18)
    
    line2, = ax2.plot(x2,y2)
    ax2.grid()
    ax2.set_xlabel("Distance dans le milieu dispersif (1)",fontsize=18)
    ax2.set_ylabel("Amplitude (1)",fontsize=18)
    
    
    def animate(i):
        global temps,xmin,xmax,N
        temps += dt
        (x,y) = onde.echantillons_proba(xmin,xmax,temps,N)
        line.set_xdata(x)
        line.set_ydata(y)
        return line,
    
    def animate2(i):
        global temps,xmin,xmax,N
        temps += dt
        (x2,y2) = onde2.echantillons_proba(xmin2,xmax2,temps,N)
        line2.set_xdata(x2)
        line2.set_ydata(y2)
        return line,line2
    
    ani = animation.FuncAnimation(fig,animate,1000,interval=40),animation.FuncAnimation(fig,animate2,1000,interval=40)

plt.show()
