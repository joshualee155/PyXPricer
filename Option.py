# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 08:54:51 2016

@author: CongLiu
"""

class Option:
    engine = None
    price = None
    def __init__(self): pass
         
    def set_engine(self, engine_):
        self.engine = engine_
        
    def set_arguments(self): pass
    
    def get_price(self):
        self.engine.calculate()
        return self.engine.result


class EuropeanOption(Option):    
      
    def __init__(self, payoff_ = None, expiry_ = None,type_ = None, strike_ = None):
        self.payoff = payoff_
        self.expiry = expiry_
        self.ty = type_
        self.strike = strike_
    
    def set_arguments(self):
        if self.engine == None:
            print '>> Pricing engine not defined. Call set_engine().\n'
            exit(1)
        arguments = {}
        arguments['Payoff'] = self.payoff
        arguments['Expiry'] = self.expiry
        arguments['Type'] = self.ty
        arguments['Strike'] = self.strike
        self.engine.set_arguments(arguments)
        
    def set_payoff(self, payoff_):
        self.payoff = payoff_

    def set_expiry(self, expiry_):
        self.expiry = expiry_        
        
    def get_payoff(self, spot): 
        return self.payoff(spot)
        
    def get_expiry(self): 
        return self.expiry

