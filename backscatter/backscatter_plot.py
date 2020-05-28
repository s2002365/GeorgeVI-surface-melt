
'''
Script to plot mean backscatter graphs using seaborn.

Created 21 May 2020
@author: Bryony Freer 
Adapted from script by HattieBranson
'''

##########################################

#import necessary packages and set local variables
import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from datetime import datetime

rootdir = "/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/results/backscatter/1920/"
outdir = "/exports/csce/datastore/geos/groups/MSCGIS/s2002365/code/results/backscatter/1920/figs/"

##########################################
#1) PREPARE STATS DATAFRAME

# Read in the backscatter csv files as data frames
path_stats = rootdir + '1920_stats_backscatter.csv'
backscatter_df = pd.read_csv(path_stats, header=0, infer_datetime_format=True)

#Prepare  for plotting
cols = ['Date', 'Mean', 'Max', 'Min', 'StD']
backscatter_df.columns = cols
backscatter_df['Date'] = pd.to_datetime(backscatter_df['Date']) #converts dates from str to datetime 

##########################################
#2) PREPARE ALL BACKSCATTER DATAFRAME  --> allows shaded std error bars to be plotted 

# Read in the backscatter csv files as data frames
path_all = rootdir + '1920_all_backscatter.csv'
backscatter_all_df = pd.read_csv(path_all, header=0, infer_datetime_format=True)

#Prepare for plotting
backscatter_all_df = backscatter_all_df.set_index('Polygon').T
backscatter_all_df.index = pd.to_datetime(backscatter_all_df.index, format='%Y-%m-%d')
backscatter_all_df.reset_index(level=0, inplace=True)
backscatter_all_df.rename(columns={'index':'Date'}, inplace=True)

# pd.melt is used to convert the wide-form DF into a long-form DF for plotting with seaborn
meltBackscatter = pd.melt(backscatter_all_df, id_vars='Date') 

##########################################
#PLOT DATA WITH SEABORN 

# Set figure size and quality
fig, ax = plt.subplots(num=None, figsize=(8, 6), dpi=300, facecolor='w', edgecolor='k')

# Control aesthetics 
sns.set()
sns.set(style="whitegrid", rc={"grid.linewidth": 0.2, "lines.linewidth": 0.5}) # White grid background, width of grid  line and series line
sns.set_context(font_scale = 0.5) # Scale of font

# Use the lineplot seaborn function to generate a plot with one categorial variable (in this case date)
#Statistics data (mean) only:
#sns.lineplot(x='Date', y='Mean', data=backscatter_df, color="slateblue", ci = "sd", err_style="band", ax=ax)

#Using all data, plots mean and std shading band 
sns.lineplot(x='Date', y='value', data=meltBackscatter, color="slateblue", estimator="mean", ci = "sd", err_style="band", ax=ax)

ax.set(xlabel='Date', ylabel='Backscatter (deciBels)')
ax.legend(labels=['Mean Backscatter'], loc='lower right')

# Add second baseline backscatter to plot.
#dB_baseline = sns.lineplot(x='variable', y='value', data=meltBaseline, color="thistle", ci = "sd", err_style="bars")
#ax2.set(ylabel='Backscatter (deciBels)')
#dB_baseline.legend(labels=['Baseline'], loc='lower left')

# Rotate the x axis labels so that they are readable
plt.setp(ax.get_xticklabels(), rotation=20)

ax.tick_params(labelsize=8) # Control the label size

#ax.xaxis_date()

# Save the figure
out_path = outdir + "19-20_mean_backscatter.png"
plt.savefig(out_path, bbox_inches='tight')

#Useful sources
#https://seaborn.pydata.org/generated/seaborn.lineplot.html
#https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.melt.html
