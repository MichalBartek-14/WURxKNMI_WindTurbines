import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns

#class for the analysis of the year depending on height
class HeightAnalysis:
    #initializing the parameters
    def __init__(self, data_file, target_fid, height):
        self.data_file = data_file
        self.target_fid = target_fid
        self.height = height
        self.data = None
        self.filtered_data = None

    def load_data(self):
        """Load and preprocess the data."""
        self.data = pd.read_csv(self.data_file, delimiter=';')
        self.data['time'] = pd.to_datetime(self.data['time'], errors='coerce', dayfirst=True)
        self.data['day'] = self.data['time'].dt.day
        self.data['month'] = self.data['time'].dt.month
        self.data['year'] = self.data['time'].dt.year
        self.data['height'] = self.data['height'].str.split(',').str[0].astype(float)

    def filter_data(self):
        """Filter the data for the given TARGET_FID and height."""
        self.filtered_data = self.data[
            (self.data['TARGET_FID'] == self.target_fid) &
            (self.data['height'] == self.height)
            ]
        self.filtered_data['wspeed'] = self.filtered_data['wspeed'].str.replace(',', '.').astype(float)
        self.filtered_data['date'] = pd.to_datetime(self.filtered_data['time'].dt.date)

    def calculate_daily_mean(self):
        """Calculate the daily mean wind speed."""
        return self.filtered_data.groupby('date')['wspeed'].mean().reset_index()

    def plot_data(self, daily_data, title):
        """Plot the daily wind speed with every second label on the x-axis."""
        plt.figure(figsize=(12, 6))
        plt.bar(daily_data['date'], daily_data['wspeed'], width=0.4, align='center', label='Windspeed')
        # Customizing the x-axis ticks
        plt.xlabel('Date', fontsize=12) #adding the fontsize so the user can read better
        plt.ylabel('Windspeed (m/s)')
        plt.title(title)
        #x-ticks to every second label
        xticks = daily_data['date'][::3]
        plt.xticks(xticks, rotation=45, ha='right',fontsize=5)
        # Optional: Use DateFormatter if necessary
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

#function that plots more instances together
def plot_multiple_heights(instances, title, max_heights=7):
    """
    Plot windspeed data for multiple HeightAnalysis instances on the same graph with different colors.

    Args:
        instances (list): A list of HeightAnalysis instances to plot.
        title (str): The title of the plot.
        max_heights (int): The maximum number of heights to plot (default is 7).
    """
    if len(instances) > max_heights:
        raise ValueError(f"Cannot plot more than {max_heights} heights at a time.")

    # Predefined colors for up to 7 heights
    colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink']
    instances = instances[::-1]
    plt.figure(figsize=(14, 7))

    for i, instance in enumerate(instances):
        # Calculate daily mean for the instance
        daily_data = instance.calculate_daily_mean()

        # Plot the data with a distinct color and label
        plt.bar(
            daily_data['date'],
            daily_data['wspeed'],
            width= 0.9, #/ len(instances),  # Adjust width based on the number of instances
            align='edge',
            alpha=0.7,
            color=colors[i % len(colors)],  # Cycle through colors if more than 7
            label=f'Height {instance.height}'
        )

    # Customize labels and title
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Windspeed (m/s)', fontsize=14)
    plt.title(title, fontsize=16)

    # Customize x-axis ticks
    plt.xticks(daily_data['date'][::3], rotation=45, ha='right', fontsize=5)
    plt.legend(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('MultipleHeights.png')
    plt.show()

class TurbineAnalysis(HeightAnalysis):
    def analyze_multiple_turbines(self, turbines, height):
        """
        Analyze statistical similarity of wind speeds across multiple turbines for each month of a year.

        Args:
            turbines (list): List of turbine IDs (TARGET_FID) to analyze.
            height (float): The height to analyze.

        Returns:
            pd.DataFrame: A DataFrame with columns ['month', 'turbine', 'mean_wspeed'].
        """
        # Initialize an empty list to store turbine-month data
        results = []

        for turbine_id in turbines:
            self.target_fid = turbine_id
            self.height = height
            self.filter_data()

            if self.filtered_data is not None and not self.filtered_data.empty:
                self.filtered_data['month'] = self.filtered_data['time'].dt.month
                #
                self.filtered_data['day'] = self.filtered_data['time'].dt.day
                #print(self.filtered_data['day'])
                for month, group in self.filtered_data.groupby('month'):
                    mean_wspeed = group['wspeed'].mean()
                    results.append({'month': month, 'turbine': turbine_id, 'monthly_mean_wspeed': mean_wspeed}) #* day was deleted
                    print(self.filtered_data['day'])
        # Convert the results into a DataFrame
        return pd.DataFrame(results)

    def analyze_multiple_turbines_daily(self, turbines, height):
        """
        Analyze daily mean wind speeds across multiple turbines for each month of a year.

        Args:
            turbines (list): List of turbine IDs (TARGET_FID) to analyze.
            height (float): The height to analyze.

        Returns:
            pd.DataFrame: A DataFrame with columns ['day', 'month', 'turbine', 'montlhy_mean_wspeed'].
        """
        results = []

        for turbine_id in turbines:
            self.target_fid = turbine_id
            self.height = height
            self.filter_data()

            if self.filtered_data is not None and not self.filtered_data.empty:
                self.filtered_data['month'] = self.filtered_data['time'].dt.month
                self.filtered_data['day'] = self.filtered_data['time'].dt.day

                for (month, day), group in self.filtered_data.groupby(['month', 'day']):
                    monthly_mean_wspeed = group['wspeed'].mean()
                    results.append(
                        {'day': day, 'month': month, 'turbine': turbine_id, 'monthly_mean_wspeed': monthly_mean_wspeed})
                for (month, day), group in self.filtered_data.groupby(['month', 'day']):
                    daily_mean_wspeed = group['wspeed'].mean()
                    results.append(
                        {'month': month, 'day': day, 'turbine': turbine_id, 'daily_mean_wspeed': daily_mean_wspeed}
                    )
        return pd.DataFrame(results)
    def plot_turbine_yearly_regression(self, turbines, height):
        """
        Plot the monthly mean windspeed for turbines and overlay regression lines.

        Args:
            turbines (list): List of turbine IDs to analyze.
            height (float): The height to analyze.
        """
        # Analyze multiple turbines to get the monthly data
        turbine_data = self.analyze_multiple_turbines(turbines, height)

        plt.figure(figsize=(12, 6))
        sns.set(style="darkgrid")

        #Iterate over turbines
        for turbine_id in turbines:
            turbine_subset = turbine_data[turbine_data['turbine'] == turbine_id]
            x = turbine_subset['month']
            y = turbine_subset['monthly_mean_wspeed']
            # Calculate yearly average windspeed for each turbine
            yearly_avg = turbine_data.groupby('turbine')['monthly_mean_wspeed'].mean()
            top_3_turbines = yearly_avg.nlargest(3).index.tolist()
            bottom_3_turbines = yearly_avg.nsmallest(3).index.tolist()

            if turbine_id in top_3_turbines or turbine_id in bottom_3_turbines:
                #highlight top and bottom 5 turbines
                plt.scatter(
                    x, y,
                    label=f'Turbine {turbine_id}',
                    s=30,  #marker size for visibility
                    alpha=0.8
                )

                z = np.polyfit(x, y, 1)  # Linear regression (degree=1)
                p = np.poly1d(z)
                plt.plot(
                    x,
                    p(x),
                    linestyle='--',
                    linewidth=2,
                    alpha=0.8,
                    label=f'Regression (Turbine {turbine_id})'
                )
            else:
                # Plot other turbines without labels
                plt.scatter(
                    x, y,
                    color='gray',
                    s=20,
                    alpha=0.5
                )

        # Customize the plot
        plt.title(f'Yearly Regression of Turbine Wind Speeds at {height}m', fontsize=16)
        plt.xlabel('Month', fontsize=14)
        plt.ylabel('Mean Windspeed (m/s)', fontsize=14)
        plt.xticks(ticks=range(1, 13), labels=range(1, 13), fontsize=12)
        plt.yticks(fontsize=12)
        plt.legend(loc='upper right', fontsize=5, title="Top3 and Bottom3 Turbines & Regressions")
        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig("Outputs/WT_yearly_windspeedH100v2.png", dpi=300, bbox_inches="tight")
        plt.show()

    def plot_monthly_windspeed(self, turbines, height):
        """
        Plot daily mean windspeed for all turbines for each month of the year.
        Only label the top and bottom 3 turbines by mean windspeed, with larger marker sizes.
        """
        # Analyze daily data for all turbines
        turbine_data = self.analyze_multiple_turbines_daily(turbines, height)

        # Create a figure with subplots for each month
        fig, axes = plt.subplots(3, 4, figsize=(16, 12))
        axes = axes.flatten()

        # Iterate through each month and create scatter plots
        for month, ax in zip(range(1, 13), axes):
            # Filter data for the current month
            month_data = turbine_data[turbine_data['month'] == month]

            # Calculate daily average windspeed for ranking turbines in the current month
            average_daily = month_data.groupby('turbine')['monthly_mean_wspeed'].mean()

            # Identify the top 3 and bottom 3 turbines for the current month
            top_3_turbines = average_daily.nlargest(3).index.tolist()
            bottom_3_turbines = average_daily.nsmallest(3).index.tolist()

            # Print the top and bottom 3 turbines for debugging
            print(f"Month {month} - Top 3 turbines: {top_3_turbines}")
            print(f"Month {month} - Bottom 3 turbines: {bottom_3_turbines}")

            # Plot the windspeed data for each turbine
            for turbine_id in turbines:
                turbine_subset = month_data[month_data['turbine'] == turbine_id]

                if turbine_subset.empty:
                    continue

                # Extract day and mean windspeed for plotting
                x = turbine_subset['day']
                y = turbine_subset['monthly_mean_wspeed']

                # Check if the turbine is in the top 3 or bottom 3
                if turbine_id in top_3_turbines or turbine_id in bottom_3_turbines:
                    # Highlight top and bottom 3 turbines with labels and larger markers
                    ax.scatter(
                        x, y,
                        label=f'Turbine {turbine_id}',
                        s=15,  # Larger marker size
                        alpha=0.8
                    )
                else:
                    # Plot other turbines with smaller markers and no labels
                    ax.scatter(
                        x, y,
                        color='gray',
                        s=8,  # Smaller marker size
                        alpha=0.5
                    )

            # Set the windspeed axis limits and labels
            ax.set_ylim(0, 22)
            ax.set_title(f'Month {month} - Daily Windspeed', fontsize=10)
            ax.set_xlabel('Day', fontsize=8)
            ax.set_ylabel('Mean Windspeed (m/s)', fontsize=8)
            ax.legend(loc='upper right', fontsize=3)
            ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Adjust layout for better visibility
        plt.tight_layout()
        plt.savefig("Outputs/WT_monthly_windspeedH100v2.png", dpi=300, bbox_inches="tight")
        plt.show()
## 00
    #--------- The instances ---------#

#to plot for all only the first turbiine
data_file = 'WT_withHarmonieData.csv'
target_fid = 1
#height = 10
#instance of HeightAnalysis
analysis1 = HeightAnalysis(data_file, target_fid, 10)
analysis2 = HeightAnalysis(data_file, target_fid, 100)
analysis3 = HeightAnalysis(data_file, target_fid, 200)
analysis4 = HeightAnalysis(data_file, target_fid, 500)

for analysis in [analysis1,analysis2,analysis3]:
    analysis.load_data()
    analysis.filter_data()

#list of instances
plot_multiple_heights([analysis1, analysis2, analysis3], f"Windspeed at Multiple Heights for turbine {target_fid}")

#----- Turbine analysis ------#
turbines = list(range(1, 56))  # 55 turbines (TARGET_FID values 1 to 55)
print(turbines)
height = 100  # Analyze data at height 100 meters

### ---instance of TurbineAnalysis
### --- plot the yearly regression
turbine_analysis = TurbineAnalysis(data_file, target_fid=None, height=None)
turbine_analysis.load_data()
turbine_analysis.plot_turbine_yearly_regression(turbines, height)

### --- plot the monthly windspeed
# Instance for the second analysis (Monthly Windspeed)
turbine_analysis2 = TurbineAnalysis(data_file, target_fid=None, height=height) # Load data for a specific turbine at given height
turbine_analysis2.load_data()
turbine_analysis2.plot_monthly_windspeed(turbines, height)  # Plot monthly windspeed

