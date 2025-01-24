# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:46:21 2025

@author: dylan
edited by: Michal

"""
import pandas as pd
import matplotlib.pyplot as plt

turbine_n = 1
#get data from a csv-file
path = "WindEnergy_HARMONIE_2.csv"
df1 = pd.read_csv(path, sep='\t')
#set the column with dates to the right format
df1['time'] = pd.to_datetime(df1['time'], dayfirst=True, format="mixed")
#group by 'TARGET_FID' and apply a function to get the row with the smallest difference between 'height' and 'ash'
def get_closest_height_to_ash(group):
    # Calculate the absolute difference between 'height' and 'ash' in the group
    group['diff'] = abs(group['height'] - group['ash'])
    closest_index = group['diff'].idxmin()
    return group.loc[closest_index]

df_closest = df1.groupby('TARGET_FID').apply(get_closest_height_to_ash).reset_index(drop=True)
print(df_closest['height'])

#keep only those rows from the unique Turbine_id which heights are equal to the heights from the
#get_closest_height_to_ash function. these are already the heights that are closest to the ash. now for 0 keepd 40 for 1 keep height 60 etc etc
def keep_closest_h(df1, df_closest):
    # Merge df1 with df_closest on 'TARGET_FID' and 'height' to keep only matching rows
    df_filtered = pd.merge(df1, df_closest[['TARGET_FID', 'height']],
                            on=['TARGET_FID', 'height'], how='inner')
    return df_filtered

df_filtered = keep_closest_h(df1, df_closest)
df_filtered.to_csv('Harmonie_energy_WTselectedOnHeights.csv')
print(df_filtered)

# search the dataframe for the id's of the wind turbines and plot them
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
        # skip both wind turbines that weren't matched
        if turbine_n == 13 or turbine_n == 38:
            turbine_n += 1

plot_EnergyWT(turbine_n,df_filtered)
