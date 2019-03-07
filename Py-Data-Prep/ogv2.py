#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 17:43:16 2019

@author: ryanleveille
"""

# ogv2.py

#We already preprocessed the data in og.py and saved that data to 'oclean.xlsx' so our group could all have the same dataset to work on. This script is now to perform analysis further.
#import libraries
import pandas as pd
import numpy as np
from pandas import Series,DataFrame
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt


###

### read in excel
ogv2 = pd.read_excel('ogclean.xlsx')

#print(ogv2)


# summary statistics on clean data starting where volumes starts. (row 54,425 from original)
countog = ogv2.count()
minog = ogv2.min()
maxog = ogv2.max()
meanog = ogv2.mean()
stdevog = ogv2.std()
print('\n')
print('\n')
###observe data## can comment this out at any time but it helps for reference
print('count',countog)
print('\n')
print('min', minog)
print('\n')
print('max',maxog)
print('\n')
print('mean',meanog)
print('\n')
print('stdev',stdevog)

#create lists to store indexes & values
volumelst = []
volindex = []
volval = []

for i in ogv2.Volume: #loop through column volume and take that value and put it into volume list
    volumelst.append(i)

volstd = meanog['Volume'] - (1.5*stdevog['Volume']) #calculate the mean of Volume - 1.5 standard deviations (you can change this to 2,3, whatever number you want)

for index, value in enumerate(volumelst): #(enumerate) allows you to store the index and value you are looking for
    if value <= volstd and value != 0: #if value is less than our threshold but above 0 then add to our lists
        volindex.append(index)
        volval.append(value)

voldic = DataFrame({'Index': volindex, 'Value': volval}) #create a dataframe with the indexes and corresponding values
print(voldic)



#ogv2.plot(x="Timestamp", y = ["Volume","CasingAPressure", "FlowlinePressure", "FlowlineTemperature", "WellheadTubingPressure"])
#plt.show() #this is here in case you want to visualize data

##Now we have the volume dataframe where the index is below the threshold but above 0. From here we can run a loop to check the previous two points (A-B) > 0 to see if the point has negative momentum and include those in a seperate data frame
#print(len(voldic)) (7924 before checking for negative momentum)

## next part  could extract index of each value for a classification tree, or run a logistic regression.

