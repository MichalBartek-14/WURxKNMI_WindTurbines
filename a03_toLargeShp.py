import os
import xarray as xr
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer
from dbfread import DBF

def large_shp(path_to_shapefiles):
    """
    Merges all shapefiles in the specified folder into a single shapefile.
    Preserves attributes, including extensive time series data.
    """
    print(f"Processing shapefiles in: {path_to_shapefiles}")

    # Initialize an empty list to store GeoDataFrames
    gdfs = []
    # Iterate through all files in the directory
    for file in os.listdir(path_to_shapefiles):
        if file.endswith('.shp'):
            file_path = os.path.join(path_to_shapefiles, file)
            print(f"Loading shapefile: {file_path}")

            # Load the shapefile into a GeoDataFrame
            gdf = gpd.read_file(file_path)

            # Check if it has valid geometries and attributes
            if gdf.empty:
                print(f"Skipping empty shapefile: {file}")
                continue

            gdfs.append(gdf)

    # Concatenate all GeoDataFrames into one
    if gdfs:
        print("Merging all shapefiles into a single GeoDataFrame...")
        merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

        # Ensure the CRS is consistent (e.g., EPSG:4326)
        if len(set(gdf.crs for gdf in gdfs)) > 1:
            print("Warning: Multiple CRS detected! Reprojecting to EPSG:4326...")
            merged_gdf = merged_gdf.to_crs("EPSG:4326")

        # Define the output path for the merged shapefile
        output_file = os.path.join(path_to_shapefiles, 'merged_windmills.shp')

        # Save the merged GeoDataFrame to a shapefile
        print(f"Saving merged shapefile to: {output_file}")
        merged_gdf.to_file(output_file)
    else:
        print("No valid shapefiles found to merge.")

def formatting_windmills():
    # Load DBF file of the wind turbines in the Netherlands
    dbf_file = "rivm_20240101_Windturbines_ashoogte.dbf"
    dbf_data = DBF(dbf_file)
    df = pd.DataFrame(iter(dbf_data))

    # Print first few rows for reference
    print(df.head())

    # Assume the DBF has 'X' and 'Y' columns in RD (EPSG:28992)
    transformer = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)

    # Convert RD to WGS84 and create geometry
    df['Longitude'], df['Latitude'] = zip(*df.apply(lambda row: transformer.transform(row['x'], row['y']), axis=1))
    df['geometry'] = df.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

    # Save as shapefile
    output_shapefile = "windturbines_wgs84.shp"
    gdf.to_file(output_shapefile, driver="ESRI Shapefile")
    print(f"Shapefile saved as {output_shapefile}")

def create_buffer_and_intersect(windmills_shapefile, merged_shapefile, buffer_distance=3000):
    """
    Creates a buffer of specified distance (3km) around windmills and intersects with a merged shapefile.
    Keeps only the windmills within the buffer distance.
    """
    print(f"Loading windmills shapefile: {windmills_shapefile}")
    windmills_gdf = gpd.read_file(windmills_shapefile)

    print(f"Loading merged windmills shapefile: {merged_shapefile}")
    merged_gdf = gpd.read_file(merged_shapefile)

    # Create 2000m buffer around windmills
    print(f"Creating {buffer_distance}m buffer around windmills...")
    windmills_gdf['buffer'] = windmills_gdf.geometry.buffer(buffer_distance)

    # Replace the original geometry with the buffer geometry
    windmills_gdf.set_geometry('buffer', inplace=True)

    # Ensure CRS is the same for both GeoDataFrames (using EPSG:4326)
    if windmills_gdf.crs != merged_gdf.crs:
        print("Reprojecting merged shapefile to the same CRS as windmills...")
        merged_gdf = merged_gdf.to_crs(windmills_gdf.crs)

    # Perform spatial intersection (clip) of the buffer with the merged shapefile
    print("Intersecting the buffers with the merged shapefile...")
    clipped_gdf = gpd.overlay(merged_gdf, windmills_gdf, how='intersection')

    # Save the result to a new shapefile
    output_clipped_shapefile = "windmills_within_buffer.shp"
    clipped_gdf.to_file(output_clipped_shapefile)
    print(f"Clipped shapefile saved as {output_clipped_shapefile}")

# Entry point for script
if __name__ == "__main__":
    # Current script directory
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Path to folder containing shapefiles
    shapefiles_path = os.path.join(current_directory, 'shpfiles_windmills')

    # Process and merge shapefiles
    large_shp(shapefiles_path)
    formatting_windmills()

    # Define the paths to the windmills shapefile and merged shapefile
    windmills_shapefile = "windturbines_wgs84.shp"
    merged_shapefile = os.path.join(shapefiles_path, 'merged_WIN50_Harmonie.shp')
    # Create buffer and intersect
    #create_buffer_and_intersect(windmills_shapefile, merged_shapefile)
