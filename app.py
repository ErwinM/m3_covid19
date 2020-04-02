## import packages
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
import pandas
import sys
from covid19_util import *
from covid19_processing import *
from dash.dependencies import Input, Output
import working_model
import model_fit as mf

# get data for question 1
data = Covid19Processing()
data.process(rows=20, debug=False)

# fit effective R for question 2, fix factors for speedup
factors = mf.fit_REIS(30)
# factors = [1.73919508, 0.4360855]
hospital = pd.read_csv("hospitalizations.csv", sep = ";")

#create figures for question 1
countries_to_plot = ["Netherlands", "Italy", "Germany", "France", "Spain",
                     "Belgium", "United Kingdom", "China"]
fig_deaths = data.create_growth_figures("deaths",countries_to_plot)
fig_confirmed = data.create_growth_figures("confirmed",countries_to_plot)
fig_growth = data.create_factor_figure(countries_to_plot)

# create bar chart for question 2
Rinitial = 1.73919508 * 2.2
Ractual = factors[1] * 2.2
Rtarget = 1
barnames = ["Estimated R before measures", "Latest estimate of R after measures", "Target to stay below IC capacity"]
effective_R = go.Bar(y= [Rinitial, Ractual, Rtarget], x = barnames, name = "Reproduction rate (R)")
repression_data = go.Bar(y= [0, Rinitial- Ractual, Rinitial-Rtarget], x = barnames, name = "Surpression of R from lockdown", marker_color = "LightGrey")
fig_bar = go.Figure(data = [effective_R, repression_data])
fig_bar.update_layout(barmode='stack')
fig_bar.update_layout(
    plot_bgcolor='white',
    title = "Figure 3: development of effective reproduction rate (R)")       

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
                                dbc.NavLink("Dashboard", href="/page-1", id = "page-1-link"),
                                dbc.NavLink("Background", href="/page-2", id = "page-2-link")],
                            brand = "M3 Consultancy | COVID dashboard",
                            brand_href="/page-1",
                            color="#E21F35",
                            dark=True,
                            # fluid = True,
                            fixed = "top")
                    ])

#page 1 with current situation
page_1_layout = html.Div([navbar, 
                 dbc.Container([
                        dbc.Jumbotron( [html.H2("How to make sense of COVID-19 figures in The Netherlands?"),
                                        html.P("""
                                               Anyone following the news in the last weeks is confonted with a lot and mostly worrying figures every day: 
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
                                               """)]),
                        dbc.Card(
                                dbc.CardBody([
                                        html.H3("Question 1: Is the spread of COVID-19 slowing down?"),
                                        html.P("""
                                               Epidemic spread of a disease follows an exponential growth pattern. Meaning that as long as everyone that
                                               gets the disease passes it on to more than 1 other person on, the number of newly infected people people will
                                               grow every day and reach scarily high numbers very fast.
                                               """),
                                               
                                        html.P("""
                                               To see if measures to stop the growth are succesfully, we could look at a few figures:
                                               the number of confirmed cases, hospitalizations and death toll. Measurement of all these figures
                                               is distorted by the amount of tests executed, even for the number of deaths. However, we can
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
                                               We can see here that indeed most European countries have moved away from the scenario where
                                               the number of deaths increases with a two-fold every day. To see more clearly how fast the number
                                               of deaths is still growing we should look at figure 2, which shows the day on day growth rate of 
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
                                               five days and compares it to the average calculated yesterday. If this number drops to 0 or below, this means
                                               spread of COVID-19 has been stabilized and is no longer growing exponentially. 
                                               """)])),
                            dbc.Card([
                                dbc.CardBody([
                                        html.H3("Question 2: Is there going to be enough IC capacity for everyone in need?"),
                                        html.P("""
                                               This is not an easy question to answer, as it involves forecasting the amount of
                                               people that need ICU care. ICU capacity in the Netherlands constrainted to ultimately
                                               2400 beds, of which 500 beds are needed for regular patients.   
                                               """),
                                       html.P("""    
                                               
                                               The RIVM provides us with new forecasts on a weekly basis, so to keep ourselves updated
                                               in the meantime we have created a simplified forecasting model similar to the models 
                                               used by the RIVM. 
                                               """
                                               ),
                                       html.P("""
                                               The main factor in these models is the reproduction rate (R) which corresponds to 
                                               the amount of other people everyone with COVID-19 infects. We have estimated this
                                               number R for two periods: (i) the ramp up period when no measure were yet taken and
                                               (ii) the surpression period, after implementation of "intelligent lockdown" in NL. 
                                               Figure 3 shows our estimations of R in these periodes as well as the amount of 
                                               surpression needed for the amount of IC patients to stay below 1900. 
                                               """),
                                        dbc.Container(
                                            children=[
                                                dcc.Graph(
                                                            id = 'R0_bar',
                                                            figure = fig_bar
                                                            ),
                                                html.P("""
                                               To see when the peak in ICU patients would happen, we have also modelled the development
                                               of outbreak over time. Figure 4 shows the expected develpment of the number of ICU patients
                                               from our model. You can see the impact of changing the reproduction rate R by moving the
                                               slider. 
                                               """),
                                                dcc.Graph(
                                                            id = 'outlook_figure',
                                                            ),
                                                html.P("Change value of the effective reproduction number (R) as of today to see impact on number of infections:"),
                                                html.Div([
                                                dcc.Slider(id = 'I1_slider',
                                                               min = 0,
                                                               max = 2,
                                                               step = 0.1,
                                                               value = Ractual,
                                                               marks = {
                                                                   0: '0',
                                                                   1: '1',
                                                                   2: '2',
                                                                   3: '3',
                                                                   4: '4'})], style = {'width': '70%'})])])], style = dict(marginTop= "20px"))
                            ], style = dict(marginTop= "20px"))])

# page two with background
page_2_layout = html.Div(navbar)

# full app layout
app.layout = html.Div(
    [dcc.Location(id = 'url', refresh = False),
     html.Div(id = 'page-content')])

# interactivity is handled by callbacks. Used here to let graph interact with slider
@app.callback(
    Output('outlook_figure', 'figure'),
    [Input('I1_slider', 'value')])
def update_figure(R):
    # get fitted model
    solution =  working_model.SEIR_solution(intervention = [(30,factors[0]),(len(hospital),factors[1]), (300,R/2.2)], e0 = 20)
    # create figure
    y_outlook = (solution["I_ic"]+solution["I_hosp"]+solution["R_ic"]+solution["R_hosp"]+0.5*solution["I_fatal"]+0.5*solution["R_fatal"])
    # y_actual = hospital.iloc[:,1]
    y_ic = solution["I_ic"] + solution["I_fatal"] * 0.5
    ic_cap = np.ones(len(y_outlook))*1900
    x_outlook = pd.date_range(start='16/2/2020', periods=len(y_outlook))
    outlook_fig = go.Figure()
    outlook_fig.add_trace(go.Scatter(y=ic_cap, x= x_outlook, name = "ic capacity",
                                     line = dict(color='Lightgrey', width=2, dash='dot')))
    # outlook_fig.add_trace(go.Scatter(y=y_outlook, x= x_outlook, name = "model hospitalizations"))
    # outlook_fig.add_trace(go.Scatter(y=y_actual, x= x_outlook, name = "actual hospitalizations"))
    outlook_fig.add_trace(go.Scatter(y=y_ic, x= x_outlook, name = "model IC beds needed"))
    outlook_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title="Days",
        title = "Figure 4: Forecast of IC utilization"
            )
    outlook_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    outlook_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    return outlook_fig 

## callback for switching page
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return page_1_layout

# serve app 
if __name__ == '__main__':
    app.run_server(debug = False)
    


