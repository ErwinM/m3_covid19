#!/usr/bin/env python
# coding: utf-8

# <h1>Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Setup" data-toc-modified-id="Setup-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Setup</a></span></li><li><span><a href="#Retrieve-and-transform-data" data-toc-modified-id="Retrieve-and-transform-data-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Retrieve and transform data</a></span><ul class="toc-item"><li><span><a href="#Process-and-add-up-all-provinces/states-into-one-row-per-country" data-toc-modified-id="Process-and-add-up-all-provinces/states-into-one-row-per-country-2.1"><span class="toc-item-num">2.1&nbsp;&nbsp;</span>Process and add up all provinces/states into one row per country</a></span></li><li><span><a href="#List-of-all-affected-countries" data-toc-modified-id="List-of-all-affected-countries-2.2"><span class="toc-item-num">2.2&nbsp;&nbsp;</span>List of all affected countries</a></span></li></ul></li><li><span><a href="#Current-situation-plots" data-toc-modified-id="Current-situation-plots-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>Current situation plots</a></span><ul class="toc-item"><li><span><a href="#Plot-trends-over-calendar-date-in-selected-countries" data-toc-modified-id="Plot-trends-over-calendar-date-in-selected-countries-3.1"><span class="toc-item-num">3.1&nbsp;&nbsp;</span>Plot trends over calendar date in selected countries</a></span></li><li><span><a href="#Plot-trends-over-days-since-start-of-local-outbreak-in-selected-countries" data-toc-modified-id="Plot-trends-over-days-since-start-of-local-outbreak-in-selected-countries-3.2"><span class="toc-item-num">3.2&nbsp;&nbsp;</span>Plot trends over days since start of local outbreak in selected countries</a></span></li><li><span><a href="#Case-fatality-rate-per-country" data-toc-modified-id="Case-fatality-rate-per-country-3.3"><span class="toc-item-num">3.3&nbsp;&nbsp;</span>Case fatality rate per country</a></span></li><li><span><a href="#Cases-by-continent" data-toc-modified-id="Cases-by-continent-3.4"><span class="toc-item-num">3.4&nbsp;&nbsp;</span>Cases by continent</a></span></li><li><span><a href="#Smoothed-growth-factor" data-toc-modified-id="Smoothed-growth-factor-3.5"><span class="toc-item-num">3.5&nbsp;&nbsp;</span>Smoothed growth factor</a></span></li><li><span><a href="#New-confirmed/Active-case-ratio" data-toc-modified-id="New-confirmed/Active-case-ratio-3.6"><span class="toc-item-num">3.6&nbsp;&nbsp;</span>New confirmed/Active case ratio</a></span></li><li><span><a href="#Stats-for-some-other-countries,-using-linear-scale" data-toc-modified-id="Stats-for-some-other-countries,-using-linear-scale-3.7"><span class="toc-item-num">3.7&nbsp;&nbsp;</span>Stats for some other countries, using linear scale</a></span></li><li><span><a href="#Pie-charts" data-toc-modified-id="Pie-charts-3.8"><span class="toc-item-num">3.8&nbsp;&nbsp;</span>Pie charts</a></span></li><li><span><a href="#Country-highlight" data-toc-modified-id="Country-highlight-3.9"><span class="toc-item-num">3.9&nbsp;&nbsp;</span>Country highlight</a></span></li></ul></li><li><span><a href="#Forecast-plots" data-toc-modified-id="Forecast-plots-4"><span class="toc-item-num">4&nbsp;&nbsp;</span>Forecast plots</a></span><ul class="toc-item"><li><span><a href="#Fit-a-logistic-curve-and-extrapolate-number-of-future-cases" data-toc-modified-id="Fit-a-logistic-curve-and-extrapolate-number-of-future-cases-4.1"><span class="toc-item-num">4.1&nbsp;&nbsp;</span>Fit a logistic curve and extrapolate number of future cases</a></span></li><li><span><a href="#Modelling-fatality-probability-per-day-of-being-infected" data-toc-modified-id="Modelling-fatality-probability-per-day-of-being-infected-4.2"><span class="toc-item-num">4.2&nbsp;&nbsp;</span>Modelling fatality probability per day of being infected</a></span></li><li><span><a href="#Generate-history-of-active-cases;-how-many-people-have-been-sick-for-how-long?" data-toc-modified-id="Generate-history-of-active-cases;-how-many-people-have-been-sick-for-how-long?-4.3"><span class="toc-item-num">4.3&nbsp;&nbsp;</span>Generate history of active cases; how many people have been sick for how long?</a></span></li><li><span><a href="#Simulate-future-development-based-on-history-and-probability-models" data-toc-modified-id="Simulate-future-development-based-on-history-and-probability-models-4.4"><span class="toc-item-num">4.4&nbsp;&nbsp;</span>Simulate future development based on history and probability models</a></span></li></ul></li></ul></div>

# # COVID-19 data visualization
# 
# This generates a series of visualizations from the raw data tables, showing some aspects of the ongoing Covid-19 epidemic that I couldn't find in other reports. Data from Johns Hopkins University.
# 
# An earlier version of the plot of cases per country since the start of the local outbreak was shared on Reddit [here](https://www.reddit.com/r/dataisbeautiful/comments/ff9jn4/oc_number_of_cases_per_country_counting_from_the/).   Another plot, of the average growth factor per country, was posted [here](https://www.reddit.com/r/dataisbeautiful/comments/fliec2/oc_covid19_growth_factor_over_time_in_various/).
# 
# Note that the Table of Contents links above don't work in the Github preview, but they do on [nbviewer](https://nbviewer.jupyter.org/github/JeroenKools/covid19/tree/master/).
# 
# Want to see these graphs for some other countries, or modify the values for the simulations? The easiest and quickest way to run the notebook and make modifications yourself is to open this notebook in [Colab](https://colab.research.google.com/github/JeroenKools/covid19/blob/master/COVID-19.ipynb).

# ## Setup

# Import code and parameters from [`covid19_util.py`](covid19_util.py) and [`covid_processing.py`](covid19_processing.py).

# In[1]:


#get_ipython().run_line_magic('load_ext', 'autoreload')
#get_ipython().run_line_magic('autoreload', '2')
import sys
is_colab = 'google.colab' in sys.modules
#if is_colab and not "covid19" in sys.path:
#  try:
#    get_ipython().system('git clone https://github.com/JeroenKools/covid19.git')
#  except e: pass
#  sys.path.append("covid19")
from covid19_util import *
from covid19_processing import *


# ## Retrieve and transform data
# 
# Thia code cell retrieves the most recent raw data on confirmed cases, deaths, and recoveries from the Johns Hopkins data repository, <br>and transforms each set into a Pandas dataframe.
# 
# For validation, it then shows a summarized version of the confirmed cases dataframe.

# In[2]:


data = Covid19Processing()


# ### Process and add up all provinces/states into one row per country 
# 
# This also adds in a few data points for China from before the start of the Johns Hopkins data, from [Wikipedia](https://en.wikipedia.org/wiki/Timeline_of_the_2019%E2%80%9320_coronavirus_outbreak_in_December_2019_%E2%80%93_January_2020).
# 
# Then, display summaries of the confirmed cases by country and by continent.

# In[3]:


data.process(rows=20, debug=False)


# ### List of all affected countries

# In[4]:


data.list_countries()


# ## Current situation plots

# ### Plot trends over calendar date in selected countries

# In[5]:


countries_to_plot = ["China", "Japan", "South Korea", "United States", "Italy", "Iran", "Germany",
                     "France", "Spain", "Netherlands", "United Kingdom", "World"]

for y_metric in ["confirmed", "deaths", "active"]:
    data.plot("calendar_date", y_metric, countries_to_plot)


# ### Plot trends over days since start of local outbreak in selected countries

# In[6]:


data.plot("day_number", "confirmed", countries_to_plot, min_cases=100)
data.plot("day_number", "deaths", countries_to_plot, min_cases=3)
data.plot("day_number", "active", countries_to_plot, min_cases=40)


# ### Case fatality rate per country

# In[7]:


data.plot("calendar_date", "deaths/confirmed", countries_to_plot, min_cases=50, use_log_scale=False)


# ### Cases by continent

# In[8]:


continents = ["Asia", "Europe", "Africa", "North America", "South America", "Oceania"]

for y_metric in ["confirmed", "deaths", "active", "new confirmed"]:
    data.plot("calendar_date", y_metric, continents, fixed_country_colors=False)


# ### Smoothed growth factor
# 
# The growth factor is the multiplier for the number of **new** cases per day. <br>For example, if there are 100 new cases on day *n* and 150 new cases on day *n+1*, the growth factor is 1.5.
# 
# * A growth factor larger than 1 means the outbreak is accelerating; it is growing exponentially.
# * A growth factor of 1 means the outbreak is growing linearly.
# * A growth factor of less than 1 means the outbreak is still growing, but slowing down.
# * A growth factor of 0 means there are no new cases.
# 
# In this plot, the growth factor is averaged over 5 days to smooth out some large day-to-day variations. 

# In[9]:


s=5
countries_to_plot2 = ["China", "South Korea", "United States", "Iran", 
                      "Italy", "Japan", "Germany", "Netherlands", "All except China"]
data.plot("day_number", "growth_factor", countries_to_plot2, min_cases=500, sigma=s, 
          fixed_country_colors=False, use_log_scale=False)    


# ### New confirmed/Active case ratio

# In[10]:


data.plot("day_number", "new confirmed/active", countries_to_plot2, min_cases=500, use_log_scale=1)


# ### Stats for some other countries, using linear scale
# 
# This shows how on a linear Y-axis, it becomes hard to examine the trend in all but the top few countries.

# In[11]:


for y_metric in ["confirmed", "deaths", "active"]:
    data.plot("calendar_date", y_metric, 
         ["Belgium", "Brazil", "Finland", "Malaysia", "India", "Singapore", "Spain", "Vietnam"],
         use_log_scale=False)


# ### Pie charts
# 
# Everybody loves pie charts.

# In[12]:


#for mode in ["country", "continent"]:
#    data.plot_pie(["confirmed cases", "deaths", "active cases"], mode)


# ### Country highlight

# In[13]:


data.country_highlight("Netherlands")


# ## Forecast plots
# 
# First, model the probability distribution of dying after a given number of days.
# 
# We can consider a case recovered if they survive for a long enough time.

# ### Fit a logistic curve and extrapolate number of future cases
# 
# This tries to fit a [logistic](https://en.wikipedia.org/wiki/Logistic_function) or 'S-shape' curve to the data so far. While it is reasonable to expect that the total number of cases in any epidemic will eventually roughly have such a shape, the crucial parameters are difficult to predict. For example, changes in spread rate due to policy changes, or the possibility of a second wave of infections from another country are not captured at all.
# 
# For some countries the results look plausible enough, while for some others it can give extremely unlikely results, like predicting a number of cases that's many times the country's population.

# In[14]:


#data.curve_fit("United States", days=150)
data.curve_fit("Netherlands", days=120)
#data.curve_fit("All except China", days=120)


# ### Modelling fatality probability per day of being infected
# 
# [Source](https://www.mdpi.com/2077-0383/9/2/538).

# In[15]:


death_chance_per_day(cfr=0.03, s=0.8, mu=6.5, sigma=6, length=32, do_plot=True)


# ### Generate history of active cases; how many people have been sick for how long?
# 
# Data on **how long** people have been sick is not available, so it is reconstructed using the assumption that new resolved cases (either death or recovery) always happens to the cases that have been active the longest. In other words, I assume a First-In-First-Out model.

# In[16]:


data.simulate_country_history(country="Netherlands", history_length=7, show_result=True);


# ### Simulate future development based on history and probability models
# 
# Please note that this is very speculative, and highly dependent on:
# 
# * The value chosen for the mitigation factor. Together with R<sub>0</sub>, this represents the effectives of quarantines, lockdowns and other countermeasures, and determines the effective reproductive rate R<sub>eff</sub> . If R<sub>0</sub> is 2, the mitigation factor is 0.8, and 98% of the population has not yet been infected,  
# R<sub>eff</sub> = 2 \* 0.8 \* 0.98 = 1.568. 
# <br><br>The input for mitigation factor is a list that gets interpolated to the same length as the number of days to simulate. <br><br>For example, simulating 5 days with a mitigation trend of `[1.0, 0.8]` will use growth rates of `[1.0, 0.95, 0.90, 0.85, 0.80]`.
# 
# 
# * The value chosen for case fatality rate (cfr); evidence so far suggests a range from 0.01 to 0.06
# 
# 
# Other limitations of the simulation:
# 
# * Doesn't consider incubation time 
# * Doesn't factor in international travel and potential recontamination/reseeding for second and later waves.
# * Doesn't consider effect on death rate when the number of active cases overwhelms capacity (**TODO**)

# In[17]:


M = 0.25              # mitigation effectiveness under major lockdown
W = 0.50              # mitigation effectiveness under weak lockdown
N = 1.00              # mitigation effectiveness under normal conditions

scenarios = {
    "Effective lockdown":   [N,W,M,M,M,M,M,M,M,M,M,M],
    "Ineffective lockdown": [N,N,W],
    "Prolonged battle":     [N,M,W,N,M,W,N,M,W,N,M,W]
}

scenario = "Effective lockdown"
simulation = data.plot_simulation(country="United States", days = 365, 
                                  mitigation_trend=scenarios[scenario], 
                                  cfr=0.03, r0=2.5, scenario_name=scenario)


# In[18]:


scenario = "Ineffective lockdown"
simulation = data.plot_simulation(country="United States", days = 365, 
                                  mitigation_trend=scenarios[scenario], 
                                  cfr=0.02, r0=2.5, scenario_name=scenario)


# In[19]:


scenario = "Prolonged battle"
simulation = data.plot_simulation(country="United States", days = 365, 
                                  mitigation_trend=scenarios[scenario], 
                                  cfr=0.02, r0=2.5, scenario_name=scenario)

