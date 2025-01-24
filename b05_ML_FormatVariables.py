import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

def calculate_dist(df1):
    """
    source of the Northseadata: https://www.marineregions.org/gazetteer.php?p=details&id=2350
    :param df1 is the df that includes the csv with coordinates of turbines:
    :returns the updated df which contains the distance to coast in meters:
    """
    #set the column with dates to the right format, create geometrycolumn for lon and lat
    #df1['time'] = pd.to_datetime(df1['time'], errors='coerce', dayfirst=True)
    print(df1['time'].head(15))
    geometry = [Point(xy) for xy in zip(df1['WT_Longtitude'], df1['WT_Latitude'])]
    df1_geo = gpd.GeoDataFrame(df1, geometry=geometry)
    #unify crs
    # Ensure all geometries have the correct CRS (EPSG:4326 for the initial data)
    df1_geo.set_crs(epsg=4326, inplace=True, allow_override=True)
    NL_contour.set_crs(epsg=4326, inplace=True, allow_override=True)
    NorthSeaContour.set_crs(epsg=4326, inplace=True, allow_override=True)

            # Reproject all datasets to RD New (EPSG:28992)
    df1_geo_rd = df1_geo.to_crs(epsg=28992)
    NorthSeaContour_rd = NorthSeaContour.to_crs(epsg=28992)
    NL_contour_rd = NL_contour.to_crs(epsg=28992)

    # Calculate coastline (NL boundary meeting North Sea)
    coastline_rd = NL_contour_rd.boundary.intersection(NorthSeaContour_rd.unary_union)

    # Calculate distances from each wind turbine to the coastline in meters
    df1_geo_rd['distance_to_coast'] = df1_geo_rd.geometry.apply(
        lambda x: x.distance(coastline_rd)
    )
    df1_geo_rd.to_csv("Harmonie_energy_with_distances.csv", index=False)
    df1_geo_rd.to_file("iho/H_E_WTsel_distances.shp")
    print(df1_geo_rd[['WT_Longtitude', 'WT_Latitude', 'distance_to_coast']].head())
    return df1_geo_rd
#.#.#
def perform_regression_distance_prod(df1):
    # Remove rows with missing values in any of the relevant columns
    df1_clean = df1.dropna(subset=['distance_to_coast', 'height', 'diam', 'ash', 'area', 'prod'])
    # Define the features (predictors) and the target variable
    X = df1_clean[['distance_to_coast', 'height', 'diam', 'ash', 'area']]  # predictors
    y = df1_clean['prod']  # target (production)

    # Add a constant (intercept) to the predictors
    X = sm.add_constant(X)

    # Fit the model using statsmodels
    model = sm.OLS(y, X).fit()

    # Get the model summary, which includes p-values, R-squared, and more
    print(model.summary())

    # Get the coefficients and intercept from the model
    print(f"Intercept: {model.params['const']}")
    print(f"Coefficients: {model.params[1:]}")

    # Make predictions
    y_pred = model.predict(X)

    # Plot the true vs predicted values
    plt.figure(figsize=(10, 6))
    plt.scatter(df1_clean['distance_to_coast'], y, label='True Production', color='blue', alpha=0.5, s=7)
    plt.plot(df1_clean['distance_to_coast'], y_pred, label='Predicted Production', color='red')
    plt.xlabel('Distance to Coast (meters)')
    plt.ylabel('Production (prod)')
    plt.title('Regression: Distance to Coast vs. Production')
    plt.legend()
    plt.show()

    # Return the model and predictions for further analysis if needed
    return model, y_pred

def plot_relations(df1):
        # List of variables to plot against 'prod'
        variables = ['height', 'diam', 'ash', 'area', 'distance_to_coast']
        plt.figure(figsize=(15, 10))
        for i, var in enumerate(variables, 1):
            plt.subplot(2, 3, i)  # Create a 2x3 grid of plots
            print(df1['prod'].describe())
            # Plot the variable vs. production
            sns.scatterplot(data=df1, x=var, y='prod', alpha=0.7)

            # Fit a regression line using seaborn (for better visualization)
            sns.regplot(data=df1, x=var, y='prod', scatter=False, color='red')

            plt.title(f'{var} vs. Production')
            plt.xlabel(var)
            plt.ylabel('Production')

        plt.tight_layout()  # Adjust layout
        plt.show()

        ## -- initiLize
#the csv with the height cloest to the ash
WT_path = "Harmonie_energy_WTselectedOnHeights.csv"
df1 = pd.read_csv(WT_path, delimiter=',')
#the json of the NL
NLjson_path = "nl.json"
NL_contour = gpd.read_file(NLjson_path)
NL_contour.to_file("NL.shp")
NorthSeaContour = gpd.read_file("iho/iho.shp")

#Call functions
df_reg = calculate_dist(df1)
plot_relations(df_reg)
model, y_pred = perform_regression_distance_prod(df_reg)

#print(calculate_dist(df1).columns)

data_cor = pd.read_csv("Harmonie_energy_with_distances.csv")
df_cor = pd.DataFrame(data_cor)
correlation = df_cor.corr(numeric_only = True)
plt.figure(figsize=(10, 8))
sns.heatmap(correlation, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Matrix Heatmap")
plt.show()
