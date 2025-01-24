# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:46:21 2025

@author: dylan
"""

import pandas as pd
import matplotlib.pyplot as plt
n = 1


#get data from a csv-file
path = "C:/Users/dylan/Downloads/WindEnergy_HARMONIE_2.csv"
df1 = pd.read_csv(path, sep='\t')

#set the column with dates to the right format
df1['time'] = pd.to_datetime(df1['time'], dayfirst = True, format= "mixed")

#search the dataframe for the id's of the wind turbines and plot them
for index, row in df1.iterrows():
    df_WTn = df1.loc[(df1['TARGET_FID'] == n)]
    df_WTn1 = pd.pivot_table(df_WTn, values = 'prod', index = ['TARGET_FID', 'time'], columns = 'height')
    
    #plot the production over time for every separate wind turbine 
    #and store a csv-file for every wind turbine with the same information
    df_WTn1.plot(figsize = (21, 9), legend = False, title = f"{n}")
    plt.show()
    df_WTn1.to_csv(f"C:/Users/dylan/Downloads/Prod_csv/Prod_per_station_{n}.csv", sep = '\t', index = True)
    n = n + 1
    
    #skip both wind turbines that weren't matched    
    if n == 13 or n == 38:
        n = n + 1