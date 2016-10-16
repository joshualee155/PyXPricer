import abc

class Option(object):
    __metaclass__ = abc.ABCMeta

    engine = None
    result = None

    @abc.abstractmethod
    def populate_arguments(self):
        raise NotImplementedError
    
    def get_price(self):
        self.populate_arguments()
        self.engine.calculate()
        return self.engine.result


class EuropeanOption(Option):
    def __init__(self, payoff_=None, expiry_=None, type_=None, strike_=None):
        super(EuropeanOption, self).__init__()
        self.payoff = payoff_
        self.expiry = expiry_
        self.ty = type_
        self.strike = strike_

    def populate_arguments(self):
        if not self.engine:
            print '>> Pricing engine not defined. Call set_engine().\n'
            exit(1)
        arguments = {'Payoff': self.payoff,
                     'Expiry': self.expiry,
                     'Type': self.ty,
                     'Strike': self.strike}
        self.engine.arguments = arguments
