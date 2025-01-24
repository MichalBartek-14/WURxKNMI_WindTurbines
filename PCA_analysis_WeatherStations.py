# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 11:18:08 2025

@author: dylan
"""

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

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
pcaWS = pcaWS.pivot_table(values = ['prod'], index = ['TARGET_FID', 'STN', 'ash'], columns = ['DateTime'])

#To calculate the total prodution over the year:
pcaWSsum = pcaWS.sum(axis = 1).reset_index(name = 'prod')

#reset the index
pcaWSsum = pcaWSsum.reset_index()
#this is used to create a csv-file of the matrix with production
pcaWSsum.to_csv("C:/Users/dylan/Downloads/WS_TotalProd2021_29WTs.csv", sep = '\t')

#store only the datetime and production in a new dataframe 
#(for the total production it is the axis height ('ash') and the total production)
x = pcaWSsum.iloc[:, 3:5]

#normalise data
scaleStandard = StandardScaler()
x1 = scaleStandard.fit_transform(x)

#perform PCA
pca1 = PCA(n_components = 2)
x_pca1 = pca1.fit_transform(x1)

#create the PCA-plot and write a csv-file with the data
df = pd.DataFrame(x_pca1, columns=['PC1', 'PC2'])
df['prod'] = x['prod']
#df.loc[:, 'STN'] = x.iloc[:, 0]
sns.pairplot(df[['PC1','PC2', 'prod']], hue='prod', palette='coolwarm')
#sns.pairplot(df[['PC1','PC2']])
plt.show()
df.to_csv("C:/Users/dylan/Downloads/PCA_WS_TotalProd2021_29WTs.csv", sep = '\t')
