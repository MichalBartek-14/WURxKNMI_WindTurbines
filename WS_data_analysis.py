# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import seaborn as sns
 

"""This script reads daily avarage wind speed data from weather stations for two hours daily. It then replaces missing values to windspeeds of the nearest weather station (spatially).
It then calculates the energy production for each windturbine based on the windspeed of the corresponding weather station.
Wind speed and energy production are then plotted"""

#Load weather station measurements 
pathmorning = ("WS_measurements_morning_29WTs.csv")
morning = pd.read_csv(pathmorning, sep=',', decimal=',')

pathevening = ("WS_measurements_evening_29WTs.csv")
evening = pd.read_csv(pathevening, sep=',', decimal=',')

#Check if datatypes are correct
print(morning.dtypes)
print(evening.dtypes)

#Convert date column to dates
#morning['YYYYMMDD'] = pd.to_datetime(morning['YYYYMMDD'], format='%Y%m%d')
morning['datetime'] = pd.to_datetime(morning['YYYYMMDD'].astype(str) + morning['HH'].astype(str).str.zfill(2), format='%Y%m%d%H')
evening['datetime'] = pd.to_datetime(evening['YYYYMMDD'].astype(str) + evening['HH'].astype(str).str.zfill(2), format='%Y%m%d%H')
#evening['YYYYMMDD'] = pd.to_datetime(evening['YYYYMMDD'], format='%Y%m%d')

#Convert necessary objects to numeric
morning['diam'] = pd.to_numeric(morning['diam'])
evening['diam'] = pd.to_numeric(evening['diam'])
morning['Windspeed'] = pd.to_numeric(morning['Windspeed'], errors='coerce')
evening['Windspeed'] = pd.to_numeric(evening['Windspeed'], errors='coerce')
morning['WT_Longitu'] = pd.to_numeric(morning['WT_Longitu'])
evening['WT_Longitu'] = pd.to_numeric(evening['WT_Longitu'])

#Check if there are Nodata values in the windspeed column
missing_values = morning[morning['Windspeed'].isna()]

# Print rows with missing values
print(missing_values)

#Filling missing values for the windspeed column
#Function to calculate the geodesic distance between two locations (Lat, Lon)
def calculate_distance(row, stations):
    current_coords = (row['WS_LON'], row['WS_LAT'])
    # Exclude the original station from distance calculations
    stations_filtered = stations[stations['WS_NAME'] != row['WS_NAME']]
    distances = stations_filtered.apply(lambda x: geodesic(current_coords, (x['WS_LAT'], x['WS_LON'])).meters, axis=1)
    closest_station = distances.idxmin()  # Get the index of the closest station
    return closest_station


#Create a DataFrame for unique weather stations (LatWS and LonWS)
stations = morning[['WS_NAME', 'WS_LON', 'WS_LAT']].drop_duplicates() #This will be the same df for evening


#Function to fill missing 'windspeedWS'
def fill_missing_windspeed(row):
    if pd.isna(row['Windspeed']):  #If the value is missing
        #Find the closest station (excluding the original station)
        closest_station_idx = calculate_distance(row, stations)
        closest_station = stations.loc[closest_station_idx, 'WS_NAME']

        #Find the windspeed of the closest station on the same date
        closest_windspeed = morning.loc[
            (morning['YYYYMMDD'] == row['YYYYMMDD']) & (morning['WS_NAME'] == closest_station),
            'Windspeed'
        ]

        #Debug: Print the value being used to fill
        if not closest_windspeed.empty:
            print(f"Using windspeed {closest_windspeed.values[0]} from {closest_station} for {row['WS_NAME']}")
            return closest_windspeed.values[0]
        else:
            print(f"No data available from closest station {closest_station} on date {row['YYYYMMDD']}")
    return row['Windspeed']  # Return original value if not missing

#Apply the function to fill missing values
morning['windspeedWS_filled'] = morning.apply(fill_missing_windspeed, axis=1)
evening['windspeedWS_filled'] = evening.apply(fill_missing_windspeed, axis=1)


#Calculate energy production
morning['area'] = np.pi * (0.5 * (morning['diam'] ** 2))
morning['prod'] = 0.5 * 1.225 * (morning['windspeedWS_filled'] ** 3) * morning['area']

evening['area'] = np.pi * (0.5 * (evening['diam'] ** 2))
evening['prod'] = 0.5 * 1.225 * (evening['windspeedWS_filled'] ** 3) * evening['area']


#Merging morning and evening into one dataset for further analysis
merged = pd.concat([morning, evening], ignore_index=True)
                   
#Export data to csv (optional)
merged.to_csv('WS_Energy_prod_29WTs.csv')

"""This part of the code calculates monthly and yearly windspeed and energy production and plots it"""

#Calculate avarage daily winspeed and average daily energy production
merged['avg_daily_windspeed'] = merged.groupby([merged['TARGET_FID'], merged['datetime'].dt.date])['windspeedWS_filled'].transform('mean')
merged['avg_daily_energyprod'] = merged.groupby([merged['TARGET_FID'], merged['datetime'].dt.date])['prod'].transform('mean')


def plot_monthly_data(column_name, y_label, title, outputfile):
    """
    Function to create monthly scatter plots for a specified column (e.g., windspeed or energy production).
    
    Parameters:
        column_name (str): The column name to plot (e.g., 'avg_daily_windspeed' or 'avg_daily_energy').
        y_label (str): Label for the y-axis (Windspeed or Energy production)
        title (str): The title of the monthly plot
        outputfile (str): The file to which the plots will be saved
    """
    # Add 'month' and 'day' columns if not already added
    if 'month' not in merged.columns:
        merged['month'] = merged['datetime'].dt.month
    if 'day' not in merged.columns:
        merged['day'] = merged['datetime'].dt.day

    # Set the style
    sns.set(style="whitegrid")

    # Create a figure with subplots for each month
    fig, axes = plt.subplots(4, 3, figsize=(20, 18), sharey=True, sharex=True)
    axes = axes.flatten()

    # Plot monthly data
    for month in range(1, 13):
        ax = axes[month - 1]
        data = merged[merged['month'] == month]

        # Identify top 3 and bottom 3 turbines for the current month
        turbine_avg_month = data.groupby('TARGET_FID')[column_name].mean()
        top_turbines = turbine_avg_month.nlargest(3).index
        bottom_turbines = turbine_avg_month.nsmallest(3).index

        # Color palette for top and bottom turbines
        colors = sns.color_palette('tab10', len(top_turbines) + len(bottom_turbines))
        color_map = {turbine: colors[i] for i, turbine in enumerate(top_turbines.union(bottom_turbines))}

        # Plot other turbines in grey
        sns.scatterplot(
            data=data[~data['TARGET_FID'].isin(top_turbines.union(bottom_turbines))],
            x='day',
            y=column_name,
            color='grey',
            alpha=0.6,
            ax=ax,
            legend=False
        )

        # Plot top and bottom turbines in color
        sns.scatterplot(
            data=data[data['TARGET_FID'].isin(top_turbines.union(bottom_turbines))],
            x='day',
            y=column_name,
            hue='TARGET_FID',
            palette=color_map,
            style=data['TARGET_FID'].apply(lambda x: 'Top 3' if x in top_turbines else 'Bottom 3'),
            ax=ax,
            alpha=0.9,
            legend=False
        )

        # Add legend for each month's turbines
        legend_handles = [
            plt.Line2D([0], [0], marker='o', color=color_map[turbine], linestyle='', markersize=8, label=str(turbine))
            for turbine in top_turbines.union(bottom_turbines)
        ]
        ax.legend(handles=legend_handles, title="Turbine IDs", loc='upper right', fontsize='small')

        ax.set_title(f'Month {month} - Daily {title}')
        ax.set_xlabel('Day')
        ax.set_ylabel(y_label)

    #Adjust layout and save figure to file
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(outputfile, dpi=300, bbox_inches="tight")
    plt.show()

# Making the plots
plot_monthly_data(column_name='avg_daily_windspeed', y_label='Mean Windspeed (m/s)', title= 'Windspeed', outputfile= 'Outputs/WS_monthly_windspeed.png')
plot_monthly_data(column_name='avg_daily_energyprod', y_label='Mean Energy production (W)', title= 'Energy Production', outputfile= 'Outputs/WS_Monthly_energyprod.png')


