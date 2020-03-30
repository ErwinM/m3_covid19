## import packages
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import os
import plotly
import dash_bootstrap_components as dbc
import pandas
import sys
is_colab = 'google.colab' in sys.modules
from covid19_util import *
from covid19_processing import *
from dash.dependencies import Input, Output
import working_model


# data processing
data = Covid19Processing()
data.process(rows=20, debug=False)



#fetch datasets for dashboard
countries_to_plot = ["Netherlands", "Italy", "Germany", "France", "Spain",
                     "Belgium", "United Kingdom", "China"]
fig_deaths = data.create_growth_figures("deaths",countries_to_plot)
fig_confirmed = data.create_growth_figures("confirmed",countries_to_plot)
fig_growth = data.create_factor_figure(countries_to_plot)


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
                                               the number of confirmed cases, hospitalizations and death toll. We consider the death toll to be the most
                                               reliable figure by which we can compare the situation in The Netherlands with other European countries as
                                               well.
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
                                        html.P("<Decription of SEIR model here>"),
                                        dbc.Container(
                                            children=[
                                                dcc.Graph(
                                                            id = 'outlook_figure',
                                                            ),
                                                html.P("Change value of the basic reproduction number (R_0) to see impact on number of infections:"),
                                                html.Div([
                                                dcc.Slider(id = 'r_slider',
                                                               min = 0,
                                                               max = 4,
                                                               step = 0.1,
                                                               value = 2.2,
                                                               marks = {
                                                                   0: '0',
                                                                   1: '1',
                                                                   2: '2',
                                                                   3: '3',
                                                                   4: '4'})], style = {'width': '70%'})])])], style = dict(marginTop= "20px"))
                            ], style = dict(marginTop= "20px"))])

# page two with forecast
page_2_layout = html.Div(navbar)

## html
app.layout = html.Div(
    [dcc.Location(id = 'url', refresh = False),
     html.Div(id = 'page-content')])

@app.callback(
    Output('outlook_figure', 'figure'),
    [Input('r_slider', 'value')])
def update_figure(R):
    solution =  working_model.SEIR_solution(N = 17000000, e0 = 0, i0 = 100 , r0 = 0,
                  R0 = R, intervention = [(20,1), (300,0.3)],
                  t_inc = 5.2, t_inf = 3)
    list_of_measures = ['I_total','I_ic', 'R_fatal']
    outlook_fig = go.Figure()
    mapping = {"I_total": "Infectious", "I_ic": "On intensive care", "R_fatal": "Deaths"}
    for measure in list_of_measures:
        y_outlook = solution[measure]
        x_outlook = solution['day']
        outlook_fig.add_trace(go.Scatter(y=y_outlook, x= x_outlook, name = mapping[measure]))
        outlook_fig.update_layout(
            plot_bgcolor='white',
            xaxis_title="Days",
            )
    outlook_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    outlook_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    return outlook_fig 


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return page_1_layout


if __name__ == '__main__':
    app.run_server(debug = False)
    


