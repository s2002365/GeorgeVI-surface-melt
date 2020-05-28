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
import argparse

##################################
# define a command line reader

def getCmdArgs():
    '''
    Read commandline arguments
    '''
    p = argparse.ArgumentParser(description=("Command line parser"))
    p.add_argument("--rootdir", dest ="rootdir", type=str, default="Y:\\s2002365\\code\\data\\s1_grd\\s1_grd_processed\\grd_processed\\19-20_complete", help=("Path to directory with processed geotiffs used for Zonal Stats calculation. \nDefault = Directory with processed 2019-20 geotiffs. "))
    p.add_argument("--outdir", dest ="outdir", type=str, default="Y:\\s2002365\\code\\results\\backscatter\\1920\\zonal_stats\\", help=("Path to directory where Zonal Stats tables will be created. \nDefault='/1920/zonal_stats/'"))
    p.add_argument("--baseline", dest ="baseline", type=bool, default=False, help=("Set to True if working with the baseline (non-lake areas). \nDefault= False"))
    p.add_argument("--season", dest ="season", type=str, default="1920", help=("Dates of season, e.g. '1920' for the 2019-20 season. \nDefault= '1920'"))

    cmdargs = p.parse_args()
    return cmdargs

##################################
#set local parameters (file paths, Windows format)
'''example using arg-parser, but not sure if this can work in arc py yet... 
cmdargs=getCmdArgs()

env.workspace = cmdargs.rootdir
arcpy.env.overwriteOutput = True

rootdir = cmdargs.rootdir
outdir = cmdargs.outdir
baseline = cmdargs.baseline
date = cmdargs.season
mask_dir = "Y:\\s2002365\\code\\data\\lake_masks\\study_area_masks\\Final_Masks\\"

if baseline == True: 
    lake_mask = mask_dir + date + "_mask_baseline.shp"
    outdir = outdir + "baseline_ZS\\"
else:
    lake_mask = mask_dir + date + "_mask_final.shp"
'''
env.workspace = "Y:\\s2002365\\code\\data\\s1_grd\\s1_grd_processed\\grd_processed\\19-20_complete"
arcpy.env.overwriteOutput = True

rootdir = "Y:\\s2002365\\code\\data\\s1_grd\\s1_grd_processed\\grd_processed\\19-20_complete"
outdir = "Y:\\s2002365\\code\\results\\backscatter\\1920\\zonal_stats\\"
mask_dir = "Y:\\s2002365\\code\\data\\lake_masks\\study_area_masks\\Final_Masks\\"
baseline = True
date = "1920"

if baseline == True: 
    lake_mask = mask_dir + date + "_mask_baseline.shp"
    outdir = outdir + "baseline_ZS\\"
else:
    lake_mask = mask_dir + date + "_mask_final.shp"


'''
#set local parameters (file paths, Windows format) --> set back to this if the command line parser has not worked
rootdir = "Y:\\s2002365\\code\\data\\s1_grd\\s1_grd_processed\\grd_processed\\19-20_complete"
lake_mask = "Y:\\s2002365\\code\\data\\lake_masks\\study_area_masks\\Final_Masks\\1920_mask_final.shp"
outdir = "Y:\\s2002365\\code\\results\\backscatter\\1920\\zonal_stats\\" 
'''

##################################
#Loop through rasters in root directory to execute zonal stats 
for raster in os.listdir(rootdir):
    if raster.endswith(".tif"):
        inRaster = rootdir + "\\" + raster
        raster_name = os.path.basename(raster).rstrip(os.path.splitext(raster)[1])
        r_name = raster_name[14:22]
        if baseline == False:
            outTable = outdir + r_name + "_lakes_ZS_table.dbf"
        else: 
            outTable = outdir + r_name + "_baseline_ZS_table.dbf"
        arcpy.gp.ZonalStatisticsAsTable(lake_mask,"FID",inRaster,outTable,"NODATA","MEAN")


##################################
#Source code adapted from: 
#https://gis.stackexchange.com/questions/206559/python-script-zonal-stats-as-table-loop-question

