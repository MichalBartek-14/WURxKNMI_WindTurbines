import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns

#class for the analysis of the year depending on height
class HeightAnalysis:
    #initializing the parameters
    def __init__(self, data_file, target_fid):
        self.data_file = data_file
        self.target_fid = target_fid
        self.data = None
        self.filtered_data = None
    ##
    def load_data(self):
        """Load and preprocess the data."""
        self.data = pd.read_csv(self.data_file, delimiter=';')
        self.data['time'] = pd.to_datetime(self.data['YYYYMMDD'], errors='coerce', dayfirst=True)
        self.data['day'] = self.data['time'].dt.day
        self.data['month'] = self.data['time'].dt.month
        self.data['year'] = self.data['time'].dt.year
        self.data['height'] = self.data['ALT_m_'].str.split(',').str[0].astype(float)

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

def correlation():
    """
    This function plots the correlation matrix with the stations data
    :return: correlation matrix
    """
    WS_file = pd.read_csv('WS_Energy_prod_sorted_by_target.csv')
    df_cor = pd.DataFrame(WS_file)
    df_cor.drop(['STN','TARGET_FID','DDLat','DDLon','Unnamed: 0'],axis=1, inplace=True)
    correlation = df_cor.corr(numeric_only = True)
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix Heatmap")
    plt.show()

def plot_EnergyWT(turbine_n, df1):
    for index, row in df1.iterrows():
        df_WTn = df1.loc[(df1['TARGET_FID'] == turbine_n)]
        df_WTn1 = pd.pivot_table(df_WTn, values='prod', index=['TARGET_FID', 'time'], columns='height')
        # plot the production over time for every separate wind turbine and store a csv-file with the same information
        df_WTn1.plot(figsize=(14, 6), legend=False, title=f"Wind Turbine {turbine_n}")
        plt.savefig(f"Outputs/EnergyHarmonieSelHeights/WT{turbine_n}_EnergyProduced_OnlyClosestHeight.png")
        #plt.show()
        plt.close()
        #   df_WTn1.to_csv(f"C:/Users/dylan/Downloads/Prod_csv/Prod_per_station_{n}.csv", sep='\t', index=True)
        turbine_n += 1

data_file = 'WS_Energy_prod_sorted_by_target.csv'
target_fid = 1
turbine_n = 1
df_filtered = pd.read_csv('WS_Energy_prod_sorted_by_target.csv')
plot_EnergyWT(turbine_n,df_filtered)
#height = 10
#instance of HeightAnalysis
analysis1 = HeightAnalysis(data_file, target_fid)
#plot_data()
#print(daily)
correlation()
#pcaWS['HH'] = pd.to_datetime(pcaWS['HH'], format="%H").dt.strftime("%H:%M:%S").astype(str)
#pcaWS['YYYYMMDD'] = pd.to_datetime(pcaWS['YYYYMMDD'], format = "%d/%m/%Y").astype(str)
#pcaWS['DateTime'] = pcaWS['YYYYMMDD'] + " " + pcaWS['HH']
#pcaWS['DateTime'] = pd.to_datetime(pcaWS['DateTime'])
#pcaWS.sort_values(by='DateTime')#