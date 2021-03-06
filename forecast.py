#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:06:50 2020
@author: erwin
"""

# Python program to make IC capacity utilization forecast

import numpy as np
import pandas as pd
from scipy.integrate import odeint
import bisect
import scipy
import plotly.graph_objs as go
import covid19_util as util
from io import StringIO
import parameters

class forecast_covid19:
    def __init__(self):
        self.hospitals = pd.read_csv("hospitalizations.csv", sep = ";")
        self.forecasts = {}
        self.factors = {}
        self.results = {}
        self.MAX_RANGE = 100000

    def get_NICE_data(self):
        # CORONAWATCHNL currently offline, temporary fix with manual input
           self.ic_actuals = pd.read_csv("ic.csv", sep = ";")["Opnamen"]
           # try:
               # import requests 
               # r = requests.get('https://raw.githubusercontent.com/J535D165/CoronaWatchNL/master/data/nice_ic_by_day.csv'                                   ,timeout = 3)
               # rawData = pd.read_csv(StringIO(r.text))
               # base = [0] * 11
               # self.ic_actuals = base + rawData["intakeCount"][1:-3].tolist()
           # except:
               # self.ic_actuals = "empty"
        
    def SEIR_solution(self, intervention = [(100,1), (100000, 0.2)],e0 = 20,
                      days = 150, t_inc = 999, t_inf = 999, t_ic = 999):

        # All parameters are imported from parameters.py
        #

        # parameters which can be set via an argument are checked and otherwise adjusted to default
        t_inc = parameters.Const.t_inc if t_inc == 999 else t_inc
        t_inf = parameters.Const.t_inf if t_inf == 999 else t_inf
        t_ic = parameters.Const.t_ic if t_ic == 999 else t_ic


        # Array of tuples: (day, Rint), Rint = 1 means no measures (eg 100% R0)
        # (up_to_day, Rint), (up_to_day, Rint)
        intervention.sort() # list must be sorted


        # Time periods (days)
        t_mild = parameters.Const.t_mild # duration of mild case
        t_hosp = parameters.Const.t_hosp # duration for hospital, but non IC cases
        t_fatal = parameters.Const.t_fatal
        t_hlag = parameters.Const.t_hlag # duration before patient ends up in hospital

        # Clinical proportions
        p_mild = parameters.Const.p_mild
        p_hosp_0 = parameters.Const.p_hosp_0 # hospitalised
        p_ic_0 = parameters.Const.p_ic_0 # IC % from dutch figures

        # mortality
        p_fatal = parameters.Const.p_fatal
        p_fatal_ic = parameters.Const.p_fatal_ic # 50% of fatalities come from IC
        
        # basic parameters
        N = 17000000  # initial susceptible population
        i0 = 1 # number of infected people at t0
        R0 = 2.2  # not used is fitted instead
        s0 = N - i0 / N

        # Static calculations
        alfa = 1 / t_inc
        gamma = 1 / t_inf

        t_mild_net = t_mild - t_inf
        t_hosp_net = t_hosp - t_inf
        t_ic_net = t_ic - t_inc

        p_hosp = p_hosp_0 - (1-p_fatal_ic) * p_fatal
        p_ic = p_ic_0 - p_fatal_ic * p_fatal
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
        t_span = np.linspace(0, days, days, endpoint=False)

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

    def fit_REIS(self, cutoff = 30, name = 'default', days_back = 0):

        # filter hostpitals
        hospital_hist = self.hospitals.iloc[0:len(self.hospitals)-days_back,:]

        #parameters
        factor_lbound = 0.000001 #lower bound for factor on R
        factor_ubound = 3.95/2.2 #upper bound for factor on R

        # use root mean squared error as loss function
        def rmse(factors):
            y1,y2 = factors
            outcome = self.SEIR_solution(intervention =
                                         [(cutoff,y1),
                                          (self.MAX_RANGE,y2)])
            model_hosp = (outcome["I_hosp"] +outcome["I_ic"]+outcome["R_hosp"]+outcome["R_ic"]+\
                          0.5*outcome["I_fatal"]+0.5*outcome["R_fatal"]).iloc[:len(self.hospitals)]
            return np.sqrt(np.mean((model_hosp - hospital_hist.iloc[:,1])**2))

        # minimize loss function
        opt1 = scipy.optimize.minimize(rmse, [1.7,0.8],
                                       bounds = [(factor_lbound, factor_ubound),
                                                 (factor_lbound, factor_ubound)],
                                       method = "L-BFGS-B")
        factors = opt1.x

        # store forecast
        self.forecasts[name] = self.SEIR_solution(intervention =
                                                  [(cutoff,factors[0]),
                                                   (self.MAX_RANGE,factors[1])])
        self.factors[name] = factors
        self.results[name] = opt1

    def determine_Rtarget(self, name = 'default'):
        #determine Rtarget
        Rtarget = 2
        maximum = 50000

        while maximum > 1900:
            Rtarget = Rtarget - 0.01
            solution =  self.SEIR_solution(intervention = [(30,self.factors[name][0]),
                                                           (self.MAX_RANGE,Rtarget/2.2)])
            IC = solution["I_ic"] + 0.5 * solution["I_fatal"]
            maximum = IC.max()
        return Rtarget

    def create_bar(self, Rtarget = 2):
        # create bar chart for question 2
        y1 = [self.factors["outlook"][0]*2.2]
        barnames = ["Before measures", "2 weeks ago",
                    "last week", "latest", "R target"]
        barcolors = ['#E21F35', '#e0e0e0', '#bfbfbf', '#949494', 'green']
        for bar in ["3d_ago_forecast", "previous_forecast", "outlook"]:
            y1.append(self.factors[bar][1]*2.2)
        y1.append(Rtarget)
        effective_R = go.Bar(y= y1, x = barnames, name = "Reproduction rate (R)", marker_color = barcolors)
        fig_bar = go.Figure(data = [effective_R])
        fig_bar.update_layout(barmode='stack', uniformtext=dict(mode='show'))
        fig_bar.update_traces(text=y1, texttemplate='%{text:.2f}', textposition='outside', cliponaxis=False)
        fig_bar.update_layout(
            plot_bgcolor='white',
            margin=dict(pad=10),
            title = dict(text="Figure 3: Estimates of effective reproduction rate (R)",
                font=dict(family="Courier New, monospace", size=20, color="#24292e")))
        return fig_bar






