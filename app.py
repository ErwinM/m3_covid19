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

## Navbar
navbar = dbc.Container(
                        children=[
                    dbc.NavbarSimple(
                            children = [
                                dbc.NavLink("Dashboard", href="/dashboard", id = "dasbhoard-link"),
                                dbc.NavLink("Background", href="/background", id = "background-link")],
                            brand = "M3 Consultancy | COVID dashboard",
                            brand_href="/dashboard",
                            color="#E21F35",
                            dark=True,
                            # fluid = True,
                            fixed = "top")
                    ])

##dashboard page
page_1_layout = html.Div([navbar, 
                 dbc.Container([
                     dbc.Jumbotron([html.H2("How to make sense of COVID-19 figures in The Netherlands?"),
                                        html.P("""
                                               Anyone following the news in the last weeks is confronted with a lot and mostly worrying figures every day: 
                                               a new number of confirmed COVID-19 cases, the daily death toll, the number of hospitalizations, number 
                                               of IC patients, the number of recoveries, number of positive tests and much more. We ourselves got 
                                               a bit flustered by all the data presented to us on a daily basis and decided to create just a couple 
                                               of graphs to keep track of the situation, with two major questions in mind:  
                                               """),
                                        html.Ul([html.P("1.  Is the spread of COVID-19 slowing down?"),
                                                 html.P("2.  Is there going to be enough IC capacity to help everyone in need?")]),
                                        html.P("""
                                               The dashboard below tries to help you get a grip on these two questions as the situation evolves.
                                               It is therefore updated daily at midnight to have the latest figures at hand. 
                                               """)
                                        ],  className="m3-jumbo"),
                                        html.H3("Question 1: Is the spread of COVID-19 slowing down?"),
                                        html.P("""
                                               Epidemic spread of a disease follows an exponential growth pattern. Meaning that as long as everyone that
                                               gets the disease passes it on to more than 1 other person on, the number of newly infected people people will
                                               grow every day and reach scarily high numbers very fast.
                                               """, className="m3-soft"),
                                               
                                        html.P("""
                                               To see if measures to stop the growth are succesful, we could look at a few figures:
                                               the number of confirmed cases, hospitalizations or death toll for example. Measurement of these figures
                                               is distorted by the amount of tests executed in each country, even for the number of deaths. However, we can
                                               compare the trajectory of the latter between various countries to get an idea of whether or not the
                                               virus is still spreading exponentially or not.                                               
                                               """),

                                        dbc.Container(
                                            children=[
                                                dcc.Graph(
                                                        id = 'deaths',
                                                        figure = fig_deaths
                                                        )]),
                                        html.P("""
                                               Figure 1 shows the growth trajectory of the number of deaths in several European countries. 
                                               The axis are logaritmic, meaning that every major step in the axis corresponds to a 10-fold increase.
                                               We can see here that most European countries have moved away from the scenario where
                                               the number of deaths increases with a two-fold every day. To see more clearly how fast the number
                                               of deaths is still growing we should look at figure 2, which shows the day-to-day growth rate of 
                                               the new number of deaths. 
                                               """),
                                        dbc.Container(
                                            children=[
                                                dcc.Graph(
                                                        id = 'growth',
                                                        figure = fig_growth
                                                        )]),
                                        html.P("""
                                               Figure 2 takes the average number of newly reported deaths of the past 
                                               five days and compares it to the average calculated yesterday. If this number drops to 0 or below, the
                                               spread of COVID-19 has been stabilized and is no longer growing exponentially. 
                                               """),
                                        html.H3("Question 2: Is there going to be enough IC capacity for everyone in need?"),
                                        html.P("""
                                               This is not an easy question to answer, as it involves forecasting the amount of
                                               people that need ICU care. ICU capacity in the Netherlands constrainted to ultimately
                                               2400 beds, of which 500 beds are needed for regular patients.   
                                               """),
                                       html.P("""    
                                               
                                               The RIVM provides us with new forecasts on a weekly basis, so to keep ourselves updated
                                               in the meantime we have created a forecasting model similar to the models 
                                               used by the RIVM, albeit a simplified version of course. 
                                               """
                                               ),
                                       html.P("""
                                               The main factor in these models is the reproduction rate (R) which corresponds to 
                                               the amount of other people everyone with COVID-19 infects. We have estimated this
                                               number R for two periods: (i) the ramp up period when no measures were yet taken and
                                               (ii) the surpression period, after implementation of "intelligent lockdown" in NL. 
                                               Figure 3 shows our estimations of the reproduction rate in these periodes as well as the rate
                                               we need for the amount of IC patients to stay below 1900. 
                                               """),
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
                                                                       4: '4'})], style = {"marginTop": "100px"}), md = 2)]),
                                        html.P("""
                                               To see when a peak in ICU patients would occur, we have also modelled the development
                                               of patients over time. Figure 4 shows the expected number of ICU patients from our model. 
                                               Changing the above slider will show you the effect of reaching a certain average reproduction rate.
                                               """),
                                        dcc.Graph(
                                                    id = 'outlook_figure',
                                                    ),
                                        html.P(["Number of deaths per country last updated per: ", str((date.today()-datetime.timedelta(days = 1)).strftime("%d/%m/%Y"))], style = {"fontSize":"70%"}),
                                        html.P(["Forecast fitted to hospitalizations in NL up until: ", forecaster.hospitals.iloc[-1,0]], style = {"fontSize":"70%"})],
                                                style = dict(marginTop= "20px",
                                                             width = "900px"))], style = dict(marginTop= "120px"))

## background page
page_2_layout = html.Div([
                    navbar,
                    dbc.Container([                        
                        html.H3("A model to forecast the COVID-19 outbreak"),
                        html.P(
                            """
                            Modelling the COVID-19 outbreak is a complex endeavour: very little is known
                            about key factors such as the infectious period, incubation time, mortality rate
                            and reproduction rate. Models by any party therefore carry a high amount of 
                            uncertainty. This does not mean they should not be made though, as they do 
                            provide insight in what direction the outbreak is progressing and are key to 
                            supporting decision-makers in their next steps. 
                            """),
                        html.P([
                            """
                            To keep ourselves up to date on the latest forecast, we have created our own
                            model to forecast the development of the COVID-19 outbreak. It is a so-called 
                            compartmental model, a common approach to modelling epedemics. You can find a good
                            description of a simple compartmental model        
                            """, 
                            html.A(" in this video", href = "https://www.youtube.com/watch?v=Qrp40ck3WpI", target = "_blank")]
                            ),
                        html.P([
                            """
                            If you are curious as to how we implemented the compartmental model and what parameters we used,
                            have a look at the source code and further descriptions on our 
                            """,
                            html.A("Github.", href = "https://github.com/ErwinM/m3_covid19", target = "_blank")]),
                        html.P(
                            """
                            To give you an idea of how the model works, Figure 5 outlines the various outcomes of the model
                            and lets you see the impact of changing some of the key input parameters. 
                            """),
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
                    style = {"marginTop":"100px",
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
    outlook_fig.add_trace(go.Scatter(y=y_ic_3d, x= x_outlook, name = "Forecast 3 days ago",
                                     line = dict(color='Lightgrey', width=2, dash='dot')))
    outlook_fig.add_trace(go.Scatter(y=y_ic_previous, x= x_outlook, name = "Forecast yesterday",
                                     line = dict(color='grey', width=2, dash='dot')))
    outlook_fig.add_trace(go.Scatter(y=y_ic_outlook, x= x_outlook, name = "Latest forecast",
                                     line = dict(color = 'grey')))
    outlook_fig.add_trace(go.Scatter(y=y_ic_target, x= x_outlook, name = "Target",
                                     line = dict(color = 'green')))
    outlook_fig.add_trace(go.Scatter(y=ic_cap, x= x_outlook, name = "ic capacity",
                                 line = dict(color='lightblue', width=2)))

    # format figure
    outlook_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title="Days",
        title = "Figure 4: Forecast of IC utilization"
            )
    outlook_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    outlook_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    return outlook_fig 

## interaction for figure 5 with sliders
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
        title = "Figure 5: Outcome of forecast model, number of people for various measures"
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
    app.run_server(debug = False)
    



