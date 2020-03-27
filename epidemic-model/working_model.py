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
gamma = 1 / rAVG



def dUdt(U, t):
    s, e, i = U
    
    
    dsdt = -beta * i / N * s
    dedt = beta * i/ N * s - alfa * e
    didt = alfa * e - gamma * i

    return [dsdt, dedt, didt]

# Create time domain
t_span = np.linspace(0, 102)

# Initial condition
e0 = 0 # exposures
i0 = 40 # infections
r0 = 0 # recoveries
s0 = N - i0 / N # susceptible population

Uzero = [s0, e0, i0]

solution = odeint(dUdt, Uzero, t_span)

# plot
plt.plot(t_span, solution[:, 0], label='Susceptible');
plt.plot(t_span, solution[:, 1], label='Exosed');
plt.plot(t_span, solution[:, 2], label='Infectious');
plt.legend();
plt.xlabel('time'); 