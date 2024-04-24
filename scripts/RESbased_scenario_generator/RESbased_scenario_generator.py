# -*- coding: utf-8 -*-
"""
Dependencies:
    python 3.11
    pillow                    10.2.0
    pandas                    2.2.0
    spyder                    5.5.0
    geopandas                 0.14.2
Created on October 2023

@author: Andrea Gabaldon Moreno
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

***********************************************************************************************

This part of the code is the main code that provides the actual recommendations

***********************************************************************************************

"""
from country_RES_library import assign_country_from_json
from country_RES_library import  country_RES_recommendations 
import os
import csv
import pandas as pd
import json
from Electricity_profiles import Electricity_demand_calculation as el
from energy_consumption import EnergyConsumption
# ***********************************************************************************************

# This part of the code gives a list based on user inputs: goal and country

# ***********************************************************************************************




def RESbased_generator_list_technologies(inputs_users):
    '''This function allows to create a list of recommended technologies for user preferences'''
    #read inputs from users
    user_objective=inputs_users['objectives']
    country_code=inputs_users['country']
    #create country object and obtain recommended scenarios for the country selected
    country_recommended_scenarios_df= country_RES_recommendations(country_code=country_code)
    #read the tables Country_VS_Actions and Goals_VS_Actions to make the MCDA analysis
    directory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data\\RESlibrary')
    country_vs_actions='country_vs_actions.csv'
    goals_vs_actions='goals_vs_actions.csv'
    country_vs_actions_df=pd.read_csv(os.path.join(directory_path,country_vs_actions))
    goals_vs_actions_df=pd.read_csv(os.path.join(directory_path,goals_vs_actions))
    #obtain w1
    goals_vs_actions_df_filtered=goals_initialisation (goals_vs_actions_df, user_objective)
    #obtain w2
    w2_df=country_initialisation (country_vs_actions_df, country_recommended_scenarios_df)
    #obtain wT
    wT=  goals_vs_actions_df_filtered.multiply(w2_df)
    wT_final = pd.concat([goals_vs_actions_df['Action'], wT], axis=1)
    # wT.set_index(goals_vs_actions_df['Action'], inplace=True)
    # Actions_weight=pd.concat([ goals_vs_actions_df['Action'], wT], axis=1, ignore_index=True)
    list_technologies=top_values(wT_final)
    # list_technologies = pd.DataFrame({'Action': list_technologies.index, 'w': list_technologies['w']})
    list_technologies=list_technologies.reset_index()
    data = {
        1:'reduction_of_demand',
        2:'demand_response',
        3:'solar_fleet',
        4:'wind_offshore_fleet',
        5:'hydro_fleet',
        6:'geothermal_fleet',
        7:'solar_thermal',
        8:'biomass_boiler',
        9:'gas_boiler',
        10:'heat_pump',
        11:'geothermal_heat',
        12:'methanisation',
        13:'gas_chp',
        14:'biomass_chp',
        15:'battery_storage',
        16:'heat_storage',
        17:'gas_storage',
        18:'creation_of_dhn',
        19:'connection_to_the_dhn',
        20:'dhn_supplier',
        21:'charging_station'
    }
    #translate into a useful json
    output_dictionary = {}
    for idx, row in list_technologies.iterrows():
        id_ = row['index'] + 1  # Increment by 1 to do match with the previous dictionary
        action_name = data[id_]
        output_dictionary[idx] = {'id': id_, 'action_name': action_name}
    
    print(output_dictionary)
    return output_dictionary


def top_values(df):
    '''This function allows to generate a ranking of a dataframe'''
    # Create a ranking of values in the DataFrame

    df.sort_values(by='w', ascending=False)

    # Get the top 5 values from the ranking DataFrame which are those with ranking above 7
    top_5_values = df.nlargest(5, 'w')

    return top_5_values




def goals_initialisation (goals_vs_actions_df, user_objective):
    '''This function allows to create dataframe of goals and filter by user objective'''
    #drop category columns because it is not used 
    goals_vs_actions_df.drop(columns=['Category'], inplace=True)

    #Linear normalization is done assuming all actions are beneficial, therefore normalized_Xij= Xij/XjMAX
     #obtain the maximum of the df, avoiding the first column that contains string values
    Xj_max=  goals_vs_actions_df.iloc[:, 1:].max().max()
     #normalize
    goals_vs_actions_df = goals_vs_actions_df.iloc[:, 1:] / Xj_max

    #filter by goal (i.e. choose a column) and rename (as it w1=df[objetive selected by user])
    goals_vs_actions_df_filtered = goals_vs_actions_df[[user_objective]].copy()
    goals_vs_actions_df_filtered.rename(columns={user_objective: 'w'}, inplace=True)

    return  goals_vs_actions_df_filtered

def country_initialisation (country_vs_actions_df, country_recommended_scenarios_df):
    '''This function allows to create country class'''
    #drop category columns because it is not used 
    country_vs_actions_df.drop(columns=['Category'], inplace=True)

    #Linear normalization is done assuming all actions are beneficial, therefore normalized_Xij= Xij/XjMAX
        #obtain the maximum of the df, avoiding the first column that contains string values
    Xj_max=  country_vs_actions_df.iloc[:, 1:].max().max()
    #normalize
    country_vs_actions_df=country_vs_actions_df.iloc[:, 1:] / Xj_max
    ####### obtain wj for the country
        #drop country column    
    country_recommended_scenarios_df.drop(columns=['Country'], inplace=True)
        # Convert columns of  country_recommended_scenarios_df to boolean type
    country_recommended_scenarios_df= country_recommended_scenarios_df.replace({'True': True, 'False': False})
        # Count the number of True values
    n_true_values = country_recommended_scenarios_df.sum().sum()
        # Replace True values with values from 0 to 1/n
    country_recommended_scenarios_df = country_recommended_scenarios_df.apply(lambda x: x.map(lambda y: 1 / n_true_values if y else 0))
    #obtain w2=sum(wj*xij)
    w2_pruduct=country_vs_actions_df*country_recommended_scenarios_df.values[0]
    # Sum all column values per row
    w2 = w2_pruduct.sum(axis=1)
    # Create a new DataFrame with the summed values and column name 'w2'
    w2_df = pd.DataFrame(w2, columns=['w'])
    return w2_df



# ***********************************************************************************************

# This part of the code creates the baseline

# ***********************************************************************************************

# building_consumption_dict = GenerationSystem(data=data, demand_profile=demand_profile)
def baseline_pathway_simple(data, front_data, demand_profile, building_consumption_dict):
    '''
    Reads information for a specified number of buildings and their building use from the provided data.    
    This function reads information for a specified number of buildings, 
    their building use, and the common consumption profile of the community.
    It then constructs dictionaries with building information and building asset context 
    based on the provided data and front-end information.
    Each building dictionary includes details such as building ID, area, construction year, 
    demand profile ID, and building use. The building asset context dictionary includes information 
    such as building ID, generation system profile ID, and calculated building consumption.

    Parameters
    ----------
    data : dict
        A dictionary containing information about the buildings, including statistics and generation system profiles.
    
    front_data : dict
        A dictionary containing front-end data about the community, such as the number of buildings and their use.

    Returns
    -------
    output_context_kpi_module : dict
        A dictionary containing the output context for the KPI module.
        
    '''
    
    # Retrieve the default demand profile for the community

    # Retrieve building characteristics
    common_construction_year = data["building_statistics"][0]["common_construction_year"]
    avg_surface = data["building_statistics"][0]["avg_surface"]
    geom = None  # Analyze if geometry is included in the intermediate data
    num_building = front_data["num_building"]
    building_use = front_data["building_use_id"]
    
    # Initialize lists to store building and asset context dictionaries
    building_asset_context = []
    
       
    # Loop through each building
    for i in range(num_building):
        # Build the building dictionary
        building_dict = {
            "id": i + 1,
            "generation_system_profile_id": 1,  # Assume a generation system profile ID of 1
            "building_energy_asset_id": i + 1,
            "building_consumption_id": i + 1,
            "building_id": i + 1,
            "context_id": 1,  # The base context always has context_id: 1
            "building_consumption": {
                "building_consumption_id": i + 1,
                "elec_consumption": building_consumption_dict["elec_consumption"],
                "heat_consumption": building_consumption_dict["heat_consumption"],
                "cool_consumption": building_consumption_dict["cool_consumption"],
                "dhw_consumption": building_consumption_dict["dhw_consumption"]
            },
            "building": {
                "geom": geom,
                "height": 6,  # meters
                "construction_year": common_construction_year,
                "building_use_id": building_use,
                "id": i + 1,
                "area_conditioned": avg_surface,
                "demandprofile_id": demand_profile["demand_profile"]["id"]
            }
        }
        building_asset_context.append(building_dict)   
        
    # Construct the output context
    output_context_kpi_module = {
        "name": "prueba",
        "timestep_count": 0,
        "timestep_duration": 0,
        "creation_date": "2024-03-22",
        "context_parent": None,
        "id": 1,
        "start_date": "2024-03-22",
        "author": "manper",
        "description": "prueba desc",
        "context_id": {
            "building_asset_context": building_asset_context
        }
    }
    
    # Create the "outputs" folder if it doesn't exist
    output_folder = "outputs"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Save the JSON to a file
    output_file = os.path.join(output_folder, "output_context.json")
    with open(output_file, "w") as f:
        json.dump(output_context_kpi_module, f, indent=4)
    
    print("File saved successfully at:", output_file)
    
    # Return output context
    return output_context_kpi_module



'''
###############################################
    BUILDINGS DEMAND 
###############################################
'''

def DemandDefault(data, front_data):
    '''
    This function retrieves the default demand profile for a community.

    Parameters
    ----------
    data : dict
        A dictionary containing information about building statistics profiles, including the default demand profile.
    front_data : dict
        A dictionary containing front-end data about the community, the common demand profile of the buildings.
    
    Returns
    -------
    demand_profile : dict
        A dictionary containing the default demand profile for the community.
            - id : int
                The ID of the demand profile.
            - heating_demand : list
                A list representing the heating demand profile.
            - cooling_demand : list
                A list representing the cooling demand profile.
            - dhw_demand : list
                A list representing the domestic hot water demand profile.
            - electricity_demand : list
                A list representing the electricity demand profile.
    '''
    
    common_profile = front_data["common_profile"]
    if common_profile == 1: #STUDENTS # CHR01
        answer = {"usuario": 
            {"number_of_family_members": 2, 
             "number_of_people_working": 2, 
             "number_of_people_students": None,
             "number_of_people_retired": None,
             "number_of_toddler": None,
             "number_of_children": None,
             "number_of_adult_young": 2,
             "number_of_adult": None,
             "number_of_senior": None}  #This is the hosuehold characteristics coming from the UI
        }
    if common_profile == 2: #ADULTS #CHR02
        answer = {"usuario": 
            {"number_of_family_members": 2, 
             "number_of_people_working": 2, 
             "number_of_people_students": None,
             "number_of_people_retired": None,
             "number_of_toddler": None,
             "number_of_children": None,
             "number_of_adult_young": None,
             "number_of_adult": 2,
             "number_of_senior": None}  #This is the hosuehold characteristics coming from the UI
        }
    if common_profile == 3: #FAMILY #CHR44
        answer = {"usuario": 
            {"number_of_family_members": 4, 
             "number_of_people_working": 1, 
             "number_of_people_students": 2,
             "number_of_people_retired": None,
             "number_of_toddler": None,
             "number_of_children": 2,
             "number_of_adult_young": None,
             "number_of_adult": 2,
             "number_of_senior": None}  #This is the hosuehold characteristics coming from the UI
        }
    if common_profile == 4: #RETIRED #CHR16
        answer = {"usuario": 
            {"number_of_family_members": 2, 
             "number_of_people_working": None, 
             "number_of_people_students": None,
             "number_of_people_retired": 2,
             "number_of_toddler": None,
             "number_of_children": None,
             "number_of_adult_young": None,
             "number_of_adult": None,
             "number_of_senior": 2}  #This is the hosuehold characteristics coming from the UI
        }
    route_base = os.path.join(os.getcwd(), "Electricity_profiles")
    route_jsons = os.path.join(route_base, "Unique_Usuarios")
    route_csvs = os.path.join(route_base, "Electricity_Profiles_LPG_Hourly")
    profile = el.LPG_electricity_profile_generator(ruta_jsons=route_jsons, ruta_csvs=route_csvs, answer=answer)
    electricity_profile_df = profile.to_frame(name='electricity_demand')
    electricity_profile = electricity_profile_df['electricity_demand'].tolist()
    dict_demand_default = data['building_statistics'][0]['demand_profile_default']
    demand_profile = {
        "demand_profile": {
            "id": 1,  # This ID might change depending on the number of demand profiles provided
            "heating_demand": dict_demand_default["heating_demand"],
            "cooling_demand": dict_demand_default["cooling_demand"],
            "dhw_demand": dict_demand_default["dhw_demand"],
            "electricity_demand":  electricity_profile,
        }
    }
        
    return demand_profile


