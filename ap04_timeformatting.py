import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

#formatting of time
#output of the function calculate_dist(df1) froom module b05_ML_Format
Harm_with_distances = "Harmonie_energy_with_distances.csv"
dfharm = pd.read_csv(Harm_with_distances, delimiter=',')
#dfharm['time'] = pd.to_datetime(dfharm['time'], dayfirst=True)
#dfharm['day'] = dfharm['time'].dt.day
#dfharm['month'] = dfharm['time'].dt.month
#dfharm['year'] = dfharm['time'].dt.year

print(dfharm['time'])

# Create alternating pattern starting with 9
dfharm['HH'] = np.where(np.arange(len(dfharm)) % 2 == 0, 9, 20)

# Check the first few rows to confirm the result
print(dfharm[['time', 'HH']].head())
##dfharm.to_csv("Harmonie_energy_Formatted.csv")


# Load the dataset
df = pd.read_csv('WS_Energy_prod_29WTs.csv')

# Convert 'YYYYMMDD' to datetime, adjusting the format to match the actual data
df['YYYYMMDD'] = pd.to_datetime(df['YYYYMMDD'], format='%d/%m/%Y')

# Check if a 'HH' column exists to differentiate morning and evening
if 'HH' not in df.columns:
    # Add 'HH' column based on a condition, assuming there's an indicator to determine morning vs evening
    # Replace this with the logic appropriate for your dataset
    raise ValueError("No column or indicator found to differentiate morning and evening sessions.")

# Sort the dataset by 'TARGET_FID', 'YYYYMMDD' (date), and 'HH' (time)
df_sorted = df.sort_values(by=['TARGET_FID', 'YYYYMMDD', 'HH'])

# Reset the index
df_sorted = df_sorted.reset_index(drop=True)

# Save the processed dataset to a new CSV
df_sorted.to_csv('WS_Energy_prod_sorted_by_target.csv', index=False)

# Optionally print the first few rows of the sorted dataset to verify
print(df_sorted.head())


