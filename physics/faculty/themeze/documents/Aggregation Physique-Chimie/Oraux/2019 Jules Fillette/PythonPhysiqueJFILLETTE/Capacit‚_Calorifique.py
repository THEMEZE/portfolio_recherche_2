# -*- coding: utf-8 -*-
"""
Created on Fri May 25 20:35:17 2018

@author: User
"""
import numpy as np
import matplotlib.pyplot as plt


def Einstein(x):
    '''capacité calorifique (normalisée par 3kB) decrite par le modele d'Einstein'''
    return 1/(x*np.sinh(1/x))**2

#capacité calorifique(normalisée par 3kB) décrite par un modèle classique
#loi de Dulong et Petit
def Dulong(x):
    '''capacité calorifique(normalisée par 3kB) décrite par un modèle classique
    loi de Dulong et Petit'''
    return 1

def integration(f,a,b,n):
    '''intègre la fonction f entre a et b
    méthode des trapèzes'''
    dx=(b-a)/n
    s=(f(a)+f(b))/2
    for k in range (1,n):
        s=s+f(a+k*dx)
    return s*dx

def fonc(t):
    '''fonction intégré dans le modele de Debye'''
    return t**4*np.exp(t)/(np.exp(t)-1)**2

def Debye(x):
    '''capacité calorifique (normalisée par 3kB) decrite par le modele de Debye'''
    n=1000
    return 3*x**3*integration(fonc,1e-9,1/x,n)

x=np.linspace(1e-5,4,1000)
y1=[]
y2=[]
y3=[]
for k in range(len(x)):
    y1.append(Dulong(x[k]))
    y2.append(Einstein(x[k]))
    y3.append(Debye(x[k]))


plt.plot(x,y1,'g',label="Dulong-Petit")
plt.plot(x,y2,'b',label="Einstein")
plt.plot(x,y3,'r',label="Debye")
plt.grid()
plt.xlabel('Température réduite')
plt.ylabel('Capacité thermique /3kB' )
plt.legend()
plt.show()