# WURxKNMI_WindTurbines Project README.md
Authors: Michal Bartek, Mirjam Krikke, Wen Chai, Dylan Bok
Analysis For Wind Turbines in the Netherlands

*Python Scripts*
The functionality of the provided python scripts: 
## **Data Processing**
1st (*a01_WINS50_v2.py*) downloads the nc files of WIN50 KNMI analysis from the API for the square (bbox) approximately fitting the land area of the Netherlands (since WIN50 has many locations in the North sea far from the Netherlands) 

2nd (*a02_NcToShp.py*) Transforms the nc files into the shapefiles but only those points which fit into the land area of the Netherlands, coming from the shapefile of the Netherladns which is intersected (the bbox was not adequate, therefore we intersect it with the exact json file of the Netherlands boundaries). 

3rd (*a03_toLargeShp*) makes the large shapefiles of all the individual shp files into one merged shapefile. It is also converting the original windmill locations into correct crs used later in ArcGIS processing and matching to other spatial data. 

Via ArcGIS buffering the original windturbines and clipping the measurements to get only the measurements close to the actual windturbines. 

# Wind Turbine Data Analysis and Modeling

This repository contains a collection of Python scripts developed to analyze and process data from weather stations and the HARMONIE dataset. The analysis focuses on wind turbines' performance and energy production, incorporating clustering and machine learning techniques for enhanced insights.

## **Data Analysis

### **Weather Station Data Analysis**
- **`WS_data_analysis.py`**: 
  - Analyzes weather station data matched with wind turbines.
  - Fills gaps in weather station data using windspeed values from the nearest station.
  - Calculates daily averages for windspeed and energy production.
  - Plots daily averages for each turbine and month.

### **HARMONIE Data Analysis**
- **`b04_HarmonieAnalysisOOP.py`**:
  - Analyzes the HARMONIE dataset for windspeed and height in a timeseries format.
  - Introduces object-oriented programming techniques for structured analysis.

- **`HARMONIE_WindEnergy.py`**:
  - Calculates energy production per wind turbine at each time point based on the HARMONIE dataset.

- **`HARMONIE_plot_unique_WT+height.py`**:
  - Plots energy production for each wind turbine using HARMONIE data.
  - Distinguishes different heights with separate lines in the graph.

---

## **Clustering Analysis**

### **K-Means Clustering**
- **`KMeans_NoOfClusters.py`**:
  - Produces a graph showing the variance explained by different numbers of clusters.
  - Helps determine the optimal number of clusters for the K-means algorithm.

- **`Kmeans.py`**:
  - Performs K-means clustering for turbines with both HARMONIE and weather station data.

### **Hierarchical Clustering (HCA)**
- **`HCA_analysis.py`**:
  - Executes hierarchical clustering for turbines with combined HARMONIE and weather station data.

### **Principal Component Analysis (PCA)**
- **`PCA_analysis_HARMONIE.py`**:
  - Conducts PCA clustering for turbines using the HARMONIE dataset.

- **`PCA_analysis_WeatherStations.py`**:
  - Performs PCA clustering for turbines with weather station data.

---

## **Energy Production Analysis**

### **Energy Data Analysis**
- **`b04_HarmonieEnergyProduced.py` / `b04_StationsEnergyProduced.py`**:
  - Analyzes energy production using techniques extended from previous code contributions.

### **Data Formatting**
- **`ap04_timeformatting.py`**:
  - Reformats time data for compatibility across datasets (HARMONIE and stations).

- **`bF04_StationsFormatting.py`**:
  - Further formats station data for energy production visualization.

---

## **Machine Learning and Predictor Analysis**

### **Preparation and Predictors**
- **`b05_ML_FormatVariables.py`**:
  - Adds the "distance to coast" variable, a significant predictor for energy production.
  - Includes direct analyses of predictors.

- **`b05_ML_FormatVariables_Stations.py`**:
  - Similar to the above, tailored for weather station data.

### **Comparative Analysis**
- Comparative analysis between weather station and HARMONIE datasets for energy production and predictors.
  - a06_HarmonieStationsComparison.py 
---

