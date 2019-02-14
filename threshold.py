#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 22:07:07 2019

@author: ryanleveille
"""


##Threshold

import numpy as np

some_data = [0,0,0,3,4,5,8,9,7,8,5,3,3,2,2,0,1,3,5,6,6,6,4,3,2,2,3,3,4,5] #test data

i = 0 #initialize
j = len(some_data) #len of data (30)

cats = []

threshold = 4 #threshold
v = np.array(some_data) #value or (volume for real data) put in array form to use where function

new_threshold = int

while (i<j):
    sub_data = some_data[i:j]
    if sub_data[0] < threshold:
            new_threshold = min(min(np.where(v >= threshold)))
            if 0 in (sub_data[0:new_threshold]):
                cats.append('HUM')
            else: 
                cats.append('DEF')
    else:
        new_threshold = min(min(np.where(v < threshold)))
        cats.append('NORM')
        
i = i + new_threshold

print(cats)