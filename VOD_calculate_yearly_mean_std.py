#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 17:34:49 2020

@author: jashvina

This file computes annual mean, standard deviation, variation, and coefficient of
variation for VOD given several input files. Don't overwrite output files.
"""
import os
from netcdf_statistics import statistics_netcdf

def main():
    
    #Years for which to compute statistics
    years = ['2015', '2016', '2017', '2018']
    
    # Set working directory
    os.chdir('/Users/jashvina/jashvina/GoogleDrive/My Drive/2019_wind_extremes/' \
             'Data/SMOS_2015_2018_SMAP_Maria_Piles/SMOS_VOD_EASE2_36km_AM_2015to2019/ASC')
    
    longterm_mean = 'VOD_2015_2018_longterm_mean.nc'
    
    for year in years:
        # Get a list of the filenames of all data in one year 
        input_files_one_year = os.listdir('./{}'.format(year))[:-1]
        input_filenames = []
        for file in input_files_one_year:
            input_filenames.append('./{}/'.format(year) + file)

        # Define output filenames
        output_file = './VOD_{}_mean_std_longterm.nc'.format(year)

        statistics_netcdf(year, input_filenames, 'VOD', 'VOD', 
                          output_file, longterm_mean, 'VOD_longterm_mean',
                          mask_negative = True)
        
main()