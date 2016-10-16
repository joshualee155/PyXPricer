# base class of 1-dim function
class Function1D(object):
    def __init__(self, innerFunc):
        self.innerFunc = innerFunc
        
    def __call__(self, x):
        return self.innerFunc(x)


# subclass: 1-dim function 1st order differentiable
class C1Function1D(Function1D):
    def __init__(self, innerFunc, firstDerivative = None):
        super(C1Function1D, self).__init__(innerFunc)
        self.firstDerivative = firstDerivative
    
    def der_1st(self, x):
        if self.firstDerivative:
            return self.firstDerivative(x)
        else:
            eps = 1e-4
            return 0.5*(self.innerFunc(x + eps) - self.innerFunc(x - eps))/eps
        
# subclass: 1-dim function  2nd order differentiable     
class C2Function1D(C1Function1D):
    def __init__(self, innerFunc, firstDerivative = None, secondDerivative = None):
        super(C2Function1D, self).__init__(innerFunc, firstDerivative)
        self.secondDerivative = secondDerivative
        
    def der_2nd(self, x):
        if self.secondDerivative:
            return self.secondDerivative(x)
        else:
            eps = 1e-4
            if self.firstDerivative:
                return 0.5*(self.firstDerivative(x+eps)-self.firstDerivative(x-eps))/eps
            else:
                return (self.innerFunc(x+eps)-2.0*self.innerFunc(x)+self.innerFunc(x-eps))/eps/eps
        
class PayoffFunc(Function1D):
    pass


        
        



        
    
        
    