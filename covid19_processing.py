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
            
        self.ICU = pd.read_csv('ICU_beds.csv', sep = ";")


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

     
    def list_countries(self, columns=5):
        confirmed_by_country = self.dataframes["confirmed_by_country"]
        n_countries = len(confirmed_by_country)
        for i, k in enumerate(confirmed_by_country.index):
            if len(k) > 19:
                k = k[:18].strip() + "."
            print(f"{k:20}", end=" " if (i + 1) % columns else "\n")  # Every 5 items, end with a newline

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
        confirmed = self.get_country_data("confirmed").loc[country]
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
                population = self.country_metadata[country]["population"]
                y_country = df[df.index == country].iloc[:,4:].transpose()
                y_country.columns = [country]
                if metric == "deaths":
                    y_country = y_country[y_country[country]/population*1000000 > 1]
                else:
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
            yaxis_type = "log"
        )            
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        return fig


    def create_factor_figure(self, countries_to_plot):
        fig = go.Figure()
        for country in countries_to_plot:
            try:
                df = self.get_new_cases_details(country)
                population = self.country_metadata[country]["population"]
                df = df[df["confirmed_deaths"]/population*1000000>1]
                y_country = df["filtered_growth_factor"].values-1
                if country == "Netherlands":
                    fig.add_trace(go.Scatter(y=y_country, name = country, line = dict(width = 6)))
                else:
                    fig.add_trace(go.Scatter(y=y_country, name = country))
            except:
                continue
        fig.update_layout(
            plot_bgcolor='white',
            xaxis_title="Days",
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', tickformat= ',.0%')
        return fig


# ICU_fig = go.Figure()
# ICU_fig.update_layout(barmode='group')
# x1 = []
# y1 = []
# y2 = []
# for country in countries_to_plot:
#     try:
#         population = data.country_metadata[country]["population"]
#         ICU_cap = ICU[ICU["Country"] == country]["number"].values[0]
#         # confirmed = data.dataframes['confirmed_by_country']
#         # confirmed = confirmed[confirmed.index == country].iloc[:,-14:].values[0][-1]-confirmed[confirmed.index == country].iloc[:,-14:].values[0][0]
#         x1.append(country)
#         y1.append(ICU_cap)
#     except:
#         continue

# ICU_fig.add_trace(go.Bar(y=y1, x = x1 , name = "ICU capacity"))
# ICU_fig.add_trace(go.Bar(y=y2, x = x1, name = "Confirmed"))
# ICU_fig.update_layout(
#             plot_bgcolor='white',
#             xaxis_title="Days",
#             yaxis_title="Cases",
#         )            
# ICU_fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
# ICU_fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
 
 