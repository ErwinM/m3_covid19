#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:06:50 2020
@author: erwin
"""

# Python program to implement Runge Kutta method 

import numpy as np
import pandas as pd
from scipy.integrate import odeint
import bisect
import matplotlib.pyplot as plt

def SEIR_solution(intervention = [(100,1), (300, 0.2)],e0 = 0):
    # INPUT PARAMETERS
    N = 17000000
    i0 = 1
    R0 = 2.2
    t_inc = 5.2
    t_inf = 3
    s0 = N - i0 / N
    
    # Array of tuples: (day, Rint), Rint = 1 means no measures (eg 100% R0)
    # (up_to_day, Rint), (up_to_day, Rint)
    intervention.sort() # list must be sorted
    
    
    # Time periods (days)
    t_mild = 11 # duration of mild case
    t_hosp = 7 # duration for hospital, but non IC cases
    t_ic = 21 # duration of IC cases
    t_fatal = 21
    t_hlag = 5 # duration before patient ends up in hospital
    
    # Clinical proportions
    p_mild = 0.8
    p_hosp_0 = 0.15 # hospitalised
    p_ic_0 = 0.05 # IC
    
    # mortality
    p_fatal = 0.02
    p_fatal_ic = 0.5 # 50% of fatalities come from IC
    
    # Static calculations
    alfa = 1 / t_inc
    gamma = 1 / t_inf
    
    t_mild_net = t_mild - t_inf
    t_hosp_net = t_hosp - t_inf
    t_ic_net = t_ic - t_inc
    
    p_hosp = p_hosp_0 - (3/4) * p_fatal
    p_ic = p_ic_0 - (1/4) * p_fatal
    assert(p_mild+p_hosp+p_ic+p_fatal == 1)
    

    def dUdt(U, t):
        s, e, i, i_mild, i_pre_hosp, i_hosp, i_pre_ic, i_ic, i_fatal, r_mild, r_hosp, r_ic, r_fatal = U
        
        # calculate beta taking measures into account. Depends on t
        pos = bisect.bisect_right(intervention, (t,))
        Rint = intervention[pos][1]
        beta = Rint * R0 / t_inf
     
        dsdt = -beta * i / N * s
        dedt = beta * i/ N * s - alfa * e
        didt = alfa * e - gamma * i
        
        # splitting up infectious
        di_mild = p_mild * gamma * i - (1/t_mild_net) * i_mild
        di_pre_hosp = p_hosp * gamma * i - (1 / t_hlag ) * i_pre_hosp
        di_hosp = (1 / t_hlag) * i_pre_hosp - (1/t_hosp_net) * i_hosp
        di_pre_ic = p_ic * gamma * i - (1 / t_hlag ) * i_pre_ic
        di_ic = (1 / t_hlag ) * i_pre_ic - (1/t_ic_net) * i_ic
        di_fatal = p_fatal * gamma * i - (1/t_fatal) * i_fatal
        
        dr_mild = (1/t_mild_net) * i_mild
        dr_hosp = (1/t_hosp_net) * i_hosp
        dr_ic = (1/t_ic_net) * i_ic
        dr_fatal = (1/t_fatal) * i_fatal
    
        return [dsdt, dedt, didt, di_mild, di_pre_hosp,
                di_hosp, di_pre_ic, di_ic, di_fatal,
                dr_mild, dr_hosp, dr_ic, dr_fatal]
    
    # Create time domain
    t_span = np.linspace(0, 100, 100, endpoint=False)
    
    # Initial condition
    Uzero = [s0, e0, i0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    solution = odeint(dUdt, Uzero, t_span)
    
    # some post manipulation and calculation of mortality rates
    df = pd.DataFrame(solution)
    
    # add column names
    df.columns = ['Susceptible', 'Exposed', 'I_total', 'I_mild', 'I_pre_hosp',
                  'I_hosp', 'I_pre_ic', 'I_ic', 'I_fatal', 'R_mild', 'R_hosp',
                  'R_ic', 'R_fatal']
    
    # add timeframe as a column
    df['day'] = t_span
    return df
