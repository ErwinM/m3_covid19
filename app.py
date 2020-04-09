## import packages
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
from covid19_util import *
from covid19_processing import *
from dash.dependencies import Input, Output
import forecast
from datetime import date

##create static figures for question 1


# get data from JHU
data = Covid19Processing()
data.process(rows=20, debug=False)

# plot deaths and daily growth rate
countries_to_plot = ["Netherlands", "Italy", "Germany", "France", "Spain",
                     "Belgium", "United Kingdom", "China"]
fig_deaths = data.create_growth_figures("deaths",countries_to_plot)
fig_growth = data.create_factor_figure(countries_to_plot)

## create static figures for question 2

# fit model to hospitalizations
forecaster = forecast.forecast_covid19()
forecaster.fit_REIS(cutoff= 30, name = "outlook")
forecaster.fit_REIS(cutoff= 30, name = "previous_forecast", days_back = 1)
forecaster.fit_REIS(cutoff= 30, name = "3d_ago_forecast", days_back = 3)


# get betas from fitted model
factors = forecaster.factors["outlook"]

# get target R to stay below 1900 IC beds
Rtarget = forecaster.determine_Rtarget(name = "outlook")

# set dates
yesterday = str((date.today()-datetime.timedelta(days = 1)).strftime("%d/%m/%Y"))
forecast_day = forecaster.hospitals.iloc[-1,0]

# App definition and authorisation
app = dash.Dash(__name__,
                external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server
app.config['suppress_callback_exceptions'] = True

# Navbar
navbar = dbc.Container(
                        children=[
                    dbc.NavbarSimple(
                            children = [
                                dbc.NavLink("Dashboard", href="/dashboard", id = "dasbhoard-link"),
                                dbc.NavLink("Background", href="/background", id = "background-link")],
                            brand = "M3 Consultancy | COVID dashboard",
                            brand_href="http://m3consultancy.nl",
                            color="#24292e",
                            dark=True,
                            # fluid = True,
                            fixed = "top")
                    ])

##dashboard page
page_1_layout = html.Div([navbar, 
                 dbc.Container([
                    dbc.Jumbotron([
                        dcc.Markdown('''
                            ## COVID19 in NL: how are we doing?
                            Like most, we follow the news on Corona daily. We are bombarded with numbers on deaths, hospitalisations and projections on the availability of IC beds. However, to us, the torrent of daily numbers lack context. Without this context it is hard to make sense of it all. Specifically, we fail to find the answer to our two main questions:

                            1. Are we slowing down the spread of COVID-19 ?
                            
                            2. Will we have enough IC beds?
                           
                            Our dashboard below tries to provide answers to these two questions based on the latest data available. **This dashboard is updated every day at midnight**.
                            ''')],
                        className="m3-jumbo"),
                    dcc.Markdown('''
                        ### Question 1: Are we slowing down the spread of COVID-19 ?
                        COVID19’s spread follows an exponential growth pattern.  Exponential growth is non-intuitive: even when the number of new cases rises daily, we could still be making progress in slowing the spread. We use the following two graphs to determine where we stand today and to what extend our mitigating measures are slowing the spread of the virus.
                        '''),
                    dbc.Container(children=[dcc.Graph(id = 'deaths', figure = fig_deaths)], className="m3-graph"),
                    dcc.Markdown('''
                        Figure 1 shows the growth trajectory of the number of deaths in selected European countries. The y-axis is logaritmic: every major step corresponds to a 10-fold increase. The graph shows that the rise in death toll is slowing down in most European countries. However, there are big differences. The death toll is no longer doubling every 4 days in The Netherlands, Italy, Germany and Spain. In France the death toll appears to still double every 4 days and in the UK the time to double is even shorter. To better understand the rate of growth we should look at figure 2, showing the day-to-day growth of COVID19 deaths.
                        '''),
                    dbc.Container(children=[dcc.Graph(id = 'growth', figure = fig_growth)], className="m3-graph"),
                    dcc.Markdown('''
                        Figure 2 takes the average number of newly reported deaths of the past five days and compares it to the average calculated the day before.  For a country to successfully contain the spread of COVID19, this number needs to drop below 0.
                        '''),
                    dcc.Markdown('''### Question 2: Will we have enough IC beds?
This is not an easy question to answer, as it involves the future. To answer it, we need to forecast both the demand and the availability of IC care in The Netherlands. For the availability we use the latest available information: 2.400 beds will be available, of which 1.900 will be available to patients suffering from COVID19.

To forecast demand, we have created our own, simplified, forecasting model based on the [SEIR model](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SEIR_model).  A key variable in this model is the reproduction rate (R) :  the number of people a person infected with COVID-19 infects.  The bulk of the measures taken in The Netherlands are aimed at lowering this reproduction rate. Lowering R means less people get infected at the same time, which means less people need IC care simultaneously: flattening the curve.

To gauge the effectiveness of measures taken so far and to project their result on IC demand we follow the approach described below.
Based on the available data, our model estimates R for two periods: 
* (i) the initial period when measures were not yet taken and 
* (ii) the suppression period, after the implementation of our “intelligent lockdown” . 
                        '''),

                    dbc.Row([
                                                dbc.Col(dcc.Graph(
                                                            id = 'R0_bar',
                                                            ), md = 10),
                                                dbc.Col(html.Div(children = [dcc.Slider(id = 'I1_slider',
                                                                   vertical = True,
                                                                   verticalHeight = 300,
                                                                   min = 0,
                                                                   max = 2,
                                                                   step = 0.01,
                                                                   value = Rtarget,
                                                                   marks = {
                                                                       0: 'Target = 0',
                                                                       1: 'Target = 1',
                                                                       2: 'Target = 2',
                                                                       3: '3',
                                                                       4: '4'})], style = {"marginTop": "100px"}), md = 2)], className="m3-graph"),
                    dcc.Markdown('''
                    Figure 3 shows our model’s estimate of the reproduction rate during these periods. Figure 3 also includes a ‘Target R’ being the maximum value for R where we still have enough IC capacity available. Figure 4 shows our model’s projection for the corresponding IC demand. Both graphs show our estimate for today and our estimates from the last two days.
                    '''),
                    dcc.Graph(id = 'outlook_figure', className="m3-graph"),
                    dcc.Markdown('''
                    Time lag plays an important role in projecting demand for IC beds. The effects of the NL measures did not have an immediate impact on hospitalisation and IC rates. It takes xx days on average from initial infection to needing IC care and yy days after that before the IC bed is released.  Because of this, the current numbers still include patients which were infected before the NL measures were implemented. As a result, our estimates of R and corresponding IC demand are still changing daily as the share of patients infected before the NL measures declines.
                    
                    To see the impact of different values of R for yourself, you can change the slider next to the graph above and it will show you the effects on IC demand. More interactive results and background on our model can be found on the [background page](/background).
                    '''),
                    html.P(["Number of deaths per country last updated per: ", str((date.today()-datetime.timedelta(days = 1)).strftime("%d/%m/%Y"))], className="m3-footnote"),
                    html.P(["Forecast fitted to hospitalizations in NL up until: ", forecaster.hospitals.iloc[-1,0]], className="m3-footnote")],
                    style = dict(marginTop= "20px", width = "900px"))], style = dict(marginTop= "120px"))

## background page
page_2_layout = html.Div([
                    navbar,
                    dbc.Container([                        
                        dcc.Markdown('''### A model to forecast the COVID-19 outbreak
Modelling the COVID-19 outbreak is a complex endeavour: very little is known about key factors such as the infectious period, incubation time, mortality rate and reproduction rate. Models by any party therefore carry a high amount of uncertainty. This does not mean they should not be made though, as they do provide insight in what direction the outbreak is progressing and are key to supporting decision-makers in their next steps.

To keep ourselves up to date on the latest forecast, we have created our own model to forecast the development of the COVID-19 outbreak. It is a so-called compartmental model, a common approach to modelling epidemics. You can find a good description of a simple compartmental model  [in this video](https://www.youtube.com/watch?v=Qrp40ck3WpI) 
If you are curious as to how we implemented the compartmental model and what parameters we used, have a look at the source code and further descriptions on our  [Github.](https://github.com/ErwinM/m3_covid19) 

To give you an idea of how the model works, Figure 5 outlines the various outcomes of the model and lets you see the impact of changing some of the key input parameters.
                            '''),
                        dcc.Graph(
                                id = 'sensitivity_figure',
                                ),
                        html.P("Choose measures"),
                        dcc.Dropdown(
                                id = 'measure_dropdown',
                                options=[
                                    {'label': 'Patients in hospital', 'value': 'Patients in hospital'},
                                    {'label': 'Patients on IC', 'value': 'Patients on IC'},
                                    {'label': 'Infectious', 'value': 'Infectious'},
                                    {'label': 'Recovered', 'value': 'Recovered'},
                                    {'label': 'Susceptible', 'value': 'Susceptible'}
                                   
                                ],
                                value=['Infectious','Patients in hospital', 'Patients on IC'],
                                multi=True
                            ),  
                        
                        html.P(["Days to forecast"], style = {"marginTop": "10px"}),
                            dcc.Slider(
                                id = 'days_slider',
                                min = 0,
                                max = 800,
                                step = 10,
                                value = 100,
                                marks = {
                                    0: '0',
                                    200: '200',
                                    400: '400',
                                    600: '600',
                                    800: '800'}),
                        html.P(["Reproduction rate after measures"], style = {"marginTop": "10px"}),
                        dcc.Slider(
                                id = 'R_slider',
                                min = 0,
                                max = 2,
                                step = 0.01,
                                value = factors[1]*2.2,
                                marks = {
                                    0: '0',
                                    1: '1',
                                    2: '2',
                                    3: '3',
                                    4: '4'}),
                        html.P(["Incubation time (days)"], style = {"marginTop": "10px"}),
                        dcc.Slider(
                                id = 'Inc_slider',
                                min = 0,
                                max = 8,
                                step = 0.01,
                                value = 5.2,
                                marks = {
                                    0: '0',
                                    2: '2',
                                    4: '4',
                                    6: '6',
                                    8: '8'}),
                        html.P(["Time on IC (days)"], style = {"marginTop": "10px"}),
                        dcc.Slider(
                                id = 'IC_slider',
                                min = 0,
                                max = 40,
                                step = 0.01,
                                value = 21,
                                marks = {
                                    0: '0',
                                    10: '10',
                                    20: '20',
                                    30: '30',
                                    40: '40'}),                            
                        ], 
                    style = {"margin-top":"100px",
                             "margin-bottom":"200px",
                             "width": "900px"})])

## build up app layout
app.layout = html.Div(
    [dcc.Location(id = 'url', refresh = False),
     html.Div(id = 'page-content')])

## interaction for figure 4 with slider
@app.callback(
    Output('outlook_figure', 'figure'),
    [Input('I1_slider', 'value')])
def update_figure1(R):    
    #TO DO: integrate most of this into forecaster class
    # get fitted model
    solution_outlook =  forecaster.forecasts["outlook"]
    solution_prev = forecaster.forecasts["previous_forecast"]
    solution_3d = forecaster.forecasts["3d_ago_forecast"]
    solution_target = forecaster.SEIR_solution(intervention = [(30,factors[0]),(300,R/2.2)])    

    # create data sets for figures with outlook IC utilization and target IC utilization
    y_ic_outlook = solution_outlook["I_ic"] + solution_outlook["I_fatal"] * 0.5
    y_ic_target = solution_target["I_ic"] + solution_target["I_fatal"] * 0.5
    y_ic_previous = solution_prev["I_ic"] + solution_prev["I_fatal"] * 0.5
    y_ic_3d = solution_3d["I_ic"] + solution_3d["I_fatal"] * 0.5
    ic_cap = np.ones(len(y_ic_outlook))*1900
    x_outlook = pd.date_range(start='16/2/2020', periods=len(y_ic_outlook))

    # create figure
    outlook_fig = go.Figure()

    outlook_fig.add_trace(go.Scatter(y=y_ic_3d, x= x_outlook, name = "Forecast 2 days ago", line = dict(color='#e0e0e0', width=2)))
    outlook_fig.add_trace(go.Scatter(y=y_ic_previous, x= x_outlook, name = "Forecast yesterday", line = dict(color='#bfbfbf', width=2)))
    outlook_fig.add_trace(go.Scatter(y=y_ic_outlook, x= x_outlook, name = "Latest forecast", line = dict(color = '#949494')))
    outlook_fig.add_trace(go.Scatter(y=y_ic_target, x= x_outlook, name = "Max R", line = dict(color = 'green')))
    outlook_fig.add_trace(go.Scatter(y=ic_cap, x= x_outlook, name = "ic capacity", line = dict(color='#E21F35', width=2, dash ="dot")))

    # format figure
    outlook_fig.update_layout(
        graph_layout,
        plot_bgcolor='white',
        xaxis_title="Days",
        title = dict(text="Figure 4: Forecast of demand for IC care", font=title_font)
            )
    outlook_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    outlook_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    return outlook_fig 

# interaction for figure 5 with sliders
@app.callback(
    Output('sensitivity_figure', 'figure'),
    [Input('measure_dropdown', 'value'),
     Input('R_slider', 'value'),
     Input('days_slider', 'value'),
     Input('Inc_slider', 'value'),
     Input('IC_slider', 'value'),
     ])
def update_figure1(measures, R, days, inc, IC):    
    #TO DO: integrate most of this into forecaster class

    # get fitted model
    solution_outlook =  forecaster.SEIR_solution(intervention = [(30,factors[0]),(len(forecaster.hospitals),R/2.2), (10000,R/2.2)],
                                                 days = days, t_inc = inc, t_ic = IC)
    solution_outlook["IC_total"] = solution_outlook["I_ic"] + solution_outlook["I_fatal"] * 0.5
    solution_outlook["R_total"] = solution_outlook["R_mild"] + solution_outlook["R_hosp"]  + solution_outlook["R_ic"]  
    solution_outlook["Hosp_tot"] = solution_outlook["I_ic"] + solution_outlook["I_hosp"] + solution_outlook["I_fatal"] 
    x_outlook = pd.date_range(start='16/2/2020', periods=len(solution_outlook))

    # create figure
    outlook_fig = go.Figure()

    for measure in measures:
        outlook_fig.add_trace(go.Scatter(y=solution_outlook[mapping[measure]], x= x_outlook, name = measure))

    # format figure
    outlook_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title="Days",
        title = "Figure 5: Outcome of forecast model, number of people for various parameters"
            )
    outlook_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    outlook_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    return outlook_fig

## interaction for figure 3 with slider
@app.callback(
    Output('R0_bar', 'figure'),
    [Input('I1_slider', 'value')])
def update_figure2(R):
    return forecaster.create_bar(Rtarget = R)

## callback for switching page
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard':
        return page_1_layout
    elif pathname == '/background':
        return page_2_layout
    else:
        return page_1_layout

# serve app
if __name__ == '__main__':
    app.run_server(debug = True)
