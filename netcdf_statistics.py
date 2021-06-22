#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 17:33:36 2020

@author: jashvina

This file contains a function to take the yearly mean, variance, coefficient of 
variation and standard deviation of netcdf files. Don't overwrite output files.
"""

import numpy as np
import xarray as xr
import netCDF4


def statistics_netcdf(year, input_filenames, input_variable, output_variable,
                      output_filepath, longterm_mean = None, longterm_mean_variable_name = None,
                      mask_negative = False):
    ''' This function computes the per pixel yearly mean, variance, standard 
        deviation, and coefficient of variation given multiple netCDF4 files (each 
        corresponding to one time point in the year). Intermediate values such 
        as count and sum are also computed at the per-pixel level.
        
        This function accounts for lack of complete spatial overlap between input files
        by excluding NaN values from computations. Output 'count' values are a
        measure of the number of non-null input values.
        
        
        Arguments:
        year: str (used for naming)
        input_filenames:
            A list of strings.  Each entry is the path of an input file that
            corresponds to one time point.  
        input_variable: str (the name of the variable in the input files, used
                             for extracting data from the input files)
        output_variable: str (determines output variable naming)
        output_filepath: filepath to write netcdf to (should end with .nc)
        longterm_mean: filepath of a netcdf with longterm mean values (used to
                       compute longterm coefficient of variation, standard
                       deviation, and variance)
        longterm_mean_variable_name: str (name of the variable containing the
                                         longterm mean values in the longterm_mean file)
        mask_negative: Boolean. If True, masks negative values from input datasets.
    '''
    # MEAN
    # Create a copy of the input dataset that will house the statistical variables: sum, count, mean, standard deviation, and variance
    # Make a copy of a dataset from one date to get the structure of the latitude and longitude coordinates
    # Set the initial values of sum and count to 0
    yr = xr.full_like(xr.open_dataset(input_filenames[0]), fill_value = 0)
    yr = yr.rename_vars({output_variable : '{}_sum_{}'.format(output_variable, year)})
    yr['count_{}'.format(year)] = xr.full_like(yr['{}_sum_{}'.format(output_variable, year)], fill_value = 0)
    
    # Get the per-pixel sum for each year and the per-pixel count of non-null values
    for date in input_filenames:
        ds = xr.open_dataset('{}'.format(date))
        if mask_negative:
            # Mask negative values
            ds['{}'.format(input_variable)] = xr.where(ds['{}'.format(input_variable)] < 0,
                                                      np.nan, ds['{}'.format(input_variable)])

        # Add values from each date to the sum of the year
        # If null, do nothing (sum value stays the same)
        yr['{}_sum_{}'.format(output_variable, year)] = xr.where(ds['{}'.format(input_variable)].notnull(),
                                                    yr['{}_sum_{}'.format(output_variable, year)] + ds['{}'.format(input_variable)],
                                                    yr['{}_sum_{}'.format(output_variable, year)])

        # Count non-null values per pixel to use for computing the per-pixel mean
        # Add a count for each non-null value
        # If null, do nothing (count value stays the same)
        yr['count_{}'.format(year)] = xr.where(ds['{}'.format(input_variable)].notnull(),
                                                   yr['count_{}'.format(year)] + 1,
                                                   yr['count_{}'.format(year)])
    
    # Set the value of pixels where there were no valid values to nan (in these pixels, all dates in the year had null values)
    # This will set the mean values for those pixels to nan as well
    yr['count_{}'.format(year)] = xr.where(yr['count_{}'.format(year)] == 0, np.nan, yr['count_{}'.format(year)])

    # Compute the mean
    yr['{}_mean_{}'.format(output_variable, year)] = yr['{}_sum_{}'.format(output_variable, year)] / yr['count_{}'.format(year)]


    # VARIANCE 
    # create empty DataArray(s) to write to
    yr['{}_variance_{}'.format(output_variable, year)] = xr.full_like(yr['{}_sum_{}'.format(output_variable, year)], fill_value = 0)
    if longterm_mean:
            yr['{}_longterm_variance_{}'.format(output_variable, year)] = xr.full_like(yr['{}_sum_{}'.format(output_variable, year)], fill_value = 0)
            longterm_mean_netcdf = xr.open_dataset(longterm_mean)
    
    # Read netcdfs file by file        
    for date in input_filenames:
        ds = xr.open_dataset('{}'.format(date))
        if mask_negative:
            # Mask negative values
            ds['{}'.format(input_variable)] = xr.where(ds['{}'.format(input_variable)] < 0,
                                                      np.nan, ds['{}'.format(input_variable)])

        # Add values from each date to the sum of the year
        # If null, do nothing (sum value stays the same)
        yr['{}_variance_{}'.format(output_variable, year)] = xr.where(ds['{}'.format(input_variable)].notnull(),
                                                    yr['{}_variance_{}'.format(output_variable, year)] + (ds['{}'.format(input_variable)] - yr['{}_mean_{}'.format(output_variable, year)])**2,
                                                    yr['{}_variance_{}'.format(output_variable, year)])
        if longterm_mean:
            yr['{}_longterm_variance_{}'.format(output_variable, year)] = xr.where(ds['{}'.format(input_variable)].notnull(),
                                                    yr['{}_longterm_variance_{}'.format(output_variable, year)] + (ds['{}'.format(input_variable)] - longterm_mean_netcdf['{}'.format(longterm_mean_variable_name)])**2,
                                                    yr['{}_longterm_variance_{}'.format(output_variable, year)])
            
    yr['{}_variance_{}'.format(output_variable, year)] = yr['{}_variance_{}'.format(output_variable, year)] / (yr['count_{}'.format(year)] - 1)
    if longterm_mean:
        yr['{}_longterm_variance_{}'.format(output_variable, year)] = yr['{}_longterm_variance_{}'.format(output_variable, year)] / (yr['count_{}'.format(year)] - 1)
   
    
    # STANDARD DEVIATION
    yr['{}_std_{}'.format(output_variable, year)] = yr['{}_variance_{}'.format(output_variable, year)] ** (1/2)
    if longterm_mean:
        yr['{}_longterm_std_{}'.format(output_variable, year)] = yr['{}_longterm_variance_{}'.format(output_variable, year)] ** (1/2)
    
    # COEFFICIENT OF VARIATION
    yr['{}_coeff_var_{}'.format(output_variable, year)] = (yr['{}_std_{}'.format(output_variable, year)] / yr['{}_mean_{}'.format(output_variable, year)]) * 100
    if longterm_mean:
        yr['{}_longterm_coeff_var_{}'.format(output_variable, year)] = (yr['{}_longterm_std_{}'.format(output_variable, year)] / longterm_mean_netcdf['{}'.format(longterm_mean_variable_name)]) * 100
    
    
    # WRITE OUT THE FILE
    yr.to_netcdf(path = output_filepath, mode = 'w', format = 'NETCDF4', engine = 'netcdf4')
    
    