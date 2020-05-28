'''Created 21 May 2020

@author: Bryony Freer '''

import csv
import os
from dbfread import DBF
from datetime import datetime
import pandas as pd 
import numpy as np 

#root directory containing all of the zonal stats data tables that will be joined 
rootdir = "/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/results/backscatter/1920/zonal_stats/"
outdir = "/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/results/backscatter/1920/"

def DBFtoCSV():

    '''Convert dbf tables (zonal stats) per date to csv files of polygon id and mean backscatter. ''' 

    for dir in os.listdir(rootdir):
        if dir.endswith(".dbf"):
            table = DBF(rootdir + dir)# table variable is a DBF object
            date_str = dir[:8]
            filename = dir[:-4]
            csv_out = rootdir + filename + ".csv" #output CSV in same directory, same name, different extension
            with open(csv_out, 'w', newline = '') as f:# create a csv file, fill it with dbf content
                writer = csv.writer(f)
                writer.writerow(["Polygon", f"{date_str}"]) # write the column names (Polygon, Date)
                rows_data = []
                for record in table:  # write the rows
                    data = [list(record.values())[0], list(record.values())[3]]
                    rows_data.append(data)
                writer.writerows(rows_data)
 

def merge_CSV():

    '''Merge CSV files per year to a collated mean backscatter per polygon per year.''' 

    frames = [] 
    for file in os.listdir(rootdir):
        if file.endswith('.csv'):
            path = rootdir + file
            df = pd.read_csv(path, index_col=0, header=0)
            df.columns = pd.to_datetime(df.columns, format="%Y%m%d")
            frames.append(df)
    
    #create data frame of all polygon BS values per date 
    csv_out = outdir + "1920_all_backscatter.csv"
    df_all = pd.concat(frames, axis=1, ignore_index=False)
    cols = df_all.columns.tolist()
    sorted_cols = sorted(cols)
    df_all = df_all[sorted_cols]
    df_all.to_csv(csv_out) #export 

    #add rows with summary statistics per date 
    df_all.loc['mean'] = df_all.mean()
    df_all.loc['max'] = df_all.max()
    df_all.loc['min'] = df_all.min()
    df_all.loc['std'] = df_all.std()

    print(df_all.tail(5))

    #create new data frame of BS statistics per date 
    csv_stats_out = outdir + "1920_stats_backscatter.csv"
    df_stats = df_all.reindex(['mean', 'max', 'min', 'std'])
    df_stats = df_stats.T
    print(df_stats.head(10))
    df_stats.to_csv(csv_stats_out) #export
   

#call functions
DBFtoCSV()
merge_CSV()


#Helpful sources 
#https://stackoverflow.com/questions/32772447/way-to-convert-dbf-to-csv-in-python
#https://stackoverflow.com/questions/20906474/import-multiple-csv-files-into-pandas-and-concatenate-into-one-dataframe
#convert column headings to datetime format (https://stackoverflow.com/questions/41677850/change-dataframe-column-names-from-string-format-to-datetime)
