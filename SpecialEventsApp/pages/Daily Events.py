# Author: Mia Cherayil <miriam.cherayil@phila.gov>
# Date: 01-12-2026
# Description: This script reads in a list of geocoded events taking place in Philadelphia between 2023
# and 2025, and maps the events occuring on a user selected date. 

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import os

# get directory of Daily Events.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# go up one level since data file is outside of pages folder
repo_root = os.path.abspath(os.path.join(current_dir, ".."))

# building full path
parquet_file = os.path.join(repo_root, "events_geocoded.parquet")  

# read geocoded events
df = pd.read_parquet(parquet_file)

#df = pd.read_parquet("c:\Users\mirian.cherayil\DataAnalysis\smartCities\SpecialEventsApp\pages\..\events_geocoded.parquet")

st.set_page_config(
    page_title="Daily events in Philadelphia, 2023–2025",
    layout="wide"
)

st.title("Daily events in Philadelphia, 2023–2025")

# convert to datetime if not already in that format
df["startDate"] = pd.to_datetime(df["startDate"])
df["endDate"] = pd.to_datetime(df["endDate"])

selected_date = st.date_input(
    "Select a date",
    value=pd.Timestamp("2025-01-01"),
    min_value=df["startDate"].min().date(),
    max_value=df["endDate"].max().date(),
    format="DD/MM/YYYY"
)

# filter for selected day
selected_date = pd.to_datetime(selected_date)

filtered = df[
    (df["startDate"] <= selected_date)
    & (df["endDate"] >= selected_date)
].dropna(subset=["latitude", "longitude"])

st.markdown(
    """
    :red[_Note: The map and table below show events that have valid lat/long attributes. They do not
    show events that have a location like "In the vicinity of.... "_]
    """
     )

st.write(
    f"Showing {len(filtered)} event(s) on {selected_date.date().strftime('%B %d, %Y')}"
)

# base map
fig = px.scatter_map(
    filtered,
    lat="latitude",
    lon="longitude",
    hover_name="name",
    hover_data=["address", "startDate", "endDate"],
    zoom=10,
    height=500,
)

fig.update_traces(marker=dict(size=10))

# final layout
fig.update_layout(
    map_style="carto-positron",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
    ),
)

# render
st.plotly_chart(fig, width="stretch")

# table of events for selected day
if not filtered.empty:
    displayData = ["name", "startDate", "endDate", "expAttend", "address"]
    st.dataframe(filtered[displayData].reset_index(drop=True))
else:
    st.write("No events found on this date.")
