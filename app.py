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
countries_to_plot = ["Netherlands", "Italy", "Germany", "France", "Spain",
                     "Belgium", "Austria", "United Kingdom"
                     ]

confirmed_cases = data.dataframes['confirmed_by_country']


fig = go.Figure()

for country in countries_to_plot:    
    try:
        population = data.country_metadata[country]["population"]
        y_country = confirmed_cases[confirmed_cases.index == country].iloc[:,4:].transpose()
#        x_country = y_country.index.tolist()
        y_country.columns = [country]
        y_country = y_country[y_country[country]/population*100000 > 1]
        y_country = np.array(y_country[country].values.tolist())/population*100000
        if country == "Netherlands" :
            fig.add_trace(go.Scatter(y=y_country, name = country, line = dict(width = 6)))
        else:
            fig.add_trace(go.Scatter(y=y_country, name = country))
    except:
        continue
        
fig.update_layout(
    plot_bgcolor='white',
    xaxis_title="Days",
    yaxis_title="Cases",
    yaxis_type = "log"
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
                            brand = "M3 Consultancy | COVID dashboard",
                            brand_href="#",
                            color="#E21F35",
                            dark=True,
                            fluid = True)
                    ]),
                dbc.Container([
                        dbc.Card(
                                dbc.CardBody([
                                        html.H3("So far, development of confirmed cases in The Netherlands has been similar to other European countries"),
                                        html.P("Number of confirmed cases per 100.000 starting on first day with more than 1 case per 100.000"),
                                dbc.Container(
                                        children=[
                                                dcc.Graph(
                                                        id = 'confirmed',
                                                        figure = fig
                                                        )])]))])])

if __name__ == '__main__':
    app.run_server(debug = True)
