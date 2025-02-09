from shiny import App, render, ui
import pandas as pd
import re
import altair as alt
import io
import altair_saver as save
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import shiny.ui as ui

# Load the GeoJSON file using GeoPandas
file_path = "Boundaries - Neighborhoods.geojson"
chicago_geojson = gpd.read_file(file_path)

# Ensure using the same coordinate system
chicago_geojson = chicago_geojson.to_crs(epsg=4326)

# Convert GeoDataFrame to JSON format suitable for Altair
chicago_geojson_json = json.loads(chicago_geojson.to_json())

waze_data = pd.read_csv("waze_data.csv")

def identify_updated_subtype(subtype):
    if pd.isna(subtype):
        return 'Unclassified'
    elif 'ACCIDENT' in subtype and 'ACCIDENT_MAJOR' in subtype:
        return "Major" 
    elif 'ACCIDENT' in subtype and 'ACCIDENT_MINOR' in subtype:
        return "Minor"
    elif 'HAZARD_ON_ROAD' in subtype and 'HAZARD_ON_ROAD' in subtype:
        return "On Road"
    elif 'HAZARD' in subtype and 'HAZARD_ON_SHOULDER' in subtype:
        return "On Shoulder"
    elif 'HAZARD' in subtype and 'HAZARD_WEATHER' in subtype:
        return "Weather"
    elif 'JAM' in subtype and 'JAM_HEAVY_TRAFFIC' in subtype:
        return "Heavy Traffic"
    elif 'JAM' in subtype and 'JAM_MODERATE_TRAFFIC' in subtype:
        return "Moderate Traffic"
    elif 'JAM' in subtype and 'JAM_LIGHT_TRAFFIC' in subtype:
        return "Light Traffic"
    elif 'JAM' in subtype and 'JAM_STAND_STILL_TRAFFIC' in subtype:
        return "Stand Still Traffic"
    elif 'ROAD' in subtype and 'ROAD_CLOSED_EVENT' in subtype:
        return "Event"
    elif 'ROAD' in subtype and 'ROAD_CLOSED_CONSTRUCTION' in subtype:
        return "Construction"
    elif 'ROAD' in subtype and 'ROAD_CLOSED_HAZARD' in subtype:
        return "Hazard"
    else:
        return "Unclassified"

# Apply the function to create a new column 'sub_subtype'
waze_data['updated_subtype'] = waze_data['subtype'].apply(identify_updated_subtype)

# Taking away underscores from type
waze_data['type'] = waze_data['type'].replace('ROAD_CLOSED', 'ROAD CLOSED')

# Define the type and subtype combinations
if 'type' in waze_data.columns and 'updated_subtype' in waze_data.columns:
    # Create a new column 'type_subtype' using a lambda function
    waze_data['type_subtype'] = waze_data.apply(lambda row: f"{row['type']} - {row['updated_subtype']}", axis=1)

else:
    print("Columns 'type' and 'subtype' are not found in the DataFrame.")    

type_subtype_combinations = waze_data['type_subtype'].tolist()

# Extracting Latitude and Longitude

# Define the regex pattern
pattern = r"POINT\((-?\d+\.\d+) (-?\d+\.\d+)\)"

# Define the function to extract coordinates
def extract_lat_long(point_str):
    matches = re.match(pattern, point_str)
    if matches:
        longitude = matches.group(1)
        latitude = matches.group(2)
        return pd.Series([latitude, longitude])
    else:
        return pd.Series([None, None])

waze_data[['latitude','longitude']] = waze_data['geo'].apply(extract_lat_long)

# Ensuring they are numeric
waze_data['latitude'] = pd.to_numeric(waze_data['latitude'], errors='coerce')
waze_data['longitude'] = pd.to_numeric(waze_data['longitude'], errors='coerce')

# Round the latitude and longitude values to 2 decimal places
waze_data['latitude'] = waze_data['latitude'].round(2)
waze_data['longitude'] = waze_data['longitude'].round(2)

# Adding waze_data['hour'] column to choose hour
# Creating waze_data['hour'] and dropping "UTC"
waze_data['hour'] = waze_data['ts'].str.replace(' UTC', '')

# Converting to datetime format
waze_data['hour'] = pd.to_datetime(waze_data['hour'])

# Extracting only hour from total timestamp
waze_data['hour'] = waze_data['hour'].dt.floor('H')

waze_data['hour'] = pd.to_datetime(waze_data['hour'], format='%H:%M')

# Extract the hour component as an integer
waze_data['hour_numeric'] = waze_data['hour'].dt.hour
##

# Setting up Chicago Map
chicago_geojson_path = "C:/Users/prash/Downloads/Boundaries - Neighborhoods.geojson"  # Replace with your file path
chicago_geojson = gpd.read_file(chicago_geojson_path)

# Plot the GeoJSON data
map_fig, ax = plt.subplots(figsize=(10, 10))
chicago_geojson.plot(ax=ax, color='lightgray', edgecolor='white')

# Define the UI
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
            body {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
            }
            .panel-title {
                text-align: center;
                color: #000000;
                font-size: 24px;
                font-weight: bold;
                margin-top: 20px;
            }
            .input-group {
                margin: 15px 0;
            }
            .slider-label {
                color: #4b0082;
                font-weight: bold;
            }
            .plot-container {
                margin-top: 30px;
            }
            .content-container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-top: -10px;  /* Adjust as needed to move content higher */
            }
        """)
    ),
    ui.div(
        ui.panel_title("Top 10 Traffic Alerts in Chicago"),
        style="text-align: center; color: #4b0082; font-size: 24px; font-weight: bold; margin-top: 20px;"
    ),
    ui.input_select("type_subtype", "Select Type and Subtype:", type_subtype_combinations),
    ui.input_switch("switch", "Switch Button", False),
    ui.output_ui("hour_selection_ui"),
    ui.div(
        ui.row(
            ui.column(6, ui.output_plot("my_plot")),
            ui.column(6, ui.output_table("my_table"))
        ),
        style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);"
    )
)


# Defining Server
def server(input, output, session):
    @output
    @render.ui
    def hour_selection_ui():
        if input.switch():
            return ui.input_slider("hour_single", "Single Hour of the Day", 0, 23, 0)
        else:
            return ui.input_slider("hour_range", "Hour Range of the Day", 0, 23, (0, 3))

    @output
    @render.plot
    def my_plot():
        selected_type_subtype = input.type_subtype()
        selected_type, selected_subtype = selected_type_subtype.split(" - ")

        if input.switch():
            selected_hour = input.hour_single()
            # Filter the dataset for the selected type, subtype, and single hour
            filtered_waze_data = waze_data[(waze_data['type'] == selected_type) & 
                                           (waze_data['updated_subtype'] == selected_subtype) & 
                                           (waze_data['hour_numeric'] == selected_hour)]
            hour_display = f'{int(selected_hour):02}:00'
        else:
            selected_hour_range = input.hour_range()
            start_hour, end_hour = selected_hour_range
            # Filter the dataset for the selected type, subtype, and hour range
            filtered_waze_data = waze_data[(waze_data['type'] == selected_type) & 
                                           (waze_data['updated_subtype'] == selected_subtype) & 
                                           (waze_data['hour_numeric'] >= start_hour) & 
                                           (waze_data['hour_numeric'] <= end_hour)]
            hour_display = f'{int(start_hour):02}:00 to {int(end_hour):02}:00'

        grouped_data = filtered_waze_data.groupby(['latitude', 'longitude']).size().reset_index(name='count')

        # Get the top 10 cases based on 'count'
        top_cases = grouped_data.sort_values(by='count', ascending=False).head(10)

        # Create a new figure
        fig, ax = plt.subplots(figsize=(10, 10))

        # Plot the GeoJSON data
        chicago_geojson.plot(ax=ax, color='lightgray', edgecolor='white')

        # Plot the scatter plot on the same figure with reduced dot size
        scatter = ax.scatter(
            top_cases['longitude'],
            top_cases['latitude'],
            s=top_cases['count'] * 5,  # Adjust dot size here if needed
            c=top_cases['count'],
            cmap='viridis',
            alpha=0.6
        )
        plt.colorbar(scatter, ax=ax, label='Count')
        ax.set_title(f'Scatter Plot of {selected_type_subtype} Cases at {hour_display}')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.grid(True)

        return fig
    @output
    @render.table
    def my_table():
        selected_type_subtype = input.type_subtype()
        selected_type, selected_subtype = selected_type_subtype.split(" - ")

        if input.switch():
            selected_hour = input.hour_single()
            # Filter the dataset for the selected type, subtype, and single hour
            filtered_waze_data = waze_data[(waze_data['type'] == selected_type) & 
                                           (waze_data['updated_subtype'] == selected_subtype) & 
                                           (waze_data['hour_numeric'] == selected_hour)]
            hour_display = f'{int(selected_hour):02}:00'
        else:
            selected_hour_range = input.hour_range()
            start_hour, end_hour = selected_hour_range
            # Filter the dataset for the selected type, subtype, and hour range
            filtered_waze_data = waze_data[(waze_data['type'] == selected_type) & 
                                           (waze_data['updated_subtype'] == selected_subtype) & 
                                           (waze_data['hour_numeric'] >= start_hour) & 
                                           (waze_data['hour_numeric'] <= end_hour)]
            hour_display = f'{int(start_hour):02}:00 to {int(end_hour):02}:00'

        grouped_data = filtered_waze_data.groupby(['latitude', 'longitude']).size().reset_index(name='count')

        # Get the top 10 cases based on 'count'
        top_cases = grouped_data.sort_values(by='count', ascending=False).head(10)
        return top_cases

# Run the Shiny app
app = App(app_ui, server)

# if __name__ == "__main__":
#    app.run()
