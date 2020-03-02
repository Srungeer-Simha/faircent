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
emi_data["EMI Date"] = pd.to_datetime(emi_data["EMI Date"], format = "%d-%m-%Y")

emi_data.rename(columns = {"Tenure": "Tenure (months)", "Rate": "Rate %"}, inplace = True)

## Removing duplication of closed loans

closed_loans = emi_data.loc[emi_data["EMI Status"] == "closed", "Loan Id"].unique()
closed_dates = emi_data[(emi_data["Loan Id"].isin(closed_loans)) & (emi_data["EMI Status"] == "closed")].groupby("Loan Id")["EMI Date"].min()

drop_rows = []
for loan in closed_loans:
    drop_rows.append(emi_data[(emi_data["Loan Id"] == loan) & (emi_data["EMI Date"] > closed_dates.loc[loan])].index)
emi_data.drop(drop_rows[0], inplace = True, axis = 0)

## Aggregating data

emi_status = emi_data.groupby(["Loan Id", "EMI Status"]).size().unstack(fill_value = 0).reset_index()

emi_agg = emi_data.groupby("Loan Id", as_index = False).agg({
                            "Borrower Name": "first",
                            "Investment Amount": np.mean,
                            "Rate %": np.mean,
                            "Tenure (months)": np.mean,
                            "EMI Amount(INR)": np.mean,
                            "Principal Amount(INR)": np.sum,
                            "Interest Amount(INR)": np.sum})

emi_agg = pd.merge(emi_agg, emi_status, on = "Loan Id", how = "left")

## Detemining loan status

emi_agg.loc[emi_agg["due"] > 1, "Status"] = "Default"
emi_agg.loc[emi_agg["due"] == 1, "Status"] = "Delayed"
emi_agg.loc[(emi_agg["due"] == 0) & (emi_agg["paid"] > 0), "Status"] = "Regular"
emi_agg.loc[emi_agg["closed"] > 0, "Status"] = "Closed"

#%% Exporting data

emi_agg.to_excel(cur_dir.strip("EMI payments") + "EMI_status.xlsx", index = False)
