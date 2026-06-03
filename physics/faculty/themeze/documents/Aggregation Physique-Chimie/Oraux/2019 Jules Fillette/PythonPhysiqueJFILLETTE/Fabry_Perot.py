#Code illustrant la selectivite de l'interferometre de Fabry-Perot.
#On represente l'intensite transmise en fonction du dephasage
#pour differentes valeurs du coefficient R (0<R<1).
#Executer trace(L) dans l'interpreteur Python.
#L est une liste de taille au plus 4 qui contient les valeurs de R que l'on souhaite etudier.
#Exemple : trace([0.5,0.8,0.99])

from matplotlib import pyplot as plt
import numpy as np

X=np.linspace(0,10*np.pi,10000)
C=['b','g','r','k']
S=['-','--','-','--']

def trace(L):
    plt.figure()
    plt.title('Intensite sur l\'ecran en fonction de la phase')
    plt.xlabel('$\phi$ (rad)')
    plt.xlim([0,10*np.pi])
    plt.xticks( [0, np.pi*2, 4*np.pi, 6*np.pi, 8*np.pi,10*np.pi],
    		[r'0',r'$2\pi$',r'$4\pi$',r'$6\pi$',r'$8\pi$',r'$10\pi$'])
    plt.ylabel('$I/I_0$')
    plt.ylim([0,1])
    for i in range(len(L)):
        R=L[i]
        M=1/(1-R)**2
        Y=[1/(1+M*np.sin(x/2)**2) for x in X]
        plt.plot(X,Y,label='R='+str(R),color=C[i],ls=S[i])
    plt.legend(loc=1)
    plt.show()

trace([0.5,0.8,0.99])