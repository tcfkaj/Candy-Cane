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
import matplotlib.pyplot as plt


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

#get rid of the "time is invalid" by replacing them with last value (this way it does not delete from the time series
ogclean.loc[ogclean['FlowlinePressure'] == "The time is invalid."] = "585.009460449219"
ogclean.loc[ogclean['CasingAPressure'] == "The time is invalid."] = "1777.83874511719"
ogclean.loc[ogclean['FlowlineTemperature'] == "The time is invalid."] = "80.6008224487305"
ogclean.loc[ogclean['Volume'] == "The time is invalid"] = "7702.91845703125"
ogclean.loc[ogclean['WellheadTubingPressure'] == "The time is invalid"] = "847.973266601563"


ogclean = ogclean.iloc[54425:,]

#change everything to float for calculations
ogclean['WellheadTubingPressure'] = ogclean.WellheadTubingPressure.astype(float)
ogclean['Volume'] = ogclean.Volume.astype(float)
ogclean['CasingAPressure'] = ogclean.CasingAPressure.astype(float)
ogclean['FlowlinePressure'] = ogclean.FlowlinePressure.astype(float)
ogclean['FlowlineTemperature'] = ogclean.FlowlineTemperature.astype(float)

#get rid of negatives in flowlinepressure!!!
ogclean.loc[ogclean['FlowlinePressure']<0] = 0

# summary statistics on clean data starting where volumes starts. (row 54,425) (but since we took out 64 rows for "No Available Data this subtracted from the data file - this eliminates are negatives from Casing and Tubing Pressure bc it is before the well started and sensors were off
countog = ogclean.count()
minog = ogclean.min()
maxog = ogclean.max()
meanog = ogclean.mean()
stdevog = ogclean.std()

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


##observational graphs
#all other predictors versus time
ogclean.plot(x="Timestamp", y = ["Volume","CasingAPressure", "FlowlinePressure", "FlowlineTemperature", "WellheadTubingPressure"])
plt.show()
#as you can see from this graph, volume has a negative linear relationship with time, so does CasingAPressure, FlowlinePressure, Flowline Temperature, WellheadTubingPressure


####correlation coeffecient#####
wtp_v = ogclean['Volume'].corr(ogclean['WellheadTubingPressure']) #wellheadtubing correlation with volume
flp_v = ogclean['Volume'].corr(ogclean['FlowlinePressure']) #flowlinepressure correlation with volume
flt_v = ogclean['Volume'].corr(ogclean['FlowlineTemperature']) #flowlinetemperature correlation with volume
cap_v = ogclean['Volume'].corr(ogclean['CasingAPressure']) #casingapressure correlation with volume

corrdf = Series({'WTB_V': wtp_v,'FLP_V': flp_v,'FLT_V': flt_v,'CAP_V': cap_v})
print("Correlation Matrix with Volume: \n",corrdf)
#WTP_V is WellheadTubingPressure and Volume (.631863)
#FLP_V is FlowlinePressure and Volume (.902992)
#FlT_V is FLowlineTemperature and Volume (.510193)
#CAP_V is CasingAPressure and Volume (.835090)
## As we can see they are all highly correlated with volume and Flowline Pressure is the highest


#grouping stats for modelling
#below stdev list (comeback to this)
#belowstdev = []
#human = []
#normal = []
#make another column for category to categorize each variable
#classifcation logistic and classification

#maybe try 1.5 stdev, human, and normal

#volumelst = []
#volindex = []
#
#for i in ogclean.Volume:
#    volumelst.append(i)
#
#volstd = meanog['Volume'] - (1.5*stdevog['Volume'])
#
#for index, value in enumerate(volumelst):
#    if value <= volstd and value != 0:
#        volindex.append(index)
#        
#    
#print(volindex)

ogclean.to_excel("ogclean.xlsx")

#def indexvalue():
#    for i in ogclean.Volume:
#        if i <= volstd:
#            volstdindex = ogclean.index[i]
#            volstdlist.append(volstdindex)           
#            
#indexvalue()
#print(volstdlist)

#for i in volstdlist:
#    volstdindex += volsdtindex[i]

            
            

#def belowstd():
#    for i in ogclean.Volume:
#        if i == 0:
#            human.append(i)
#        elif i <= meanog['Volume'] - (1.5*stdevog['Volume']):
#            oneptfivebelowstdev.append(i)
#        else:
#            normal.append(i)
#
#belowstd()  
#print()         

#correlation matrix
#print(ogclean.corr())
#plt.matshow(ogclean.corr()) 

## next part  could extract index of each value for a classification tree, or run a logistic regression.

#volumelst = []
#volindex = []
#
#for i in ogclean.Volume:
#    volumelst.append(i)
#
#volstd = meanog['Volume'] - (1.5*stdevog['Volume'])
#
#for index, value in enumerate(volumelst):
#    if value <= volstd and value != 0:
#        volindex.append(index)
#        
#    
#print(volindex)



