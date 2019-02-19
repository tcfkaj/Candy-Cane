# Candy-Cane
RNN-LTSM to predict deferment on synthetic oil-well data.

#og.xlsx is the original data file containing the synthetic oil-well data.

#og.py is the script that cleans the original excel file (og.xlsx).

During the data preprocessing phase we:

1) Performed exploratory data analysis.
2) Searched for Na's or missing data.
3) Renamed columns to have no spaces to make querying easier.
4) Dropped the 3 unnecessary / insignificant columns (Name ,Type, Casing B Pressure (no data))
5) Sliced the dataframe from where the 'Volume' production began (ogclean.iloc[54425:,]) so data starts from when production started.
6) Replaced all negative values for 'FlowlinePressure' to 0 (this meant the sensors were either off or it was 0).
7) Converted all the data to float format for statistical analysis.
8) Performed statistical analysis to better understand our data.
9) Plotted the data to visualize the data over time.
10) Checked the correlation between our variables.
11) Saved our cleaned dataframe to the excel file 'ogclean.xlsx'.
12) Categorized our data as either a HUM,DEF,or NORM.
13) Recategorized our data to DEF or NOT DEF to be our Y response for our Nueral.
14) Implemented a time lag for our DEF or NOT DEF predictor because our Nueral needs to predict 1 day in advance.
