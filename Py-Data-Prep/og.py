# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


##Oil and Gas Data Project

###import libraries
import pandas as pd
import numpy as np
from pandas import Series,DataFrame
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split # Import train_test_split function
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn.linear_model import LogisticRegression
#arima result - logisitic regression


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

#data missingness map
#ogclean = ogclean.iloc[54423:,] #this is from the place when volume began (if interested)
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
plt.xlabel('Time')
plt.ylabel('Volume')
plt.title('Predictors vs Time')
plt.show()
#as you can see from this graph, volume has a negative linear relationship with time, so does CasingAPressure, FlowlinePressure, Flowline Temperature, WellheadTubingPressure

####correlation coeffecient#####
wtp_v = ogclean['Volume'].corr(ogclean['WellheadTubingPressure']) #wellheadtubing correlation with volume
flp_v = ogclean['Volume'].corr(ogclean['FlowlinePressure']) #flowlinepressure correlation with volume
flt_v = ogclean['Volume'].corr(ogclean['FlowlineTemperature']) #flowlinetemperature correlation with volume
cap_v = ogclean['Volume'].corr(ogclean['CasingAPressure']) #casingapressure correlation with volume

corrdf = Series({'TubingPressure': wtp_v,'FLowlinePressure': flp_v,'FLowlineTemperature': flt_v,'CasingAPressure': cap_v})
print("Correlation Matrix with Volume: \n",corrdf)
#WTP_V is WellheadTubingPressure and Volume (.631863)
#FLP_V is FlowlinePressure and Volume (.902992)
#FlT_V is FLowlineTemperature and Volume (.510193)
#CAP_V is CasingAPressure and Volume (.835090)

ogclean.head()

## As we can see they are all highly correlated with volume and Flowline Pressure is the highest

###Final Cats all in one  DF

final_cats = pd.DataFrame(ogclean)
final_cats['Categories'] = '' #create a new column in Cats that will consist of strings (labels)

final_cats.loc[final_cats.Volume>=4000, 'Categories'] = 'REG' #initial category (if it is above threshold it is always REG)
final_cats.loc[final_cats.Volume<4000, 'Categories'] = 'HUM' #anything below 4000 we will categorize as HUM, then if 0 is Not in that section we will change it to DEF.

final_cats['section'] = (final_cats.Categories != final_cats.Categories.shift()).cumsum()

for n, g in final_cats.groupby('section'): #search through section by grouping them together and looking for their values and 
    if 0 not in g.Volume.values and 'HUM' in g.Categories.values: #this is saying that if 0 is NOT in the group of values and HUM is, then this whole section is now DEF!
        final_cats.loc[g.index, 'Categories'] = 'DEF'

for n, g in final_cats.groupby('section'):
    if 'HUM' in g.Categories.values:
        final_cats.loc[g.index, 'Categories'] = 'NOT'

for n, g in final_cats.groupby('section'):
    if 'REG' in g.Categories.values:
        final_cats.loc[g.index, 'Categories'] = 'NOT'
        
final_cats['section'] = (final_cats.Categories != final_cats.Categories.shift()).cumsum() 

sectionsize = final_cats.groupby(['section']).size() 


#######
###Stephens Threshold
##time 19619

cc = pd.read_csv("CC.csv")
##

final_cats = pd.DataFrame(cc)
threshold = final_cats.loc[:, "pred.band4sd"]

final_cats['Categories'] = '' #create a new column in Cats that will consist of strings (labels)

final_cats.loc[final_cats.Volume>=threshold, 'Categories'] = 'REG' #initial category (if it is above threshold it is always REG)
final_cats.loc[final_cats.Volume<threshold, 'Categories'] = 'HUM' #anything below 4000 we will categorize as HUM, then if 0 is Not in that section we will change it to DEF.

final_cats['section'] = (final_cats.Categories != final_cats.Categories.shift()).cumsum()

for n, g in final_cats.groupby('section'): #search through section by grouping them together and looking for their values and 
    if 0 not in g.Volume.values and 'HUM' in g.Categories.values: #this is saying that if 0 is NOT in the group of values and HUM is, then this whole section is now DEF!
        final_cats.loc[g.index, 'Categories'] = 'DEF'

for n, g in final_cats.groupby('section'):
    if 'HUM' in g.Categories.values:
        final_cats.loc[g.index, 'Categories'] = 'NOT'

for n, g in final_cats.groupby('section'):
    if 'REG' in g.Categories.values:
        final_cats.loc[g.index, 'Categories'] = 'NOT'
        
final_cats['section'] = (final_cats.Categories != final_cats.Categories.shift()).cumsum() 

sectionsize = final_cats.groupby(['section']).size() 


####


##CONVERT TIMESTAMP

final_cats['Datetime'] = pd.to_datetime(final_cats['Timestamp'], errors='coerce')
final_cats.set_index('Datetime',inplace=True)
ogclean['Volume'].describe()



from sklearn.metrics import mean_squared_error


###This turns our NOT or DEF into Binary Data 1 or 0.
from sklearn.preprocessing import LabelEncoder
number = LabelEncoder()
final_cats['Categories'] = number.fit_transform(final_cats['Categories'].astype('str'))

##1 is NOT
##0 is DEF

##Drop Timestamp column, and sections
final_cats = final_cats.drop(columns = ['Timestamp','section'])



daily_groups = final_cats.resample('D')
daily_data = daily_groups.sum()


jarrod_excel = final_cats.to_excel("JData.xlsx")

# summarize
print(daily_data.shape)
print(daily_data.head())


###

#export_excel = final_cats.to_excel("Data.xlsx")

target = final_cats.Categories

#plt histogram
plt.hist(final_cats.Volume, bins=500)
plt.hist(final_cats['Categories' == 1], bins=200)
#Histogram of the value
#seaborn plot
#g = sns.FacetGrid(finalcats, col='Survived')
#g.map(plt.hist, 'Age', bins=20)

target = final_cats.Categories
final_cats = final_cats.drop(columns = ['Categories'])

#Difference Data
final_cats.plot()
final_cats = final_cats - final_cats.shift(1)
final_cats = final_cats.dropna()
final_cats.plot()


##Split into Test/Training Data
feature_cols = ['WellheadTubingPressure', 'FlowlinePressure', 'FlowlineTemperature', 'CasingAPressure']
X = final_cats[feature_cols] # Features
y = target[1:] # Target variable


#TEST/TRAIN SPLIT
#from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, shuffle=False)



##Standardize data
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X_train) 
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)


##Split into Test/Training Data
feature_cols = ['WellheadTubingPressure', 'FlowlinePressure', 'FlowlineTemperature', 'CasingAPressure']
X = final_cats[feature_cols] # Features
y = final_cats.Categories # Target variable



#TEST/TRAIN SPLIT
#from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, shuffle=False)



    ##
   ####
 ########    
##########
#####TREE####
#split dataset in features and target variable###
#feature_cols = ['WellheadTubingPressure', 'FlowlinePressure', 'FlowlineTemperature', 'CasingAPressure', 'Volume']
#X = final_cats[feature_cols] # Features
#y = final_cats.Categories # Target variable
# Split dataset into training set and test set
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1) # 70% training and 30% test

# Create Decision Tree classifer object
clf = DecisionTreeClassifier()

# Train Decision Tree Classifer
clf = clf.fit(X_train,y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)

print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
## 99% accuracy, as expected with the unbalanced data set.


########
####Logistic Regression### we now have a binary response , DEF or NOT
##
#


#feature_cols = ['WellheadTubingPressure', 'FlowlinePressure', 'FlowlineTemperature', 'CasingAPressure', 'Volume']
#X = final_cats[feature_cols] # Features
#y = final_cats.Categories # Target variable
LogReg = LogisticRegression() 
LogReg.fit(X_train, y_train)
y_pred = LogReg.predict(X_test)

from sklearn.metrics import confusion_matrix
confusion_matrix = confusion_matrix(y_test, y_pred)

###*******
##SVM

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X_train)  # Don't cheat - fit only on training data
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

#y_train = scaler.transform(y_train)
#y_test = scaler.transform(y_test)

###SVM

from sklearn.linear_model import SGDClassifier

clf_sgd = SGDClassifier(loss="log", penalty="l2", max_iter=20, class_weight = 'balanced', learning_rate = 'optimal')
clf_sgd.fit(X_train, y_train)


#clf_prob = SGDClassifier(loss="log", max_iter=5).fit(X_train, y_train)
#clf_prob.predict_proba(X_test)

clf_pred = clf_sgd.predict(X_test)

from sklearn.metrics import confusion_matrix

confusion_matrix = confusion_matrix(y_test, clf_pred)








#####STEVEN CODE
#####


#cc_labs = pd.read_csv("cc_labs_234sd.csv")

cc_data_band = pd.read_csv("CC.csv")

vol_list = cc_data_band.loc[:, "Vol.Day"]
vol_list = list(vol_list)

cats = pd.DataFrame(vol_list, columns=['Values']) #create new dataframe cats to store categories 
cats['Categories'] = '' #create a new column in Cats that will consist of strings (labels)

threshold = cc_data_band.loc[:, "pred.band4sd"]

cats.loc[cats.Values>=threshold, 'Categories'] = 'REG' #initial category (if it is above threshold it is always REG)
cats.loc[cats.Values<threshold, 'Categories'] = 'HUM' #anything below 4000 we will categorize as HUM, then if 0 is Not in that section we will change it to DEF.

cats.Categories.value_counts()
        
cats['section'] = (cats.Categories != cats.Categories.shift()).cumsum() 
#To tell 'HUM' sections with 0 in Values from those without, we mark all sections with a different number to be able to group them

sectionsize = cats.groupby(['section']).size() #this shows for the size of the sections, very interesting
sectionmedian = cats.groupby(['section']).median() #this shows the median for each section
#This is very interesting for data exploration
sectionmean = cats.groupby('section').mean()

for n, g in cats.groupby('section'): #search through section by grouping them together and looking for their values and 
    if 0 not in g.Values.values and 'HUM' in g.Categories.values: #this is saying that if 0 is NOT in the group of values and HUM is, then this whole section is now DEF!
        cats.loc[g.index, 'Categories'] = 'DEF' #this locates all the indexes within our grouped sections and replaces them to DEF

#lab1 = cats["Categories"]
#lab2 = cats["Categories"]
#lab3 = cats["Categories"]
#
#cc_labs = pd.DataFrame({"lab_2sd":lab1, "lab_3sd":lab2, "lab_4sd":lab3})
#
#cc_labs.to_csv("cc_labs_234sd_python.csv", index=0)


for n, g in cats.groupby('section'):
    if 'HUM' in g.Categories.values:
        cats.loc[g.index, 'Categories'] = 'NOT'

for n, g in cats.groupby('section'):
    if 'REG' in g.Categories.values:
        cats.loc[g.index, 'Categories'] = 'NOT'
        
        #We now have sections that were HUM/REG and they are now NOT, so we are going to shift sections so it is only DEF or NOT. (we have 52 sections now from 136 before)
cats['section'] = (cats.Categories != cats.Categories.shift()).cumsum() 

sectionsize = cats.groupby(['section']).size()



##ARIMA


feature_cols = ['WellheadTubingPressure', 'FlowlinePressure', 'FlowlineTemperature', 'CasingAPressure','Volume']
X = final_cats[feature_cols] # Features
y = target

from statsmodels.tsa.arima_model import ARIMA
model = ARIMA(final_cats['Volume'], order=(1, 1, 0))
model_fit = model.fit(disp=0)
print(model_fit.summary())

plt.plot(model_fit)
plt.show()
###

model_fit.resid.plot()

model_fit.resid.plot(kind='kde')


final_cats['forecast'] = model_fit.predict(start = 180000, end=182147 , dynamic= True)  
final_cats[['Volume','forecast']].plot(figsize=(10,10))


##NUERAL 

import tensorflow as tf
from tensorflow.contrib import rnn

class RNNGenerator:
    def create_LSTM(self, inputs, weights, biases, seq_size, num_units):
        # Reshape input to [1, sequence_size] and split it into sequences
        inputs = tf.reshape(inputs, [-1, seq_size])
        inputs = tf.split(inputs, seq_size, 1)
    
        # LSTM with 2 layers
        rnn_model = rnn.MultiRNNCell([rnn.BasicLSTMCell(num_units),rnn.BasicLSTMCell(num_units)])
    
        # Generate prediction
        outputs, states = rnn.static_rnn(rnn_model, inputs, dtype=tf.float32)
    
        return tf.matmul(outputs[-1], weights['out']) + biases['out']


import math


def evaluate_forecasts(actual, predicted):
	scores = list()
	# calculate an RMSE score for each day
	for i in range(actual.shape[1]):
		# calculate mse
		mse = mean_squared_error(actual[:, i], predicted[:, i])
		# calculate rmse
		rmse = math.sqrt(mse)
		# store
		scores.append(rmse)
	# calculate overall RMSE
	s = 0
	for row in range(actual.shape[0]):
		for col in range(actual.shape[1]):
			s += (actual[row, col] - predicted[row, col])**2
	score = math.sqrt(s / (actual.shape[0] * actual.shape[1]))
	return score, scores




#timeseries = final_cats['Volume']
#
#timeseries.rolling(2).mean().plot(label='Day Rolling Mean')
#timeseries.rolling(2).std().plot(label='Day Rolling Std')
#timeseries.plot()
#plt.legend()
#
#plt.plot(X_train[:,2])
#plt.show()


###VAR
#
#final_cats.dtypes
#
#final_cats = final_cats.drop(columns = ['Timestamp','section'])
#    
##final_cats['Timestamp'] = pd.to_datetime(final_cats.Timestamp , format = '%Y/%m/%d %H.%M.')
#
#var_plz.dtypes
#
#var_plz = final_cats
#var_plz = var_plz.drop(columns = ['Timestamp','section'])
#
#var_plz['Categories'] = var_plz.Categories.astype(int)
#
#from statsmodels.tsa.vector_ar.var_model import VAR
#
#model = VAR(endog=X_train)
#model_fit = model.fit()
#
#prediction = model_fit.forecast(model_fit.y, steps=len(X_test))
#
#cols = var_plz.columns
#
##converting predictions to dataframe
#pred = pd.DataFrame(index=range(0,len(prediction)),columns=[cols])
#for j in range(0,5):
#    for i in range(0, len(prediction)):
#       pred.iloc[i][j] = prediction[i][j]
#
from sklearn.metrics import mean_squared_error
#import math
#
##check rmse
#for i in cols:
#    print('rmse value for', i, 'is : ', math.sqrt(mean_squared_error(pred[i], X_test[i])))
#   
#
###LAGGING, took forever 
#lags = range(1, 1441)  # Just two lags for demonstration.
#
#final_cats.assign(**{
#    '{} (t-{})'.format(col, t): final_cats[col].shift(t)
#    for t in lags
#    for col in final_cats
#})


##Nueral Network
###before you do this , to predict 24 hours in advance , you will have to do a time lag### for 24 hour for Nueral Network (1440, then cut off the last 1440 since it cant predict a day in advance onces it is 1399 or less left of the dataframe)

##incorporate a 24 hour time lag for 1440 to predict 1 day in advance

#this might not work great because the data is negatively trending downward (data with a pattern dont have to worry about windowing?)

## Feature Scaling
#from sklearn.preprocessing import StandardScaler
#sc = StandardScaler()
#X_train = sc.fit_transform(X_train)
#X_test = sc.transform(X_test)

#x1 = casingpresure
#x2 = temperature
#y = DEF OR NOT

#for n, g in finalcats.groupby('section'):
#    if any 'REG' in g.Categories.values:
#        finalcats.loc[g.index, 'Categories'] = 'NOT'
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
##



######Categorization#############
#      
#vol_list = [] #create list to store values for Volume (when Volume is an array or Series it does not work so we make it a list)
#for i in ogclean['Volume']: #search through column Volume
#    vol_list.append(i) #add volume to volume list
#
#cats = pd.DataFrame(vol_list, columns=['Values']) #create new dataframe cats to store categories 
#cats['Categories'] = '' #create a new column in Cats that will consist of strings (labels)
#
#cats.loc[cats.Values>=4000, 'Categories'] = 'REG' #initial category (if it is above threshold it is always REG)
#cats.loc[cats.Values<4000, 'Categories'] = 'HUM' #anything below 4000 we will categorize as HUM, then if 0 is Not in that section we will change it to DEF.
#
#cats['section'] = (cats.Categories != cats.Categories.shift()).cumsum() 
##To tell 'HUM' sections with 0 in Values from those without, we mark all sections with a different number to be able to group them
#
#sectionsize = cats.groupby(['section']).size() #this shows for the size of the sections, very interesting
#sectionmedian = cats.groupby(['section']).median() #this shows the median for each section
##This is very interesting for data exploration
#sectionmean = cats.groupby('section').mean()
#
#for n, g in cats.groupby('section'): #search through section by grouping them together and looking for their values and 
#    if 0 not in g.Values.values and 'HUM' in g.Categories.values: #this is saying that if 0 is NOT in the group of values and HUM is, then this whole section is now DEF!
#        cats.loc[g.index, 'Categories'] = 'DEF' #this locates all the indexes within our grouped sections and replaces them to DEF
#
#for name, group in cats.groupby('section'):
#    print(name)
#    print(group)
##This allows you to check out each section individually (we should drop the last section off as a DEF bc volume goes below 4000 and bc the well is dying at this point.)
#        
#print(cats)

#
#
######### 3 Categories to 2 ########
#
#finalcats = cats #make a copy DF to go from 3 variables, HUM,REG,and DEF, to NOT DEF or DEF.
#
#for name, group in finalcats.groupby('section'):
#    print(name)
#    print(group) #this is great for checking to see if it worked (it does)
#
#for n, g in finalcats.groupby('section'):
#    if 'HUM' in g.Categories.values:
#        finalcats.loc[g.index, 'Categories'] = 'NOT'
#
#for n, g in finalcats.groupby('section'):
#    if 'REG' in g.Categories.values:
#        finalcats.loc[g.index, 'Categories'] = 'NOT'
#        
#        #We now have sections that were HUM/REG and they are now NOT, so we are going to shift sections so it is only DEF or NOT. (we have 52 sections now from 136 before)
#finalcats['section'] = (finalcats.Categories != finalcats.Categories.shift()).cumsum() 
#
#sectionsize = finalcats.groupby(['section']).size()
##check the size of each section



#all below was unused code but I would like to keep it in the file as comments in case I want to reference it in the future.
#grouping stats for modelling

#plotly
#import plotly.plotly as py
#import plotly.graph_objs as go
#data = [go.Histogram(x=finalcats.Values,
#                     histnorm='probability')]
#py.iplot(data, filename='histogram')
    
#import lightgbm as lgb
#d_train = lgb.Dataset(X_train, label=y_train)
#params = {}
#params['learning_rate'] = 0.003
#params['boosting_type'] = 'gbdt'
#params['objective'] = 'binary'
#params['metric'] = 'binary_logloss'
#params['sub_feature'] = 0.5
#params['num_leaves'] = 10
#params['min_data'] = 50
#params['max_depth'] = 10
#clf_1 = lgb.train(params, d_train, 100)
#
#
##Prediction
#y_pred=clf_1.predict(X_test)
##convert into binary values
#for i in range(0,99):
#    if y_pred[i]>=.5:       # setting threshold to .5
#       y_pred[i]=1
#    else:  
#       y_pred[i]=0
#       
#       
#
#
#cm = confusion_matrix(y_test, y_pred)
##Accuracy
#from sklearn.metrics import accuracy_score
#accuracy=accuracy_score(y_pred,y_test)

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

