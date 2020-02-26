'''
Project: Analysing Faircent Portfolio performance
Purpose: Aggregating monhtly emi status reports
Author: Srungeer Simha
'''
#%% Loading libraries

import pandas as pd
import numpy as np
import os

cur_dir = "C:\\Apps\\Srungeer\\Documents\\Personal\\Personal Finance\\Faircent\\EMI payments"

#%% Loading files
emi_data = []

for file in os.listdir(cur_dir):
    print(file)
    
    df = pd.read_csv(cur_dir + "\\" + file, header = 2)
    df["Month"] = file.rstrip(".csv").split("_")[-1]
    emi_data.append(df)

emi_data = pd.concat(emi_data, sort = False)

#%% Data cleaning and processing

## Fixing datatypes

emi_data["Investment Amount"] = emi_data["Investment Amount"].str.replace(",", "").astype(np.float32)
emi_data["Rate"] = emi_data["Rate"].str.strip("%").astype(np.float32)
emi_data["Tenure"] = emi_data["Tenure"].str.strip(" months").astype(np.int16)

emi_data.rename(columns = {"Tenure": "Tenure (months)", "Rate": "Rate %"}, inplace = True)

## Removing duplication of closed loans


## Aggregating data

emi_status = emi_data.groupby(["Loan Id", "EMI Status"]).size().unstack(fill_value = 0).reset_index()

emi_data = emi_data.groupby("Loan Id", as_index = False).agg({
                            "Borrower Name": "first",
                            "Investment Amount": np.mean,
                            "Rate %": np.mean,
                            "Tenure (months)": np.mean,
                            "EMI Amount(INR)": np.sum,
                            "Principal Amount(INR)": np.sum,
                            "Interest Amount(INR)": np.sum})

emi_data = pd.merge(emi_data, emi_status, on = "Loan Id", how = "left")

## Detemining loan status



