from covid19_util import *
from matplotlib import dates as mdates
import pandas as pd
import requests
import scipy.optimize
import scipy.stats
from io import StringIO
import datetime
import geonamescache
import plotly.graph_objs as go
import math
import numpy as np
from scipy.integrate import odeint


class Covid19Processing:
    def __init__(self):
        self.dataframes = {}
        gc = geonamescache.GeonamesCache()
        gc_data = gc.get_countries()
        self.country_metadata = {}
        normalized_names = {
            "Timor Leste": "East Timor",
            "Vatican": "Vatican City",
            "Democratic Republic of the Congo": "Congo (Kinshasa)",
            "Republic of the Congo": "Congo (Brazzaville)",
            "Cabo Verde": "Cape Verde"
        }

        for country_code in gc_data:
            metadata = gc_data[country_code]
            name = metadata["name"]
            if name in normalized_names:
                name = normalized_names[name]
            population = metadata["population"]
            area = metadata["areakm2"]
            continent = continent_codes[metadata["continentcode"]]

            self.country_metadata[name] = {
                "population": population,
                "area": area,
                "continent": continent
            }

        for metric in data_urls.keys():
            url = base_url + data_urls[metric]  # Combine URL parts
            r = requests.get(url)  # Retrieve from URL
            self.dataframes[metric] = pd.read_csv(StringIO(r.text), sep=",")  # Convert into Pandas dataframe

    def process(self, rows=20, debug=False):
        # Clean up
        for metric in data_urls.keys():
            by_country = self.dataframes[metric].groupby("Country/Region").sum()  # Group by country
            dates = by_country.columns[2:]  # Drop Lat/Long

            # Convert to columns to matplotlib dates
            by_country = by_country.loc[:, dates]
            dates = pd.to_datetime(dates)
            by_country.columns = dates

            if metric == "confirmed":
                # Early China data points
                early_china_data = {
                    "1/17/20": 45,
                    "1/18/20": 62,
                    "1/20/20": 218
                }

                # Insert data points
                for d, n in early_china_data.items():
                    by_country.loc["China", pd.to_datetime(d)] = n

                # Retain chronological column order
                by_country = by_country.reindex(list(sorted(by_country.columns)), axis=1)
                by_country = by_country.fillna(0)

                # Correct an odd blip in the Japanese data. 
                # From 2/5 to 2/7, the Johns Hopkins data for Japan goes 22, 45, 25. 
                # I assume that the 45 is incorrect. Replace with 23.5, halfway between the values for 2/5 and 2/7
                by_country.loc["Japan", pd.to_datetime("2/06/20")] = 23.5

            # Change some weird formal names to more commonly used ones
            by_country = by_country.rename(index={"Republic of Korea": "South Korea",
                                                  "Holy See": "Vatican City",
                                                  "Iran (Islamic Republic of)": "Iran",
                                                  "Viet Nam": "Vietnam",
                                                  "Taipei and environs": "Taiwan",
                                                  "Republic of Moldova": "Moldova",
                                                  "Russian Federaration": "Russia",
                                                  "Korea, South": "South Korea",
                                                  "Taiwan*": "Taiwan",
                                                  "occupied Palestinian territory": "Palestine",
                                                  "Bahamas, The": "Bahamas",
                                                  "Cote d'Ivoire": "Ivory Coast",
                                                  "Gambia, The": "Gambia",
                                                  "US": "United States",
                                                  "Cabo Verde": "Cape Verde",
                                                  })
            by_country.sort_index(inplace=True)

            # Store processed results for metric
            self.dataframes[metric + "_by_country"] = by_country.fillna(0).astype(int)


        # Add in continents
        for metric in list(data_urls.keys()):
            continent_data = {}
            by_country = self.dataframes[metric+"_by_country"]
            for country in by_country.index:
                if country in self.country_metadata:
                    continent = self.country_metadata[country]["continent"]
                    if continent in continent_data:
                        continent_data[continent] += by_country.loc[country, :]
                    else:
                        continent_data[continent] = by_country.loc[country, :]

                elif metric == "confirmed" and debug:
                    print(f"Missing metadata for {country}!")

            by_continent = pd.DataFrame(columns=by_country.columns)
            for continent in continent_data:
                by_continent.loc[continent, :] = continent_data[continent]

            # Add in special regions
            all_countries = by_country.sum()
            by_continent.loc["All except China", :] = all_countries - by_country.loc["China", dates]
            by_continent.loc["World", :] = all_countries
            by_continent = by_continent
            self.dataframes[metric + "_by_continent"] = by_continent.fillna(0).astype(int)


    def get_country_data(self, metric):
        if metric+"_by_country" in self.dataframes:
            return pd.concat([self.dataframes[metric + "_by_country"], self.dataframes[metric + "_by_continent"]])
        elif metric.startswith("new") and metric.split(" ")[1] in self.dataframes:
            metric = metric.split(" ")[1]
            return pd.concat([self.dataframes[metric + "_by_country"].diff(axis="columns"),
                              self.dataframes[metric + "_by_continent"].diff(axis="columns")]
                             )
        else:
            return None

    def get_new_cases_details(self, country, avg_n=5, median_n=3):
        deaths = self.get_country_data("deaths").loc[country]
        df = pd.DataFrame(deaths)
        df = df.rename(columns={country: "confirmed_deaths"})
        df.loc[:, "new_deaths"] = np.maximum(0, deaths.diff())
        df = df.loc[df.new_deaths > 1, :]
        df.loc[:, "growth_factor"] = df.new_deaths.diff() / df.new_deaths.shift(1) + 1
        df[~np.isfinite(df)] = np.nan
        df.loc[:, "filtered_new_deaths"] = \
            scipy.ndimage.convolve(df.new_deaths, np.ones(avg_n) / avg_n, origin=-avg_n // 2 + 1)
        df.loc[:, "filtered_growth_factor"] = \
            df.filtered_new_deaths.diff() / df.filtered_new_deaths.shift(1) + 1
        df.filtered_growth_factor = scipy.ndimage.median_filter(df.filtered_growth_factor, median_n, mode="nearest")
        return df
    
    def create_growth_figures(self, metric, countries_to_plot):
        if metric == "deaths":
            df = self.dataframes['deaths_by_country']
        else:
            df = self.dataframes['confirmed_by_country']
        fig = go.Figure()
        for country in countries_to_plot:    
            try:
                # population = self.country_metadata[country]["population"]
                y_country = df[df.index == country].iloc[:,1:].transpose()
                y_country.columns = [country]
                if metric == "deaths":
                    y_country = y_country[y_country[country] > 1]
                else:
                    y_country = y_country[y_country[country] > 1]
                y_country = np.array(y_country[country].values.tolist())
                if country == "China":    
                    y_country = y_country[:len(y_country)-30]
                if country == "Netherlands" :
                    fig.add_trace(go.Scatter(y=y_country, name = country, line = dict(width = 6, color="black")))
                else:
                    fig.add_trace(go.Scatter(y=y_country, name = country))
            except:
                continue
        double = [1]
        for x in range(1,15): double.append(double[x-1]*(2))    
        double2 = [1]
        for x in range(1,30): double2.append(double2[x-1]*np.sqrt(2))
        double4 = [1]
        for x in range(1,45): double4.append(double4[x-1]*np.sqrt(np.sqrt(2)))
        fig.add_trace(go.Scatter(y=double, name = "doubles per day",
                                 line = dict(color='Lightgrey', width=2, dash='dot'), showlegend=False))          
        fig.add_trace(go.Scatter(y=double2, name = "doubles per 2 days",
                                 line = dict(color='Darkgrey', width=2, dash='dot'), showlegend=False))                                     
        fig.add_trace(go.Scatter(y=double4, name = "doubles per 4 days",
                                 line = dict(color='Grey', width=2, dash='dot'), showlegend=False))     
        fig.add_annotation(annotation_layout, x=14, y=4.21, text="doubles per day")
        fig.add_annotation(annotation_layout, x=29, y=4.36, text="doubles per 2 days")
        fig.add_annotation(annotation_layout, x=42, y=3.16, text="doubles per 4 days")

        fig.update_traces(mode='lines')

        fig.update_layout(
            graph_layout,
            plot_bgcolor='white',
            xaxis_title="Days",
            yaxis_type = "log",
            title = dict(text="Figure 1: Number of fatalities since the first fatality", font=title_font)
            )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        return fig


    def create_factor_figure(self, countries_to_plot):
        fig = go.Figure()
        for country in countries_to_plot:
            try:
                df = self.get_new_cases_details(country)
                # population = self.country_metadata[country]["population"]
                df = df[df["confirmed_deaths"]>1]
                y_country = df["filtered_growth_factor"].values-1
                y_country = y_country[4:]
                if country == "China":    
                    y_country = y_country[:len(y_country)-30]
                if country == "Netherlands":
                    fig.add_trace(go.Scatter(y=y_country, name = country, line = dict(width = 6, color="black")))
                else:
                    fig.add_trace(go.Scatter(y=y_country, name = country))
            except:
                continue
        fig.add_trace(go.Scatter(y=np.ones(50)*0, showlegend = False, line = dict(width = 2, color="LightGrey", dash = 'dot')))
        fig.add_annotation(annotation_layout, x=45, y=0, text="0% growth")
        fig.update_layout(
            graph_layout,
            plot_bgcolor='white',
            xaxis_title="Days",
            title = dict(text="Figure 2: 5-day average growth of fatalities since the first fatality", font=title_font)
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', tickformat= ',.0%')
        fig.update_traces(mode='lines')
        return fig
