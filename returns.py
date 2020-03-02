'''
Project: Analysing Faircent Portfolio performance
Purpose: Calculating returns and other metrics
Author: Srungeer Simha
'''
#%% Loading libraries

import pandas as pd
import numpy as np

#%% Loading data

cur_dir = "C:\\Apps\\Srungeer\\Documents\\Personal\\Personal Finance\\Faircent\\"
emi_agg = pd.read_excel(cur_dir + "EMI_status.xlsx")
account_details = pd.read_excel(cur_dir + "account_details.xlsx")

#%% Calculating returns

# Calculating portfolio value
'''
Below calculation is incorrect. Portvalue should be
amount received till date + PV(future EMI payments)
'''
portfolio_value = np.sum(emi_agg["Tenure (months)"]*emi_agg['EMI Amount(INR)'])

# Calculating bad loans amount
default_loans = emi_agg.loc[emi_agg["Status"] == "Default"]
default_amount = default_loans["Investment Amount"].sum() - (default_loans["paid"]*default_loans["EMI Amount(INR)"]).sum()

# Amount transferred
amount_added = account_details.loc[account_details["Category"] == "Recharge", "Amount"].sum()

# Net returns
returns = portfolio_value - amount_added - default_amount

# Return on investment
roi = returns/amount_added

# % Bad loans
default_rate = len(emi_agg[emi_agg["Status"] == "Default"])/len(emi_agg)

# CAGR
n = (pd.datetime.now() - account_details["Date"].min()).days/365
cagr = np.power((1 + roi), n - 1)

#%% QC

disbursed_amount = account_details.loc[account_details["Category"] == "Disbursement", "Amount"].sum()
invested_amount = emi_agg["Investment Amount"].sum()

print("Disbursed amount in escrow account details: {0}".format(disbursed_amount))
print("Disbrused amount in emi_details: {0}".format(invested_amount))
