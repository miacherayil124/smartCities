# Author: Mia Cherayil <miriam.cherayil@phila.gov>
# Date: 01-12-2026
# Description: This script reads in a list of geocoded events taking place in Philadelphia between 2023
# and 2025, and creates a heatmap of all the events occuring in month/months selected by the user. 

import calendar
import streamlit as st
import plotly.express as px
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import calendar
import os

# get directory of Montly Events.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# go up one level since data file is outside of pages folder
repo_root = os.path.abspath(os.path.join(current_dir, ".."))

# building full path
parquet_file = os.path.join(repo_root, "events_geocoded.parquet")
boundary_file = os.path.join(repo_root, "City_Limits.geojson")  

# read geocoded events and philadelphia boundary file
df = pd.read_parquet(parquet_file)
gdf = gpd.read_file(boundary_file)

# reading in Philadelphia boundary
phil_boundary = gdf.__geo_interface__

st.set_page_config(
    page_title="Monthly events in Philadelphia, 2023–2025",
    layout="wide"
)

st.title("Monthly events in Philadelphia, 2023–2025")
st.subheader("Heatmap of monthly events weighted by attendance")

# column only for months
df["month"] = df["startDate"].dt.to_period("M")

available_months = (
    df["month"]
    .dropna()
    .sort_values()
    .unique()
)

# create labels for months in specified format
month_labels = {
    p: p.to_timestamp().strftime("%B, %Y")
    for p in available_months
}

# month selector for users
selected_labels = st.multiselect(
    "Select month(s) for  heatmap and calendar viz",
    options=list(month_labels.values()),
    default=[month_labels[available_months[-1]]]
)

# store months that user selected
selected_months = [
    p for p, label in month_labels.items()
    if label in selected_labels
]

fig = go.Figure()

fig.update_layout(
    mapbox=dict(
        style="carto-positron",
        center={"lat": 39.9526, "lon": -75.1652},
        zoom=11,
        layers=[
            {
                "sourcetype": "geojson",
                "source": phil_boundary,   
                "type": "line",
                "color": "black",
                "opacity": 1,
                "line": {"width": 3},
                "below": ""
            }
        ]
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)


fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_layers=[
        {
            'sourcetype': 'geojson',
            'source': phil_boundary,
            'type': 'line', # Can be 'fill', 'line', or 'circle'
            'color': 'black',
            'opacity': 1
        }
    ],
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    mapbox_zoom=11,
    mapbox_center={'lat': 39.9526, 'lon': -75.1652} # centre of Philadelphia
)

if selected_months:
    heat_data = df[
        df["month"].isin(selected_months)
    ].dropna(subset=["latitude", "longitude"])

    if not heat_data.empty:
        # Clean attendance
        heat_data["attendance_clean"] = heat_data["expAttend"].fillna(0)

        # Limit extremely high values
        cap = heat_data["attendance_clean"].quantile(0.95)

        heat_data["attendance_weight"] = (
            heat_data["attendance_clean"]
            .clip(upper=cap)
            # assign events with attendance of 0 a value of 1, so that they still show up on map
            .clip(lower=1)
        )
        fig.add_trace(
             go.Densitymap(
                lat=heat_data["latitude"],
                lon=heat_data["longitude"],
                z=heat_data["attendance_weight"],
                radius=35,
                colorscale="blues",
                showscale=True,
                customdata=heat_data["attendance_clean"].values,
                hovertemplate="Expected attendance: %{customdata}<extra></extra>"
            )
        )  
    else:
        st.info("No events with locations found for the selected months.")


# final layout
fig.update_layout(
    map_style="carto-positron",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    map_zoom=11,
    map_center={'lat': 39.9526, 'lon': -75.1652}
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Event density by month")

if selected_months:

    cols_per_row = 3

    for i in range(0, len(selected_months), cols_per_row):
        # extracting months from selected_months list that will go in each row
        row_periods = selected_months[i : i + cols_per_row]
        # creating streamlit column for each selected month
        cols = st.columns(len(row_periods))

        for col, period in zip(cols, row_periods):
            # get the year and month for each selected month/s
            year = period.year
            month = period.month

            month_start = pd.Timestamp(year=year, month=month, day=1)
            month_end = month_start + pd.offsets.MonthEnd(1)

            month_events = df[
                (df["startDate"] <= month_end) &
                (df["endDate"] >= month_start)
            ]

            if month_events.empty:
                col.info(f"No events in {month_start.strftime('%B %Y')}")
                continue

            # get all dates in selected month/s
            all_days = pd.date_range(month_start, month_end, freq="D")

            daily_counts = []
            # gets number of events happening each day
            for d in all_days:
                count = (
                    (month_events["startDate"] <= d) &
                    (month_events["endDate"] >= d)
                ).sum()

                daily_counts.append({
                    "date": d,
                    "count": count,
                    "weekday": d.weekday(),
                    "week": d.isocalendar().week,
                })

            cal_df = pd.DataFrame(daily_counts)
            cal_df["week_index"] = cal_df["week"] - cal_df["week"].min()

            cal_df["date_str"] = cal_df["date"].dt.strftime("%B %d, %Y")

            heatmap_data = cal_df.pivot(
                index="week",
                columns="weekday",
                values="count"
            )

            fig_cal = px.imshow(
                heatmap_data,
                x=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                color_continuous_scale="blues",
            )
            
            # adding gap between days/cells so that each day is distinct
            fig_cal.update_traces(
                xgap=1,
                ygap=1
            )

            # show exact date when hovering over a cell
            fig_cal.update_traces(
                hovertemplate=(
                    "Date: %{customdata}</b><br>" + 
                    "Number of events: %{z}<extra></extra>"
                ),
                customdata=cal_df.pivot(
                    index="week",
                    columns="weekday",
                    values="date_str",
                ).values
            )       

            # setting the title of the calendar to be the month and year selected
            fig_cal.update_layout(
                title=f"{calendar.month_name[month]} {year}",
                height=300,
                margin=dict(l=20, r=20, t=50, b=20),
            )

            # show grid lines so each day (cell) is outlined
            fig_cal.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(200,200,200,0.6)",
                ticks="",
            )

            # show grid lines so each day (cell) is outlined
            fig_cal.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(200,200,200,0.6)",
                ticks="",
            )

            col.plotly_chart(fig_cal, use_container_width=True)
           

elif (selected_months == 0):
    st.info("Select one or more months to view calendar heatmaps.")

elif (selected_months > 6):
    st.info("Select 6 or less months for readability")

