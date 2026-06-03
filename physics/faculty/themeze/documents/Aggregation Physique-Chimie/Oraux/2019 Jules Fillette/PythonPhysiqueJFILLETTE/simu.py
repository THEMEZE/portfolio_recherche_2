#!/usr/bin/env python
# coding: utf-8

# In[1]:


from ipywidgets import *
import matplotlib.pyplot as plt  
import numpy as np


# In[2]:


N= 1;
d = 0.000001;
l = 632e-9;
f = 1;
a = 0.00002;
  
X = np.arange(-0.4,0.4,0.0001) ; 
S = (np.sinc(np.pi*X*d/(l*f))**2);
I = (np.sinc(np.pi*X*d/(l*f))**2)*((np.sin(N*np.pi*X*a/(l*f)))/(np.sin(np.pi*X*a/(l*f))))**2/N**2;
plt.plot(X, I,X,S)
plt.rcParams['figure.figsize'] = [30, 12]
plt.xlabel('X')  
plt.ylabel('I')    
plt.grid(True)  
plt.show()


# In[4]:


N= 2;
d = 0.000001;
l = 632e-9;
f = 1;
a = 0.00002;
  
X = np.arange(-0.4,0.4,0.0001) ; 
S = (np.sinc(np.pi*X*d/(l*f))**2);
I = (np.sinc(np.pi*X*d/(l*f))**2)*((np.sin(N*np.pi*X*a/(l*f)))/(np.sin(np.pi*X*a/(l*f))))**2/N**2;
plt.plot(X, I,X,S)
plt.rcParams['figure.figsize'] = [30, 12]
plt.xlabel('X')  
plt.ylabel('I')    
plt.grid(True)  
plt.show()


# In[ ]:




