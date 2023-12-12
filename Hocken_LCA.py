import numpy as np
import pandas as pd


'''

This code conducts a life cycle assessment using values from the Pressley et al. single-stream MRF spreadsheet model to 
quantify the environmental impact of processing 1 t of waste as delivered to the MRF with and without a cyclone. This 
code employs the same LCA framework from a study by Olafasakin et al. This code uses emission factors reported in 
Olafasakin et al.

'''


# This function imputs the total facility electricity, distance covered in the collection and transportation process, 
# total facility diesel use, amount of baling wire used, and the emission factors. It outputs the emissions for each 
# impact category in the form of a dictionary and a list.
def get_emissions(facility_electricity, collection_dist, facility_diesel_use, baling_wire, EF_factors):
    # defining impact categories
    keys = ['GWP', 'ODP', 'AP', 'ETP', 'EP', 'PO', 'C', 'NC', 'RE']
    # create empty dictionary and list
    emissions_dict = {key: 0 for key in keys}
    emissions_list = []

    for key in keys:
        # calculate emissions of electricity, collection/transport, baling wire, and diesel for each impact category
        factors = EF_factors[key]
        elect_emi = factors['Electricity'] * facility_electricity 
        col_tra_elect_emi = factors['Collection and Transportation'] * collection_dist 
        baling_wire_emi = factors['Baling Wire'] * baling_wire
        diesel_emi = factors['Diesel'] * facility_diesel_use 
        
        # sum the for emissions from the four materials
        emission = elect_emi + col_tra_elect_emi + baling_wire_emi + diesel_emi
        
        # add emission value to the dictionary and to the list
        emissions_dict[key] = emission
        emissions_list.append(emission)

    return emissions_dict, emissions_list

# This funciton calculates net savings when including the emissions avoided, emissions from recovery, and emissions from 
# landfilling residue
def calculate_net_savings(emis_avoid, emis_list, GWP_residue):
    return sum(emis_avoid) - emis_list[0] - GWP_residue

# USER INPUTS


# Environmental Impacts:
# GWP - 100-year global warming potential in kg CO2-eq
# AP - Acidification potential in H+ -eq
# EP - Eutrophication potential in kg N
# ETP - Ecotoxicity in kg 2,4-D-eq
# ODP - Ozone depletion in CFC-11-eq
# PO - photochemical oxidation in kg NOx-eq. 

# Human health impacts:
# C - Carcinogenics in kg benzene eq 
# NC - non-carcinogenic in kg toluene eq
# RE - Respiratory Effects


# All impact factors are in per liter of diesel, per kwh of electricity, per KM dist,per KG of baling wire

# Source of inventory data: USLCI database
# Impact assessment tool: TRACI


# Emissions factors provided by USLCI database with openLCA TRACI (Olafasakin et al., 2023)
EF_factors = { 'GWP': {"Diesel":4.423200,
               "Electricity":0.504540,
               "Baling Wire":0.304640,
               "Collection and Transportation":0.006886},
      'ODP':{"Diesel" : 9.215190e-08,
             "Electricity" : 3.038520e-08,
             "Baling Wire" : 1.926640e-08,
             "Collection and Transportation" : 4.712000e-11},
      'AP':{"Diesel":2.846750,
            "Electricity":0.148720,
            "Baling Wire":0.061420,
            "Collection and Transportation":0.002384},
      'ETP':{"Diesel" : 0.185280,
             "Electricity" : 0.171790,
             "Baling Wire" : 0.064400,
             "Collection and Transportation" : 0.000271},
      'EP':{"Diesel":2.990000e-03,
            "Electricity":9.569790e-05,
            "Baling Wire":6.063060e-05,
            "Collection and Transportation":1.953054e-06},
      'PO':{"Diesel":0.066490,
            "Electricity":0.001790,
            "Baling Wire":0.001140,
            "Collection and Transportation":0.000026},
      'C':{"Diesel":0.001050,
           "Electricity":0.000850,
           "Baling Wire":0.000250,
           "Collection and Transportation":0.000008},
      'NC':{"Diesel":9.671330,
            "Electricity":6.704060,
            "Baling Wire":6.420490,
            "Collection and Transportation":0.011235},
      'RE':{"Diesel":0.001050,
            "Electricity":0.000850,
            "Baling Wire":0.000250,
            "Collection and Transportation":0.000008}    
}

diesel = 0.7 # L/ton (assumed)
col_dist = 30 # km (assumed)
recyclables = ['Al', 'PET', 'HDPE', 'Fe', 'Glass', 'OCC', 'Non-OCC', 'Plastic film']

# The following three variables are lists of values for the recyclables listed in the variable 'recyclables'
#                   Al,  PET, HDPE,  Fe, Glass,  OCC,Non-OCC, Film
GWP =           [12.57, 2.72, 1.84, 0.11, 1.03, 0.64,   1.84, 1.84]  #per kg of virgin material produced (from Olafasakin et al.)
GWP_secondary = [ 2.18, 0.53, 0.35, 1.27, 0.46, 0.82, 0.7433, 0.63] # kg CO2 eq for preprocess recyclate before use in new products (from Olafasakin et al.)
sub_ratio =     [    1, 0.66, 0.66,    1,    1,    1,      1, 0.66] # substitution ratios for using recovered in place of virgin (from Olafasakin et al.)

# electricity and wire consumption of MRF without cyclone (from Presseley et al. spreadsheet model)
electricity_base = [3.99, 3.98, 3.97] # 5%, 10%, 15% plastics in glass stream 
baling_wire_base = [0.92, 0.91, 0.90] # 5%, 10%, 15% plastics in glass stream

# electricity an wire consumption of MRF with cyclone (from Presseley et al. spreadsheet model)
electricity_trial = [4.19, 4.20, 4.20] # 5%, 10%, 15% plastics in glass stream
baling_wire_trial = [0.93, 0.93, 0.93] # 5%, 10%, 15% plastics in glass stream

# electricity and extra wire consumption of cyclone (assumed to be difference btwn trial and base)
electricity_cyclone = [electricity_trial[i] - electricity_base[i] for i in range(len(electricity_base))]
baling_wire_cyclone = [baling_wire_trial[i] - baling_wire_base[i] for i in range(len(electricity_base))]


# Percentages of total input recovered in MRF without cyclone (from Presseley et al. spreadsheet model) 
#                  Al,  PET,   HDPE,  Fe,   Glass,   OCC,  Non-OCC,  Film
RecMat_trial = [[2.522, 3.621, 3.033, 3.724, 12.044, 39.639, 28.411, 4.86], # 5% plastics in glass stream
                [2.522, 3.615, 3.029, 3.724, 12.044, 39.639, 28.411, 4.86], # 10% plastics in glass stream
                [2.522, 3.610, 3.024, 3.724, 12.044, 39.639, 28.411, 4.86]] # 15% plastics in glass stream

# Percentages of total input recovered in MRF with cyclone (from Presseley et al. spreadsheet model)
#                  Al,  PET,   HDPE,  Fe,   Glass,   OCC,  Non-OCC,  Film
RecMat_base =  [[2.522, 3.445, 2.886, 3.724, 12.416, 39.639, 28.411, 4.86], # 5% plastics in glass stream
                [2.522, 3.263, 2.734, 3.724, 12.416, 39.639, 28.411, 4.86], # 10% plastics in glass stream
                [2.522, 3.082, 2.582, 3.724, 12.416, 39.639, 28.411, 4.86]] # 15% plastics in glass stream


# Percentages of total input recovered by addition of cyclone ('extra' recovery due to cyclone)
RecMat_cyclone = np.subtract(RecMat_trial, RecMat_base) 


# Percent of input mass that ends up in residue stream + impurities in 'pure' glass bale
residue_base = [2.097, 2.430, 2.764] # 5, 10, 15% plastic in glass stream
residue_trial = [2.146, 2.156, 2.166] # 5, 10, 15% plastic in glass stream
residue_cyclone = [residue_trial[i] - residue_base[i] for i in range(len(residue_base))]

# # uncomment if you don't want to include landfilling emissions
# residue_base = [0, 0, 0]
# residue_trial = [0, 0, 0]
# residue_cyclone = [0, 0, 0]

# GWP from landfilling residue (https://doi.org/10.1016/j.resconrec.2018.03.024)
residue_GWP = 356.67 # kg CO2 eq per 1 t residue

## CALCULATE EMISSIONS FROM LANDFILLING RESIDUE
GWP_residue_base = [(r / 100) * residue_GWP for r in residue_base]
GWP_residue_trial = [(r / 100) * residue_GWP for r in residue_trial]
GWP_residue_cyclone = [(r / 100) * residue_GWP for r in residue_cyclone]



## BASE CASE (MRF without cyclone): CALCULATE RECOVERY EMISSIONS & AVOIDED EMISSIONS

# Inititalize list for emissions from recovery for MRF without cyclone
emis_list_base = [] 

# Initialize list for avoided emissions from 1:1 virgin replacement based on recovery from MRF without cyclone
emis_avoid_base = [] 

# Initialize list for net savings with 1:1 virgin replacement for MRF without cyclone
net_savings_base = []

# Initialize list for avoided emissions from secondary virgin replacement (accounts for secondary processing and substitution ratios) for MRF without cyclone
emis_avoid_base_secondary = []

# Initialize list for net savings with secondary virgin replacement for MRF without cyclone
net_savings_base_secondary = []

for i in range(len(electricity_base)):
    emis_dict_base, emis_list_base_i = get_emissions(electricity_base[i], col_dist, diesel, baling_wire_base[i], EF_factors)
    emis_list_base.append(emis_list_base_i)
    
    emis_avoid_base_i = []
    emis_avoid_base_secondary_i = []
    for m in range(len(recyclables)):
        emis_avoid_base_i.append(RecMat_base[i][m] * GWP[m] * 10)
        emis_avoid_base_secondary_i.append((RecMat_base[i][m]*GWP[m]*sub_ratio[m] * 10)-(RecMat_base[i][m] * GWP_secondary[m] * 10)) 
    emis_avoid_base.append(emis_avoid_base_i)
    emis_avoid_base_secondary.append(emis_avoid_base_secondary_i)
    
    net_savings_base.append(calculate_net_savings(emis_avoid_base[i], emis_list_base[i], GWP_residue_base[i]))
    net_savings_base_secondary.append(calculate_net_savings(emis_avoid_base_secondary[i], emis_list_base[i], GWP_residue_base[i]))
    


## TRIAL CASE (MRF with cyclone): CALCULATE RECOVERY EMISSIONS & AVOIDED EMISSIONS

# Inititalize list for emissions from recovery for MRF with cyclone
emis_list_trial = []

# Initialize list for avoided emissions from 1:1 virgin replacement based on recovered material from MRF with cyclone
emis_avoid_trial = []

# Initialize list for net savings with 1:1 virgin replacement for a MRF with cyclone
net_savings_trial = []

# Initialize list for avoided emissions from secondary virgin replacement (accounts for secondary processing and substitution ratios) for MRF with cyclone
emis_avoid_trial_secondary = []

# Initialize list for net savings with secondary virgin replacement for MRF with cyclone
net_savings_trial_secondary = []

for i in range(len(electricity_trial)):
    emis_dict_trial, emis_list_trial_i = get_emissions(electricity_trial[i], col_dist, diesel, baling_wire_trial[i], EF_factors)
    emis_list_trial.append(emis_list_trial_i)
    
    emis_avoid_trial_i = []
    emis_avoid_trial_secondary_i = []
    for m in range(len(recyclables)):
        emis_avoid_trial_i.append(RecMat_trial[i][m] * GWP[m] * 10)
        emis_avoid_trial_secondary_i.append((RecMat_trial[i][m]*GWP[m]*sub_ratio[m] * 10)- (RecMat_trial[i][m] * GWP_secondary[m] * 10))
    emis_avoid_trial.append(emis_avoid_trial_i)
    emis_avoid_trial_secondary.append(emis_avoid_trial_secondary_i)
    
    net_savings_trial.append(calculate_net_savings(emis_avoid_trial[i], emis_list_trial[i], GWP_residue_trial[i]))
    net_savings_trial_secondary.append(calculate_net_savings(emis_avoid_trial_secondary[i], emis_list_trial[i], GWP_residue_trial[i]))

## CYCLONE: CALCULATE RECOVERY EMISSIONS & AVOIDED EMISSIONS

# Inititalize list for 'extra' emissions from recovery for addition of cyclone
emis_list_cyclone = []

# Initialize list for avoided emissions from 1:1 virgin replacement based on 'extra' recovered material from addition of cyclone
emis_avoid_cyclone = []

# Initialize list for 'extra' net savings with 1:1 virgin replacement from addition of cyclone
net_savings_cyclone = []

# Initialize list for 'extra' avoided emissions from secondary virgin replacement (accounts for secondary processing and substitution ratios) from addition of cyclone
emis_avoid_cyclone_secondary = []

# Initialize list for 'extra' net savings with secondary virgin replacement from addition of cyclone
net_savings_cyclone_secondary = []

for i in range(len(electricity_cyclone)):
    emis_dict_cyclone, emis_list_cyclone_i = get_emissions(electricity_cyclone[i], 0, 0, baling_wire_cyclone[i], EF_factors)
    emis_list_cyclone.append(emis_list_cyclone_i)
    
    emis_avoid_cyclone_i = []
    emis_avoid_cyclone_secondary_i = []
    for m in range(len(recyclables)):
        emis_avoid_cyclone_i.append(RecMat_cyclone[i][m] * GWP[m] * 10)
        emis_avoid_cyclone_secondary_i.append((RecMat_cyclone[i][m]*GWP[m]*sub_ratio[m] * 10)-(RecMat_cyclone[i][m] * GWP_secondary[m] * sub_ratio[m] * 10)) 
    emis_avoid_cyclone.append(emis_avoid_cyclone_i)
    emis_avoid_cyclone_secondary.append(emis_avoid_cyclone_secondary_i)
    
    net_savings_cyclone.append(calculate_net_savings(emis_avoid_cyclone[i], emis_list_cyclone[i], GWP_residue_cyclone[i]))
    net_savings_cyclone_secondary.append(calculate_net_savings(emis_avoid_cyclone_secondary[i], emis_list_cyclone[i], GWP_residue_cyclone[i]))

for case in range(len(net_savings_trial)):
    print(f'Total Savings (base case, {(1+case)*5}% plastic): {net_savings_base[case]}')
    print(f'Total Savings (trial case, {(1+case)*5}% plastic): {net_savings_trial[case]}')
    print(f'Total Savings (base case, secondary, {(1+case)*5}% plastic): {net_savings_base_secondary[case]}')
    print(f'Total Savings (trial case, secondary, {(1+case)*5}% plastic): {net_savings_trial_secondary[case]}')
    print(f'Total Savings (cyclone case, {(1+case)*5}% plastic): {net_savings_cyclone[case]}')
    print(f'Total Savings (cyclone case, secondary, {(1+case)*5}% plastic): {net_savings_cyclone_secondary[case]}')
    
## TRASNFERRING DATA INTO DATAFRAMES

# percentage of plastic that falls through glass breaker screen
plastic_percentages = ['5%', '10%', '15%']

# Function that extracts GWP from recovery from the emissions lists and put them into a vector  
def get_GWP_recovery(emis_list):
    GWP_recovery = [emis_list[0][0], emis_list[1][0], emis_list[2][0]]
    return GWP_recovery

# Extracting GWP for each plastic % case
GWP_recovery_base = get_GWP_recovery(emis_list_base)
GWP_recovery_trial = get_GWP_recovery(emis_list_trial)
GWP_recovery_cyclone = get_GWP_recovery(emis_list_cyclone)


# Dataframe for emissions from recovery (recovery/landfilling data)
df_recovery = pd.DataFrame()
df_recovery['Plastic %'] = plastic_percentages
# sum GWP from recovery and residue disposal
df_recovery['Base'] = [sum(x) for x in zip(GWP_recovery_base, GWP_residue_base)]
df_recovery['Trial'] = [sum(x) for x in zip(GWP_recovery_trial, GWP_residue_trial)]
df_recovery['Cyclone'] = [sum(x) for x in zip(GWP_recovery_cyclone, GWP_residue_cyclone)]

print('Emissions from recovery:')
print(df_recovery)

# DataFrames for summed avoided emissions
df_avoided = pd.DataFrame()
df_avoided['Plastic %'] = ['5%', '10%', '15%']
df_avoided['Base'] = [sum(emis_avoid_base[0]), sum(emis_avoid_base[1]), sum(emis_avoid_base[2])]
df_avoided['Trial'] = [sum(emis_avoid_trial[0]), sum(emis_avoid_trial[1]), sum(emis_avoid_trial[2])]
df_avoided['Cyclone'] = [sum(emis_avoid_cyclone[0]), sum(emis_avoid_cyclone[1]), sum(emis_avoid_cyclone[2])]

print('Avoided Emissions (without secondary processing):')
print(df_avoided)

df_avoided_secondary = pd.DataFrame()
df_avoided_secondary['Plastic %'] = ['5%', '10%', '15%']
df_avoided_secondary['Base secondary'] = [sum(emis_avoid_base_secondary[0]), sum(emis_avoid_base_secondary[1]), sum(emis_avoid_base_secondary[2])]
df_avoided_secondary['Trial secondary'] = [sum(emis_avoid_trial_secondary[0]), sum(emis_avoid_trial_secondary[1]), sum(emis_avoid_trial_secondary[2])]
df_avoided_secondary['Cyclone secondary'] = [sum(emis_avoid_cyclone_secondary[0]), sum(emis_avoid_cyclone_secondary[1]), sum(emis_avoid_cyclone_secondary[2])]

print('Avoided Emissions (with secondary processing):')
print(df_avoided_secondary)

# Putting net emissions impact in data frame
df_net = pd.DataFrame()
df_net['Plastic %'] = ['5%', '10%', '15%']
df_net['Base'] = (-1 * df_avoided['Base']) + df_recovery['Base']
df_net['Trial'] = (-1 * df_avoided['Trial']) + df_recovery['Trial']
df_net['Base secondary'] = (-1 * df_avoided_secondary['Base secondary']) + df_recovery['Base']
df_net['Trial secondary'] = (-1 * df_avoided_secondary['Trial secondary']) + df_recovery['Trial']

print('Net Emissions:')
print(df_net)
