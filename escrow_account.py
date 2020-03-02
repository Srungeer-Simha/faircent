'''
Project: Analysing Faircent Portfolio performance
Purpose: Processing escrow account details
Author: Srungeer Simha
'''
#%% Loading libraries

import pandas as pd
import numpy as np

#%% Loading escrow account details

cur_dir = "C:\\Apps\\Srungeer\\Documents\\Personal\\Personal Finance\\Faircent\\"
filename = "ESCROW_ACCOUNT_BALANCE_641143_01-02-20.csv"

data = pd.read_csv(cur_dir + filename, header = 1)

#%% Adding categories and cleaning data

# Renaming column names
data.columns = ["Date", "Description", "Debit", "Credit", "Balance"]

# Converting date column into datetime
data["Date"] = pd.to_datetime(data["Date"], format = "%Y-%m-%d")

## Adding categories

data.loc[data["Description"].str.lower().str.contains("recharge"), "Category"] = "Recharge"
data.loc[data["Description"].str.lower().str.contains("disbursed"), "Category"] = "Disbursement"
data.loc[data["Description"].str.lower().str.contains("fee"), "Category"] = "Fees"
data.loc[data["Description"].str.lower().str.contains("payment"), "Category"] = "Payment"

#%% Exporting data

data.to_excel(cur_dir + "account_details.xlsx", index = False)