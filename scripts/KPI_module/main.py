# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:17:08 2024
    
Created on October 2023

@author: Iciar Bernal
License: GNU GPLv3
The GNU General Public License is a free, copyleft license for software and other kinds of works.
https://www.gnu.org/licenses/gpl-3.0.html
You may copy, distribute and modify the software as long as you track changes/dates in source files.
 Any modifications to or software including (via compiler) GPL-licensed code must also be made 
 available under the GPL along with build & install instructions. 
 This means, you must:
     - Include original
     - State Changes
     - Disclose source
     - Include the same license -- to make sure it remains free software for all its users.
     - Include copyright
     - Include install instructions 
     
You cannot: sublicense or hold liable.

Copyright @CARTIF 2024
@author: iciber
"""

# ***********************************************************************************************

# This part of the code is part of the KPI module

# ***********************************************************************************************
import pandas as pd
import numpy as np
import os
import KPI_module
import json

# %% INPUTS FROM INTERFACE


def inputs_from_user():
    '''
    This function reads the JSON files containing inputs from the user and from the database.

    Returns
    -------
    front_data : dict
        A dictionary containing front-end inputs.
    data : dict
        A dictionary containing inputs from the database.
    '''
    # Path to the JSON file containing database inputs
    database_json_path = os.path.join(os.getcwd(),'data', 'database_simple_path_v3.txt')
    # Read the JSON file and load its contents as a dictionary
    with open(database_json_path, "r") as database_file:
        #import database tree
        database_structure = json.load(database_file)
    
    # Path to the JSON file containing front-end inputs
    front_json_path = os.path.join(os.getcwd(),'data', 'inputs_simple_path.json')
    # Read the JSON file and load its contents as a dictionary
    with open(front_json_path, "r") as front_file:
        #import user inputs to user interface
        user_data = json.load(front_file)        
        
    return user_data, database_structure 


def inner_KPI_module_transform_data_model (context_Baseline, recommendedScenarios):
    new_context=print("change data model of the database")
    
    return new_context
	
def inner_simulationAndOptimisation():
	multimeseries=print("runARTELYSCrystal")
	return multimeseries


# %%TEST EXAMPLE


front_data, data = inputs_from_user()
demand_profile_json_path = os.path.join(os.getcwd(),'data', 'demand_profile.json')
with open(demand_profile_json_path, "r") as front_file:
#import demandprofile
    demand_profile = json.load(front_file) 

building_consumption_dict = KPI_module.GenerationSystem(data=data, demand_profile=demand_profile)


def inner_perform_KPIs():
    #Calculate primary energy consumption
    total_primary_energy, total_primary_energy_MWh = KPI_module.TotalPrimaryEnergy(data=data, building_consumption_dict=building_consumption_dict)
    #calculate peak heat demand
    KPI_peak_heat_demand = KPI_module.KPI_peak_heat_demand(data=data, front_data=front_data, demand_profile=demand_profile)
    #calculate peak cooling demand
    KPI_peak_elec_demand = KPI_module.KPI_peak_electricity_demand(data=data, demand_profile=demand_profile)
    #Extract dictionary of Citizen_KPIs_factors
    citizen_KPIs_factors=KPI_module.KPI_ctz_factors()
    #KPI number of members of the community
    num_members = KPI_module.KPI_scenario_objective(front_data=front_data)
    #KPI Equivalent TV hours
    TV_h = KPI_module.TV_h(citizen_KPIs_factors=citizen_KPIs_factors, total_primary_energy=total_primary_energy)
    #KPI Equivalent streaming hours
    streaming_h = KPI_module.streaming_h(citizen_KPIs_factors=citizen_KPIs_factors, total_primary_energy=total_primary_energy)
    #KPI equivalent pizza items
    Pizza_h = KPI_module.Pizza_h(citizen_KPIs_factors=citizen_KPIs_factors, total_primary_energy=total_primary_energy)
    #Equivalent battery usage estimation
    Battery_charges = KPI_module.Battery_charges(citizen_KPIs_factors=citizen_KPIs_factors, total_primary_energy=total_primary_energy)
    #Equivalent electric car charging times
    ElCar_charges = KPI_module.ElCar_charges(citizen_KPIs_factors=citizen_KPIs_factors, total_primary_energy=total_primary_energy)
    #Equivalent trees
    Trees_number = KPI_module.Trees_number(citizen_KPIs_factors=citizen_KPIs_factors, total_primary_energy=total_primary_energy)
    # Equivalent Streaming impact in emissions
    streaming_emissionhours = KPI_module.streaming_emissionhours(citizen_KPIs_factors=citizen_KPIs_factors, total_primary_energy=total_primary_energy)
    #
    ICV_km = KPI_module.ICV_km(citizen_KPIs_factors=citizen_KPIs_factors, total_primary_energy=total_primary_energy)
    #Equivalent wine bottels produced
    Wine_bottles=KPI_module.Wine_bottles(citizen_KPIs_factors=citizen_KPIs_factors, total_primary_energy=total_primary_energy)
    #All citizen KPIs outputs
    ctz_kpi_df, building_consumption_df = KPI_module.save_to_csv(
        demand_profile=demand_profile, 
        building_consumption_dict=building_consumption_dict,
        total_primary_energy_MWh=total_primary_energy_MWh,
        KPI_peak_heat_demand=KPI_peak_heat_demand,
        KPI_peak_elec_demand=KPI_peak_elec_demand,
        num_members=num_members,
        TV_h=TV_h,
        streaming_h=streaming_h,
        Pizza_h=Pizza_h,
        Battery_charges=Battery_charges,
        ElCar_charges=ElCar_charges,
        Trees_number=Trees_number,
        streaming_emissionhours=streaming_emissionhours,
        ICV_km=ICV_km,
        Wine_bottles=Wine_bottles
    )
    return ctz_kpi_df


inner_perform_KPIs()