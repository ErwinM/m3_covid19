## import packages
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import os
import plotly
import dash_bootstrap_components as dbc



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
                    ])
])

if __name__ == '__main__':
    app.run_server(debug = True)
