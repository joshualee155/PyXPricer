# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 08:43:56 2016

@author: CongLiu
"""

import numpy as np
import TriDiag as TD
from scipy.stats import norm
import abc

class PricingEngine(object):
    __metaclass__ = abc.ABCMeta

    result = None
    arguments = {}

    @abc.abstractmethod
    def calculate(self):
        return

class MCEuropeanEngine(PricingEngine):
    def __init__(self, process_ = None, discount_=0, daysperyear_ = 260, numofruns_ = 10000):
        super(MCEuropeanEngine, self).__init__()
        self.process = process_
        self.discount = discount_
        self.daysperyear = daysperyear_
        self.numofruns = numofruns_

    def calculate(self):
        if not self.arguments:
            print '>> Specify arguments of the option. Call set_argument()\n'
            exit(1)
        T = self.arguments['Expiry']
        payoff = self.arguments['Payoff']
        discoutfactor = np.exp(-self.discount * T)          
        
        terminalprice = self.process.get_terminalvalue(T, int(T)*self.daysperyear, self.numofruns)        
        optionprice = discoutfactor * np.asarray(map(payoff, terminalprice)) 

        self.result = np.mean(optionprice)
        
class FDEuropeanNoDriftTimeHomoIto(PricingEngine):
    boundarytype = None
    upper_value = None
    lower_value = None

    def __init__(self, process_=None, discount_=0, nT_=100, nS_=100, maxS_=2, minS_=0, scheme_=0):
        super(FDEuropeanNoDriftTimeHomoIto, self).__init__()
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
        if not self.boundarytype:
            print '>> Unknown Boundary Conditions. Call set_boundary().\n'
            exit(1)

        S0 = self.process.x0
        diffusion = self.process.diffusion
        expiry = self.arguments['Expiry']
        payoff = self.arguments['Payoff']
        
        dt = float(expiry)/self.nT
        dS = float(S0) * (self.maxS-self.minS)/self.nS

        gridS = np.linspace(S0 * self.minS, S0 * self.maxS, self.nS + 1)

        oldU = np.asarray(map(payoff, gridS))  # size: nS+1
        newU = np.zeros(np.shape(oldU))                    # size: nS+1
        volvector = np.asarray(map(diffusion, gridS))  # size: nS+1
        
        alpha = 0.5 * dt/dS/dS * volvector * volvector     # size: nS+1
        alpha_b = alpha[1:-1]    # b; size: nS-1
        alpha_c = alpha_b[0:-1]  # c; size: nS-2
        alpha_a = alpha_b[1:]    # a; size: nS-2
            
        Db = 1 + 2 * (1-self.scheme) * alpha_b    # size: nS-1       
        Dc = -(1-self.scheme) * alpha_c           # size: nS-2 
        Da = -(1-self.scheme) * alpha_a           # size: nS-2
        
        for tt in range(self.nT - 1, -1,-1):
            # Cu size: nS-1
            Cu = TD.TriDiagMultVector(self.scheme * alpha_a, 1 - 2 * self.scheme * alpha_b, self.scheme * alpha_c,
                                      oldU[1:-1])
            if self.boundarytype == 'Dirichlet':
                newU[0] = self.lower_value
                newU[-1] = self.upper_value
                b0 = -self.scheme * alpha_b[0] * oldU[0] - (1-self.scheme)*alpha_b[0]*newU[0]
                b1 = -self.scheme * alpha_b[-1]* oldU[-1]- (1-self.scheme)*alpha_b[-1]*newU[-1]
                Cu[0] -= b0
                Cu[-1] -= b1
                newU[1:-1] = TD.TriDiagSolver(Da,Db,Dc,Cu)
            elif self.boundarytype == 'Neumann':
                b0 = -self.scheme * alpha_b[0] * oldU[0] + (1-self.scheme)*alpha_b[0]*dS*self.lower_value
                b1 = -self.scheme * alpha_b[-1]*oldU[-1] - (1-self.scheme)*alpha_b[-1]*dS*self.upper_value
                Db[0] -= (1 - self.scheme) * alpha_b[0]
                Db[-1] -= (1 - self.scheme) * alpha_b[-1]
                Cu[0] -= b0
                Cu[-1] -= b1
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
        super(BSAnalyticEngine, self).__init__()
        self.process = process_
        self.discount = discount_

    @staticmethod
    def __BSPutCall(S0, K, r, sigma, T, ty):
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
        S0 = self.process.x0
        vol = self.process.sigma
        
        self.result = self.__BSPutCall(S0,strike,discount,vol,T,ty)