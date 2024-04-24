# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 11:56:09 2024

@author: iciber
"""
'''
-------------------------------------------------------------------------------
numpy                         1.26.4
jsonschema                    4.19.2
jsonschema-specifications     2023.7.1
pandas                        2.2.1
Python                        3.9
spyder                        5.5.1
-------------------------------------------------------------------------------

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

'''
# %% IMPORTS

# Inputs from database (json format)
import pandas as pd
import numpy as np
import os
from energy_consumption import EnergyConsumption


def GenerationSystem(data, demand_profile):
    '''
    This function processes data related to generation systems and calculates energy consumption based on the provided profiles.
    It reads information about generation system profiles, including heating, cooling, electricity, and DHW systems. It then iterates through each system and calculates the energy consumption.

    For each system:
    - It checks if the system is present.
    - If present, it defines the energy consumption type based on the system.
    - It creates a generation system profile dictionary with the system type and fuel yield values.
    - It calculates the energy consumption using the EnergyConsumption function.
    - If the consumption is not None, it assigns the calculated consumption to the respective variable; otherwise, it fills the variable with zeros.
    
    Finally, it returns dictionaries containing the generation system information and the calculated energy consumption for each building.

    Parameters
    ----------
    data : dict
        A dictionary containing information about generation system profiles, demand profiles, and building statistics.

    demand_profile : dict
        A dictionary containing information about demand profiles for heating, cooling, electricity, and DHW.

    Returns
    -------

    building_consumption_dict : dict
        A dictionary containing the calculated energy consumption values for each building.
    '''
    # Extract data from the provided dictionary
    building_statistics_profiles = data.get("building_statistics_profile", [])
    
    # Initialize dictionaries to store generation system information and consumption values
    
    building_consumption_dict = {}
    
    # Loop through each building's statistics profile
    for building_profile in building_statistics_profiles:
        # Extract generation system information for each building
        generation_system_id = building_profile["generation_system_profile_id"]
        generation_system_p = building_profile["generation_system_profile"]
        
        # Initialize lists to store generation system profiles and consumption values
        generation_system_profile_list = []
        heating_consumption = []
        electricity_consumption = []
        dhw_consumption = []
        cooling_consumption = []
        
        # Extract individual system profiles
        heating_system = generation_system_p.get("heating_system", {})
        electricity_system = generation_system_p.get("electricity_system", {})
        dhw_system = generation_system_p.get("dhw_system", {})
        cooling_system = generation_system_p.get("cooling_system", {})
        
        # Processing heating system
        if heating_system is not None:
            EC_type = "heating_demand"
            FY_1 = heating_system.get("fuel_yield1")
            FY_2 = heating_system.get("fuel_yield2")
            # Create a generation system profile dictionary
            generation_system_profile = {
                "heating_system": {
                    "system_type": EC_type,
                    "fuel_yield_1": FY_1,
                    "fuel_yield_2": FY_2,
                } 
            }
            generation_system_profile_list.append(generation_system_profile) 
            # Calculate heating consumption
            heating_consumption = EnergyConsumption(generation_system_profile=generation_system_profile, demand_profile=demand_profile)
            
            if heating_consumption is not None:
                heating_consumption = heating_consumption
            else:
                heating_consumption =[0] * 8760
                
        else:
            heating_consumption =[0] * 8760
            
        # Processing electricity system
        if electricity_system is not None:
            EC_type = "electricity_demand"
            FY_1 = electricity_system.get("fuel_yield1")
            FY_2 = electricity_system.get("fuel_yield2")
            # Create a generation system profile dictionary
            generation_system_profile = {
                "electricity_system": {
                    "system_type": EC_type,
                    "fuel_yield_1": FY_1,
                    "fuel_yield_2": FY_2,
                } 
            }
            generation_system_profile_list.append(generation_system_profile) 
            # Calculate electricity consumption
            electricity_consumption = EnergyConsumption(generation_system_profile=generation_system_profile, demand_profile=demand_profile)
    
            if electricity_consumption is not None:
                electricity_consumption = electricity_consumption
            else:
                electricity_consumption =[0] * 8760
                
        else:
            electricity_consumption =[0] * 8760       
            
        # Processing DHW system
        if dhw_system is not None:
            EC_type = "dhw_demand"
            FY_1 = dhw_system.get("fuel_yield1")
            FY_2 = dhw_system.get("fuel_yield2")
            # Create a generation system profile dictionary
            generation_system_profile = {
                "dhw_system": {
                    "system_type": EC_type,
                    "fuel_yield_1": FY_1,
                    "fuel_yield_2": FY_2,
                } 
            }
            generation_system_profile_list.append(generation_system_profile) 
            # Calculate DHW consumption
            dhw_consumption = EnergyConsumption(generation_system_profile=generation_system_profile, demand_profile=demand_profile)
            
            if dhw_consumption is not None:
                dhw_consumption = dhw_consumption
            else:
                dhw_consumption =[0] * 8760
                
        else:
            dhw_consumption =[0] * 8760 
            
        # Processing cooling system
        if cooling_system is not None:
            EC_type = "cooling_demand"
            FY_1 = cooling_system.get("fuel_yield1")
            FY_2 = cooling_system.get("fuel_yield2")
            # Create a generation system profile dictionary
            generation_system_profile = {
                "cooling_system": {
                    "system_type": EC_type,
                    "fuel_yield_1": FY_1,
                    "fuel_yield_2": FY_2,
                } 
            }
            generation_system_profile_list.append(generation_system_profile) 
            # Calculate cooling consumption
            cooling_consumption = EnergyConsumption(generation_system_profile=generation_system_profile, demand_profile=demand_profile)
    
            if cooling_consumption is not None:
                cooling_consumption = cooling_consumption
            else:
                cooling_consumption =[0] * 8760
                
        else:
            cooling_consumption =[0] * 8760 
        

        building_consumption_dict = {
            "elec_consumption": electricity_consumption,
            "heat_consumption": heating_consumption,
            "cool_consumption": cooling_consumption,
            "dhw_consumption": dhw_consumption,
        }
    
    return building_consumption_dict

def TotalPrimaryEnergy(data,building_consumption_dict):
    '''
    This function calculates the total primary energy consumption based on the provided building data and building consumption

    Parameters
    ----------
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    building_consumption_dict : dict
        A dictionary containing information about building consumption from a building.

    Returns
    -------
    total_primary_energy : float
        The total primary energy consumption.
    '''

    # Initialize the total primary energy variable
    total_primary_energy = 0
    # Get the building consumption data from the GenerationSystem function
    
    # Iterate through each building's statistics profile
    for building_data in data["building_statistics_profile"]:
        # Extract the generation system profile for the building
        generation_system_p = building_data.get("generation_system_profile", {})
    
        # Get the consumption data for each type of generation system
        heating_consumption = building_consumption_dict["heat_consumption"]
        electricity_consumption = building_consumption_dict["elec_consumption"]
        cooling_consumption = building_consumption_dict["cool_consumption"]
        dhw_consumption = building_consumption_dict["dhw_consumption"]
            
        # Process the heating system
        heating_system = generation_system_p.get("heating_system", {})
        if heating_system is not None:
            # Get the total primary energy factor for heating
            pef_tot = heating_system["energy_carrier_input_1"]["national_energy_carrier_production"][0]["pef_tot"]
            # Calculate the primary energy for heating
            primary_energy_heating = sum(heating_consumption) * pef_tot
            total_primary_energy += primary_energy_heating
        
        # Process the electricity system
        electricity_system = generation_system_p.get("electricity_system", {})
        if electricity_system is not None:
            # Get the total primary energy factor for electricity
            pef_tot = electricity_system["energy_carrier_input_1"]["national_energy_carrier_production"][0]["pef_tot"]
            # Calculate the primary energy for electricity
            primary_energy_elec = sum(electricity_consumption) * pef_tot
            total_primary_energy += primary_energy_elec
        
        # Process the DHW system
        dhw_system = generation_system_p.get("dhw_system", {})
        if dhw_system is not None:
            # Get the total primary energy factor for DHW
            pef_tot = dhw_system["energy_carrier_input_1"]["national_energy_carrier_production"][0]["pef_tot"]
            # Calculate the primary energy for DHW
            primary_energy_dhw = sum(dhw_consumption) * pef_tot
            total_primary_energy += primary_energy_dhw
        
        # Process the cooling system
        cooling_system = generation_system_p.get("cooling_system", {})
        if cooling_system is not None:
            # Get the total primary energy factor for cooling
            pef_tot = cooling_system["energy_carrier_input_1"]["national_energy_carrier_production"][0]["pef_tot"]
            # Calculate the primary energy for cooling
            primary_energy_cooling = sum(cooling_consumption) * pef_tot
            total_primary_energy += primary_energy_cooling
            
        total_primary_energy_MWh = total_primary_energy/1000
    return total_primary_energy, total_primary_energy_MWh

def KPI_peak_heat_demand(data,front_data,demand_profile):
    '''
    This function calculates the peak heat demand based on the provided building data.

    Parameters
    ----------
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.

    Returns
    -------
    max_sh : float
        Maximum space heating demand.
    max_sc : float
        Maximum space cooling demand.
    max_dhw : float
        Maximum domestic hot water demand.
    KPI_peak_heat_demand : float
        Maximum peak heat demand.
    '''

    Spaceheating = demand_profile["demand_profile"]["heating_demand"]
    Spacecooling = demand_profile["demand_profile"]["cooling_demand"]
    DHW = demand_profile["demand_profile"]["dhw_demand"]
    
    max_sh = np.amax(Spaceheating)
    max_sc = np.amax(Spacecooling)
    max_dhw = np.amax(DHW)
    
    KPI_peak_heat_demand = max(max_sh, max_sc, max_dhw)
    #transform it into MWh 
    return KPI_peak_heat_demand


def KPI_peak_electricity_demand(data, demand_profile):
    '''
    This function calculates the peak electricity demand based on the provided building data.

    Parameters
    ----------
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.

    Returns
    -------
    KPI_peak_elec_demand : float
        Maximum peak electricity demand.
    '''
    Electricity = demand_profile["demand_profile"]["electricity_demand"]
    KPI_peak_elec_demand = np.amax(Electricity)
    #transform it into MWh 
    return KPI_peak_elec_demand


def KPI_ctz_factors():
    '''
    This function defines the factors for calculating citizen KPIs.

    Returns
    -------
    citizen : dict
        A dictionary containing the factors for various KPI calculations.
    '''
    citizen_KPIs_factors = {
        # ENERGY SAVINGS
        "f_tv": 0.250,    #[kW]
        "f_streaming":0.077,    #[kWh]
        "f_pizza": 2,          # [kW]
        "f_battery": 68.7,     # [kWh/charge]
        "f_km": 354,           # [km/charge]
        "f_elcar": 0.196,      # [kWh/km]
        "f_wine": 540,         # [kWh/bottle of wine]
        # CO2 SAVINGS
        "f_trees": 25,         # [kg_CO2/year]
        "f_em_net": 0.036,     # [kg_CO2/hour]
        "f_ICV": 0.1163,       # [kg_CO2/km]
        # ECONOMIC SAVINGS     # TO DEFINE

    }

    return citizen_KPIs_factors  

def KPI_scenario_objective(front_data):
    '''
    This function calculates the scenario objective based on the front data and building data.

    Parameters
    ----------
    front_data : dict
        A dictionary containing information about the front data.

    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.

    Returns
    -------
    num_members : int
        The number of members in the scenario.
    '''
    num_members = front_data["num_building"]
    
    return num_members


def TV_h(citizen_KPIs_factors,total_primary_energy):
    '''
    Equivalent TV hours
    Description: Calculates the number of hours equivalent to the energy consumption, 
    representing the time spent watching TV.

    Parameters
    ----------
    citizen_KPIs_factors : dict
        A dictionary containing information about citizen factors.
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    total_primary_energy : dict
        A dictionary containing information about total_primary_energy 

    Returns
    -------
    TV_h : float
        Equivalent TV hours.
    '''
    TV_h = total_primary_energy / citizen_KPIs_factors["f_tv"]  # [h]
    return TV_h


def streaming_h(citizen_KPIs_factors,total_primary_energy):
    '''
    Equivalent streaming hours
    Description: Estimates the hours equivalent to the energy consumed, 
    reflecting the duration of streaming.

    Parameters
    ----------
    citizen : dict
        A dictionary containing information about citizen factors.
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    total_primary_energy : dict
        A dictionary containing information about total_primary_energy 

    Returns
    -------
    streaming_h : float
        Equivalent streaming hours
    '''
    
    streaming_h = total_primary_energy / citizen_KPIs_factors["f_streaming"]  # [h]
    return streaming_h


def Pizza_h(citizen_KPIs_factors,total_primary_energy):
    '''
    Pizza consumption comparison
    Description: Converts the energy consumption into hours of pizza consumption, 
    providing a relatable comparison.

    Parameters
    ----------
    citizen : dict
        A dictionary containing information about citizen factors.
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    total_primary_energy : dict
        A dictionary containing information about total_primary_energy 

    Returns
    -------
    Pizza_h : float
        Equivalent pizza consumption hours.
    '''
    
    Pizza_h = total_primary_energy / citizen_KPIs_factors["f_pizza"]  # [h]
    return Pizza_h


def Battery_charges(citizen_KPIs_factors,total_primary_energy):
    '''
    Battery usage estimation
    Description: Determines the number of times a battery could be charged 
    with the energy consumed.

    Parameters
    ----------
    citizen : dict
        A dictionary containing information about citizen factors.
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    total_primary_energy : dict
        A dictionary containing information about total_primary_energy 

    Returns
    -------
    Battery_charges : float
        Number of battery charges.
    '''
    Battery_charges = total_primary_energy / citizen_KPIs_factors["f_battery"]  # [charges]
    return Battery_charges


def ElCar_charges(citizen_KPIs_factors,total_primary_energy):
    '''
    Electric car charging estimation
    Description: Computes the number of times an electric car could be charged 
    with the energy consumed.

    Parameters
    ----------
    citizen : dict
        A dictionary containing information about citizen factors.
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    total_primary_energy : dict
        A dictionary containing information about total_primary_energy 

    Returns
    -------
    ElCar_charges : float
        Number of electric car charges.
    '''

    ElCar_charges = total_primary_energy / citizen_KPIs_factors["f_km"]  # [charges]
    return ElCar_charges


def Trees_number(citizen_KPIs_factors,total_primary_energy):
    '''
    Trees required for carbon offset
    Description: Calculates the number of trees needed to offset the carbon emissions 
    resulting from the energy consumption.

    Parameters
    ----------
    citizen : dict
        A dictionary containing information about citizen factors.
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    total_primary_energy : dict
        A dictionary containing information about total_primary_energy 
    Returns
    -------
    Trees_number : float
        Number of trees required for carbon offset.
    '''

    Trees_number = total_primary_energy / citizen_KPIs_factors["f_trees"]  # [trees/year]
    return Trees_number


def streaming_emissionhours(citizen_KPIs_factors,total_primary_energy):
    '''
    Streaming emissions impact
    Description: Assesses the environmental impact in terms of streaming usage 
    associated with the energy consumption.

    Parameters
    ----------
    citizen : dict
        A dictionary containing information about citizen factors.
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    total_primary_energy : dict
        A dictionary containing information about total_primary_energy 

    Returns
    -------
    Streaming_emissionhours : float
        Streaming emissions impact in hours.
    '''

    streaming_emissionhours = total_primary_energy / citizen_KPIs_factors["f_em_net"]  # [h]
    return streaming_emissionhours


def ICV_km(citizen_KPIs_factors,total_primary_energy):
    '''
    Carbon emissions per kilometer
    Description: Calculates the carbon emissions per kilometer traveled 
    as a result of the energy consumption.

    Parameters
    ----------
    citizen : dict
        A dictionary containing information about citizen factors.
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    total_primary_energy : dict
        A dictionary containing information about total_primary_energy 

    Returns
    -------
    ICV_km : float
        Carbon emissions per kilometer.
    '''

    ICV_km = total_primary_energy / citizen_KPIs_factors["f_ICV"]  # [km]
    return ICV_km

def Wine_bottles(citizen_KPIs_factors,total_primary_energy):
    '''
    Consume related to Wine bottles production
    Description: Calculates the number of wine bottles producted based on energy consumption.

    Parameters
    ----------
    citizen : dict
        A dictionary containing information about citizen factors.
    data : dict
        A dictionary containing information about building statistics profiles, including generation system profiles.
    total_primary_energy : dict
        A dictionary containing information about total_primary_energy 

    Returns
    -------
    Wine_bottles : float
        Number of wine bottles generated.
    '''

    Wine_bottles = total_primary_energy / citizen_KPIs_factors["f_wine"]  # [bottles]
    return Wine_bottles

def save_to_csv(building_consumption_dict, demand_profile, total_primary_energy_MWh, KPI_peak_heat_demand, KPI_peak_elec_demand, num_members,
                TV_h, streaming_h, Pizza_h, Battery_charges, ElCar_charges, Trees_number, streaming_emissionhours, ICV_km, Wine_bottles):
    '''
    This function saves building consumption and KPI calculation data to a CSV file.

    Parameters
    ----------
    building_consumption_dict : dict
        A dictionary containing building consumption data.
    demand_profile : dict
        A dictionary containing information about demand profiles for heating, cooling, electricity, and DHW.
    total_primary_energy_MWh : float
        Total primary energy consumption in MWh.
    KPI_peak_heat_demand_MWh : float
        Peak heat demand in MWh.
    KPI_peak_elec_demand_MWh : float
        Peak electricity demand in MWh.
    num_members : int
        Number of members in the household.
    TV_h : float
        Equivalent TV hours in kW.
    streaming_h : float
        Equivalent streaming hours in kW.
    Pizza_h : float
        Pizza consumption comparison in kW.
    Battery_charges : float
        Battery usage estimation in kWh per charge.
    ElCar_charges : float
        Electric car charging estimation in kWh per charge.
    Trees_number : float
        Number of trees required for carbon offset in kg CO2 per year.
    streaming_emissionhours : float
        streaming emissions impact in kg CO2 per hour.
    ICV_km : float
        Carbon emissions per kilometer in kg CO2 per km.
    Wine_bottles : float
        Wine bottles production in kWh per bottle.

    Returns
    -------
    ctz_kpi_df : pandas.DataFrame
        DataFrame containing citizen KPIs results.
    building_consumption_df : pandas.DataFrame
        DataFrame containing energy consumption per system type.
    '''

    # Define CSV file names
    csv_filename_consumption = "building_id_1.csv"
    csv_filename_kpi = "ctz_KPIs.csv"
    
    # Create the 'outputs' folder if it doesn't exist
    output_folder = os.path.join(os.getcwd(), 'outputs')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Full path of the CSV file for building consumption
    csv_filepath_1 = os.path.join(output_folder, csv_filename_consumption)

    # Create DataFrame with columns for building consumption
    building_consumption_df = pd.DataFrame(columns=["elec_consumption", "heat_consumption", "cool_consumption", "dhw_consumption"])

    # Add building consumption data to the DataFrame
    for i in range(8760):
        building_consumption_df.loc[i] = {
            "elec_consumption": building_consumption_dict["elec_consumption"][i],
            "heat_consumption": building_consumption_dict["heat_consumption"][i],
            "cool_consumption": building_consumption_dict["cool_consumption"][i],
            "dhw_consumption": building_consumption_dict["dhw_consumption"][i]
        }

    # Write DataFrame to the CSV file
    building_consumption_df.to_csv(csv_filepath_1, index=False)
    Energy_use_MWh = (sum(demand_profile["demand_profile"]["electricity_demand"])+sum(demand_profile["demand_profile"]["heating_demand"])
                      +sum(demand_profile["demand_profile"]["cooling_demand"])+sum(demand_profile["demand_profile"]["dhw_demand"]))/1000
    # Create DataFrame for citizen KPIs
    ctz_kpi_df = pd.DataFrame({
        "KPI": [
            "Energy_use_[MWh]",            
            "KPI_peak_heat_demand_[kWh]",
            "KPI_peak_elec_demand_[kWh]",
            "total_primary_energy_[MWh]",
            "num_members",
            "EquivalentTVHours_[kW]",
            "EquivalentstreamingHours_[kW]",
            "PizzaConsumptionComparison_[kW]", 
            "BatteryUsageEstimation_[kWh/charge]", 
            "ElectricCarChargingEstimation_[kWh/charge]",
            "WineBottlesProduction_[kWh/bottle]",
            "TreesRequiredForCarbonOffset_[kg_CO2/year]",
            "streamingEmissionsImpact_[kg_CO2/hour]", 
            "CarbonEmissionsPerKilometer_[kg_CO2/km]"
            
        ],
        "Results": [
            Energy_use_MWh, KPI_peak_heat_demand, KPI_peak_elec_demand,total_primary_energy_MWh,num_members, TV_h, streaming_h, Pizza_h, Battery_charges, ElCar_charges, Wine_bottles, Trees_number,
            streaming_emissionhours, ICV_km
        ]
    })
    
    # Full path of the CSV file for citizen KPIs
    csv_filepath_2 = os.path.join(output_folder, csv_filename_kpi)
    
    # Write DataFrame of KPIs to the CSV file (without header if the file already exists)
    ctz_kpi_df.to_csv(csv_filepath_2, index=False)
    
    return ctz_kpi_df, building_consumption_df

