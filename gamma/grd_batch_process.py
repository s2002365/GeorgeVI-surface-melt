#activate the gamma environment in the shell
#gma
#geoutils

import os
import subprocess

dem = "/home/s2002365/Dissertation/code/data/DEM/REMA_200m_resampled_20m.dem"
dem_par = "/home/s2002365/Dissertation/code/data/DEM/REMA_200m_resampled_20m.dem_par"
outdir = "/home/s2002365/Dissertation/code/data/s1_grd/s1_grd_processed/test"
rootdir = '/home/s2002365/Dissertation/code/data/s1_grd/test_20m_resampled/'

def processGRD():
    for dirname in os.listdir(rootdir):
        if dirname.endswith(".SAFE"):
            #set directory and file names
            dir = f'/home/s2002365/Dissertation/code/data/s1_grd/test_20m_resampled/{dirname}'
            print(dirname)
            filename= str(dirname).lower().replace("_", "-")[:-10]
            print(filename)
            filenameHH = filename.replace("1ssh","hh").replace("grdh","grd")

            #Generate MLI and GRD images and parameter files from a Sentinel-1 GRD product
            par_command1= f"par_S1_GRD {dir}/measurement/{filenameHH}-001.tiff {dir}/annotation/{filenameHH}-001.xml {dir}/annotation/calibration/calibration-{filenameHH}-001.xml - {dir}/{filenameHH}_HH_grd.par {dir}/{filenameHH}_HH_grd - - - - -"
            os.system(par_command1)

            # correct orb files must be allocated beforehand in SAFE folder (/osv/POEORB) 
            for file in os.listdir(f'{dir}/osv/POEORB/'):
                if file.endswith("EOF"):
                    orb = file

            #Extract Sentinel-1 OPOD state vectors and copy into the ISP image parameter file
            opod1 = f"S1_OPOD_vec {dir}/{filenameHH}_HH_grd.par {dir}/osv/POEORB/{orb} -"
            os.system(opod1)

            #Multi-looking of intensity (MLI) images
            multlook1 = f"multi_look_MLI {dir}/{filenameHH}_HH_grd {dir}/{filenameHH}_HH_grd.par {dir}/{filenameHH}_HH_grd_mli {dir}/{filenameHH}_HH_grd_mli.par 2 2 - - -"
            os.system(multlook1)

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
            product1 = f"product {dir}/{filenameHH}_HH_grd_mli {dir}/{filename}_pix_fine {dir}/{filenameHH}_HH_grd_mli_pan {mli_samples} 1 1 -"
            os.system(product1)

            #Geocoding of image data using a geocoding lookup table
            dem_samples = subprocess.check_output(f"grep width {dir}/{filename}_dem_seg_geo.par", shell=True)
            dem_samples = str(dem_samples).replace("\n'","").split(' ')[-1][:-3]
            print("DEM Samples:", dem_samples)
            geocode_back1 = f"geocode_back {dir}/{filenameHH}_HH_grd_mli_pan {mli_samples} {dir}/{filename}_lut_init {dir}/{filenameHH}_HH_grd_mli_pan_geo {dem_samples} - 2 - - - -"
            os.system(geocode_back1)

            #Compute backscatter coefficient gamma (sigma0)/cos(inc)
            sigma2gamma1 = f"sigma2gamma {dir}/{filenameHH}_HH_grd_mli_pan_geo {dir}/{filename}_inc_geo {dir}/{filenameHH}_HH_grd_mli_norm_geo {dem_samples}"
            os.system(sigma2gamma1)

            #Conversion of data between linear and dB scale
            linear_to_dB1 = f"linear_to_dB {dir}/{filenameHH}_HH_grd_mli_norm_geo {dir}/{filenameHH}_HH_grd_mli_norm_geo_db {dem_samples} 0 -99"
            os.system(linear_to_dB1) 

            #convert geocoded data with DEM parameter file to GeoTIFF format (dB)
            data2geotiff1 = f"data2geotiff {dir}/{filename}_dem_seg_geo.par {dir}/{filenameHH}_HH_grd_mli_norm_geo_db 2 {outdir}/{filenameHH}_HH_grd_mli_norm_geo_db.tif -99" 
            os.system(data2geotiff1)

            #Produce different types of geotiffs (unhash lines below if want to create them)
            #data2geotiff2 = f"data2geotiff {dir}/{filename}_dem_seg_geo.par {dir}/{filename}_inc_geo 2 {outdir}/{filename}_inc_geo.tif -99"
            #os.system(data2geotiff2)
            #data2geotiff3 = f"data2geotiff {dir}/{filename}_dem_seg_geo.par {dir}/{filename}_ls_map_geo 5 {outdir}/{filename}_ls_map_geo.tif 0"
            #os.system(data2geotiff3)
            
            print("I finished the scene")

processGRD()


