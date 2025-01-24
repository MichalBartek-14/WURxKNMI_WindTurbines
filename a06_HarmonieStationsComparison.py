import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np

def compare_measurements(data_s, data_h):
    # Convert time columns to datetime
    data_s['time'] = pd.to_datetime(data_s['YYYYMMDD'], dayfirst=True, format="mixed")
    data_h['time'] = pd.to_datetime(data_h['time'], dayfirst=True, format="mixed")
    print(data_s['time'].head(10))
    print(data_h['time'].head(10))
    # Ensure time parsing was successful
    if data_s['time'].isna().any():
        print("Warning: Some Station dates couldn't be parsed correctly.")
    if data_h['time'].isna().any():
        print("Warning: Some Harmonie dates couldn't be parsed correctly.")

    data_s['day'] = data_s['time'].dt.date  # Extract the date
    station_daily = data_s.groupby('day').mean(numeric_only=True).reset_index()
    station_daily['time'] = pd.to_datetime(station_daily['day'])

    data_h['day'] = data_h['time'].dt.date  # Extract the date
    harmonie_daily = data_h.groupby('day').mean(numeric_only=True).reset_index()
    harmonie_daily['time'] = pd.to_datetime(harmonie_daily['day'])  # Re-create datetime column for merging

    # Merge datasets on time
    merged_data = pd.merge(station_daily, harmonie_daily, on='time', suffixes=('_station', '_harmonie'))

    # Plot both productions over time
    plt.figure(figsize=(14, 7))
    plt.plot(merged_data['time'], merged_data['prod_station'], label='Station Production', color='blue', linewidth=2)
    plt.plot(merged_data['time'], merged_data['prod_harmonie'], label='Harmonie Production (Daily Mean)',
             color='orange', linewidth=2)

    # Add labels, title, legend, and grid
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Production', fontsize=12)
    plt.title('Comparison of Station and Harmonie Productions Over Time', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Show the plot
    plt.tight_layout()
    plt.show()

    # Compare relevant columns (adjust column names as needed)
    columns_to_compare = ['prod']
    for column in columns_to_compare:
        #regression that will show r2
        x = merged_data[f'{column}_station'].values.reshape(-1, 1)  # Station values
        y = merged_data[f'{column}_harmonie'].values.reshape(-1, 1)  # Harmonie values
        reg_model = LinearRegression()
        reg_model.fit(x, y)
        y_pred = reg_model.predict(x)
        # Calculate R^2
        r2 = r2_score(y, y_pred)

        plt.figure(figsize=(12, 6))
        plt.scatter(x, y, label=f'{column.capitalize()} Comparison', alpha=0.6, color='blue')
        plt.plot(x, y_pred, color='orange', label=f'Regression Line (R² = {r2:.2f})', linewidth=2)
        plt.xlabel(f'{column.capitalize()} (Station)', fontsize=12)
        plt.ylabel(f'{column.capitalize()} (Harmonie)', fontsize=12)
        plt.title(f'Regression of {column.capitalize()} Between Weather stations and Harmonie Model', fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(axis='both', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

        #the lineplot with the comparison of HARMONIE and station data
        plt.figure(figsize=(12, 6))
        plt.scatter(merged_data[f'{column}_station'], merged_data[f'{column}_harmonie'])
        plt.xlabel(f'{column} (Station)')
        plt.ylabel(f'{column} (Harmonie)')
        plt.title(f'Comparison of {column}')
        plt.plot([merged_data[f'{column}_station'].min(), merged_data[f'{column}_station'].max()],
                 [merged_data[f'{column}_station'].min(), merged_data[f'{column}_station'].max()],
                 'r--', lw=2)
        plt.savefig(f'comparison_{column}.png')
        plt.close()

        # Calculate and print correlation
        correlation = merged_data[f'{column}_station'].corr(merged_data[f'{column}_harmonie'])
        print(f"Correlation for {column}: {correlation}")


# Load the data
data_stations = pd.read_csv("Stations_energy_with_distances.csv")
data_harmonie = pd.read_csv("Harmonie_energy_with_distances.csv")

# Call the function with DataFrames
compare_measurements(data_stations, data_harmonie)