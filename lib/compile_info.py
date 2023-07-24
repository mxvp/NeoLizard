import pandas as pd

df = pd.read_csv('Predictions.txt',index_col=0)

headers = df[:,3]


# to do: 
##  read in the original header system of the maf files
##  create aditional column for each in predictions and fill them out
##  (check if any aditional info is in annovar files)