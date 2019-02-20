import pandas as pd
from collections import deque
import random
import numpy as np


# Already, detrended and normalized and predictor defined.
main_df = pd.read_csv("../RNN-ready-DT-MA30-NORM.csv", index_col=0)
print(main_df.head())

# Define some globals here
SEQ_LEN = 4320


# Separate validation set.
times = sorted(main_df.index.values)
last_15pct = sorted(main_df.index.values)[-int(0.15*len(times))]

validation_main = main_df[(main_df.index > last_15pct)]
main_df = main_df[(main_df.index <= last_15pct)]


# Define function to get sequences
def sequentize(df):
    df.drop("time",1)

    sequential_data = []
    prev_mins = deque(maxlen=SEQ_LEN)
    for i in df.values:
        prev_mins.append([n for n in i[:-1]])
        if len(prev_mins) == SEQ_LEN:
            sequential_data.append([np.array(prev_mins), i[-1]])


    random.shuffle(sequential_data)



sequentize(main_df)

