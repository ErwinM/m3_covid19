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



# data processing
data = Covid19Processing()
data.process(rows=20, debug=False)



#fetch datasets for dashboard
countries_to_plot = ["Netherlands", "Italy", "Germany", "France", "Spain",
                     "Belgium", "Austria", "United Kingdom"]

fig_deaths = data.create_growth_figures("deaths",countries_to_plot)
fig_confirmed = data.create_growth_figures("confirmed",countries_to_plot)
fig_growth = data.create_factor_figure(countries_to_plot)


# App definition and authorisation
app = dash.Dash(__name__,
                external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server


## html
app.layout = html.Div(
        children=[
                dbc.Container(
                        children=[
                    dbc.NavbarSimple(
                            brand = "M3 Consultancy | COVID dashboard (test version 28-03-2020)",
                            brand_href="#",
                            color="#E21F35",
                            dark=True,
                            # fluid = True,
                            fixed = "top")
                    ]),
                dbc.Container([
                        dbc.Card(
                                dbc.CardBody([
                                        html.H3("28/03/2020: The number of confirmed cases in The Netherlands is below other European countries, but likely impacted by limited testing"),
                                        html.P("Number of confirmed cases per 100.000 starting on first day with more than 1 case per 100.000"),
                                dbc.Container(
                                        children=[
                                                dcc.Graph(
                                                        id = 'confirmed',
                                                        figure = fig_confirmed
                                                        )])])),
                        dbc.Card(
                                dbc.CardBody([
                                        html.H3("28/03/2020: However, numbers of reported deaths indicates COVID outbreak in The Netherlands is progressing averagely"),
                                        html.P("Number of confirmed deaths per 1 Million starting on first day with more than 1 death per 1 Million"),
                                dbc.Container(
                                        children=[
                                                dcc.Graph(
                                                        id = 'deaths',
                                                        figure = fig_deaths
                                                        )])])),
                        dbc.Card(
                                dbc.CardBody([
                                        html.H3("28/03/20: Surpression measures are kicking in throughout Europe, with Dutch day-on-day growth down to 16%"),
                                        html.P("Moving average (5 days) of day-on-day growth % of the number of deaths, starting on first day with more than 1 death per 1 Million"),
                                dbc.Container(
                                        children=[
                                                dcc.Graph(
                                                        id = 'growth',
                                                        figure = fig_growth
                                                        )])]))
                        ], style = dict(marginTop= "50px"))])

if __name__ == '__main__':
    app.run_server(debug = False)
