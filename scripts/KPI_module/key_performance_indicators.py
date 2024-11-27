import os
import json
from scripts.RESbased_scenario_generator.classes_database import FinalEnergy, BuildingKPIs
import pandas as pd
from scripts.KPI_module.KPI_module import (kpi_ctz_factors,tv_h, streaming_h, pizza_h, battery_charges, el_car_charges,trees_number,
                        streaming_emission_hours,icv_km,wine_bottles)

def handle_demand_profile(building_asset_context,generation_system_profile,consumption_profile):
    consumption_profile_length=len(consumption_profile['elec_consumption'])
    # Handle demand_profile: If it doesn't exist, calculate using generation system profiles
    building_id=building_asset_context.get('id')
    demand_profile = building_asset_context.get('building', {}).get('demandprofile')
    if demand_profile is None and generation_system_profile is not None:
        # Retrieve fuel yield values from the generation system profiles
        if generation_system_profile.get('heating_system', {}) is not None:
            fuel_yield1_heating = generation_system_profile.get('heating_system', {}).get('fuel_yield1', 1)
        else:
            fuel_yield1_heating = 0

        if generation_system_profile.get('cooling_system', {}) is not None:
            fuel_yield1_cooling = generation_system_profile.get('cooling_system', {}).get('fuel_yield1', 1)
        else:
            fuel_yield1_cooling = 0
            consumption_profile['cool_consumption']=[0]*consumption_profile_length
        if generation_system_profile.get('dhw_system', {}) is not None:
            fuel_yield1_dhw = generation_system_profile.get('dhw_system', {}).get('fuel_yield1', 1)
        else:
            fuel_yield1_dhw = 0
            consumption_profile['dhw_consumption']=[0]*consumption_profile_length

        # Calculate demand profile using the consumption profile and fuel yields
        demand_profile = {
            "electricity_demand": consumption_profile["elec_consumption"],
            "heating_demand": [x * fuel_yield1_heating for x in
                               consumption_profile.get("heat_consumption", [])],
            "cooling_demand": [x * fuel_yield1_cooling for x in
                               consumption_profile.get("cool_consumption", [])],
            "dhw_demand": [x * fuel_yield1_dhw for x in consumption_profile.get("dhw_consumption", [])]
        }
        return demand_profile

    elif demand_profile is None:
        return ValueError(
            f"Demand profile could not be calculated because generation system profile is missing for building ID: {building_id}")

def calculate_self_consumption(total_electricity_use, total_PV):
    return [
        min(total_electricity_use[i], total_PV[i])
        for i in range(len(total_electricity_use))
    ]


def calculate_rate_of_self_consumption(self_consumption, total_PV):
    return [
        (self_consumption[i] / total_PV[i]) * 100 if total_PV[i] > 0 else 0
        for i in range(len(self_consumption))
    ]


def calculate_grid_consumption(total_electricity_use, self_consumption):
    return [
        total_electricity_use[i] - self_consumption[i]
        for i in range(len(total_electricity_use))
    ]


def calculate_self_sufficiency(self_consumption, total_electricity_use):
    return [
        (self_consumption[i] / total_electricity_use[i]) * 100 if total_electricity_use[i] > 0 else 0
        for i in range(len(self_consumption))
    ]


def add_electricity_consumption(total_electricity_use, consumption):
    for i in range(len(total_electricity_use)):
        if consumption[i] is None:
            consumption[i] = 0  # Handle None values in consumption
        total_electricity_use[i] += consumption[i]
    return total_electricity_use

def check_system_type_to_get_consumption(system_name,consumption_profile):
    print(type(consumption_profile))
    print(consumption_profile.keys())
    system_type=None
    if system_name == "dhw_system_id":
        consumption = consumption_profile["dhw_consumption"].copy()
        system_type='dhw_system'
    elif system_name == 'heating_system_id':
        consumption = consumption_profile["heat_consumption"].copy()
        system_type='heating_system'
    elif system_name == 'cooling_system_id':
        consumption = consumption_profile["cool_consumption"].copy()
        system_type='cooling_system'
    else:
        consumption=[0]*8760
        system_type='electricity_system'
    return consumption, system_type


def instantiate_final_energy_with_json():
    parent_directory = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(parent_directory,
                                  'catalogues', 'energy_carrier.json')
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    total_final_energy = {} #diccionario de instancias de la clase Final Energy para cada energy carrier
    for entry in json_data:
        if entry.get("final"):
            id = entry['id']
            total_final_energy[id] = FinalEnergy(id)
            total_final_energy[id].name = entry['name']
            total_final_energy[id].final = entry['final']

    return total_final_energy



def load_energy_system_catalogue():
    parent_directory = os.path.dirname(os.path.abspath(__file__))
    input_files_path = os.path.join(parent_directory,'catalogues',
                                    'generation_systems_catalogue.json')
    with open(input_files_path, 'r') as file:
        energy_systems_catalogue = json.load(file)
    return energy_systems_catalogue


def filter_energy_systems_catalogue(energy_systems_catalogue, new_generation_system_id):
    # Loop through each system in the 'systems' list
    for system in energy_systems_catalogue:
        # Check if the 'id' in the system matches the new_generation_system_id
        if system['id'] == new_generation_system_id:
            return system  # Return the matching system dictionary

    return None  # Return None if no matching system is found

def calculate_building_indicators(consumption_profile, generation_system_profile, building_energy_asset,timestep_count):
    """

    Parameters
    ----------
    consumption_profile is the dictionary of consumption, typically:
        "building_consumption":{
            "id": int,
            "heat_consumption":[],
            "dhw_consumption":[],
            "elec_consumption":[],
            "cool_consumption":[]
            }
    generation_system_profile is the dictionary of the energy systems
    building_energy_asset is a list of several assets

    Returns
    -------

    """
    #initilize:
    rate_of_self_consumption = []
    grid_consumption = []
    self_sufficiency = []
    total_electricity_use = []
    list_of_hps = [1, 2, 3, 4, 5, 6, 7, 8, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 41, 61, 62, 63, 64, 65, 66,
                   67, 68, 73]
    #dhn 145, 147, 153, 155 is out of the list as el. is consumed somewhere else
    cooling_hps_list = [1, 2, 3, 4, 5, 6, 7, 8]
    heating_hps_list = [61, 62, 63, 64, 65, 66, 67, 68, 73]
    dhw_hps_list = [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 41]
    chp_list = [88, 89, 90, 91]
    electric_asset_list = [80, 81, 82, 83, 84, 85, 86, 87]
    solar_thermal = [37, 38, 39, 40, 69, 70, 71, 72]
    #any other id is a boiler?????
    total_fuels_use={}
    cooling_asset = False
    heating_asset = False
    dhw_asset = False
    electricity_asset = False
    total_final_energy=instantiate_final_energy_with_json()
    energy_systems_catalogue=load_energy_system_catalogue()
    consumption=[]
    print(consumption_profile)
    if building_energy_asset is not None:
        print(consumption_profile.keys())
        # Initialize total_electricity_use with the base consumption profile
        total_electricity_use = consumption_profile.get('elec_consumption', [])
        for asset in building_energy_asset:
            if asset['generation_system_id'] in list_of_hps:
                # Perform element-wise summation for time_series_input1
                time_series_input1_values =asset["availability_ts"]["value_input1"].copy()
                total_electricity_use = [
                            total_electricity_use[i] + time_series_input1_values[i]
                            for i in range(len(total_electricity_use))
                        ]
                if asset['generation_system_id'] in cooling_hps_list:
                    cooling_asset = True
                if asset['generation_system_id'] in dhw_hps_list:
                    dhw_asset = True
                if asset['generation_system_id'] in heating_hps_list:
                    heating_asset = True
            #falta ..

        for system_name, system_id in generation_system_profile.items():
            # Check if the value is an integer (system ID)
            if not isinstance(system_id, int):
                continue  # Skip if the value is not an integer
            #System_id is an integer, you can safely check it
            #Get consumption
            consumption, system_type=check_system_type_to_get_consumption(system_name, consumption_profile)
            if system_name == "dhw_system_id" and system_id in dhw_hps_list and dhw_asset == False:
                total_electricity_use = add_electricity_consumption(total_electricity_use, consumption)
            elif system_name =='heating_system_id' and system_id in heating_hps_list and heating_asset == False:
                total_electricity_use = add_electricity_consumption(total_electricity_use, consumption)
            elif system_name =='cooling_system_id' and system_id in cooling_hps_list and cooling_asset == False:
                #If cooling_system_id is in list_of_new_hps and is not already found in asset['generation_system_id],
                # the program will proceed to sum the corresponding cool_consumption values with total_electricity_use for each hour.
                total_electricity_use = add_electricity_consumption(total_electricity_use, consumption)
            elif system_name == "dhw_system_id" and dhw_asset == False and generation_system_profile[system_type] is not None:
                fuels_id=generation_system_profile[system_type]['energy_carrier_input_1_id']
                total_final_energy[fuels_id].add_new_consumption(consumption)
            elif system_name == "heating_system_id" and heating_asset == False and generation_system_profile[system_type] is not None:
                fuels_id=generation_system_profile[system_type]['energy_carrier_input_1_id']
                total_final_energy[fuels_id].add_new_consumption(consumption)
            elif system_name == "cooling_system_id" and cooling_asset == False and generation_system_profile[system_type] is not None:
                fuels_id=generation_system_profile[system_type]['energy_carrier_input_1_id']
                total_final_energy[fuels_id].add_new_consumption(consumption)

        for asset in building_energy_asset:
            if asset['generation_system_id'] in electric_asset_list:
                # PV system, scale output by pmax_scalar
                # Perform element-wise summation for time_series_input1
                time_series_input1_values =asset["availability_ts"]["value_input1"].copy()
                total_PV = [x * asset['pmax_scalar'] for x in time_series_input1_values]
                electricity_asset = True
                # Calculate self-consumption
                self_consumption = calculate_self_consumption(total_electricity_use, total_PV)

                # Calculate rate of self-consumption
                rate_of_self_consumption = calculate_rate_of_self_consumption(self_consumption, total_PV)

                # Calculate grid consumption
                grid_consumption = calculate_grid_consumption(total_electricity_use, self_consumption)

                #Calculate self-sufficiency
                self_sufficiency = calculate_self_sufficiency(self_consumption, total_electricity_use)
            if asset['generation_system_id'] not in list_of_hps and asset[
                'generation_system_id'] not in electric_asset_list:
                    time_series_input1_values = asset["availability_ts"]["value_input1"].copy()
                    total_input1 = [x * asset['pmax_scalar'] for x in time_series_input1_values]
                    system = filter_energy_systems_catalogue(energy_systems_catalogue, asset['generation_system_id'])
                    fuels_id=int(system['energy_carrier_input_1_id'])
                    total_final_energy[fuels_id].add_new_consumption(total_input1)

        if electricity_asset == False:
            # If no electricity asset, set grid_consumption equal to total_electricity_use
            grid_consumption = total_electricity_use
            # Set rate_of_self_consumption and self_sufficiency to lists of 8760 zeros
            self_consumption = [0] * timestep_count
            rate_of_self_consumption = [0] * timestep_count
            self_sufficiency = [0] * timestep_count
            total_PV =[0] * timestep_count
    else:
        #there is no asset in this building
        # Initialize total_electricity_use with the base consumption profile
        total_electricity_use = consumption_profile['elec_consumption'].copy()
        for system_name, system_id in generation_system_profile.items():
            # Check if the value is an integer (system ID)
            if not isinstance(system_id, int):
                continue  # Skip if the value is not an integer
            # Get consumption
            consumption, system_type = check_system_type_to_get_consumption(system_name, consumption_profile)
                # Now, system_id is an integer, and you can safely check it
            if system_name == "dhw_system_id" and system_id in dhw_hps_list:
                total_electricity_use = add_electricity_consumption(total_electricity_use, consumption)
            elif system_name == "heating_system_id" and system_id in heating_hps_list:
                total_electricity_use = add_electricity_consumption(total_electricity_use, consumption)
            elif system_name == "cooling_system_id" and system_id in cooling_hps_list:
                total_electricity_use = add_electricity_consumption(total_electricity_use, consumption)
            elif system_name == "electricity_system_id" and system_id == 79:
                # This is the grid
                # grid_consumption equal to total_electricity_use
                grid_consumption = total_electricity_use
                # Set rate_of_self_consumption and self_sufficiency to lists of 8760 zeros
                self_consumption = [0] * timestep_count
                rate_of_self_consumption = [0] * timestep_count
                self_sufficiency = [0] * timestep_count
                total_PV =[0] * timestep_count
            #consumption_profile
            else:
                #this means is not a heat pump nor electricity grid but other type of system, therefore:
                if generation_system_profile[system_type] is not None:
                    fuels_id=generation_system_profile[system_type]['energy_carrier_input_1_id']
                    total_final_energy[fuels_id].add_new_consumption(consumption)

    total_final_energy[12].add_new_consumption(grid_consumption)
    KPIs = {}  # Dictionary to store the BuildingKPIs objects

    # Loop through the generation_system_profile
    for system_name, system in generation_system_profile.items():
        if system_name.endswith(
                '_system') and system is not None:  # Check if system ends with '_system' and is not None
            if 'energy_carrier_input_1' in system and system['energy_carrier_input_1'].get('final') == True:
                # Get the ID and KPI data
                energy_carrier_id = system['energy_carrier_input_1']['id']
                kpi_data = system['energy_carrier_input_1']['national_energy_carrier_production'][
                    0]
                if kpi_data is not None:
                    KPIs[energy_carrier_id] = BuildingKPIs(total_final_energy[energy_carrier_id], kpi_data)


    return (total_PV,rate_of_self_consumption, self_sufficiency, total_electricity_use, self_consumption,
            total_final_energy, KPIs)

def aggregate_demand_profiles(demand_profile):
    # Initialize a dictionary to store the aggregated demand
    total_demand = {}

    # Loop over each building's demand profile
    for building in demand_profile:
        # Get the specific demand profile dictionary for each building
        profile = building.get('demand_profile', {})

        # Loop through each demand type in the building's demand profile
        for demand_type, demand_values in profile.items():
            # If the demand type is already in total_demand, sum it element-wise
            if demand_type in total_demand:
                total_demand[demand_type] = [
                    total_demand[demand_type][i] + demand_values[i]
                    for i in range(len(demand_values))
                ]
            else:
                # If it's the first occurrence, initialize it in total_demand
                total_demand[demand_type] = demand_values

    return total_demand


def community_KPIs(citizen_KPIs,total_demand):
    # Initialize an empty dictionary to hold the sum of each KPI
    aggregate_KPIs = {}

    # Loop through each building's KPI data in citizen_KPIs
    for building_id, kpis in citizen_KPIs.items():
        # Loop through each KPI entry for the building
        for kpi in kpis:
            kpi_name = kpi["name"]
            kpi_value = kpi["value"]
            # Check if the KPI value is a number (int or float)
            if isinstance(kpi_value, (int, float)):
                # If the KPI name already exists in the aggregate dictionary, add to its value
                if kpi_name in aggregate_KPIs:
                    aggregate_KPIs[kpi_name]["value"] += kpi_value
                else:
                    # Initialize the entry in the aggregate dictionary with the current value and unit
                    aggregate_KPIs[kpi_name] = {"value": kpi_value, "unit": kpi["unit"]}

            # Check if the KPI value is a list (time series data)
            elif isinstance(kpi_value, list):
                # Determine the length of the time series if not provided
                timestep_count = len(kpi_value)

                # If the KPI name already exists, add each timestep's value element-wise
                if kpi_name in aggregate_KPIs:
                    aggregate_KPIs[kpi_name]["value"] = [
                        aggregate_KPIs[kpi_name]["value"][i] + kpi_value[i]
                        for i in range(timestep_count)
                    ]
                else:
                    # Initialize the entry in the aggregate dictionary with the list and unit
                    aggregate_KPIs[kpi_name] = {"value": kpi_value, "unit": kpi["unit"]}

    aggregate_KPIs['KPI_peak_heat_demand_[kWh]']={"value": max(total_demand['heating_demand']),"unit": 'kWh'}
    aggregate_KPIs['KPI_peak_dhw_demand_[kWh]']={"value":max(total_demand['dhw_demand']),"unit": 'kWh'}
    aggregate_KPIs['KPI_peak_cooling_demand_[kWh]']={"value": max(total_demand['cooling_demand']),"unit": 'kWh'}
    aggregate_KPIs['KPI_peak_elec_demand_[kWh]']={"value": max(total_demand['electricity_demand']),"unit": 'kWh'}
    aggregate_KPIs['KPI_peak_electricity_consumption_[kWh]']={"value": max(aggregate_KPIs['final_energy_electricity_grid']['value']),"unit": 'kWh'}
    # `aggregate_KPIs` now contains the summed values for each KPI across all buildings
    return aggregate_KPIs


def get_totals_per_building (KPIs,timestep_count,final_energy):
    # Initialize totals for the current building
    total_primary_energy= [0] * timestep_count
    total_primary_energy_renewable = [0] * timestep_count
    total_primary_energy_non_renewable = [0] * timestep_count
    total_non_h_costs = [0] * timestep_count
    total_h_costs = [0] * timestep_count
    total_co2= [0] * timestep_count
    for id_carrier, energy_instance in KPIs.items():
        if energy_instance is not None:
            # Use dot notation to access the energy instance attributes
            total_primary_energy = [
                total_primary_energy[i] + energy_instance.PEF_total[i]
                for i in range(timestep_count)
            ]

            total_primary_energy_renewable = [
                total_primary_energy_renewable[i] + energy_instance.PEF_ren[i]
                for i in range(timestep_count)
            ]

            total_primary_energy_non_renewable = [
                total_primary_energy_non_renewable[i] + energy_instance.PEF_nren[i]
                for i in range(timestep_count)
            ]

            total_non_h_costs = [
                total_non_h_costs[i] + energy_instance.non_h_costs[i]
                for i in range(timestep_count)
            ]

            total_h_costs= [
                total_h_costs[i] + energy_instance.household_costs[i]
                for i in range(timestep_count)
            ]

            total_co2 = [
                total_co2[i] + energy_instance.co2[i]
                for i in range(timestep_count)
            ]
    total_primary_energy_kWh = total_primary_energy  # it is already in kWh unless we decide otherwise
    total_co2_kg = [x / 1000 for x in total_co2]
    # Extract dictionary of citizen_kpis_factors
    citizen_kpis_factors = kpi_ctz_factors()
    # KPI Equivalent TV hours
    TV_h = tv_h(citizen_kpis_factors=citizen_kpis_factors,
                total_primary_energy=total_primary_energy_kWh)
    # KPI Equivalent streaming hours
    streaming_hours = streaming_h(citizen_kpis_factors=citizen_kpis_factors,
                                  total_primary_energy=total_primary_energy_kWh)
    # KPI equivalent pizza items
    Pizza_h = pizza_h(citizen_kpis_factors=citizen_kpis_factors,
                      total_primary_energy=total_primary_energy_kWh)
    # Equivalent battery usage estimation
    Battery_charges = battery_charges(citizen_kpis_factors=citizen_kpis_factors,
                                      total_primary_energy=total_primary_energy_kWh)
    # Equivalent electric car charging times
    ElCar_charges = el_car_charges(citizen_kpis_factors=citizen_kpis_factors,
                                   total_primary_energy=total_primary_energy_kWh)
    # Equivalent trees - - CO2
    Trees_number = trees_number(citizen_kpis_factors=citizen_kpis_factors, total_co2=total_co2_kg)

    # Equivalent Streaming impact in emissions - - CO2
    streaming_emissionhours = streaming_emission_hours(citizen_kpis_factors=citizen_kpis_factors,
                                                       total_co2=total_co2_kg)
    # - - CO2
    ICV_km = icv_km(citizen_kpis_factors=citizen_kpis_factors, total_co2=total_co2_kg)
    # Equivalent wine bottles produced - - CO2
    Wine_bottles = wine_bottles(citizen_kpis_factors=citizen_kpis_factors,
                                total_primary_energy=total_primary_energy_kWh)
    FinalEnergy_dic = {}

    for key, energy_instance in final_energy.items():
        # Check if there's any non-zero value in hourly_data
        if any(value > 0 for value in energy_instance.hourly_data):
            # Add to the dictionary with the appropriate name as key
            FinalEnergy_dic[f'final_energy_{energy_instance.name}'] = energy_instance.hourly_data

    return (total_primary_energy_kWh, total_co2,total_primary_energy_non_renewable, total_primary_energy_renewable,
            total_h_costs, total_non_h_costs, TV_h, streaming_hours, Pizza_h, Battery_charges, ElCar_charges, Trees_number,
            streaming_emissionhours, ICV_km, Wine_bottles,FinalEnergy_dic)




def recalculate_indicators (community_context):
    rate_of_self_consumption={}
    self_sufficiency={}
    total_electricity_use={}
    self_consumption={}
    total_final_energy={}
    total_PV={}
    #groups
    KPIs={}
    citizen_KPIs={}
    # Totals
    total_primary_energy = {}
    total_primary_energy_renewable = {}
    total_primary_energy_non_renewable = {}
    total_non_h_costs = {}
    total_h_costs = {}
    total_co2 = {}
    hourly_KPIs = {}
    demand_profiles_context=[]
    if 'building_asset_context' in community_context and isinstance(community_context['building_asset_context'], list):
        for building_asset_context in community_context['building_asset_context']:
            idx=0
            # Check if 'generation_system_profile_id' is in the building_dic
            if 'generation_system_profile_id' in building_asset_context:
                # Handle building_id: If it doesn't exist, assign an incremented id
                building_id = building_asset_context.get('id', f'building_{idx + 1}')  # Incremental ID if missing

                # Handle consumption_profile: Raise an error if it doesn't exist
                if 'building_consumption' not in building_asset_context or building_asset_context[
                    'building_consumption'] is None:
                    raise ValueError(f"Consumption profile does not exist for building ID: {building_id}")

                consumption_profile = building_asset_context['building_consumption']

                # Handle timestep_count: If null, use the length of any of the consumption profile arrays
                timestep_count = community_context.get('timestep_count')
                if timestep_count is None:
                    if len(consumption_profile) > 0:
                        timestep_count = len(
                            next(iter(consumption_profile.values())))  # Length of first consumption array
                    else:
                        raise ValueError(f"Timestep count could not be determined for building ID: {building_id}")

                # Handle building_energy_asset: Assign None if it doesn't exist
                building_energy_asset = building_asset_context.get('building_energy_asset', None)

                # Handle generation_system_profile: Assign None if it doesn't exist
                generation_system_profile = building_asset_context.get('generation_system_profile', None)
                demand_profile=handle_demand_profile(building_asset_context,generation_system_profile,consumption_profile)
                demand_profiles_context.append({'demand_profile': demand_profile})
                # Further processing such as adding to KPIs, calculating other values, etc.
                #timestep_count=community_context['timestep_count']
                #building_id = building_asset_context['id']
                #building_energy_asset = building_asset_context['building_energy_asset']
                #generation_system_profile = building_asset_context['generation_system_profile']
                #consumption_profile = building_asset_context['building_consumption']
                #demand_profile=building_asset_context['building']['demandprofile']
                hourly_KPIs[building_id] = {}
                # Calculate building indicators
                (
                    total_PV[building_id],
                    rate_of_self_consumption[building_id],
                    self_sufficiency[building_id],
                    total_electricity_use[building_id],
                    self_consumption[building_id],
                    total_final_energy[building_id],
                    KPIs[building_id]
                ) = calculate_building_indicators(consumption_profile, generation_system_profile, building_energy_asset,
                                                  timestep_count)

                # Add consumption_profile and demand_profile
                for key, value in consumption_profile.items():
                    hourly_KPIs[building_id].update({
                        f'consumption_profile_{key}': value})

                for key, value in demand_profile.items():
                    hourly_KPIs[building_id].update({
                        f'demand_profile_{key}' : value})
                idx+=1

            (total_primary_energy_kWh, total_co2, total_primary_energy_non_renewable, total_primary_energy_renewable,
             total_h_costs, total_non_h_costs, TV_h, streaming_hours, Pizza_h, Battery_charges, ElCar_charges,
             Trees_number,
             streaming_emissionhours, ICV_km, Wine_bottles, FinalEnergy_dic) = get_totals_per_building(KPIs[building_id],
                                                                                                       timestep_count=timestep_count,
                                                                                                       final_energy=total_final_energy[building_id])
            # calculate peak heat demand
            KPI_peak_heat_demand = max(demand_profile['heating_demand'])
            # calculate peak cooling demand
            KPI_peak_elec_demand = max(total_electricity_use[building_id])

            # Store citizen KPIs for the building
            citizen_KPIs[building_id] = [
                {"id": 1, "name": "KPI_peak_heat_demand_[kWh]", "value": KPI_peak_heat_demand, "unit": "kWh"},
                {"id": 2, "name": "KPI_peak_elec_demand_[kWh]", "value": KPI_peak_elec_demand, "unit": "kWh"},
                {"id": 3, "name": "total_primary_energy_[kWh]", "value": total_primary_energy_kWh, "unit": "kWh"},
                {"id": 4, "name": "num_members", "value": 0, "unit": "a.u."},
                {"id": 5, "name": "EquivalentTVHours_[h]", "value": TV_h, "unit": "h"},
                {"id": 6, "name": "EquivalentstreamingHours_[h]", "value": streaming_hours, "unit": "h"},
                {"id": 7, "name": "PizzaConsumptionComparison_[pizza]", "value": Pizza_h, "unit": "pizza"},
                {"id": 8, "name": "BatteryUsageEstimation_[charges]", "value": Battery_charges,
                 "unit": "charges"},
                {"id": 9, "name": "ElectricCarChargingEstimation_[charges]", "value": ElCar_charges,
                 "unit": "charges"},
                {"id": 10, "name": "WineBottlesProduction_[bottles]", "value": Wine_bottles, "unit": "bottles"},
                {"id": 11, "name": "TreesRequiredForCarbonOffset_[trees]", "value": Trees_number,
                 "unit": "trees"},
                {"id": 12, "name": "streamingEmissionsImpact_[hours]", "value": streaming_emissionhours,
                 "unit": "hours"},
                {"id": 13, "name": "CarbonEmissionsPerKilometer_[km]", "value": ICV_km, "unit": "km"},
                {"id": 14, "name": "Total_PV_[kWh]", "value": total_PV[building_id], "unit": "kWh"},
                {"id": 15, "name": "Total_self_consumption", "value": self_consumption[building_id], "unit": "a.u."},
                {"id": 16, "name": "Total_self_sufficiency", "value": self_sufficiency[building_id], "unit": "a.u."},
                {"id": 17, "name": "rate_of_self_consumption", "value": rate_of_self_consumption[building_id], "unit": "%"},
                {"id": 18, "name": "renewable_primary_energy_[kWh]", "value": total_primary_energy_renewable[building_id], "unit": "kWh"},
                {"id": 19, "name": "non_renewable_primary_energy_[kWh]", "value": total_primary_energy_non_renewable[building_id], "unit": "kWh"},
                {"id": 20, "name": "non_households_costs_[€]", "value": total_non_h_costs[building_id], "unit": "€"},
                {"id": 21, "name": "households_costs_[€]", "value": total_h_costs[building_id], "unit": "€"},
                {"id": 22, "name": "Total_co2", "value": total_co2[building_id], "unit": "g"},
            ]
            id_for_citizen_kpi = 23
            for key, energy_instance in FinalEnergy_dic.items():
                citizen_KPIs[building_id].append({"id": id_for_citizen_kpi, "name": key, "value": energy_instance, "unit": "kWh"})
                id_for_citizen_kpi += 1
    return citizen_KPIs, demand_profiles_context


def get_indicators_from_baseline(front_data, data, building_consumption_dict, demand_profile):
    """

    Parameters
    ----------
    front_data = {
    data
    building_consumption_dict

    Returns
    -------

    """
    rate_of_self_consumption = {}
    self_sufficiency = {}
    total_electricity_use = {}
    self_consumption = {}
    total_final_energy = {}
    total_PV = {}
    # groups
    KPIs = {}
    citizen_KPIs = {}

    # Define the number of hours for each month (non-leap year)
    hours_per_month = {
        "January": 744, "February": 672, "March": 744, "April": 720,
        "May": 744, "June": 720, "July": 744, "August": 744,
        "September": 720, "October": 744, "November": 720, "December": 744
    }

    # Total hours in a day
    hours_per_day = 24

    for i, item in enumerate(front_data):
        # Case 1: building_statistics_profile_id is in front_data and there is a loop for each item in front_data (per building)
        if "building_statistics_profile_id" in item:
            building_statistics_profile_id = item["building_statistics_profile_id"]
            building_profile = next(
                (profile for profile in data if profile.get("id") == building_statistics_profile_id), None)

            if building_profile is None:
                raise ValueError(
                    f"No se encontró el perfil de estadísticas del edificio con id {building_statistics_profile_id}")

            generation_system_profile = building_profile.get("generation_system_profile", {})

        else:
            # Else case: No "building_statistics_profile_id" found, we use the "building_statistics_profile"
            building_statistics_profiles = data.get("building_statistics_profile", [])
            generation_system_profile = building_statistics_profiles.get("generation_system_profile", {})

            if isinstance(building_statistics_profiles, dict):
                building_statistics_profiles = [building_statistics_profiles]
        building_id=i+1
        # Get the consumption data for each type of generation system (8760 hourly values)
        building_consumption = building_consumption_dict.get(f"building_id_{i + 1}", {})
        heating_consumption = building_consumption.get("heat_consumption", [0] * 8760)
        electricity_consumption = building_consumption.get("elec_consumption", [0] * 8760)
        cooling_consumption = building_consumption.get("cool_consumption", [0] * 8760)
        dhw_consumption = building_consumption.get("dhw_consumption", [0] * 8760)

        # Check if demand_profile contains multiple buildings or a single building
        if isinstance(demand_profile, list):
            # Multiple buildings: loop through each building
            demand_profile_building = demand_profile[i]
            demand_profile_building = demand_profile_building['demand_profile']
        else:
            # Single building case
            demand_profile_building = demand_profile['demand_profile']
            # Process the single building profile here

        # Define the systems to process (linking them to the profiles)
        systems = {
            "heating_system": heating_consumption,
            "electricity_system": electricity_consumption,
            "cooling_system": cooling_consumption,
            "dhw_system": dhw_consumption
        }

        building_energy_asset=[]
        (
            total_PV[building_id],
            rate_of_self_consumption[building_id],
            self_sufficiency[building_id],
            total_electricity_use[building_id],
            self_consumption[building_id],
            total_final_energy[building_id],
            KPIs[building_id]
        ) = calculate_building_indicators(consumption_profile=building_consumption,
                                          generation_system_profile=generation_system_profile,
                                          building_energy_asset=building_energy_asset,
                                          timestep_count=len(dhw_consumption))

        (total_primary_energy_kWh, total_co2, total_primary_energy_non_renewable, total_primary_energy_renewable,
         total_h_costs, total_non_h_costs, TV_h, streaming_hours, Pizza_h, Battery_charges, ElCar_charges, Trees_number,
         streaming_emissionhours, ICV_km, Wine_bottles, FinalEnergy_dic) = get_totals_per_building(KPIs[building_id],
                                                                                                   timestep_count=len(
                                                                                                       dhw_consumption),
                                                                                                   final_energy=
                                                                                                   total_final_energy[
                                                                                                           building_id])
        KPI_peak_heat_demand = max(demand_profile_building['heating_demand'])
        # calculate peak cooling demand
        KPI_peak_elec_demand = max(total_electricity_use[building_id])
        # Store citizen KPIs for the building
        citizen_KPIs[building_id] = [
            {"id": 1, "name": "KPI_peak_heat_demand_[kWh]", "value": KPI_peak_heat_demand, "unit": "kWh"},
            {"id": 2, "name": "KPI_peak_elec_demand_[kWh]", "value": KPI_peak_elec_demand, "unit": "kWh"},
            {"id": 3, "name": "total_primary_energy_[kWh]", "value": total_primary_energy_kWh,
             "unit": "kWh"},
            {"id": 4, "name": "num_members", "value": 0, "unit": "a.u."},
            {"id": 5, "name": "EquivalentTVHours_[h]", "value": TV_h, "unit": "h"},
            {"id": 6, "name": "EquivalentstreamingHours_[h]", "value": streaming_hours, "unit": "h"},
            {"id": 7, "name": "PizzaConsumptionComparison_[pizza]", "value": Pizza_h, "unit": "pizza"},
            {"id": 8, "name": "BatteryUsageEstimation_[charges]", "value": Battery_charges,
             "unit": "charges"},
            {"id": 9, "name": "ElectricCarChargingEstimation_[charges]", "value": ElCar_charges,
             "unit": "charges"},
            {"id": 10, "name": "WineBottlesProduction_[bottles]", "value": Wine_bottles, "unit": "bottles"},
            {"id": 11, "name": "TreesRequiredForCarbonOffset_[trees]", "value": Trees_number,
             "unit": "trees"},
            {"id": 12, "name": "streamingEmissionsImpact_[hours]", "value": streaming_emissionhours,
             "unit": "hours"},
            {"id": 13, "name": "CarbonEmissionsPerKilometer_[km]", "value": ICV_km, "unit": "km"},
            {"id": 14, "name": "Total_PV_[kWh]", "value": total_PV[building_id], "unit": "kWh"},
            {"id": 15, "name": "Total_self_consumption", "value": self_consumption[building_id], "unit": "a.u."},
            {"id": 16, "name": "Total_self_sufficiency", "value": self_sufficiency[building_id], "unit": "a.u."},
            {"id": 17, "name": "rate_of_self_consumption", "value": rate_of_self_consumption[building_id],
             "unit": "%"},
            {"id": 18, "name": "renewable_primary_energy_[kWh]",
             "value": total_primary_energy_renewable[building_id], "unit": "kWh"},
            {"id": 19, "name": "non_renewable_primary_energy_[kWh]",
             "value": total_primary_energy_non_renewable[building_id], "unit": "kWh"},
            {"id": 20, "name": "non_households_costs_[€]", "value": total_non_h_costs[building_id], "unit": "€"},
            {"id": 21, "name": "households_costs_[€]", "value": total_h_costs[building_id], "unit": "€"},
            {"id": 22, "name": "Total_co2", "value": total_co2, "unit": "g CO2eq"},
        ]
        id_for_citizen_kpi=23
        for key, energy_instance in FinalEnergy_dic.items():
            citizen_KPIs[building_id].append({"id":id_for_citizen_kpi, "name": key, "value":energy_instance, "unit": "kWh"})
            id_for_citizen_kpi +=1

    return citizen_KPIs