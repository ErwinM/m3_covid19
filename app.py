## import packages
import os
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
import dash_table

# get data from JHU
data = Covid19Processing()
data.process(rows=20, debug=False)
data.list_countries()
params = pd.read_csv("params.csv", sep = ";")

# fit model to hospitalizations
forecaster = forecast.forecast_covid19()
forecaster.get_NICE_data()
forecaster.fit_REIS(cutoff= 30, name = "outlook")
forecaster.fit_REIS(cutoff= 30, name = "previous_forecast", days_back = 7)
forecaster.fit_REIS(cutoff= 30, name = "3d_ago_forecast", days_back = 14)

# get betas from fitted model
factors = forecaster.factors["outlook"]

# get target R to stay below 1900 IC beds
Rtarget = forecaster.determine_Rtarget(name = "outlook")

# set dates
yesterday = str((date.today()-datetime.timedelta(days = 1)).strftime("%d/%m/%Y"))
forecast_day = forecaster.hospitals.iloc[-1,0]

## dash app
# App definition and authorisation
app = dash.Dash(__name__,
                external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server
app.config['suppress_callback_exceptions'] = True
app.title = "M3 COVID Dashboard"

# Navbar
navbar =\
dbc.Container([
    dbc.NavbarSimple([
        dbc.NavLink("Dashboard", href="/dashboard", id = "dasbhoard-link"),
        dbc.NavLink("Background", href="/background", id = "background-link")],
        brand = "M3 Consultancy | COVID dashboard",
        brand_href="http://m3consultancy.nl",
        color="#24292e",
        dark=True,
        # fluid = True,
        fixed = "top")
                ])

# Dashboard page
page_1_layout = \
html.Div([navbar,
    dbc.Container([
        dbc.Jumbotron([
            dcc.Markdown('''
                ## Fighting COVID19 in NL: how are we doing?
                Like most, we follow the news on COVID19 daily. We are bombarded with numbers on deaths, hospitalisations and availability of IC beds. However, to us, this torrent of daily numbers lacks context. Without context it is hard to make sense of it all. We built a live dashboard that tries to answer two questions:

                1. Are we slowing down the spread?

                2. Will we have enough IC beds?

                Of course, the weekly RIVM briefing answer these same questions. Our dashboard tries to answers them every day based on the latest data available. **Our dashboard is updated every day at midnight**.
                ''')],
               className="m3-jumbo"),
        dcc.Markdown('''
           ### Question 1: Are we slowing down the spread ?
           COVID19’s spread follows an exponential growth pattern.  Exponential growth is non-intuitive: even when the number of new cases rises daily, we could still be making progress in slowing the spread. We use the following two graphs to determine where we stand today and to what extend our mitigating measures are slowing the spread of the virus.
           '''),
        dbc.Container([
            dcc.Graph(id = 'deaths', ),
            dcc.Dropdown(
                id = 'country_dropdown',
                options= data.option_list,
                value=["Netherlands", "Italy", "Germany", "France", "Spain",
                         "Belgium", "United Kingdom"],
                multi=True)],className = "m3-graph"),
        dcc.Markdown('''
           Figure 1 is a widely used and useful graph: it shows the growth trajectory of the number of deaths in selected European countries. The y-axis is logaritmic: every major step corresponds to a 10-fold increase. We have selected several other European countries to compare with The Netherlands.

           The graph shows that the rise in death toll is slowing down in most European countries. The curves are bending away from exponential growth. However, this graph lacks the detail required to place the daily numbers into context. Figure 2 drills into the underlying growth rates.
           '''),
        dbc.Container(children=[dcc.Graph(id = 'growth', )], className="m3-graph"),
        dcc.Markdown('''
           Figure 2 takes the average number of newly reported deaths of the past seven days and compares it to the average calculated the day before.  For a country to successfully contain the spread of COVID19, this line needs to drop below 0.
           '''),
        dcc.Markdown('''
           ### Question 2: Will we have enough IC beds?
           This is not an easy question to answer, as it involves the future. To answer it, we need to forecast both the demand and the availability of IC care in The Netherlands. For availability we use the latest available information: 2.400 beds, of which 1.900 will be available to patients suffering from COVID19.

           To forecast demand, we have created our own, simplified, forecasting model based on the [SEIR model](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SEIR_model).  A key variable in this model is the reproduction rate (R): the number of people a person infected with COVID-19 infects. The bulk of the measures taken in The Netherlands are aimed at lowering R. A lower R means less people get infected at the same time, which means less people need IC care simultaneously, thus flattening the curve.

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
        Figure 3 shows our model’s estimate of the reproduction rate during both periods. Figure 4 shows our model’s projection for the corresponding IC demand. Both graphs show our estimate for today and our estimates from the last two weeks. The latest forecast is based on hospitalizations up until 5 days ago, as it takes a while for hospitals to report.
        '''),
        dcc.Graph(id = 'outlook_figure', className="m3-graph"),
        dcc.Markdown('''
        Time-lag plays an important role in projecting demand for IC beds. The effects of the NL measures did not have an immediate impact on hospitalisation and IC rates. It takes roughly 2 weeks from initial infection to needing IC care and 3 weeks after that before the IC bed is released.  Because of this, current numbers still include patients which were infected before measures were implemented. As a result, our estimates of R and corresponding IC demand still change daily as the share of patients infected before the NL measures declines.

        To simulate the impact of different values of R for yourself, you can change the slider next to Figure 3 and see the corresponding effects on IC demand in Figure 4. More interactive results and background on our model can be found on the [background page](/background). 

        If you have any questions or comments, we would love to here them. Send an email to [Gijs](mailto:gijs@m3consultancy.nl) or [Erwin](mailto:erwin@m3consultancy.nl).
        '''),
        html.P(["Number of deaths per country. Source: John Hopkins University. lastly retrieved per: ",
                str(date.today().strftime("%d/%m/%Y"))+" 00:00 CET"],
               className="m3-footnote"),
        html.P(["Forecast based on hospitalizations in the Netherlands from RIVM, data used up until: ",
                forecaster.hospitals.iloc[-1,0]],
               className="m3-footnote"),
        html.P(["Actual IC patients from NICE, data used up until: ",
                forecaster.hospitals.iloc[-1,0]],
               className="m3-footnote")],
                     style = dict(marginTop= "20px", width = "900px"))],
style = dict(marginTop= "120px"))

## Background page
page_2_layout = \
html.Div([
    navbar,
    dbc.Container([
        dcc.Markdown('''
            ### A model to forecast the COVID-19 outbreak
            Modelling the COVID-19 outbreak is a complex endeavour: very little is known about key factors such as the infectious period, incubation time, mortality rate and reproduction rate. Models therefore carry a high amount of uncertainty. This does not mean they should not be made, as they do provide insight in what direction the outbreak is progressing and are key to supporting decision-makers in their next steps.

            To keep ourselves up to date on the latest forecast, we have created our own model to forecast the development of the COVID-19 outbreak. It is a so-called compartmental model and more specifically [a SEIR model](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SEIR_model), a common approach to modelling epidemics. You can find a good description of a simple compartmental model  [in this video](https://www.youtube.com/watch?v=Qrp40ck3WpI)
            If you are curious how we implemented the compartmental model, have a look at the source code [Github](https://github.com/ErwinM/m3_covid19). The parameters our model uses can be found [here](https://github.com/ErwinM/m3_covid19/blob/master/parameters.py).
            '''),
        dcc.Markdown('''
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
            multi=True,
            className="m3-graph"),
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
        html.P(["Reproduction rate after measures"],
               style = {"marginTop": "10px"}),
        dcc.Slider(
            id = 'R_slider',
            min = 0,
            max = 2,
            step = 0.1,
            value = factors[1]*2.2,
            marks = {
                0: '0',
                1: '1',
                2: '2',
                3: '3',
                4: '4'}),
        html.P(["Incubation time (days)"],
               style = {"marginTop": "10px"}),
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
        html.P(["Time on IC (days)"],
               style = {"marginTop": "10px"}),
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
        ], style = {"margin-top":"100px",
             "margin-bottom":"200px",
             "width": "900px"})])

# Build up app layout
app.layout = html.Div(
                [dcc.Location(id = 'url', refresh = False),
                 html.Div(id = 'page-content')])


# callback for adding countries to figure 1
@app.callback(
    Output('deaths', 'figure'),
    [Input('country_dropdown', 'value')])
def update_figure3(options):
    data = Covid19Processing()
    data.process(rows=20, debug=False)
    data.list_countries()
    return data.create_growth_figures("deaths",options)

# callback for adding countries to figure 2
@app.callback(
    Output('growth', 'figure'),
    [Input('country_dropdown', 'value')])
def update_figure4(options):
    data = Covid19Processing()
    data.process(rows=20, debug=False)
    data.list_countries()
    return data.create_factor_figure(options)

# interaction for figure 3 with slider
@app.callback(
    Output('R0_bar', 'figure'),
    [Input('I1_slider', 'value')])
def update_figure2(R):
    return forecaster.create_bar(Rtarget = R)

# interaction for figure 4 with slider
@app.callback(
    Output('outlook_figure', 'figure'),
    [Input('I1_slider', 'value')])
def update_figure1(R):
    #TO DO: integrate most of this into forecaster class
    # get fitted model
    solution_outlook =  forecaster.forecasts["outlook"]
    solution_prev = forecaster.forecasts["previous_forecast"]
    solution_3d = forecaster.forecasts["3d_ago_forecast"]
    solution_target = forecaster.SEIR_solution(intervention = [(30,factors[0]),
                                                               (300,R/2.2)])

    # create data sets for figures with outlook IC utilization
    y_ic_outlook = solution_outlook["I_ic"] + solution_outlook["I_fatal"] * 0.5
    y_ic_target = solution_target["I_ic"] + solution_target["I_fatal"] * 0.5
    y_ic_previous = solution_prev["I_ic"] + solution_prev["I_fatal"] * 0.5
    y_ic_3d = solution_3d["I_ic"] + solution_3d["I_fatal"] * 0.5
    ic_cap = np.ones(len(y_ic_outlook))*1900
    ic_min = np.ones(len(y_ic_outlook))*700
    x_outlook = pd.date_range(start='16/2/2020', periods=len(y_ic_outlook))

    # create figure
    outlook_fig = go.Figure()
    outlook_fig.add_trace(go.Scatter(y=y_ic_3d,
                                     x= x_outlook,
                                     name = "Forecast 2 weeks ago",
                                     line = dict(color='#e0e0e0', width=2),
                                     hovertemplate = '%{x}, '+'%{y:.0f}'))
    outlook_fig.add_trace(go.Scatter(y=y_ic_previous,
                                     x= x_outlook,
                                     name = "Forecast last week",
                                     line = dict(color='#bfbfbf', width=2),
                                     hovertemplate = '%{x}, '+'%{y:.0f}'))
    outlook_fig.add_trace(go.Scatter(y=y_ic_outlook,
                                     x= x_outlook,
                                     name = "Latest forecast",
                                     line = dict(color = '#949494'),
                                     hovertemplate = '%{x}, '+'%{y:.0f}'))
    outlook_fig.add_trace(go.Scatter(y=y_ic_target,
                                     x= x_outlook,
                                     name = "R Target",
                                     line = dict(color = 'green'),
                                     hovertemplate = '%{x}, '+'%{y:.0f}'))
    outlook_fig.add_trace(go.Scatter(
                                    y=forecaster.ic_actuals,
                                    x= x_outlook,
                                    name = "Actual (COVID) IC patients",
                                    line = dict(color='black', width=2),
                                    mode = 'markers',
                                    hovertemplate = '%{x}, '+'%{y:.0f}'))
    outlook_fig.add_trace(go.Scatter(
                                y=ic_cap,
                                x= x_outlook,
                                name = "ic capacity",
                                line = dict(color='#E21F35', width=2, dash ="dot"),
                                showlegend=False,
                                hovertemplate = '%{x}, '+'%{y:.0f}'))
    outlook_fig.add_trace(go.Scatter(
                                y=ic_min,
                                x= x_outlook,
                                name = "short term objective",
                                line = dict(color='green', width=2, dash ="dot"),
                                showlegend=False,
                                hovertemplate = '%{x}, '+'%{y:.0f}'))
    outlook_fig.add_annotation(annotation_layout,
                               x=(date.today()-datetime.timedelta(days = 50)),
                               y=1870,
                               text="Max IC capacity")
    outlook_fig.add_annotation(annotation_layout,
                               x=(date.today()+datetime.timedelta(days = 10)),
                               y=700,
                               text="Normalized IC occupation")

    # format figure
    outlook_fig.update_layout(
        graph_layout,
        plot_bgcolor='white',
        xaxis_title="Days",
        title = dict(text="Figure 4: Forecast of demand for IC care",
                     font=title_font)
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
    solution_outlook =\
        forecaster.SEIR_solution(intervention = \
                                    [(30,factors[0]),
                                     (len(forecaster.hospitals),
                                      R/2.2), (10000,R/2.2)],
                                days = days,
                                t_inc = inc,
                                t_ic = IC)
    solution_outlook["IC_total"] = solution_outlook["I_ic"] + \
                                    solution_outlook["I_fatal"] * 0.5
    solution_outlook["R_total"] = solution_outlook["R_mild"] +\
                                    solution_outlook["R_hosp"]  +\
                                    solution_outlook["R_ic"]
    solution_outlook["Hosp_tot"] = solution_outlook["I_ic"] +\
                                    solution_outlook["I_hosp"] +\
                                    solution_outlook["I_fatal"]
    x_outlook = pd.date_range(start='16/2/2020',
                              periods=len(solution_outlook))

    # create figure
    outlook_fig = go.Figure()

    for measure in measures:
        outlook_fig.add_trace(
            go.Scatter(y=solution_outlook[mapping[measure]],
                       x= x_outlook,
                       name = measure,
                       hovertemplate = '%{y:.0f}'))

    # format figure
    outlook_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title="Days",
        title = """Figure 5: Outcome of forecast model,
        number of people for various parameters"""
            )
    outlook_fig.update_xaxes(showgrid=True,
                             gridwidth=1,
                             gridcolor='LightGrey')
    outlook_fig.update_yaxes(showgrid=True,
                             gridwidth=1,
                             gridcolor='LightGrey')
    return outlook_fig

# callback for switching page
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard':
        return page_1_layout
    elif pathname == '/background':
        return page_2_layout
    else:
        return page_1_layout

# serve app
is_prod = os.environ.get('IS_HEROKU', None)

if __name__ == '__main__':
    if is_prod:
        app.run_server(debug=False)
    else:
        app.run_server(debug=False)
