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
import matplotlib.pyplot as plt

### read in excel
og = pd.read_excel('og.xlsx')

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

### Number of NA's: From this we observe that they only NA's are in the CasingB Pressure.
numna = og.isnull().sum()
#print(numna)
##the only Nas are in CasingB Pressure

###The question is now what is the length of CasingB Pressure to check if the entire column is empty or not.
#casingbpressure = og["CasingBPressure"]
#casingbsum = casingbpressure.astype(str).sum()
#print(casingbsum)
### (We found that the length is 422378 for this therefore there are 64 values in CasingBPressure all of which are "No Data Available" so we are going to drop CasingBPressure.


##delete dataframes that are unneccessary - those include NameofFacility,TypeofFacility,WellheadCasingB (name is repetitive, type is too, wellheadcasing B is an empty column with no data)
ogclean = og.drop(columns = ['Name','Type', 'CasingBPressure'])
#ogcleanhead = ogclean.head()
#print(ogcleanhead)
#the columns were successfully dropped

#get rid of the "time is invalid" by replacing them with last value (this way it does not delete from the time series)
ogclean.loc[ogclean['FlowlinePressure'] == "The time is invalid."] = "585.009460449219"
ogclean.loc[ogclean['CasingAPressure'] == "The time is invalid."] = "1777.83874511719"
ogclean.loc[ogclean['FlowlineTemperature'] == "The time is invalid."] = "80.6008224487305"
ogclean.loc[ogclean['Volume'] == "The time is invalid"] = "7702.91845703125"
ogclean.loc[ogclean['WellheadTubingPressure'] == "The time is invalid"] = "847.973266601563"

#Starting the dataset from this time. (58084)
#10/4/2017  1:00:00 AM

#ogclean = ogclean.iloc[54425:,] #this is from the place when volume began (if interested)
ogclean = ogclean.iloc[58084:,] #This is when the volume starts to consistenly hover around 8000. 
#Everything before this point was either the run up in volume or would skew our deferments (would pass our threshold quite often if we started before this)

#change everything to float for calculations
ogclean['WellheadTubingPressure'] = ogclean.WellheadTubingPressure.astype(float)
ogclean['Volume'] = ogclean.Volume.astype(float)
ogclean['CasingAPressure'] = ogclean.CasingAPressure.astype(float)
ogclean['FlowlinePressure'] = ogclean.FlowlinePressure.astype(float)
ogclean['FlowlineTemperature'] = ogclean.FlowlineTemperature.astype(float)

#get rid of negatives in flowlinepressure
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

#####Categorization##############3
      
vol_list = [] #create list to store values for Volume (when Volume is an array or Series it does not work so we make it a list)
for i in ogclean['Volume']: #search through column Volume
    vol_list.append(i) #add volume to volume list

cats = pd.DataFrame(vol_list, columns=['Values']) #create new dataframe cats to store categories 
cats['Categories'] = '' #create a new column in Cats that will consist of strings (labels)

cats.loc[cats.Values>=4000, 'Categories'] = 'REG' #initial category (if it is above threshold it is always REG)
cats.loc[cats.Values<4000, 'Categories'] = 'HUM' #anything below 4000 we will categorize as HUM, then if 0 is Not in that section we will change it to DEF.

cats['section'] = (cats.Categories != cats.Categories.shift()).cumsum() 
#To tell 'HUM' sections with 0 in Values from those without, we mark all sections with a different number to be able to group them

sectionsize = cats.groupby(['section']).size() #this shows for the size of the sections, very interesting
#This is very interesting for data exploration
sectionmean = cats.groupby('section').mean()

for n, g in cats.groupby('section'): #search through section by grouping them together and looking for their values and 
    if 0 not in g.Values.values and 'HUM' in g.Categories.values: #this is saying that if 0 is NOT in the group of values and HUM is, then this whole section is now DEF!
        cats.loc[g.index, 'Categories'] = 'DEF' #this locates all the indexes within our grouped sections and replaces them to DEF

for name, group in cats.groupby('section'):
    print(name)
    print(group)
#This allows you to check out each section individually (we should drop the last section off as a DEF bc volume goes below 4000 and bc the well is dying at this point.)
        
print(cats)

######## 3 Categories to 2 ########

finalcats = cats #make a copy DF to go from 3 variables, HUM,REG,and DEF, to NOT DEF or DEF.

for name, group in finalcats.groupby('section'):
    print(name)
    print(group) #this is great for checking to see if it worked (it does)

for n, g in finalcats.groupby('section'):
    if 'HUM' in g.Categories.values:
        finalcats.loc[g.index, 'Categories'] = 'NOT'

for n, g in finalcats.groupby('section'):
    if 'REG' in g.Categories.values:
        finalcats.loc[g.index, 'Categories'] = 'NOT'
        
        
#Last Cat for our Nueral Network, this will eventually be our Y response in our Nueral that we are trying to predict. Either DEF or NOT. (we need to use a 1440 lag because that is 1 day)

#if (size(group=="NOT")<1440):
#    group="DEF"
#    
#else:
#    starting_index_of_next_group - 1440: starting_index_of_next_group = "DEF"
###start at first point it crosses mean threshold
#print(cats_1)
#
#section = cats_1['section']
#
#if len(section) in g.Categories.values <1440:
#    cats_1.loc[g.index, 'Categories'] = 'DEF'
#    
#print(cats_1)

###if a section of NOT is less than 1440 then there was a def within that 24 hour range so all of those NOTS / indexes of NOt are now equal to DEF
## IFFF the NOT section Is > 1440 you chop off the extra to until YOU MAKE THE CLOSEST 1440 a DEFERMENT (it can be 240) (if it is a long section like 4000, then it is only 1440 and the remaining 2600 are still NOT)






























































#all below was unused code but I would like to keep it in the file as comments in case I want to reference it in the future.
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
#ogclean.to_excel("ogclean.xlsx")

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

            
            
#
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

#create lists to store indexes & values for classifcation and algorithim
#volumelst = []
#belowval = []
#belowind = []
#
#for i in ogclean.Volume: #loop through column volume and take that value and put it into volume list
#    volumelst.append(i)
#
###volstd = meanog['Volume'] - (1.5*stdevog['Volume']) #calculate the mean of Volume - 1.5 standard deviations (you can change this to 2,3, whatever number you want)
#threshold = 4000
#
#for index, value in enumerate(volumelst): #(enumerate) allows you to store the index and value you are looking for
#    if value <= 4000: #if value is less than our threshold but above 0 then add to our lists
#        belowval.append(value)
#        belowind.append(index)
#
#voldic = DataFrame({'Index': belowind, 'Value': belowval}) #create a dataframe with the indexes and corresponding values
#print(voldic)
#
##this is a way to get all of the points and index where they are below the threshold of 4k..
#
#      
#
#
#
#some_data = [0,0,0,3,4,5,8,9,7,8,5,3,3,2,2,0,1,3,5,6,6,6,4,3,2,2,3,3,4,5] #test data
#
#i = 0 #initialize
#j = len(some_data) #len of data (30)
#
#cats = [] #categories' list
#human = []
#defr = []
#norm = []
#
#
#threshold = 4 #threshold
#v = np.array(some_data) #value or (volume for real data) put in array form to use where function
#print(v)
#
#next_thresh = min([i for i in range(len(v)) if v[i] >= threshold]) #this variable was created to loop through the data #stored as int in python
#next_thresh_next = min([i for i in range(next_thresh+1,len(v)) if v[i] <= threshold]) #trying to create a function that crosses over the thresholds and classifies if the 
#next_thresh_next = min([i for i in range(next_thresh+1,len(v)) if v[i] >= threshold])
#index_above_thresh = [i for i in range(len(v)) if v[i] >= threshold] #this produces the list of indexes for the indexes in the range of the array and if the value of that index is >= threshold
#index_below_thresh = [i for i in range(len(v)) if v[i] <= threshold] #this produces the list of indexes for the indexes in the range of the array and if the value of that index is <= threshold
#index_at_zero = [i for i in range(len(v)) if v[i] == 0] #this produces the list of indexes for the indexes in the range of the array and if the value of that index is == 0
#index_below_human = [i for i in range(next_thresh) if v[i] <= threshold]
#next_thresh_next = min([i for i in range(next_thresh+1,len(v)) if v[i] <= threshold])
#
#next_threshold = int(next_threshold)
#
#new_threshold = int
#
#while (i<j):
#    sub_data = some_data[i:j]
#    if sub_data[0] < threshold:
#            new_threshold = min(min(np.where(v >= threshold))) #this should now equal index 0123(4) because index 4 is where it reaches 4 again. So now what? ###### somehow write if the value 0 is found in the range from index 0 to 4 then add all to human####
#            if 0 in (sub_data[0:new_threshold]):
#                human.append("HUM")
#            else: 
#                defr.append("DEF")
#    else:
#        norm.append("NORM")
#        new_threshold = min(min(np.where(v < threshold)))
#    i = i + new_threshold
#    
#print(human)
#print(defr)
#print(norm)

#         else {
#                 next_thr <- min(min(which(sub_data < threshold)),length(sub_data))
#                 labs <- c(labs, rep("REG", next_thr - 1))
#         }
#         i <- i + next_thr -1
#         iter <- iter+1
# }
#
# labs <- c(labs, labs[length(labs)])
#
# iter
# test_df <- data.frame(Val=some_data, Labs=labs)
# test_df
    
#
#human = np.where(v == 0) #this is the indexes where volume (v) is equal to 0 
#thresh = np.where(v <= threshold) #this is the indexes where volume (v is <= threshold (4 for practice))

#valthresh = v[np.where(v <= threshold)]


#print(human)


#threshhuman = next(thresh.where(v <= threshold and 0 in range(thresh))
#
#i = 0
#j = len(some_data)
#human = []
#deferment = []
#normal = []
#threshold = 4
#nextthr = min
#
#def firstcategory():
#    for idx,val in enumerate(some_data):
#        if val == 0:
#            human.append(idx)
#        elif i <= threshold:
#            deferment.append(idx)
#        else:
#            normal.append(idx)
#            
#belowstd()
#
#print(deferment)
#
#
#for index, value in enumerate(deferment):
#    print(index)
#
#
#human = []
#deferment = []
#normal = []
#thresholdindex = []
#threshold = 4
#i = 0
#j = len(some_data)
#
#for index, value in enumerate(some_data):
#    if value <= threshold and value !=0:
#
#val = val for (idx, val) in enumerate(some_data))
#
#while i > j:
#   val, idx = ((val, idx) for (idx, val) in enumerate(some_data))
#   sub_data = some_data[i:j]
#   if sub_data[0] < threshold:
#        next_thr = min(index) >= threshold, len(sub_data)  
                        #next_thr <- min(min(which(sub_data >= threshold)),length(sub_data))
#                 if (0 %in% sub_data[1: (next_thr -1)]){
#                         labs <- c(labs, rep("HUM", next_thr -1))
#                 }
#                 else {
#                         labs <- c(labs, rep("DEF", next_thr -1))
#                 }
#         }
#         else {
#                 next_thr <- min(min(which(sub_data < threshold)),length(sub_data))
#                 labs <- c(labs, rep("REG", next_thr - 1))
#         }
#         i <- i + next_thr -1
#         iter <- iter+1
# }
#
# labs <- c(labs, labs[length(labs)])
#
# iter
# test_df <- data.frame(Val=some_data, Labs=labs)
# test_df
    
    #sub_data = some_data[i:j]
    #if value < threshold:
    #    next_thr = min(index).where( >= threshold in some_data
    #and if 0 is in some_data[:(next_thr - 1)]:
    #    human.append[next_thr - 1]


#while i < j:
#    sub_data = some_data[i:j]
#    if (sub_data[i] < threshold):
#       next_thr = min(sub_data[i] >= threshold) in len(sub_data)
#       if 0 in sub_data[0: (next_thr - 1)]:
#           human.append[next_thr - 1]
#           i += 1
#print(human)
           

#print(labs)
#                         labs <- c(labs, rep("DEF", next_thr -1))
#                 }
#         }
#         else {
#                 next_thr <- min(min(which(sub_data < threshold)),length(sub_data))
#                 labs <- c(labs, rep("REG", next_thr - 1))
#         }
#         i <- i + next_thr -1
#         iter <- iter+1
# }
#
# labs <- c(labs, labs[length(labs)])
#
# iter
# test_df <- data.frame(Val=some_data, Labs=labs)
# test_df



