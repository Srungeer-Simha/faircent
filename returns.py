'''
Project: Analysing Faircent Portfolio performance
Purpose: Calculating returns and other metrics
Author: Srungeer Simha
'''
#%% Loading libraries

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#%% Loading data

cur_dir = "C:\\Apps\\Srungeer\\Documents\\Personal\\Personal Finance\\Faircent\\"
emi_agg = pd.read_excel(cur_dir + "EMI_status.xlsx")
account_details = pd.read_excel(cur_dir + "account_details.xlsx")

#%% Calculating returns

## Calculating portfolio value

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
cashflow["PV"] = cashflow.apply(lambda x: np.npv(0.08/12, pd.concat([pd.Series(0), x[0:len(x)].dropna()])), axis = 1)
cashflow["MOD"] = cashflow.drop("PV", axis = 1).sum(axis = 1)

# Default rate
default_rate = len(emi_agg[emi_agg["Status"] == "Default"])/len(emi_agg)

# Portfolio value
future_cashflow = cashflow["PV"].sum()

portfolio_value = amount_received + future_cashflow*(1-default_rate)
unrisked_portfolio_value = amount_received + future_cashflow

## Calculating return metrics

# Calculating bad loans amount
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

cagr = np.power(portfolio_value/amount_added, 1/n) - 1
cagr_unrisked = np.power(unrisked_portfolio_value/amount_added, 1/n) - 1

#%% Plots

# Storing results in data frame format

values = [["Portfolio Value", portfolio_value],
          ["Amount Invested", amount_added],
          ["Default Amount", default_amount]]
values = pd.DataFrame(values, columns=["Parameter", "Value"])

rates = [["CAGR", cagr],
         ["ROI", roi],
         ["Default Rate", default_rate]]
rates = pd.DataFrame(rates, columns = ["Parameter", "Value"])

## Creating bar plots 

fig, ax = plt.subplots(1,2, figsize = (9, 5))

ax[0].bar(values["Parameter"], values["Value"], color = ["green", "blue", "red"])
ax[1].bar(rates["Parameter"], rates["Value"], color = ["green", "yellow", "red"])

ax[0].set_xlabel('')
ax[0].set_ylabel('')
ax[1].set_xlabel('')
ax[1].set_ylabel('')

ax[0].title.set_text('Portfolio Value')
ax[1].title.set_text('Returns')

plt.suptitle("Faircent Portfolio Performance", size = 16)

plt.tight_layout()
plt.subplots_adjust(top=0.84)

# Printing results

print("")
print("Risked Portfolio Value of {0} with {1} invested @ CAGR of {2}".format(np.round(portfolio_value,1), amount_added, np.round(cagr, 2)))
print("Unrisked Portflio Value is {0} @ unrisked CAGR of {1}".format(np.round(unrisked_portfolio_value, 1), np.round(cagr_unrisked, 2)))
print("Current Bad loans amount: {0} @ default rate of {1}".format(np.round(default_amount, 1), np.round(default_rate, 2)))
print("")

#%% Scratch area

disbursed_amount = account_details.loc[account_details["Category"] == "Disbursement", "Debit"].sum()
invested_amount = emi_agg["Investment Amount"].sum()

undiscounted_unrisked_portfolio_value = np.sum(emi_agg["EMI Amount(INR)"]*emi_agg["Tenure (months)"])
undiscounted_future_cashflow = cashflow["MOD"].sum()
undiscounted_portfolio_value = amount_received + undiscounted_future_cashflow*(1-default_rate)
