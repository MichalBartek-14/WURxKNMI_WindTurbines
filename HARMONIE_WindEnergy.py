# -*- coding: utf-8 -*-
""""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as nd

#get data from a csv-file
path = "C:/Users/dylan/Downloads/WT_withHarmonieData.csv"
df = pd.read_csv(path, sep=';', decimal=',')

#calculate the area of the rotors of the wind turbines
df['area'] = nd.pi * ((0.5*df['diam']) * (0.5*df['diam']))

#calculate the production of every wind turbine per day
df['prod'] = 0.5 * 1.225 * df['wspeed'] * df['wspeed'] * df['wspeed'] * df['area']

#write the dataframe to a csv-file
df.to_csv('C:/Users/dylan/Downloads/WindEnergy_HARMONIE_2.csv', columns = ['TARGET_FID', 'WT_ID', 'WT_Longtitude', 'WT_Latitude', 'height', 'time', 'diam', 'ash', 'area', 'prod'], index = False, sep='\t')

