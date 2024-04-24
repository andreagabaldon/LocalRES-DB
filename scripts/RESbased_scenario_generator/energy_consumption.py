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
# %% ENERGY CONSUMPTION

def EnergyConsumption(generation_system_profile, demand_profile):
    '''
    This function calculates the energy consumption for different systems based on the provided generation system profiles and demand profiles.
    It iterates through each system in the generation system profile and checks if the corresponding demand exists in the demand profile. If the demand is present, it calculates the energy consumption using the fuel yield values of the respective systems.

    For heating demand:
    - It checks if heating demand is present in the generation system profile.
    - If present, it calculates the heating consumption based on the fuel yield for heating.
    - Then, it extends the consumption list with the calculated heating consumption.

    For DHW demand:
    - It checks if DHW demand is present in the generation system profile.
    - If present, it calculates the DHW consumption based on the fuel yield for DHW.
    - Then, it extends the consumption list with the calculated DHW consumption.

    For electricity demand:
    - It checks if electricity demand is present in the generation system profile.
    - If present, it calculates the electricity consumption based on the fuel yield for electricity.
    - Then, it extends the consumption list with the calculated electricity consumption.

    For cooling demand:
    - It checks if cooling demand is present in the generation system profile.
    - If present, it calculates the cooling consumption based on the fuel yield for cooling.
    - Then, it extends the consumption list with the calculated cooling consumption.

    Finally, it returns the list of consumption values for each generation system.

    Parameters
    ----------
    generation_system_profile : dict
        A dictionary containing information about the generation systems installed in the buildings, including heating, cooling, electricity, and DHW systems.

    demand_profile : dict
        A dictionary containing information about the demand profiles for heating, cooling, electricity, and DHW.

    generation_systems : dict
        A dictionary containing the specific parameters of each generation system.

    Returns
    -------
    consumption_per_generation_system : list
        A list containing the calculated energy consumption values for each generation system.


    '''
    # Initialize an empty list to store the calculated consumption values
    consumption_per_generation_system = []
    
    # Check if heating demand is present
    try:
        if 'heating_system' in generation_system_profile and 'heating_demand' in demand_profile['demand_profile']:
            # If heating demand is present, proceed with calculations
            # Create a list of fuel yield values for heating
            fuel_yield_1_heating_list = [generation_system_profile["heating_system"]["fuel_yield_1"]] * 8760
            # Calculate heating consumption
            consumption_per_generation_system = [demand / fuel_yield for demand, fuel_yield in zip(demand_profile['demand_profile']['heating_demand'], fuel_yield_1_heating_list)]
            # Extend consumption list with heating consumption
            # consumption_per_generation_system.extend(heating_consumption_list)
    except KeyError:
        pass
    
    # Check if domestic hot water (DHW) demand is present
    try:
        if 'dhw_system' in generation_system_profile and 'dhw_demand' in demand_profile['demand_profile']:
            # If DHW demand is present, proceed with calculations
            # Create a list of fuel yield values for DHW
            fuel_yield_1_dhw_list = [generation_system_profile["dhw_system"]["fuel_yield_1"]] * 8760
            # Calculate DHW consumption
            consumption_per_generation_system = [demand / fuel_yield for demand, fuel_yield in zip(demand_profile['demand_profile']['dhw_demand'], fuel_yield_1_dhw_list)]
            # Extend consumption list with DHW consumption
            # consumption_per_generation_system.extend(dhw_consumption_list)
    except KeyError:
        pass
    
    # Check if electricity demand is present
    try:
        if 'electricity_system' in generation_system_profile and 'electricity_demand' in demand_profile['demand_profile']:
            # If electricity demand is present, proceed with calculations
            # Create a list of fuel yield values for electricity
            fuel_yield_1_electricity_list = [generation_system_profile["electricity_system"]["fuel_yield_1"]] * 8760
            # Calculate electricity consumption
            consumption_per_generation_system = [demand / fuel_yield for demand, fuel_yield in zip(demand_profile['demand_profile']['electricity_demand'], fuel_yield_1_electricity_list)]
            # Extend consumption list with electricity consumption
            # consumption_per_generation_system.extend(electricity_consumption_list)
    except KeyError:
        pass
    
    # Check if cooling demand is present
    try:
        if 'cooling_system' in generation_system_profile and 'cooling_demand' in demand_profile['demand_profile']:
            # If cooling demand is present, proceed with calculations
            # Create a list of fuel yield values for cooling
            fuel_yield_1_cooling_list = [generation_system_profile["cooling_system"]["fuel_yield_1"]] * 8760
            # Calculate cooling consumption
            consumption_per_generation_system = [demand / fuel_yield for demand, fuel_yield in zip(demand_profile['demand_profile']['cooling_demand'], fuel_yield_1_cooling_list)]
            # Extend consumption list with cooling consumption
            # consumption_per_generation_system.extend(cooling_consumption_list)
    except KeyError:
        pass

    return consumption_per_generation_system
