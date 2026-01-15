import streamlit as st

st.set_page_config(
    page_title="Special Events: Philadelphia",
    layout="wide"
)

st.title("Analysis of Special Events in Philadelphia, 2023-2025")
st.caption("Created by: Miriam Cherayil, SmartCityPHL")
st.caption("Contact: miriam.cherayil@phila.gov")
st.subheader("About this app")
st.markdown(
    """
    This app provides **geospatial and temporal visualizations** of special events that took place in **Philadelphia between 2023 and 2025**.
    
    **Daily Events page** *(see sidebar)*  
    - Displays point-level map data for events that took place on a **selected date**
    - Allows users to choose any date within the **2023–2025** time period
    - Shows a table listing:
        - Event names  
        - Event dates  
        - Address
        - Expected attendance  

    **Monthly Events page** *(see sidebar)*  
    - Displays an **attendance-weighted heatmap** of events for one or more selected months
    - Higher expected attendance results in **greater heatmap density**
    - Includes a **calendar heatmap view** showing:
        - Days with the highest number of events
        - Days with the highest expected attendance

    **Note:**  
    A maximum of **6 calendar heatmaps** can be displayed at one time.  
    Please select **no more than 6 months** from the available options.
    """
)



