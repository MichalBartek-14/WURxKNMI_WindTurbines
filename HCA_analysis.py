# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 14:12:21 2025

@author: dylan
"""

from scipy.cluster.hierarchy import dendrogram, linkage
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

#get data from a csv-file
path = "C:/Users/dylan/Downloads/WS_Energy_prod_29WTs.csv"
pcaWS = pd.read_csv(path, sep=',')

#drop the columns that aren't needed, set the date and hour in the right format
#and sort the table based on the date and time
pcaWS = pcaWS.drop(columns = ['land','regio', 'windspeedWS_filled', 'DDLat', 'DDLon', 'diam', 'kw', 'WT_Longitu', 'WT_Latitud', 'area', 'ALT_m_'])
pcaWS['HH'] = pd.to_datetime(pcaWS['HH'], format="%H").dt.strftime("%H:%M:%S").astype(str)
pcaWS['YYYYMMDD'] = pd.to_datetime(pcaWS['YYYYMMDD'], format = "%d/%m/%Y").astype(str)
pcaWS['DateTime'] = pcaWS['YYYYMMDD'] + " " + pcaWS['HH']
pcaWS['DateTime'] = pd.to_datetime(pcaWS['DateTime'])
pcaWS.sort_values(by='DateTime')

#make a new table which takes the wind turbines as rows, datetime as columns
#and fills the cells with the production
pcaWS = pcaWS.pivot_table(values = ['prod'], index = ['TARGET_FID','STN', 'ash'], columns = ['DateTime'])

#To calculate the total prodution over the year:
pcaWSsum = pcaWS.sum(axis = 1).reset_index(name = 'prod')

#reset the index
pcaWSsum = pcaWSsum.reset_index()

#store only the datetime and production in a new dataframe 
#(for the total production it is the axis height ('ash') and the total production)
x = pcaWSsum.iloc[:, 4:5]

#normalise data
scaleStandard = StandardScaler()
x1 = scaleStandard.fit_transform(x)

#perform the hierarchical cluster analysis and create a plot
linkage_data = linkage(x1, method='ward', metric='euclidean')
dendrogram(linkage_data)

plt.show()