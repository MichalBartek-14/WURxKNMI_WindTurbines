# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 12:22:05 2025

@author: dylan
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

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

#select the column to perform K-means on 
#and plot a figure which shows the variance explained per amount of clusters
data_clustervars = pcaWSsum[['prod']]
sse = {}
for k in range(1, 10):
    kmeans = KMeans(n_clusters=k, max_iter=1000,n_init=150).fit(data_clustervars)
    pcaWS["clusters"] = kmeans.labels_
    #print(data["clusters"])
    sse[k] = kmeans.inertia_ # Inertia: Sum of distances of samples to their closest cluster center
plt.figure()
plt.plot(list(sse.keys()), list(sse.values()))
plt.xlabel("Number of cluster")
plt.ylabel("SSE")
plt.show()