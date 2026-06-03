# -*- coding: utf-8 -*-
"""
Created on Sun May 21 14:39:50 2017

@author: ENS de Lyon

Objectif : On part d'un signal comportant du bruit ou tout simplement des fréquences non désirées. 
On regarde le spectre du signal et on applique un filtre passe bas pour supprimer les fréquences non voulues.
On calcule alors le signal théorique qu'on devrait obtenir après le filtre pour montrer qu'on a bien diminué
les hautes fréquences qui nous gênaient. Le signal est un cosinus amorti et le bruit aussi dont on controle la
 fréquence et facteur de qualité

Entrées: 
        -T = temps du signal (le prendre grand pour avoir une FFT résolu) en seconde
        -N = nombre de points dans le signal 
        -f1 = basse fréquence que l'on souhaite garder en hertz
        -f2 = haute fréquence que l'on souhaite supprimer en hertz
        -Q1 = facteur de qualité de la basse fréquence
        -Q2 = facteur de qualité de la haute fréquence
        -fc = fréquence de coupure du filtre passe bas en hertz

Sortie : On obtient une figure contenant 5 graphes : en haut à gauche le signal et en haut à droite le signal
 filtré, en bas à gauche la FFT du signal et en bas à droite la FFT du signal filtré, au milieu en bas la 
 fonction de transfert du filtre passe bas

"""

import numpy as np
import matplotlib.pyplot as plt

#entrées : 
T=10 # en s
N=100000 
f1=10#en Hz
f2=150# en Hz
fc = 10 # en Hz

t = np.linspace(0,T,N)# on crée la ligne de temps
#on crée le signal
#signal = np.exp(-np.pi*f1/Q1*t)*np.cos(2*np.pi*f1*t)+np.exp(-np.pi*f2/Q2*t)*np.cos(2*np.pi*f2*t)
signal = np.cos(2*np.pi*f1*t)+np.cos(2*np.pi*f2*t)

#on calcule la FFT du signal et les fréquences
TF = np.fft.fftshift(np.fft.fft(signal))
fr= np.fft.fftshift(np.fft.fftfreq(N,T/N))

plt.figure()
plt.clf()
# on trace le signal
plt.subplot(2,2,2)
plt.plot(t,signal)
plt.xlim([0,0.5]) # le signal pour les paramètres initiaux est compris entre 0 et 0.1 seconde
plt.xlabel('Temps (s)')
plt.ylabel('Signal')
plt.title('Signal')
# on trace la FFT du signal
#plt.subplot(2,2,1)
#plt.plot(fr,np.abs(TF))
#plt.xlim([0,1100]) # pour les paramètres initiaux, les fréquences intéressantes sont inférieure à 1100 Hz
#plt.xlabel('Fréquence (Hz)')
#plt.ylabel('TF du signal')
#plt.title('TF du Signal')


# on trace la fonction de transfert du filte
#plt.subplot(2,2,3)
H = 1/(1+np.complex(0,1)*fr/fc) # Calcule de la fonction de transfert pour un filtre PB d'ordre 1
#plt.loglog(fr,np.abs(H))
#plt.xlim([0,1100]) # on garde le même affichage que la FFT du signal
#plt.xlabel('Fréquence (Hz)')
#plt.ylabel('Fonction de transfert du filtre')
#plt.title('Filtre passe bas de fréquence de coupure {}Hz'.format(fc))

# On trace la FFT du signal filtré
#plt.subplot(2,2,1)
TFfiltre= [TF[i]*H[i] for i in range(len(fr))]# on calcule la FFT du signal filtré en multipliant la FFT du signal par la fonction de transfert
#plt.plot(fr,np.abs(TFfiltre))
#plt.xlim([0,1100])# on garde le même affichage pour rester logique
#plt.xlabel('Fréquence (Hz)')
#plt.ylabel('TF du signal filtré')
#plt.title('TF de Signal filtré')

plt.subplot(1,2,1)
plt.semilogx(fr,np.abs(TF))
plt.semilogx(fr,np.abs(TFfiltre))
ax2 = plt.gca().twinx()
ax2.loglog(fr,np.abs(H), color = 'red')
plt.xlim([0,1100])

#on trace le signal filtré
plt.subplot(2,2,4)
signalfiltre = np.real(np.fft.ifft(np.fft.fftshift(TFfiltre)))#on calcule le signal filtré à partir de sa FFT
plt.plot(t,signalfiltre)
plt.xlim([0,0.5])# on garde le même affichage que pour le signal
plt.xlabel('Temps (s)')
plt.ylabel('Signal filtré')
plt.title('Signal filtré')


plt.show()