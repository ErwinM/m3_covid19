# Where to get the data. There have been some issues with the data quality lately. 
# For the most recent data, use branch 'master'.
# For stable March 13 data, use 'c2f5b63f76367505364388f5a189d1012e49e63e'
branch = "master"
base_url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/{branch}/" + \
           "csse_covid_19_data/csse_covid_19_time_series/"
data_urls = {
    "confirmed": "time_series_covid19_confirmed_global.csv",
    "deaths": "time_series_covid19_deaths_global.csv",
    # No longer being updated: "recovered": "time_series_19-covid-Recovered.csv"
}

continent_codes = {
    "AF": "Africa",
    "AN": "Antarctica",
    "AS": "Asia",
    "EU": "Europe",
    "NA": "North America",
    "OC": "Oceania",
    "SA": "South America"
}


mapping = {"Patients in hospital": "Hosp_tot",
           "Patients on IC": "IC_total",
           "Infectious": "I_total",
           "Deaths":"R_fatal",
           "Recovered": "R_total",
           "Susceptible": "Susceptible",
           "Deaths": "R_fatal"}


        