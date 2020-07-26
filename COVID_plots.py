#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Based on this blog: https://iscinumpy.gitlab.io/post/johns-hopkins-covid/
# Github of Johns Hopkins: https://github.com/CSSEGISandData/COVID-19/

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from urllib.error import HTTPError
import os.path
import math
plt.style.use('ggplot')

def get_day(day: pd.Timestamp):

    # Read in a datafile from GitHub
    try:
        if not os.path.isfile("./data/"f"{day:%m-%d-%Y}.csv"):
            print("Data not there yet, attempting to get from Johns Hopkins: ", "./data/"f"{day:%m-%d-%Y}.csv")
            table = pd.read_csv(
                "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/"
                "master/csse_covid_19_data/csse_covid_19_daily_reports/"
                f"{day:%m-%d-%Y}.csv",
                )
            table.to_csv("./data/"f"{day:%m-%d-%Y}.csv")
        else:
            #print("Found saved file", "./data/"f"{day:%m-%d-%Y}.csv")
            table = pd.read_csv( "./data/"f"{day:%m-%d-%Y}.csv")
            
    except HTTPError:
        return pd.DataFrame()
    
    # Cleanup - sadly, the format has changed a bit over time - we can normalize that here
    table.columns = [
        f.replace("/", "_")
        .replace(" ", "_")
        .replace("Latitude", "Lat")
        .replace("Longitude", "Long_")
        for f in table.columns
    ]

    # This column is new in recent datasets
    if "Admin2" not in table.columns:
        table["Admin2"] = None

    # New datasets have these, but they are not very useful for now
    table.drop(
        columns=["FIPS", "Combined_Key", "Lat", "Long_"], errors="ignore", inplace=True
    )
    
    # If the last update time was useful, we would make this day only, rather than day + time
    #   table["Last_Update"] = pd.to_datetime(table["Last_Update"]).dt.normalize()
    #
    # However, last update is odd, let's just make this the current day
    table["Last_Update"] = day
    
    # Make sure indexes are not NaN, which causes later bits to not work. 0 isn't
    # perfect, but good enough.
    # Return as a multindex
    mytable = table.fillna(0).set_index(
        ["Last_Update", "Country_Region", "Province_State", "Admin2"], drop=True
    )

    return mytable



def get_all_days(end_day = None):

    # Assume current day - 1 is the latest dataset if no end given
    if end_day is None:
        end_day = pd.Timestamp.now().normalize()

    # Make a list of all dates
    date_range = pd.date_range("2020-01-22", end_day)
    
    
    # Create a generator that returns each day's dataframe
    day_gen = (get_day(day) for day in date_range)
          
    # Make a big dataframe, NaN is 0
    df = pd.concat(day_gen).fillna(0).astype(int)
    
    
    # Remove a few duplicate keys
    df = df.groupby(level=df.index.names).sum()
    
    # Sometimes active is not filled in; we can compute easily
    df["Active"] = np.clip(
        df["Confirmed"] - df["Deaths"] - df["Recovered"], 0, None
    )
    
    # Change in confirmed cases (placed in a pleasing location in the table)
    df.insert(
        1,
        "ΔConfirmed",
        df.groupby(level=("Country_Region", "Province_State", "Admin2"))["Confirmed"]
        .diff()
        .fillna(0)
        .astype(int),
    )
    
    # Change in deaths
    df.insert(
        3,
        "ΔDeaths",
        df.groupby(level=("Country_Region", "Province_State", "Admin2"))["Deaths"]
        .diff()
        .fillna(0)
        .astype(int),
    )
    
    return df

def plot_all():
    startday = "2020-01-22"
    endday ="2020-08-01"
    dcountry = df.groupby(level="Last_Update").sum()
    fig, ax = plt.subplots(figsize=(7,7))
    ax.bar(dcountry.ΔConfirmed.index.values, dcountry.ΔConfirmed.values, label="Data", color='blue')
    #set ticks every week
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    #set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.set(ylim=[0, None])
    ax.set(xlabel="Date",title="Confirmed cases per day ",xlim=[startday, endday])
    ax.legend()

def plot_data(country, provinces):

    if len(provinces) == 0:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,7), squeeze=False)
    else:
        nrows = math.ceil((len(provinces)+1)/2)
        fig, ax = plt.subplots(nrows=nrows, ncols=2, figsize=(15,7), squeeze=False)
    dcountry = df.xs(country, level="Country_Region")

    # plot country data
    startday = "2020-01-22"
    endday ="2020-08-01"
    dcountry_all_states = dcountry.groupby(level="Last_Update").sum()
    dcountry_all_states.ΔConfirmed.rolling(7, center=True).mean().plot(ax = ax[0][0], logy=False, style='-', label="Rolling mean");
    ax[0][0].bar(dcountry_all_states.ΔConfirmed.index.values, dcountry_all_states.ΔConfirmed.values, label="Data", color='blue')
    #set ticks every week
    ax[0][0].xaxis.set_major_locator(mdates.MonthLocator())
    #set major ticks format
    ax[0][0].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax[0][0].set(ylim=[0, None])
    ax[0][0].set(xlabel="Date", title="Confirmed cases per day in "+country,xlim=[startday, endday])

    ax[0][0].legend()

    # plot province data
    startday = "2020-06-01"
    endday ="2020-08-01"
    dby_state = dcountry.groupby(level=("Last_Update", "Province_State")).sum()
    count_cells = 0
    for j in range(len(provinces)):
        if j ==0:
            k = 1
            r = 0
            count_cells += 1
        else:
            k = j%2
            r = r + count_cells%2
            count_cells += 1
        interesting=dby_state.ΔConfirmed.loc[startday:endday,provinces[j]].groupby(level="Last_Update").sum()
        interesting.rolling(7, center=False).mean().plot(ax = ax[r][k], logy=False, style='-', label=provinces[j]);
        ax[r][k].bar(interesting.index.values, interesting.values, label="Data", color='blue')
        ax[r][k].set(xlabel="",xlim=[startday, endday])
        ax[r][k].set(ylim=[0, None])
        #set ticks every week
        ax[r][k].xaxis.set_major_locator(mdates.WeekdayLocator())
        #set major ticks format
        ax[r][k].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax[r][k].xaxis.set_minor_locator(mdates.WeekdayLocator())
        ax[r][k].legend()
        
def print_provinces(country, ntail = 55):
    print("Guessing provinces from tail...")
    dcountry = df.xs(country, level="Country_Region")
    bystate = dcountry.groupby(level=("Last_Update", "Province_State")).sum()
    print(bystate.tail(ntail))
    
    
print("Loading data...")
df = get_all_days()
print("...done!")