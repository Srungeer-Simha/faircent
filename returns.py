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

## Calculating portfolio value
'''
Below calculation is incorrect. Portvalue should be
amount received till date + PV(future EMI payments)
'''
# Amount received till date
amount_received = account_details.loc[account_details["Category"] == "Payment", "Credit"].sum()

# Remaining payments
remaining_loans = emi_agg[emi_agg["Status"] != "Closed"]
remaining_loans["pending"] = remaining_loans["Tenure (months)"] - (remaining_loans["due"] + remaining_loans["paid"])

cashflow = []
for loan in remaining_loans["Loan Id"]:
    loan_details = remaining_loans[remaining_loans["Loan Id"] == loan]
    future_cashflow = loan_details["EMI Amount(INR)"].to_list()*loan_details["pending"].values[0]
    cashflow.append(future_cashflow)

cashflow = pd.DataFrame(cashflow)
#cashflow["PV"] = cashflow.apply(lambda x: np.npv(0.08/12, x[0:len(x)].dropna()), axis = 1)
cashflow["PV"] = cashflow.apply(lambda x: np.npv(0.08/12, pd.concat([pd.Series(0), x[0:len(x)].dropna()])), axis = 1)
cashflow["MOD"] = cashflow.drop("PV", axis = 1).sum(axis = 1)

# % Bad loans
default_rate = len(emi_agg[emi_agg["Status"] == "Default"])/len(emi_agg)

# Risked portfolio value
future_cashflow = cashflow["PV"].sum()
portfolio_value = amount_received + future_cashflow*(1-default_rate)

## Calculating bad loans amount
default_loans = emi_agg.loc[emi_agg["Status"] == "Default"]
default_amount = default_loans["Investment Amount"].sum() - (default_loans["paid"]*default_loans["EMI Amount(INR)"]).sum()

# Amount transferred
amount_added = account_details.loc[account_details["Category"] == "Recharge", "Credit"].sum()

# Net returns
returns = portfolio_value - amount_added - default_amount

# Return on investment
roi = returns/amount_added

# CAGR
n = (pd.datetime.now() - account_details["Date"].min()).days/365
cagr = np.power((1 + roi), n - 1)

#%% QC

disbursed_amount = account_details.loc[account_details["Category"] == "Disbursement", "Debit"].sum()
invested_amount = emi_agg["Investment Amount"].sum()

print("Disbursed amount in escrow account details: {0}".format(disbursed_amount))
print("Disbrused amount in emi_details: {0}".format(invested_amount))

undiscounted_unrisked_portfolio_value = np.sum(emi_agg["EMI Amount(INR)"]*emi_agg["Tenure (months)"])