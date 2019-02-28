import pandas as pd
from collections import deque
import random
import numpy as np
import time


# Already, detrended and normalized and predictor defined.
main_df = pd.read_csv("../../RNN-ready-DT-MA30-NORM.csv", index_col=0)
print(main_df.head())

# Define some globals here
SEQ_LEN = 2


# Separate validation set.
times = sorted(main_df.index.values)
last_15pct = sorted(main_df.index.values)[-int(0.15*len(times))]

validation_main = main_df[(main_df.index > last_15pct)]
main_df = main_df[(main_df.index <= last_15pct)]


