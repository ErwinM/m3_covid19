## import packages
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import os
import plotly
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas
import sys
is_colab = 'google.colab' in sys.modules
from covid19_util import *
from covid19_processing import *


# data processing
data = Covid19Processing()
data.process(rows=20, debug=False)

#fetch
countries_to_plot = ["China", "Japan", "South Korea", "United States", "Italy", "Iran", "Germany",
                     "France", "Spain", "Netherlands", "United Kingdom", "World", "Belgium"]

confirmed_cases = data.dataframes['confirmed'].groupby(by="Country/Region").sum().reset_index()

fig = go.Figure()

for country in countries_to_plot:    
    try:
        y_country = confirmed_cases[confirmed_cases['Country/Region'] == country].iloc[:,4:].transpose()
        x_country = y_country.index.tolist()
        y_country.columns = [country]
        y_country = y_country[country].values.tolist()
        fig.add_trace(go.Scatter(x=x_country, y=y_country, name = country))
    except:
        continue
        
fig.update_layout(
    plot_bgcolor='white'
)

fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')


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
                            brand = "COVID dashboard",
                            brand_href="#",
                            color="primary",
                            dark=True,
                            fluid = True)
                    ]),
                dbc.Container([
                        dbc.Jumbotron([
                                html.H1("Landing page for dashboard"),
                                html.P("Initial dashboard with some text")])
                    ]),
                dbc.Container(
                        children=[
                                dcc.Graph(
                                        id = 'confirmed',
                                        figure = fig
                                        )
                                ])
])

if __name__ == '__main__':
    app.run_server(debug = True)
