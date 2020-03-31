# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 15:10:54 2020

@author: Gijs
"""

import random
import scipy
from covid19_processing import *
import working_model

# data processing
data = Covid19Processing()
data.process(rows=20, debug=False)
rivm = data.dataframes["RIVM"]

def SEIR(factor):
    outcome = working_model.SEIR_solution(intervention = [(20,1), (300,factor)])
    outcome = outcome[outcome["R_hosp"] > rivm["Aantal"].iloc[0]]
    outcome = outcome.iloc[:len(rivm["Aantal"])]
    return outcome["R_hosp"]

def rmse(factor):
    outcome = SEIR(factor)
    rmse = []
    for t in range(0,len(rivm["Aantal"])):
        se = outcome.iloc[t] - rivm["Aantal"].iloc[t]
        se_sq = se**2
        rmse.append(se_sq)
    sum_rmse = sum(rmse)
    return sum_rmse

y = scipy.optimize.minimize(rmse, 0.7).x

