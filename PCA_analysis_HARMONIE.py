# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 15:25:47 2025

@author: dylan
"""

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

#get data from a csv-file
path = "C:/Users/dylan/Downloads/Harmonie_energy_Formatted.csv"
pcaWS = pd.read_csv(path, sep=',')

#drop the columns that aren't needed, set the date and hour in the right format
#and sort the table based on the date and time
pcaWS = pcaWS.drop(columns = ['Unnamed: 0','Unnamed: 0.1','WT_Longtitude','WT_Latitude', 'diam', 'area', 'geometry', 'distance_to_coast'])
pcaWS['HH'] = pd.to_datetime(pcaWS['HH'], format="%H").dt.strftime("%H:%M:%S").astype(str)
pcaWS['time'] = pd.to_datetime(pcaWS['time'], format = "%Y-%m-%d").astype(str)
pcaWS['DateTime'] = pcaWS['time'] + " " + pcaWS['HH']
pcaWS['DateTime'] = pd.to_datetime(pcaWS['DateTime'])
pcaWS.sort_values(by='DateTime')

#make a new table which takes the wind turbines as rows, datetime as columns
#and fills the cells with the production
pcaWS = pcaWS.pivot_table(values = ['prod'], index = ['TARGET_FID', 'height', 'ash'], columns = ['DateTime'])

#To calculate the total prodution over the year:
#pcaWSsum = pcaWS.sum(axis = 1).reset_index(name = 'prod')

#reset the index
pcaWS = pcaWS.reset_index()

#this is used to create a csv-file of the matrix with production
pcaWS.to_csv("C:/Users/dylan/Downloads/WS_DailyProd2021.csv", sep = '\t')

#store only the datetime and production in a new dataframe
#(for the total production it is the axis height ('ash') and the total production)
x = pcaWS.iloc[:, 3:733]

#normalise data
scaleStandard = StandardScaler()
x1 = scaleStandard.fit_transform(x)

#perform PCA
pca1 = PCA(n_components = 2)
x_pca1 = pca1.fit_transform(x1)

#create the PCA-plot and write a csv-file with the data
df = pd.DataFrame(x_pca1, columns=['PC1', 'PC2'])
df['prod'] = x['prod']
df['prod'].astype(str)
#df.loc[:, 'STN'] = x.iloc[:, 0]
sns.pairplot(df[['PC1','PC2', 'prod']], hue='prod', palette='coolwarm')
plt.show()
#df.to_csv("C:/Users/dylan/Downloads/PCA_HAR_TotalProd2021.csv", sep = '\t')