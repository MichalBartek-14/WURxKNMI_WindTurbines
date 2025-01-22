import os
import xarray as xr
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def process_the_nc(input_file,output_file,boundaries):

    nc_file = input_file
    ds = xr.open_dataset(input_file)
    # the ds manipulation in order to obtain only measurements at 8am and 8pm for 2021
    time_str = ds['time'].values.astype(str)
    time_pd = pd.to_datetime(time_str)
    # Filter for the year 2021 and 8am
    time_2021 = time_pd[time_pd.year == 2021]
    #time_2021_8am = time_2021[time_2021.hour == 8]
    #the timestamp was changed to 8am AND 8pm
    time_2021_8am = time_2021[(time_2021.hour == 8) | (time_2021.hour == 20)]
    # filter the data
    filtered_data = ds.sel(time=time_2021_8am)
    fdf = filtered_data.to_dataframe()

    dataset = xr.open_dataset(nc_file)
    # Convert NetCDF data to a pandas DataFrame
    df = dataset.to_dataframe()
    # Save as CSV (if necessary)
    #df.to_csv("ix052_iy180_2019010100-2022010100.csv")

    geometry = [Point(lon, lat) for lon, lat in zip(fdf['lon'], fdf['lat'])]
    gdf = gpd.GeoDataFrame(fdf, geometry=geometry)
    # Set the correct CRS (Coordinate Reference System), typically WGS84 (EPSG:4326) for lat/lon
    gdf.crs = "EPSG:4326"
    # Save the data to a shapefile ONLY:
    # Here I add the condition to only proceed if the shapefile is within the netherlands.
    if not boundaries.crs == "EPSG:4326":
        boundaries = boundaries.to_crs("EPSG:4326")
        print("CRS of the boundaries changed into the WGS1984")

    # Merge all boundary polygons into a single geometry using unary_union
    unified_boundary = boundaries.geometry.union_all()
    # Filter windmills that intersect with the unified boundary
    gdf_within_netherlands = gdf[gdf.geometry.intersects(unified_boundary)]

    #If we want also windmills in the sea
    #gdf.to_file(output_file)

    #Save the filtered GeoDataFrame to a shapefile ONLY if it contains data WITHIN land of NL
    if not gdf_within_netherlands.empty:
        gdf_within_netherlands.to_file(output_file)
    else:
        print("No windmills are within the Netherlands' boundaries. File not saved.")

def loop_through_files(input_directory,output_directory):
    # Loop through all the NetCDF files in the directory
    for file_name in os.listdir(input_directory):
        if file_name.endswith('.nc'):
            # Extract ix and iy from the filename using regular expressions or string manipulation
            base_name = os.path.basename(file_name)  # Get the base filename

            # Example: WINS50_43h21_fERA5_WFP_ptA_NETHERLANDS.NL_ix052_iy180_2019010100-2022010100.nc
            parts = file_name.split('_')
            print(parts)
            ix = parts[6][2:]  # Extract the 'ix' part (e.g., 'ix205' -> '205')
            iy = parts[7][2:]
            print(ix)
            print(iy)
            # Generate the output shapefile name with the extracted ix and iy
            output_shapefile = os.path.join(output_directory, f"SHP_WINS50_ix{ix}_iy{iy}_2021_8am.shp")
            input_file = os.path.join(input_directory, file_name)  # Full path to the input file

            # Process the current NetCDF file and save the output shapefile
            process_the_nc(input_file, output_shapefile,nl_border)

# We read the borders for the Netherlands since for this purpose we only need the dutch windmills
nl_border = gpd.read_file('nl.json')

# Define the directory containing your NetCDF files
input_directory = os.path.dirname(os.path.realpath(__file__))

# Get the current working directory (where the Python script is located)
current_directory = os.path.dirname(os.path.realpath(__file__))

# Define the input directory (where your .nc files are located)
input_directory = os.path.join(current_directory, 'nc_files_windmills')

# Define the output directory (where the .shp files will be saved)
output_directory = os.path.join(current_directory, 'shpfiles_windmills')

loop_through_files(input_directory,output_directory)

