# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 16:01:39 2016

@author: CongLiu
"""

    
 # base class of 1-dim function   
class Function1D:
    def __init__(self, innerFunc_):
        self.innerFunc = innerFunc_
        
    def __call__(self, x):
        return self.innerFunc(x)


# subclass: 1-dim function 1st order differentiable
class C1Function1D(Function1D):
    def __init__(self, innerFunc_, firstDerivative_ = None):
        self.innerFunc = innerFunc_
        self.firstDerivative = firstDerivative_
    
    def der_1st(self, x):
        if self.firstDerivative != None:
            return self.firstDerivative(x)
        else:
            eps = 1e-4
            return 0.5*(self.innerFunc(x + eps) - self.innerFunc(x - eps))/eps
        
# subclass: 1-dim function  2nd order differentiable     
class C2Function1D(C1Function1D):
    def __init__(self, innerFunc_, firstDerivative_ = None, secondDerivative_ = None):
        self.innerFunc = innerFunc_
        self.firstDerivative = firstDerivative_
        self.secondDerivative = secondDerivative_
        
    def der_2nd(self, x):
        if self.secondDerivative != None:
            return self.secondDerivative(x)
        else:
            eps = 1e-4
            if self.firstDerivative != None:
                return 0.5*(self.firstDerivative(x+eps)-self.firstDerivative(x-eps))/eps
            else:
                return (self.innerFunc(x+eps)-2.0*self.innerFunc(x)+self.innerFunc(x-eps))/eps/eps
        
class PayoffFunc(Function1D):
    pass


        
        



        
    
        
    