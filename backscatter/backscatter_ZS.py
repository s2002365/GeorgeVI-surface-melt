'''Created 25 May 2020

@author: Bryony Freer '''

'''Script to batch process zonal stats as table for MEAN backscatter per S1 scene'''

#To be executed in the Arcpy window within ArcGIS (Windows)
#Can just copy and paste these commands into the python window in ArcGIS to run
#lake mask comprises multiple (thousands) of polygons, so stats calculated over each one 

#import necessary modules and set workspace 
import arcpy, os
from arcpy import env
from arcpy.sa import *
env.workspace = "Y:\\s2002365\\code\\data\\s1_grd\\s1_grd_processed\\grd_processed\\19-20_complete"
arcpy.env.overwriteOutput = True

#set local parameters (file paths, Windows format)
rootdir = "Y:\\s2002365\\code\\data\\s1_grd\\s1_grd_processed\\grd_processed\\19-20_complete"
lake_mask = "Y:\\s2002365\\code\\data\\lake_masks\\study_area_masks\\Final_Masks\\1920_mask_final.shp"
outdir = "Y:\\s2002365\\code\\results\\backscatter\\1920\\zonal_stats\\" 

#loop through rasters in root directory to execute zonal stats 
for raster in os.listdir(rootdir):
    if raster.endswith(".tif"):
        inRaster = rootdir + "\\" + raster
        raster_name = os.path.basename(raster).rstrip(os.path.splitext(raster)[1])
        r_name = raster_name[14:22]
        outTable = outdir + r_name + "_lakes_ZS_table.dbf"
        arcpy.gp.ZonalStatisticsAsTable(lake_mask,"FID",inRaster,outTable,"NODATA","MEAN")

#Source code adapted from: 
#https://gis.stackexchange.com/questions/206559/python-script-zonal-stats-as-table-loop-question

