import matplotlib.pyplot as plt
import numpy as np

'''

This code conducts a technoechonomic assessment using values from the Pressley et al. single-stream MRF spreadsheet model to 
quantify the financial feasiblity of processing 1 t of waste as delivered to a MRF with and without a cyclone. 

'''


## INPUTS

# Diesel Use
diesel_cyclone = [0, 0, 0]  # L/t, 'extra' diesel used in MRF with cyclone

# Electricity Use and Baling Wire Use
# electricity and wire consumption of MRF without cyclone (from Presseley et al. spreadsheet model)
electricity_base = [3.99, 3.98, 3.97] # kWh/t waste; 5%, 10%, 15% plastics in glass stream 
baling_wire_base = [0.92, 0.91, 0.90] # kWh/t waste; 5%, 10%, 15% plastics in glass stream

# electricity an wire consumption of MRF with cyclone (from Presseley et al. spreadsheet model)
electricity_trial = [4.19, 4.20, 4.20] # kWh/t waste; 5%, 10%, 15% plastics in glass stream
baling_wire_trial = [0.93, 0.93, 0.93] # kWh/t waste; 5%, 10%, 15% plastics in glass stream

# electricity and extra wire consumption of cyclone (assumed to be difference btwn trial and base)
electricity_cyclone = [electricity_trial[i] - electricity_base[i] for i in range(len(electricity_base))]
baling_wire_cyclone = [baling_wire_trial[i] - baling_wire_base[i] for i in range(len(electricity_base))]

# Residue 'Use'
# Percent of input mass that ends up in residue stream + impurities in 'pure' glass bale
residue_base = [2.097, 2.430, 2.764] # 5, 10, 15% plastic in glass stream
residue_trial = [2.146, 2.156, 2.166] # 5, 10, 15% plastic in glass stream
residue_cyclone = [residue_trial[i] - residue_base[i] for i in range(len(residue_base))]

# Revenue Calcs
# Percentages of total input recovered in MRF without cyclone (from Presseley et al. spreadsheet model)... 
#                  Al,  PET,   HDPE,  Fe,   Glass,   OCC,  Non-OCC,  Film
RecMat_trial = [[2.522, 3.621, 3.033, 3.724, 12.044, 39.639, 28.411, 4.86], # 5% plastics in glass stream
                [2.522, 3.615, 3.029, 3.724, 12.044, 39.639, 28.411, 4.86], # 10% plastics in glass stream
                [2.522, 3.610, 3.024, 3.724, 12.044, 39.639, 28.411, 4.86]] # 15% plastics in glass stream

# Percentages of total input recovered in MRF with cyclone (from Presseley et al. spreadsheet model)... 
#                  Al,  PET,   HDPE,  Fe,   Glass,   OCC,  Non-OCC,  Film
RecMat_base =  [[2.522, 3.445, 2.886, 3.724, 12.416, 39.639, 28.411, 4.86], # 5% plastics in glass stream
                [2.522, 3.263, 2.734, 3.724, 12.416, 39.639, 28.411, 4.86], # 10% plastics in glass stream
                [2.522, 3.082, 2.582, 3.724, 12.416, 39.639, 28.411, 4.86]] # 15% plastics in glass stream

#                  Al,  PET,   HDPE,  Fe,   Glass,   OCC,  Non-OCC,  Film
RecMat_prices = [1750,  400,   900,   200,   10,     200,    80,     650] # $/t

def get_revenue(RecMat_list, RecMat_prices):
    revenue = []
    for i in range(len(RecMat_list)):
        revenue.append(sum([RecMat/100 * price for RecMat,price in zip(RecMat_list[i],RecMat_prices)]))
    return revenue

revenue_base = get_revenue(RecMat_base, RecMat_prices)
revenue_trial = get_revenue(RecMat_trial, RecMat_prices)

revenue_cyclone = [revenue_trial[i] - revenue_base[i] for i in range(len(revenue_base))]

## PARAMETERS
# 'Fixed' parameters
land_cost_rate = 12000 # $/acre
construct_cost_rate = 97.7 # $/ft^2
equipment_cost = 87800 # $

# User-defined parameters and variable costs
space_requirement = 144 #ft^2 ****
diesel_cost = 3.03 # $/gal
electricity_cost = 0.169 # $/kWh ***
residue_disposal_fee = 40 # $/t waste
bale_wire_cost = 2150 # $/t wire
waste_processed_yearly = 120000 # t/yr
waste_tipping_fees = 0 # $/t input; no difference btwn base and trial MRF


## COST CALCULATIONS
# One-time Costs
investment = equipment_cost # $
land_cost = (space_requirement/42560) * land_cost_rate # $; 1 acre = 43560 ft^2
construct_cost = space_requirement * construct_cost_rate # $
project_contingencies = 0.37 * equipment_cost # $
legal_contractor_fees = 0.23 * equipment_cost # $

# Yearly Costs
equipment_maintenance = 10200 # $/yr
waste_tipping_cost_yearly = waste_tipping_fees * waste_processed_yearly # $/yr
diesel_cost_yearly = [(diesel_cyclone[i] / 3.7854) * diesel_cost * waste_processed_yearly for i in range(len(diesel_cyclone))] # $/yr; 1 gal = 3.7854 L
electricity_cost_yearly = [electricity_cyclone[i] * electricity_cost * waste_processed_yearly for i in range(len(electricity_cyclone))] # $/yr
residue_disposal_cost_yearly = [(residue_cyclone[i] / 100) * residue_disposal_fee * waste_processed_yearly for i in range(len(residue_cyclone))] # $/yr
bale_wire_cost_yearly = [(baling_wire_cyclone[i] / 907) * bale_wire_cost * waste_processed_yearly for i in range(len(baling_wire_cyclone))] # $/yr; 1 t = 907 kg

# Total Costs
total_investment_cost = investment + land_cost + construct_cost + project_contingencies + legal_contractor_fees 
total_yearly_cost = [equipment_maintenance + waste_tipping_cost_yearly + diesel_cost_yearly[i] + electricity_cost_yearly[i] + residue_disposal_cost_yearly[i] + bale_wire_cost_yearly[i]
                     for i in range(3)]

# ROI & BREAKEVEN CALCS
profit_yearly = []
ROI_1yr = []

for i in range(len(revenue_cyclone)):
    profit_yearly.append(waste_processed_yearly * revenue_cyclone[i])
    ROI_1yr.append((profit_yearly[i]-total_investment_cost-total_yearly_cost[i])/(total_investment_cost + total_yearly_cost[i]) * 100)

breakeven_time = [total_investment_cost/(profit_yearly[i]-total_yearly_cost[i]) for i in range(len(profit_yearly))]


## PLOTTING
# Figure 1: ROI and Breakeven Time
fig1 = plt.figure()

ax1 = fig1.add_subplot(111)
ax2 = ax1.twinx()

width = 0.25

x = np.arange(len(['5%', '10%', '15%']))

ax1.bar(x, ROI_1yr, width, color = 'lightgreen')
ax2.bar(x+width, breakeven_time, width, color = 'forestgreen')
ax1.set_xticks(x+0.5*width, ['5%', '10%', '15%'])
ax1.set_xlabel('Plastic %')
ax1.set_ylabel('ROI over 1 yr (%)', color = 'lightgreen')
ax2.set_ylabel('Breakeven time (years)', color = 'forestgreen')

ytick_positions = np.arange(0,400+1, 100)
ax1.set_yticks(ytick_positions)

fig1.set_size_inches(7,6)

plt.show()

