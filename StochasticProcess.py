# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 14:43:45 2016

@author: CongLiu
"""

'''
. 2 Discretization schemes are considered,  Discretization = Enum('Euler', 'Milstein')
. simulation grids currently assumed equally segmented, can be further generalized 
'''

import numpy as np
import FunctionClass


class StochasticProcess1D:
    def __init__(self, x0_ = None, d_ = None):
        self.x0 = x0_
        self.Discretization = d_
     
    def increment(self, oldX, h):
        return oldX
    
    def get_samplepath(self, T, numberofsteps, numberofpaths):
        N = numberofsteps
        h = float(T)/N       
        path = np.zeros([N+1,numberofpaths])
        path[0,:] = self.x0
        oldX = path[0,:]
        
        for ii in range(N):
            newX = self.increment(oldX,h)
            oldX = newX
            path[ii+1,:] = newX
            
        return path
        
    def get_terminalvalue(self, T, numberofsteps, numberofpaths):
        N = numberofsteps
        h = float(T)/N
        oldX = self.x0 * np.ones(numberofpaths)
        
        for ii in range(N):
            newX = self.increment(oldX, h)
            oldX = newX
            
        return newX
        
    def get_currentvalue(self): return self.x0
    
    
class TimeHomoItoProcess1D(StochasticProcess1D):
    
    def __init__(self,x0_,drift_, diffusion_,d_ = 'Euler'):
        self.x0 = x0_
        self.drift = drift_
        self.diffusion = diffusion_
        self.Discretization = d_

    def increment(self,oldX,h):
        try:
            tmpZ = np.random.normal(0,1,len(oldX))
            Z = (tmpZ - np.mean(tmpZ))/np.std(tmpZ)
        except:
            Z = np.random.normal(0,1)
        mu = np.asarray(map(self.drift, oldX))
        sigma = np.asarray(map(self.diffusion, oldX))
        if self.Discretization == 'Euler':
            newX = oldX + mu * h + sigma * np.sqrt(h) * Z
        elif self.Discretization == 'Milstein':
            if isinstance(self.diffusion, FunctionClass.C2Function1D):
                newX = oldX + mu * h + sigma * np.sqrt(h) * Z + 0.5 * sigma * self.diffusion.der_1st(oldX) * h * (Z * Z - 1.0)
            else:
                print '>> C^2 function required for Milstein scheme. \n'
                exit(1)  
        else:
            print '>> No such scheme defined.\n'
            exit(1)
        
        return newX
        
        
class GBM1D(StochasticProcess1D):
    def __init__(self,x0_,mu_, sigma_,d_ = None):
        self.x0 = x0_
        self.mu = mu_
        self.sigma = sigma_
        self.Discretization = d_
    
    def increment(self, oldX, h):
        try:
            Z = np.random.normal(0,1,len(oldX))
        except:
            Z = np.random.normal(0,1)
        
        oldlogX = np.log(oldX)        
        newlogX = oldlogX + (self.mu - 0.5*self.sigma*self.sigma) * h + self.sigma * np.sqrt(h)*Z        
        newX = np.exp(newlogX)
        
        return newX

 
        