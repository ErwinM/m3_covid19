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
app.config['suppress_callback_exceptions'] = True

# Navbar
navbar = dbc.Container(
                        children=[
                    dbc.NavbarSimple(
                            children = [
                                dbc.NavLink("Current situation", href="/page-1", id = "page-1-link"),
                                dbc.NavLink("Outlook", href="/page-2", id = "page-2-link")],
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

# page two with forecast
page_2_layout = html.Div([navbar,
                 dbc.Container([
                        dbc.Card(
                                dbc.CardBody([
                                        html.H3("Number of infections strongly impacted by basic reproduction number"),
                                        html.P("Number of infectious and exposed people starting with 50 infections"),
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
                                                               4: '4'})], style = {'width': '70%'})])]))]
                     , style = dict(marginTop= "50px"))])

## html
app.layout = html.Div(
    [dcc.Location(id = 'url', refresh = False),
     html.Div(id = 'page-content')])

@app.callback(
    Output('outlook_figure', 'figure'),
    [Input('r_slider', 'value')])
def update_figure(R):
    solution = solve_SEIR(R, 2.9 , 5.2 ,  14 ,7000000)
    outlook_fig = go.Figure()
    y_outlook = solution[:,1]
    y_outlook2 = solution[:,2]
    outlook_fig.add_trace(go.Scatter(y=y_outlook, name = "exposed"))
    outlook_fig.add_trace(go.Scatter(y=y_outlook2, name = "infectious"))
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
