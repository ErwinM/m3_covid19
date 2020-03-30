#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:06:50 2020

@author: erwin
"""

# Python program to implement Runge Kutta method 


import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Parameters 

R0 = 2.2
tINF = 2.9
tINC = 5.2
rAVG = 14
N = 7000000 # size of population

# calculated for clarity
alfa = 1 / tINC
beta = R0 /tINF
gamma = 1 / tINF



def dUdt(U, t):
    s, e, i = U
    
    
    dsdt = -beta * i / N * s
    dedt = beta * i/ N * s - alfa * e
    didt = alfa * e - gamma * i

    return [dsdt, dedt, didt]

# Create time domain
t_span = np.linspace(0, 200, 100, endpoint=False)

# Initial condition
e0 = 0 # exposures
i0 = 1 # infections
r0 = 0 # recoveries
s0 = N - i0 / N # susceptible population

Uzero = [s0, e0, i0]
solution = odeint(dUdt, Uzero, t_span)

# insert t_span into solution to prevent total confusion
t = np.reshape(t_span, (100,1))
inspect_solution = np.append(solution, t, axis=1 )


# plot
#plt.plot(t_span, solution[:, 0], label='masse');
plt.plot(t_span, solution[:, 1], label='Exposed');
plt.plot(t_span, solution[:, 2], label='Infectious');
plt.legend();
plt.xlabel('time'); 
