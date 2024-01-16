
# coding: utf-8

# Importations
import inspect
import sys
import os
from itertools import repeat
import itertools
import numpy as np
import pandas as pd

# Weather class: Weather objects where all parameters like Wind speed, Wind direction, 
# Dew Point, Temperature, etc., are computed and updated from an initial state
"""
March 2018: A weather data frame is required. It might have only one row.
The new class has a public interface that callers can send in a date-time
or a row number and get all the corresponding weather-related data one
way or the other. (E.g., ffmc might be from the weather file or might
be computed). The weather data can be returned in the form of a named 
attributes with FBP input field names (extras are OK, "Scenario"). Here
is what we are hoping for, but we can live without some...
because they may come in from Data.dat...:
datetime, AACP, TMP, RH, WS, WD, FFMC, DMC, DC, ISI, BUI, FWI
TBD: if the weather data does not have FFMC, compute it.
"""
class Weather:
       
    '''
    Inputs:
    wdf_path          string
    '''
    def __init__ (self, wdf_path):
        """Constructor:
            args: wdf is a path to a csv file with rows over time
            outputs: updates the object so that access to the weather can be 
                     entirely via the object.
        """
        self._wdf = pd.read_csv(wdf_path, sep=",", index_col="datetime") # header implied
        self._wdf.columns = self._wdf.columns.str.lower()
        self._wdf.rename(columns={'wd': 'waz'}, inplace=True)     # Associate Waz and WD for main DF
        self._wdf["waz"] = self._wdf["waz"] + 180.0                # Associate Waz and WD for main DF  + 180 working angles     -90 PREVIOUS!!!
        Greater360 = self._wdf["waz"] >= 360                      # Get entries greater than 360
        self._wdf["waz"][Greater360] = self._wdf["waz"][Greater360] - 360     # No more than 360
        self.rows = self._wdf.shape[0]                            # Get nrows for max fire periods in main
        

    '''
    Returns          void
    
    Inputs:
    df               dataframe
    datetime         datetime object
    Row              int
    '''
    def set_columns(self, df, datetime=None, Row=None):
        """
        Update df (presumably for FBP) using whatever data we have from the weather 
        inputs:
            df: data frame to update
        """
        assert (datetime is None or Row is None)
        if Row != None:
            for dfcolname in df.columns:
                if dfcolname in self._wdf.columns:
                    weatherval = self._wdf.loc[self._wdf.index[Row], dfcolname]
                    df.loc[:,dfcolname] = weatherval
        else:
            raise RuntimeError("Datetime not supported yet")
                        
    
    ##### CP: TO BE MODIFIED! (Random weather not implemented)
    '''
    Returns          Dataframe
    
    Inputs:
    df               Dataframe
    WeatherOpt       string
    weatherperiod    int
    datetime         datetime object
    '''
    def update_Weather_FBP(self, df, WeatherOpt, weatherperiod=None, datetime=None):
        # Updates the current weather in df 
        # Has some code for random weather Weather
        if WeatherOpt == "constant":
            print("weather constant, so why is",inspect.stack()[0][3],"called from",inspect.stack()[1][3])
            return df

        if WeatherOpt == "rows":
            # print "Weather is not random"
            self.set_columns(df, Row=weatherperiod)
            return df

        if WeatherOpt == "random":
	    self.set_columns(df, Row=weatherperiod)
            return df
            # Random sampling from a weather file
	    """
            RandomRow = np.random.randint(1, self.rows)
            print("\n--------------------------------------------------------------")
            print("     DEBUG: Taking random row", RandomRow + 2, "from weather file")
            print("--------------------------------------------------------------\n")
            b, c = self._wdf.iloc[weatherperiod].copy(), self._wdf.iloc[RandomRow].copy()
            self._wdf.iloc[weatherperiod], self._wdf.iloc[RandomRow] = c, b
            self.set_columns(df, Row=weatherperiod)
	    """
            return df        
  
    
    '''
    Returns          void
    
    Inputs:
    period           int
    '''
    # Prints-out weather report for current period
    def print_info(self, period):
        print("Weather Info for weather period ", str(period))
        print(self._wdf.iloc[[period]])

