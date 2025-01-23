# WURxKNMI_WindTurbines Project README.md
Authors: Michal Bartek, Mirjam Krikke, Wen Chai, Dylan Bok
Analysis For Wind Turbines in the Netherlands
*Python Scripts*
The functionality of the provided python scripts: 

1st (*a01_WINS50_v2.py*) downloads the nc files of WIN50 KNMI analysis from the API for the square (bbox) approximately fitting the land area of the Netherlands (since WIN50 has many locations in the North sea far from the Netherlands) 

2nd (*a02_NcToShp.py*) Transforms the nc files into the shapefiles but only those points which fit into the land area of the Netherlands, coming from the shapefile of the Netherladns which is intersected (the bbox was not adequate, therefore we intersect it with the exact json file of the Netherlands boundaries). 

3rd (*a03_toLargeShp*) makes the large shapefiles of all the individual shp files into one merged shapefile. It is also converting the original windmill locations into correct crs used later in ArcGIS processing and matching to other spatial data. 

Via ArcGIS buffering the original windturbines and clipping the measurements to get only the measurements close to the actual windturbines. 
