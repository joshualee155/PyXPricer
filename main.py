import numpy as np
import StochasticProcess as SP
import PricingEngine as PE
import Option
import FunctionClass as FC
from scipy.stats import norm

def main():
    price_EuropeanCall()
    price_CallOrNothing()

def payoff_EuropeanCall(K):
    return FC.Function1D(lambda x: max(x-K,0))

def payoff_CashOrNothing(K):
    rtn = 1
    return FC.Function1D(lambda x: rtn * (x>K) + 0 * (x<=K))

def price_option(option, engine):
    option.set_engine(engine)
    option.set_arguments()
    return option.get_price()
    
def price_EuropeanCall():
    s0 = 10  # initial spot prices
    r = 0    # risk free rate
    sigma0 = 0.2
    expiry = 1
    drift = FC.C2Function1D(lambda x: 0)
    Kset = np.linspace(8.0,12.0,41)
    diffusion_set = {'const': FC.C2Function1D(lambda x: sigma0),
                     'linear': FC.C2Function1D(lambda x: sigma0 * x),
                     'sqrt': FC.Function1D(lambda x: sigma0 * np.sqrt(x)),
                     'sine': FC.C2Function1D(lambda x: np.sin(x))}
                     
    # ===== linear diffusion ===== #
    process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['linear'])
    price_FD = np.zeros(len(Kset))   
    price_MC = np.zeros(len(Kset)) 
    price_BS = np.zeros(len(Kset))
    for kk, strike in enumerate(Kset):
        payoff = payoff_EuropeanCall(strike)
        option = Option.EuropeanOption(payoff, expiry, 'call', strike)                
        
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MC[kk] = price_option(option,engineMC)
        
        engineFD = PE.FDEuropeanNoDriftTimeHomoIto(process, r, 200, 500)
        engineFD.set_boundary('Neumann',1,0)
        price_FD[kk] = price_option(option,engineFD)
        
        GBMprocess = SP.GBM1D(s0,0.0,sigma0)
        GBMengine = PE.BSAnalyticEngine(GBMprocess, r)
        price_BS[kk] = price_option(option,GBMengine)
    
    results = np.zeros([len(Kset),4])
    results[:,0] = Kset 
    results[:,1] = price_FD     
    results[:,2] = price_MC
    results[:,3] = price_BS
    print results

    # ===== constant diffusion ===== #
    process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['const'])
    price_FD = np.zeros(len(Kset))   
    price_MC = np.zeros(len(Kset)) 
    price_B = np.zeros(len(Kset))
    for kk in range(len(Kset)):
        print kk
        strike = Kset[kk]
        payoff = payoff_EuropeanCall(strike)
        option = Option.EuropeanOption(payoff, expiry, 'call', strike) 
        
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MC[kk] = price_option(option,engineMC)
        
        engineFD = PE.FDEuropeanNoDriftTimeHomoIto(process, r, 100,400)
        engineFD.set_boundary('Neumann',1,0)
        price_FD[kk] = price_option(option,engineFD)
        
        d1 = (s0 - strike)/sigma0/np.sqrt(expiry)
        price_B[kk] = (s0 - strike)*norm.cdf(d1) + sigma0*np.sqrt(expiry) * norm.pdf(d1)
        
    results = np.zeros([len(Kset),4])
    results[:,0] = Kset 
    results[:,1] = price_FD     
    results[:,2] = price_MC
    results[:,3] = price_B
    #pd.DataFrame(results).to_csv(outputdir + 'Call_const.csv', header = False, index = False)    

    # ===== sqrt diffusion ===== #
    process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['sqrt'])
    price_FD = np.zeros(len(Kset))   
    price_MC = np.zeros(len(Kset)) 
    for kk in range(len(Kset)):
        print kk
        strike = Kset[kk]
        payoff = payoff_EuropeanCall(strike)
        option = Option.EuropeanOption(payoff, expiry, 'call', strike)        
        
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MC[kk] = price_option(option,engineMC)
        
        engineFD = PE.FDEuropeanNoDriftTimeHomoIto(process, r, 200,500)
        engineFD.set_boundary('Neumann',1,0)
        price_FD[kk] = price_option(option,engineFD)
        
    results = np.zeros([len(Kset),3])
    results[:,0] = Kset 
    results[:,1] = price_FD     
    results[:,2] = price_MC
    #pd.DataFrame(results).to_csv(outputdir + 'Call_sqrt.csv', header = False, index = False)    

    # ===== sine diffusion ===== #    
    price_FD = np.zeros(len(Kset))   
    price_MC = np.zeros(len(Kset)) 
    price_MS = np.zeros(len(Kset))
    for kk in range(len(Kset)):
        print kk
        strike = Kset[kk]
        payoff = payoff_EuropeanCall(strike)
        option = Option.EuropeanOption(payoff, expiry, 'call', strike) 
        
        process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['sine'])
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MC[kk] = price_option(option,engineMC)
        
        process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['sine'],'Milstein')
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MS[kk] = price_option(option,engineMC)        
        
        engineFD = PE.FDEuropeanNoDriftTimeHomoIto(process, r,200,500)
        engineFD.set_boundary('Neumann',1,0)
        price_FD[kk] = price_option(option,engineFD)
        
    results = np.zeros([len(Kset),4])
    results[:,0] = Kset 
    results[:,1] = price_FD     
    results[:,2] = price_MC
    results[:,3] = price_MS
    #pd.DataFrame(results).to_csv(outputdir + 'Call_sine.csv', header = False, index = False)    


def price_CallOrNothing():
    s0 = 10  # initial spot prices
    r = 0    # risk free rate
    sigma0 = 0.2
    expiry = 1
    rtn = 1
    drift = FC.C2Function1D(lambda x: 0)
    Kset = np.linspace(8.0,12.0,41)
    diffusion_set = {'const': FC.C2Function1D(lambda x: sigma0),
                     'linear': FC.C2Function1D(lambda x: sigma0 * x),
                     'sqrt': FC.Function1D(lambda x: sigma0 * np.sqrt(x)),
                     'sine': FC.C2Function1D(lambda x: np.sin(x))}     
    # ===== linear diffusion ===== #
    process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['linear'])
    price_FD = np.zeros(len(Kset))   
    price_MC = np.zeros(len(Kset)) 
    price_BS = np.zeros(len(Kset))
    for kk in range(len(Kset)):
        print kk
        strike = Kset[kk]
        payoff = payoff_CashOrNothing(strike)
        option = Option.EuropeanOption(payoff, expiry, strike_ = strike)        
        
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MC[kk] = price_option(option,engineMC)
        
        engineFD = PE.FDEuropeanNoDriftTimeHomoIto(process, r,200,500)
        engineFD.set_boundary('Neumann',0,0)
        price_FD[kk] = price_option(option,engineFD)
    
        d2 = 1/sigma0/np.sqrt(expiry)*(np.log(s0/strike)+(r-0.5*sigma0**2)*expiry)
        price_BS[kk] = rtn * np.exp(-r*expiry)*norm.cdf(d2)

    results = np.zeros([len(Kset),4])
    results[:,0] = Kset 
    results[:,1] = price_FD     
    results[:,2] = price_MC
    results[:,3] = price_BS
    #pd.DataFrame(results).to_csv(outputdir + 'Digital_linear.csv', header = False, index = False)    

    # ===== constant diffusion ===== #
    process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['const'])
    price_FD = np.zeros(len(Kset))   
    price_MC = np.zeros(len(Kset)) 
    price_B = np.zeros(len(Kset))
    for kk in range(len(Kset)):
        print kk
        strike = Kset[kk]
        payoff = payoff_CashOrNothing(strike)
        option = Option.EuropeanOption(payoff, expiry, strike_ = strike)               
        
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MC[kk] = price_option(option,engineMC)
        
        engineFD = PE.FDEuropeanNoDriftTimeHomoIto(process, r,100,400)
        engineFD.set_boundary('Neumann',0,0)
        price_FD[kk] = price_option(option,engineFD)

        d1 = (s0 - strike)/sigma0/np.sqrt(expiry)
        price_B[kk] = norm.cdf(d1) 

    results = np.zeros([len(Kset),4])
    results[:,0] = Kset 
    results[:,1] = price_FD     
    results[:,2] = price_MC
    results[:,3] = price_B
    #pd.DataFrame(results).to_csv(outputdir + 'Digital_const.csv', header = False, index = False)    

    # ===== sqrt diffusion ===== #
    process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['sqrt'])
    price_FD = np.zeros(len(Kset))   
    price_MC = np.zeros(len(Kset)) 
    for kk in range(len(Kset)):
        print kk
        strike = Kset[kk]
        payoff = payoff_CashOrNothing(strike)
        option = Option.EuropeanOption(payoff, expiry, strike_ = strike)                
        
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MC[kk] = price_option(option,engineMC)
        
        engineFD = PE.FDEuropeanNoDriftTimeHomoIto(process, r,200,500)
        engineFD.set_boundary('Neumann',0,0)
        price_FD[kk] = price_option(option,engineFD)
    
    results = np.zeros([len(Kset),3])
    results[:,0] = Kset 
    results[:,1] = price_FD     
    results[:,2] = price_MC
    #pd.DataFrame(results).to_csv(outputdir + 'Digital_sqrt.csv', header = False, index = False)    

    # ===== sine diffusion ===== #
    price_FD = np.zeros(len(Kset))   
    price_MC = np.zeros(len(Kset)) 
    price_MS = np.zeros(len(Kset))
    for kk in range(len(Kset)):
        print kk
        strike = Kset[kk]
        payoff = payoff_CashOrNothing(strike)
        option = Option.EuropeanOption(payoff, expiry, strike_ = strike)   
    
    
        process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['sine'])
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MC[kk] = price_option(option,engineMC)
        
        process = SP.TimeHomoItoProcess1D(s0,drift,diffusion_set['sine'],'Milstein')
        engineMC = PE.MCEuropeanEngine(process, r)
        price_MS[kk] = price_option(option,engineMC)
        
        engineFD = PE.FDEuropeanNoDriftTimeHomoIto(process, r, 200, 500)
        engineFD.set_boundary('Neumann',0,0)
        price_FD[kk] = price_option(option,engineFD)
    
    results = np.zeros([len(Kset),4])
    results[:,0] = Kset 
    results[:,1] = price_FD     
    results[:,2] = price_MC
    results[:,3] = price_MS
    #pd.DataFrame(results).to_csv(outputdir + 'Digital_sine.csv', header = False, index = False)    


main()
