#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 14:44:33 2019

@author: ryanleveille
"""

##Oil and Gas Data Project

###import libraries
import pandas as pd
import numpy as np
from pandas import Series,DataFrame
from sklearn.linear_model import LogisticRegression
###

### read in excel
og = pd.read_excel('og.xlsx')
###

### rename columns w/o spaces
og = og.rename(columns = {"Wellhead Tubing - Pressure": "WellheadTubingPressure"})
og = og.rename(columns = {"Volume - Calendar Day Production": "Volume"})
og = og.rename(columns = {'Wellhead Casing "B" - Pressure': "CasingBPressure"})
og = og.rename(columns = {'Wellhead Casing "A" - Pressure': "CasingAPressure"})
og = og.rename(columns = {'Flowline Pressure': "FlowlinePressure"})
og = og.rename(columns = {'Flowline Temperature': "FlowlineTemperature"})
og = og.rename(columns = {'Name of Facility': "Name"})
og = og.rename(columns = {'Type of Facility': "Type"})
###

### Check head to see if data was renamed (it is)
#data_top = og.head()
#print(data_top)
###

### Number of NA's: From this we observe that they only NA's are in the CasingB Pressure.
numna = og.isnull().sum()
#print(numna)
##the only Nas are in CasingB Pressure

###The question is now what is the length of CasingB Pressure to check if the entire column is empty or not.
#casingbpressure = og["CasingBPressure"]
#print(len(casingbpressure))
#casingbsum = casingbpressure.astype(str).sum()
#print(casingbsum)
### (We found that the length is 422378 for this therefore there are 64 values in CasingBPressure all of which are "No Data Available" so we are going to drop CasingBPressure.


##delete dataframes that are unneccessary - those include NameofFacility,TypeofFacility,WellheadCasingB (name is repetitive, type is too, wellheadcasing B is an empty column with no data)
ogclean = og.drop(columns = ['Name','Type', 'CasingBPressure'])
#ogcleanhead = ogclean.head()
#print(ogcleanhead)
#the columns were successfully dropped


#get rid of the "time is invalid"
ogclean1 = ogclean[ogclean.WellheadTubingPressure != "The time is invalid."]
ogclean1 = ogclean[ogclean.Volume != "The time is invalid."]
ogclean1 = ogclean[ogclean.CasingAPressure != "The time is invalid."]
ogclean1 = ogclean[ogclean.FlowlinePressure != "The time is invalid."]
ogclean1 = ogclean[ogclean.FlowlineTemperature != "The time is invalid."]

#get rid of "no available data"
ogclean2 = ogclean1[ogclean1.WellheadTubingPressure != "No Available Data"]
ogclean2 = ogclean1[ogclean1.Volume != "No Available Data"]
ogclean2 = ogclean1[ogclean1.CasingAPressure != "No Available Data"]
ogclean2 = ogclean1[ogclean1.FlowlinePressure != "No Available Data"]
ogclean2 = ogclean1[ogclean1.FlowlineTemperature != "No Available Data"]

#change everything to float for calculations
ogclean2['WellheadTubingPressure'] = ogclean2.WellheadTubingPressure.astype(float)
ogclean2['Volume'] = ogclean2.Volume.astype(float)
ogclean2['CasingAPressure'] = ogclean2.CasingAPressure.astype(float)
ogclean2['FlowlinePressure'] = ogclean2.FlowlinePressure.astype(float)
ogclean2['FlowlineTemperature'] = ogclean2.FlowlineTemperature.astype(float)

#word = "The time is invalid." #this approach might or might not work
#ogclean = ogclean[~ogclean.str.contains("The time is invalid.")]
#ogclean1 = ogclean[~ogclean.WellheadTubingPressure.str.contains(word)]
#ogclean1 = ogclean[~ogclean.Volume.str.contains(word)]
#ogclean1 = ogclean[~ogclean.CasingAPressure.str.contains(word)]
#ogclean1 = ogclean[~ogclean.FlowlinePressure.str.contains(word)]
#ogclean1 = ogclean[~ogclean.FlowlineTemperature.str.contains(word)]

#statistics on clean data starting where volumes starts. (row 54,425) - this eliminates are negatives from Casing and Tubing Pressure bc it is before the well started and sensors were off
countog = ogclean2.iloc[54425:,].count()
minog = ogclean2.iloc[54425:,].min()
maxog = ogclean2.iloc[54425:,].max()
meanog = ogclean2.iloc[54425:,].mean()
stdevog = ogclean2.iloc[54425:,].std()

main_stats = DataFrame({'Count': countog, 'Min': minog, 'Max': maxog, 'Mean': meanog, 'Stdev' :stdevog})
main_stats = main_stats.T
print(main_stats)
print('\n')
print('\n')
#observe data
print('count',countog)
print('\n')
print('min', minog)
print('\n')
print('max',maxog)
print('\n')
print('mean',meanog)
print('\n')
print('stdev',stdevog)

belowstdev = []

def belowstd():
    for i in ogclean2.Volume:
        if i <= 6200: #standard deviation is 1584 so i just did a rough subtraction of 1600 from the mean (7841)
            belowstdev.append(i)

belowstd()            
print(belowstdev)
            

#casingapressure = ogclean1['CasingAPressure']
#print(len(casingapressure))
#casingasum = casingapressure.astype(str).sum()
#print(casingasum)

#41388 row

###### data exploration / observations

#tubing = og["WellheadTubingPressure"]
#tubemax = tubing.max()
#print(tubemax)

#tubingpressuremax = og.groupby('WellheadTubingPressure').max()
#print("Wellhead Tubing - Pressure: max",tubingpressuremax)

# ^^ or ?? tubing = og['WellheadTubingPressure']
#tubingmax = tubing.max()
#print(tubingmax)

#tubing = og["WellheadTubingPressure"]
#production = og["Volume"]
#Y = tubing
#X = production
##run a regresion?? data is not cleaned!!

#grouped = og.groupby(['WellheadTubingPressure', 'Volume'])
#grouped.agg('mean')
#print(grouped)
#errors because data is not clean1!!

#dfag = og.agg(['sum', 'min'])
#print(dfag)

