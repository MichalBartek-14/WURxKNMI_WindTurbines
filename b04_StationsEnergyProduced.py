import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns

class HeightAnalysis:
    def __init__(self, data_file, target_fid):
        self.data_file = data_file
        self.target_fid = target_fid
        self.data = None
        self.filtered_data = None

    def load_data(self):
        """Load and preprocess the data."""
        self.data = pd.read_csv(self.data_file, delimiter=',')  # Adjust delimiter if necessary
        # Convert YYYYMMDD to datetime
        self.data['YYYYMMDD'] = self.data['YYYYMMDD'].astype(str).str.replace(r'[-/]', '', regex=True)
        self.data['time'] = pd.to_datetime(self.data['YYYYMMDD'], format='%Y%m%d', errors='coerce')
        # Extract day, month, and year
        self.data['day'] = self.data['time'].dt.day
        self.data['month'] = self.data['time'].dt.month
        self.data['year'] = self.data['time'].dt.year
        # Convert ALT_m_ to float
        if 'ALT_m_' in self.data.columns:
            self.data['ALT_m_'] = self.data['ALT_m_'].astype(float)

    def filter_data(self):
        """Filter the data for the given TARGET_FID."""
        if 'TARGET_FID' not in self.data.columns:
            raise ValueError("Column 'TARGET_FID' not found in data.")

        # If target_fid is a range, convert it to a list and filter
        if isinstance(self.target_fid, range):
            target_fid_list = list(self.target_fid)
            self.filtered_data = self.data[self.data['TARGET_FID'].isin(target_fid_list)]
        else:
            self.filtered_data = self.data[self.data['TARGET_FID'] == self.target_fid]

        if self.filtered_data.empty:
            print(f"No data found for TARGET_FID = {self.target_fid}")
        else:
            # Process FH column
            self.filtered_data['FH'] = self.filtered_data['windspeedWS_filled'].astype(float)  # / 10
            self.filtered_data['date'] = pd.to_datetime(self.filtered_data['time'].dt.date)
            print(self.filtered_data['date'].head())
    def calculate_daily_mean(self):
        """Calculate the daily mean wind speed."""
        print(self.filtered_data.groupby('date')['FH'].mean())

        return self.filtered_data.groupby('date')['FH'].mean().reset_index()

    def plot_data(self, daily_data, title):
        """Plot the daily wind speed with every second label on the x-axis."""
        plt.figure(figsize=(12, 6))
        plt.bar(daily_data['date'], daily_data['FH'], width=0.4, align='center', label='Windspeed')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Windspeed (m/s)', fontsize=12)
        plt.title(title, fontsize=14)
        xticks = daily_data['date'][::5]
        plt.xticks(xticks, rotation=45, ha='right', fontsize=8)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_EnergyWT(self):
        """Plot energy production for all turbines in the filtered data."""
        if self.filtered_data is None or self.filtered_data.empty:
            print("No filtered data available for plotting.")
            return

        # Get all unique turbine IDs
        turbine_ids = self.filtered_data['TARGET_FID'].unique()
        print(f"Found {len(turbine_ids)} turbines to plot.")

        for turbine_id in turbine_ids:
            # Filter data for the current turbine
            df_WTn = self.filtered_data[self.filtered_data['TARGET_FID'] == turbine_id]

            if df_WTn.empty:
                print(f"No data found for Turbine ID {turbine_id}")
                continue

            # Pivot data for plotting
            df_WTn_pivot = pd.pivot_table(df_WTn, values='prod', index=['date'], columns='ALT_m_')

            # Plot the production over time for the turbine
            plt.figure(figsize=(14, 6))
            df_WTn_pivot.plot(legend=True, title=f"Wind Turbine {turbine_id}")

            plt.xlabel("Date")
            plt.ylabel("Energy Produced")
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()

            # Save the plot
            output_path = f"Outputs/EnergyStations/WT{turbine_id}_EnergyProduced_Stations.png"
            plt.savefig(output_path)
            print(f"Plot for Turbine ID {turbine_id} saved to {output_path}")
            plt.close()

data_file = 'WS_Energy_prod_sorted_by_target.csv'

# o
# Example usage
#data_file = 'WS_Energy_prod_29WTs.csv'
target_fid = range(1,56)  # Change this to the desired TARGET_FID

analysis = HeightAnalysis(data_file, target_fid)
analysis.load_data()
analysis.filter_data()

# Calculate daily mean windspeed
daily_data = analysis.calculate_daily_mean()

# Extract the height for the TARGET_FID
height = analysis.filtered_data['ALT_m_'].iloc[0]  # Assuming ALT_m_ is consistent for TARGET_FID
title = f"Windspeed at {height}m for turbine {target_fid}"

# Plot the data
analysis.plot_data(daily_data, title)
print(analysis.data.head())  # Check the first few rows of the loaded data
print(analysis.data.columns)  # Verify column names
print(daily_data)

### remove
turbine_n = 1
df_filtered = pd.read_csv('WS_Energy_prod_sorted_by_target.csv')
analysis.plot_EnergyWT()