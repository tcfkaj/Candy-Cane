#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 22:07:07 2019

@author: ryanleveille
"""


##Threshold


some_data = [0,0,0,3,4,5,8,9,7,8,5,3,3,2,2,0,1,3,5,6,6,6,4,3,2,2,3,3,4,5]

#you can do it with pandas:

import pandas as pd #import pandas

#First, create a pandas dataframe from your data list:

df = pd.DataFrame(some_data, columns=['Values'])
#Then add a new column for the categories:

df['Categories'] = '' #this creates the categories column in our data frame that is based on strings

#In a first step, all Values greater or equal to the threshold are 'REG', all others 'HUM':

df.loc[df.Values>=4, 'Categories'] = 'REG'
df.loc[df.Values<4, 'Categories'] = 'HUM'

#To tell 'HUM' sections with 0 in Values from those without, we'll mark all sections with a different number to be able to group them:

df['aux'] = (df.Categories != df.Categories.shift()).cumsum() #not entirely sure how this works but it does haha
#So the dataframe now looks like
#
#    Values Categories  aux
#0        0        HUM    1
#1        0        HUM    1
#2        0        HUM    1
#3        3        HUM    1
#4        4        REG    2
#5        5        REG    2
#6        8        REG    2
#7        9        REG    2
#8        7        REG    2
#9        8        REG    2
#10       5        REG    2
#11       3        HUM    3
#12       3        HUM    3
#13       2        HUM    3
#14       2        HUM    3
#15       0        HUM    3
#16       1        HUM    3
#17       3        HUM    3
#18       5        REG    4
#19       6        REG    4
#20       6        REG    4
#21       6        REG    4
#22       4        REG    4
#23       3        HUM    5
#24       2        HUM    5
#25       2        HUM    5
#26       3        HUM    5
#27       3        HUM    5
#28       4        REG    6
#29       5        REG    6
#and grouping works now with the aux column. Now we can iterate over all groups and change the Categories entries to 'DEF' in the dataframe only for groups in which 0 is not in Values and 'HUM' is in Categories:

for n, g in df.groupby('aux'):
    if 0 not in g.Values.values and 'HUM' in g.Categories.values: #also need to figure out how this is all working
        df.loc[g.index, 'Categories'] = 'DEF'



print(df)
#Result: #the desired output

#    Values Categories  aux
#0        0        HUM    1
#1        0        HUM    1
#2        0        HUM    1
#3        3        HUM    1
#4        4        REG    2
#5        5        REG    2
#6        8        REG    2
#7        9        REG    2
#8        7        REG    2
#9        8        REG    2
#10       5        REG    2
#11       3        HUM    3
#12       3        HUM    3
#13       2        HUM    3
#14       2        HUM    3
#15       0        HUM    3
#16       1        HUM    3
#17       3        HUM    3
#18       5        REG    4
#19       6        REG    4
#20       6        REG    4
#21       6        REG    4
#22       4        REG    4
#23       3        DEF    5
#24       2        DEF    5
#25       2        DEF    5
#26       3        DEF    5
#27       3        DEF    5
#28       4        REG    6
#29       5        REG    6