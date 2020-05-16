#activate the gamma environment in the shell
#gma
#geoutils

import os
import os.path
from os import path
import subprocess
from pyroSAR import identify
#import faulthandler; faulthandler.enable()

dem = "/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/data/DEM/REMA_resampled_10m.dem"
dem_par = "/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/data/DEM/REMA_resampled_10m.dem_par"
outdir = "/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/data/s1_grd/s1_grd_processed/grd_processed"
rootdir = '/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/data/s1_grd/'
study_area = '/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/study_area/study_area_square.shp'
surplus_files = '/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/data/s1_grd/s1_grd_processed/to_be_deleted/'

def unzip(): 

    '''Unzips S1.zip files into .SAFE folders.'''

    for dirname in os.listdir(rootdir):
        if dirname.endswith(".zip"):
            filename = str(dirname)[:-4]
            #unzip S1 data to .SAFE file 
            if not path.exists(f"{rootdir}{filename}.SAFE"):
                unzip = f"unzip {rootdir}{dirname} -d {rootdir}"
                os.system(unzip)
                print(f"{dirname} is now unzipped.")


def mk_POEORB_dir():

    '''creates the file structure needed for the orbit files. 
    Make sure the correct orbit file is downloaded and placed inside the 
    POEORB directory before running the processGRD() function. '''

    for dirname in os.listdir(rootdir):
        if dirname.endswith(".SAFE"):
            if not path.exists(f"{rootdir}{dirname}/osv/"):
                os.makedirs(f"{rootdir}{dirname}/osv/")
                print("Directories for orbit files created.")

def downloadOSV(): 

    '''downloads the OSV file associated with each S1 image and places it into the correct file structure''' 
    for dirname in os.listdir(rootdir):
        if dirname.endswith(".zip"):
            filename = str(dirname)[:-4]
            if path.exists(f"{rootdir}{filename}.SAFE/osv/"):
                scene = f"{rootdir}{dirname}"
                platform = str(dirname)[:3]
                year = str(dirname)[17:21]
                month = str(dirname)[21:23]
                day = str(dirname)[23:25]
                id = identify(scene)
                id.getOSV(osvdir=f'{rootdir}{filename}.SAFE/osv/', osvType='POE') #downloads OSV file as a zip file located in {rootdir}/POEORB/S1B/2019/05/
                if day != "01":
                    unzip = f"unzip {rootdir}{filename}.SAFE/osv/POEORB/{platform}/{year}/{month}/*.zip -d {rootdir}{filename}.SAFE/osv/POEORB"
                else:
                    pre_month = int(month)-1
                    if pre_month > 9:
                        orb_month = str(pre_month)
                    else:
                        orb_month = '0'+ str(pre_month)
                    unzip = f"unzip {rootdir}{filename}.SAFE/osv/POEORB/{platform}/{year}/{orb_month}/*.zip -d {rootdir}{filename}.SAFE/osv/POEORB"
                os.system(unzip)
            else: 
                print(f"Correct file structure for OSV files does not exist: {dirname}.")

def processGRD():

    '''Processes the Sentinel 1 data using the Gamma workflow''' 

    for dirname in os.listdir(rootdir):
        if dirname.endswith(".SAFE"):
            #set directory and file names
            dir = f'{rootdir}{dirname}'
            if path.exists(f"{dir}/osv/POEORB/"):
                filename= str(dirname).lower().replace("_", "-")[:-10]
                filenameHH = filename.replace("1ssh","hh").replace("grdh","grd")

                #Generate MLI and GRD images and parameter files from a Sentinel-1 GRD product
                par_command= f"par_S1_GRD {dir}/measurement/{filenameHH}-001.tiff {dir}/annotation/{filenameHH}-001.xml {dir}/annotation/calibration/calibration-{filenameHH}-001.xml - {dir}/{filenameHH}_HH_grd.par {dir}/{filenameHH}_HH_grd - - - - -"
                os.system(par_command)

                # correct orb files must be allocated beforehand in SAFE folder (/osv/POEORB) 
                for file in os.listdir(f'{dir}/osv/POEORB/'):
                    if file.endswith("EOF"):
                        orb = str(file)

                #Extract Sentinel-1 OPOD state vectors and copy into the ISP image parameter file
                opod = f"S1_OPOD_vec {dir}/{filenameHH}_HH_grd.par {dir}/osv/POEORB/{orb} -"
                os.system(opod)

                #Multi-looking of intensity (MLI) images
                multilook = f"multi_look_MLI {dir}/{filenameHH}_HH_grd {dir}/{filenameHH}_HH_grd.par {dir}/{filenameHH}_HH_grd_mli {dir}/{filenameHH}_HH_grd_mli.par 2 2 - - -"
                os.system(multilook)

                #Calculate terrain-geocoding lookup table and DEM derived data products
                gc_map = f"gc_map {dir}/{filenameHH}_HH_grd_mli.par - {dem_par} {dem} {dir}/{filename}_dem_seg_geo.par {dir}/{filename}_dem_seg_geo {dir}/{filename}_lut_init 1.0 1.0 - - - {dir}/{filename}_inc_geo - {dir}/{filename}_pix_geo {dir}/{filename}_ls_map_geo 8 2 -"
                os.system(gc_map)

                #Calculate terrain-based sigma0 and gammma0 normalization area in slant-range geometry
                pixel_area = f"pixel_area {dir}/{filenameHH}_HH_grd_mli.par {dir}/{filename}_dem_seg_geo.par {dir}/{filename}_dem_seg_geo {dir}/{filename}_lut_init {dir}/{filename}_ls_map_geo {dir}/{filename}_inc_geo - - - - {dir}/{filename}_pix_fine -"
                os.system(pixel_area)

                #Calculate product of two images: (image 1)*(image 2)
                mli_samples = subprocess.check_output(f"grep samples {dir}/{filenameHH}_HH_grd_mli.par", shell=True)
                mli_samples = str(mli_samples).replace("\n'","").split(' ')[-1][:-3]
                print("MLI Samples:", mli_samples)
                product = f"product {dir}/{filenameHH}_HH_grd_mli {dir}/{filename}_pix_fine {dir}/{filenameHH}_HH_grd_mli_pan {mli_samples} 1 1 -"
                os.system(product)

                #Geocoding of image data using a geocoding lookup table
                dem_samples = subprocess.check_output(f"grep width {dir}/{filename}_dem_seg_geo.par", shell=True)
                dem_samples = str(dem_samples).replace("\n'","").split(' ')[-1][:-3]
                print("DEM Samples:", dem_samples)
                geocode_back = f"geocode_back {dir}/{filenameHH}_HH_grd_mli_pan {mli_samples} {dir}/{filename}_lut_init {dir}/{filenameHH}_HH_grd_mli_pan_geo {dem_samples} - 2 - - - -"
                os.system(geocode_back)

                #Compute backscatter coefficient gamma (sigma0)/cos(inc)
                sigma2gamma = f"sigma2gamma {dir}/{filenameHH}_HH_grd_mli_pan_geo {dir}/{filename}_inc_geo {dir}/{filenameHH}_HH_grd_mli_norm_geo {dem_samples}"
                os.system(sigma2gamma)

                #Conversion of data between linear and dB scale
                linear_to_dB = f"linear_to_dB {dir}/{filenameHH}_HH_grd_mli_norm_geo {dir}/{filenameHH}_HH_grd_mli_norm_geo_db {dem_samples} 0 -99"
                os.system(linear_to_dB) 

                #convert geocoded data with DEM parameter file to GeoTIFF format (dB)
                data2geotiff = f"data2geotiff {dir}/{filename}_dem_seg_geo.par {dir}/{filenameHH}_HH_grd_mli_norm_geo_db 2 {outdir}/{filenameHH}_HH_grd_mli_norm_geo_db.tif -99" 
                os.system(data2geotiff)

                #Produce different types of geotiffs (unhash lines below if want to create them)
                #data2geotiff2 = f"data2geotiff {dir}/{filename}_dem_seg_geo.par {dir}/{filename}_inc_geo 2 {outdir}/{filename}_inc_geo.tif -99"
                #os.system(data2geotiff2)
                #data2geotiff3 = f"data2geotiff {dir}/{filename}_dem_seg_geo.par {dir}/{filename}_ls_map_geo 5 {outdir}/{filename}_ls_map_geo.tif 0"
                #os.system(data2geotiff3)

                print("I finished the scene")
            else:
                print(f"OSV files have not been downloaded: {dirname}.")


def transform_geotiff():  #Tested and works 

    '''Transforms geotiff into the UTM 19S projection (EPSG: 32719)'''

    for geotiff in os.listdir(outdir):
        if geotiff.endswith("db.tif"):
            filename= str(geotiff)[:-4]
            transform = f"gdalwarp -t_srs EPSG:32719 {outdir}/{filename}.tif {outdir}/{filename}_utm_19S.tif"
            os.system(transform)
            #gdal.Warp()
            print(f"{geotiff} transformed to EPSG 32719.")

def crop_geotiff(): #Tested and works

    '''Crops transformed geotiff to the study area boundary''' 

    for geotiff in os.listdir(outdir):
        if geotiff.endswith("_utm_19S.tif"):
            filename = str(geotiff)[:-4]
            print(filename)
            crop = f"gdalwarp -cutline {study_area} -crop_to_cutline {outdir}/{filename}.tif {outdir}/{filename}_cropped.tif"
            os.system(crop)
            print(f"{geotiff} cropped to study area.")

def move_surplus_files(): #Tested and works (also need to work on it so it deletes per S1 scene, rather than the whole folder, to ensure safety.)

    '''Moves surplus files to other folder, from which they can then be deleted where necessary. 
    Should only run once the previous steps have been run on all of the geotiffs in the folder.'''

    if any(File.endswith("_utm_19S_cropped.tif") for File in os.listdir(outdir)):
        for geotiff in os.listdir(outdir):
            if geotiff.endswith("geo_db.tif") or geotiff.endswith("_utm_19S.tif") or geotiff.endswith("geo.tif") or geotiff.endswith(".tif.ovr"):
                os.rename(f"{outdir}/{geotiff}", f"{surplus_files}{geotiff}")
                print(f"{geotiff} has been moved to the to_be_deleted folder.")
            elif geotiff.endswith("_utm_19S_cropped.tif"):
                print(f"{geotiff} is the final product (transformed and cropped).")
            else: 
                print("The geotiff is yet to be cropped to the study area. Complete this step first, before removing the file from this folder.")
    elif any(File.endswith("_utm_19S.tif") for File in os.listdir(outdir)):
        for geotiff in os.listdir(outdir):
            if geotiff.endswith("geo_db.tif"):
                os.rename(f"{outdir}/{geotiff}", f"{surplus_files}{geotiff}")
                #os.remove(geotiff)
            elif geotiff.endswith("_utm_19S_cropped.tif"):
                print(f"{geotiff} is the final product (transformed and cropped).")
            else:
                print(f"{geotiff} is yet to be transformed into UTM Zone 19S. Complete this step first, before removing the file from this folder.")
    else: 
        print("No surplus files exist in this directory.")


'''Run the functions. Hash them out where necessary.'''
#data preparation steps 
unzip()
mk_POEORB_dir()
downloadOSV()
#data processing steps, transformation, crop, and move surplus files
processGRD()
transform_geotiff()
crop_geotiff()
move_surplus_files()

        
