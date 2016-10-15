# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 08:43:56 2016

@author: CongLiu
"""

import numpy as np
import TriDiag as TD
from scipy.stats import norm

class PricingEngine:
    result = None
    arguments = {}
    def __init__(self): pass

    def set_arguments(self, arguments_):
        self.arguments = arguments_
         
    def get_arguments(self): pass
   
    def get_result(self): return self.result
   
   
class MCEuropeanEngine(PricingEngine):
    def __init__(self, process_ = None, discount_=0, daysperyear_ = 260, numofruns_ = 10000):
        self.process = process_
        self.discount = discount_
        self.daysperyear = daysperyear_
        self.numofruns = numofruns_
        
    def set_process(self, process_):
        self.process = process_
        
    def calculate(self): 
        if self.arguments == {}:
            print '>> Specify arguments of the option. Call set_argument()\n'
            exit(1)
        T = self.arguments['Expiry']
        payoff = self.arguments['Payoff']
        discoutfactor = np.exp(-self.discount * T)          
        
        terminalprice = self.process.get_terminalvalue(T, int(T)*self.daysperyear, self.numofruns)        
        optionprice = discoutfactor * np.asarray(map(payoff, terminalprice)) 

        self.result = np.mean(optionprice)
        
class FDEuropeanNoDriftTimeHomoIto(PricingEngine):
    def __init__(self, process_ = None, discount_ = 0, nT_=100, nS_=100, \
                 maxS_ = 2, minS_ = 0, scheme_ = 0):
        self.process = process_
        self.discount = discount_
        self.nT = nT_
        self.nS = nS_
        self.maxS = maxS_
        self.minS = minS_
        self.scheme = scheme_   # 0: Explicit, 1: Implicit, 0.5: Crank Nikoson
        
    def set_boundary(self, boundarytype_= None, upper_value_ = None, lower_value_ = None):       
        self.boundarytype= boundarytype_
        self.upper_value = upper_value_  
        self.lower_value = lower_value_
        
    def calculate(self):       
        if self.boundarytype == None:
            print '>> Unknown Boundary Conditions. Call set_boundary().\n'
            exit(1)
    
        S0 = self.process.get_currentvalue()
        diffusion = self.process.diffusion
        expiry = self.arguments['Expiry']
        payoff = self.arguments['Payoff']
        
        dt = float(expiry)/self.nT
        dS = float(S0) * (self.maxS-self.minS)/self.nS
        
        self.gridT = np.linspace(0,expiry,self.nT+1)
        self.gridS = np.linspace(S0*self.minS,S0*self.maxS, self.nS+1)
        
        oldU = np.asarray(map(payoff, self.gridS))         # size: nS+1
        newU = np.zeros(np.shape(oldU))                    # size: nS+1
        volvector = np.asarray(map(diffusion, self.gridS)) # size: nS+1
        
        alpha = 0.5 * dt/dS/dS * volvector * volvector     # size: nS+1
        alpha_b = alpha[1:-1]    # b; size: nS-1
        alpha_c = alpha_b[0:-1]  # c; size: nS-2
        alpha_a = alpha_b[1:]    # a; size: nS-2
            
        Db = 1 + 2 * (1-self.scheme) * alpha_b    # size: nS-1       
        Dc = -(1-self.scheme) * alpha_c           # size: nS-2 
        Da = -(1-self.scheme) * alpha_a           # size: nS-2
        
        for tt in range(self.nT - 1, -1,-1):
            # Cu size: nS-1
            Cu = TD.TriDiagMultVector(self.scheme * alpha_a, 1-2*self.scheme*alpha_b,\
                                      self.scheme * alpha_c, oldU[1:-1])
            if self.boundarytype == 'Dirichlet':
                newU[0] = self.lower_value
                newU[-1] = self.upper_value
                b0 = -self.scheme * alpha_b[0] * oldU[0] - (1-self.scheme)*alpha_b[0]*newU[0]
                b1 = -self.scheme * alpha_b[-1]* oldU[-1]- (1-self.scheme)*alpha_b[-1]*newU[-1]
                Cu[0] = Cu[0] - b0
                Cu[-1] = Cu[-1] - b1
                newU[1:-1] = TD.TriDiagSolver(Da,Db,Dc,Cu)
            elif self.boundarytype == 'Neumann':
                b0 = -self.scheme * alpha_b[0] * oldU[0] + (1-self.scheme)*alpha_b[0]*dS*self.lower_value
                b1 = -self.scheme * alpha_b[-1]*oldU[-1] - (1-self.scheme)*alpha_b[-1]*dS*self.upper_value
                Db[0] = Db[0] - (1-self.scheme)*alpha_b[0]
                Db[-1] = Db[-1]-(1-self.scheme)*alpha_b[-1]
                Cu[0] = Cu[0] - b0
                Cu[-1] = Cu[-1] - b1
                newU[1:-1] = TD.TriDiagSolver(Da,Db,Dc,Cu)
                newU[0] = newU[1] - dS * self.lower_value
                newU[-1]= newU[-2]+ dS * self.upper_value
            else:
                print '>> Boundary type not supported.\n'
                exit(1)
            
            oldU = newU
        
        self.result = np.exp(-self.discount * expiry)*  oldU[self.nS/2]
        
        
class BSAnalyticEngine(PricingEngine):        
    def __init__(self, process_ = None, discount_ = 0):
        self.process = process_
        self.discount = discount_
    
    def __BSPutCall(self,S0,K,r,sigma,T,ty):
        d1 = (np.log(S0/K) + (r + 0.5*sigma*sigma)*T )/ (sigma*np.sqrt(T)+1.e-7)
        d2 = d1 - sigma * np.sqrt(T)
        
        if ty.lower() == 'call':
            return S0 * norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        elif ty.lower() == 'put':
            return K*np.exp(-r*T)*norm.cdf(-d2) - S0 * norm.cdf(-d1)
        else:
            print '>> Option type neither call or put. \n'
            exit(1)

    def calculate(self): 
        if self.arguments == {}:
            print '>> Specify arguments of the option. Call set_argument()\n'
            exit(1)
        T = self.arguments['Expiry']
        ty = self.arguments['Type']
        strike = self.arguments['Strike']
        discount = self.discount  
        S0 = self.process.get_currentvalue()
        vol = self.process.sigma
        
        self.result = self.__BSPutCall(S0,strike,discount,vol,T,ty)