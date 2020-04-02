# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 15:10:54 2020

@author: Gijs
"""

import scipy
from covid19_processing import *
import working_model
import numpy as np
import pandas as pd

def fit_REIS(cutoff = 30):
    cutoff = 30
    
    # data processing
    hospital = pd.read_csv("hospitalizations.csv", sep = ";")
    
    def rmse(factors):
        y1,y2 = factors
        outcome = working_model.SEIR_solution(intervention = [(cutoff,y1), (300,y2)], e0 = 20)
        model_hosp = (outcome["I_hosp"] +outcome["I_ic"]+outcome["R_hosp"]+outcome["R_ic"]+0.5*outcome["I_fatal"]+0.5*outcome["R_fatal"]).iloc[:len(hospital)]
        return np.sqrt(np.sum((model_hosp - hospital.iloc[:,1])**2))
    
    opt1 = scipy.optimize.minimize(rmse, [1.7,0.8], bounds = [(0.000001, 3), (0.000001, 3)], method = "L-BFGS-B")
    factors = opt1.x
    return factors

