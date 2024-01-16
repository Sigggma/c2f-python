
# coding: utf-8
# Importations
import numpy as np

# Lightning Class: Fire ignition class, determines the week when fire starts, based on a poisson strike	
class Lightning:
    PoissonRate = None

    '''
    Returns      int
    
    Inputs:
    period       int
    '''
    # Returns a random generated week
    def Lambda_Simple_Test(self, period):
        Selected_Week = np.random.randint(1, 13)
        return Selected_Week

    
    '''
    Returns      boolean
    
    Inputs:
    period       int
    verbose      boolean
    '''
    # Returns True if fire, False otherwise
    def Lambda_NH(self, period, verbose):
        Fire_Rate = 0.5
        AlfaFact = 0.1
        Poisson_Mean = (Fire_Rate / 2.0) * (2.0 + AlfaFact * ((period ** 2) - (period-1) ** 2 - 2.0))
        ProbsNoFire = np.round(np.exp(-Poisson_Mean), 2)
        if verbose == True:
            print("Probs of not fire (week ", period, "): ", ProbsNoFire)
         
        if np.round(np.random.uniform(0,1), 2) > ProbsNoFire:
            return True
        else:
            return False
        
    
    
    '''
    Returns      boolean
    
    Inputs:
    period       int
    verbose      boolean
    '''        
    # Returns True if fire, False otherwise
    def Lambda_H(self, period, verbose):
        Poisson_Mean = 0.5
        ProbsNoFire = np.round(np.exp(-Poisson_Mean), 2)
        if verbose == True:
            print("Probs of not fire (week ", period, "): ",ProbsNoFire)
            
        if np.round(np.random.uniform(0,1), 2) > ProbsNoFire:
            return True
        else:
            return False


