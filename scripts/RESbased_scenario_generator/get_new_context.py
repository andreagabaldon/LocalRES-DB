# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 16:10:28 2024

@author: andgab
"""
import os
from scripts.RESbased_scenario_generator.context_creation import (update_building_system, get_centroid, call_PVGIS, update_community_energy_assets,
                              create_grid_community_asset, convert_geometries_to_strings,
                              update_building_consumption)
from scripts.RESbased_scenario_generator.classes_database import BuildingConsumption
from datetime import datetime
from scripts.KPI_module.key_performance_indicators import handle_demand_profile
import pandas as pd
def assign_incremental_ids_to_community_assets(community_energy_asset):
    current_id = 1  # Start with an initial id value
    nodes_id=1
    # Loop through each building in the list
    for assets in community_energy_asset:
        # Loop through each energy asset within the building
            assets["id_temp"] = current_id
            if assets["availability_ts"] is not None:
                assets["availability_ts"]["id_temp"]= current_id
            assets['input_node']['id_temp'] = nodes_id
            nodes_id+=1
            if 'output_node' in assets:
                assets['output_node']['id_temp'] = nodes_id
                nodes_id += 1
            # Increment the id for the next asset
            current_id += 1

    return community_energy_asset
def assign_incremental_ids(building_asset_context):
    current_id = 1  # Start with an initial id value

    # Loop through each building in the list
    for building_assets_context in building_asset_context:
        # Loop through each energy asset within the building
        for building_energy_asset in building_assets_context["building_energy_asset"]:
            # Assign the current incremental id to the 'id' field
            building_energy_asset["id_temp"] = current_id
            building_energy_asset["availability_ts"]["id_temp"]= current_id
            # Increment the id for the next asset
            current_id += 1

    return building_asset_context

def resbased_generator_context_creation(goal, community_context,recommendations_dic):
    """
    Modifies the systems of each building, according to the list of recommended actions for one scenario

    Parameters
    ----------
    goal: from front
    community_context: The context input of the energy community
    recommendations_dic : ids of the recommended actions

    Returns
    -------
    generation_system_profile_df : modified building systems, as well as new building_energy_assets
    This means a new context is produced

    """
    #Esto es solo una prueba, falta: que sea aplicable para varias action keys,y que permita
    #añadir nuevos energy assets

    # Call the function and get the grouped buildings
    community_context_updated = community_context.copy()
    group_of_geoms = {}
    community_context_updated['context_parent']=community_context.get("id")
    community_context_updated['id_temp']= community_context_updated['context_parent']+1
    if 'id' in community_context_updated:
        del(community_context_updated['id'])
    name_of_actions_applied='Scenario with actions: '
    if 'building_asset_context' in community_context and isinstance(community_context['building_asset_context'], list):
        new_buildings_asset_contexts=[]
        temp_id = 1
        for building_asset_context in community_context['building_asset_context']:
            # get group of geoms
            group_of_geoms[building_asset_context['building']['id']] = {
                "geom": building_asset_context['building']['geom'],
                "name": building_asset_context['name']
            }
        # get gdf and centroids
        gdf, community_centroid = get_centroid(group_of_geoms)
        longitude, latitude = community_centroid.x, community_centroid.y
        # get pv_profile for the centroid of the community
        irradiance_dic, pv_profile_kWh_per_kWp, solar_elevation = call_PVGIS(longitude, latitude, tilt_angle=35)
        # translate actions to new generation systems
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data',
                                 'actions_to_generation_systems.csv')
        actions_to_generation_systems = pd.read_csv(file_path)

        for building_asset_context in community_context['building_asset_context']:
            # Check if 'generation_system_profile_id' is in the building_dic
            if 'generation_system_profile_id' in building_asset_context:
                for i, actions in recommendations_dic.items():
                    #get the action key
                    if 'id' in actions:
                        action_key = int(actions['id'])
                        #Action key is demand reduction then:
                        if action_key in [1,2]:
                            print('these actions are not yet populated')
                            new_system=False
                            pass
                        elif action_key in [15,14,16,21]:
                            print('this action is populated at community level')
                            new_system = False
                            pass
                        else:
                            #get building_id
                            building_id_geom=building_asset_context['building']['id']
                            #get the name of actions applied to the scenario
                            name_of_actions_applied += f' {action_key} with name {actions['action_name']},'
                            print(f"Processing action_key: {action_key} with name {actions['action_name']}")
                            #get existing building energy assets
                            building_energy_asset = building_asset_context['building_energy_asset']
                            # get generation system profile dics
                            generation_system = building_asset_context['generation_system_profile']
                            #get building footprint
                            building_geom=float(building_asset_context['building']['area_conditioned'])
                            #get connsumption profile
                            consumption_profile= building_asset_context['building_consumption']
                            # get building demand profile
                            demandprofile=handle_demand_profile(building_asset_context,generation_system,consumption_profile)
                            #change building system
                            updated_generation_system_profile,updated_building_energy_asset,new_system= update_building_system (goal=goal, building_id=building_id_geom,
                                                                                                                                 building_geom=building_geom,demandprofile=demandprofile,pvprofile=pv_profile_kWh_per_kWp,
                                                                                                                                 buildings_generation_system=generation_system,building_energy_asset=building_energy_asset,
                                                                                                                                 actions_to_generation_systems=actions_to_generation_systems,action_key=action_key,solar_elevation=solar_elevation)
                            #update building energy assets
                            building_asset_context['building_energy_asset']=updated_building_energy_asset.copy()
                            #update generation_system_profile_dic
                            building_asset_context['generation_system_profile']=updated_generation_system_profile.copy()
                    else:
                        print('error encountered with action id')
                        pass

                building_asset_context['id_temp']=temp_id
                print(temp_id)

                building_asset_context['context_id']=community_context_updated['id_temp']
                print(action_key)
                print(building_asset_context['name'])
                if building_asset_context['name'] is not None:
                    building_asset_context['name']=building_asset_context['name']+f' with action {action_key}, '
                print(f"  Building id: {building_asset_context['id_temp']} changed its generation system profile"
                      f"to {building_asset_context['generation_system_profile_id']}")
                building_asset_context['building_consumption_id_temp']=temp_id
                if new_system:  # Only check if new_system is True
                    updated_building_dic=update_building_consumption(temp_id,demandprofile,building_asset_context)
                    building_asset_context['building_consumption'] = updated_building_dic
                new_buildings_asset_contexts.append(building_asset_context)
                temp_id+=1
    else:
        print("'building_asset_context' is not a valid list in bd")

    for building_asset_context in community_context['building_asset_context']:
        del (building_asset_context['generation_system_profile']['electricity_system'])
        del (building_asset_context['generation_system_profile']['heating_system'])
        del (building_asset_context['generation_system_profile']['cooling_system'])
        del (building_asset_context['generation_system_profile']['dhw_system'])
        del (building_asset_context['building_consumption_id'])
        del (building_asset_context['id'])
        building_asset_context['generation_system_profile_id'] = None
    updated_community_energy_asset=[]
    community_centroid_string=convert_geometries_to_strings(community_centroid)
    updated_community_energy_asset.append(create_grid_community_asset(community_centroid_string))
    for i, actions in recommendations_dic.items():
        # get the action key
        action_key = int(actions['id'])
        if action_key==15:
            updated_community_energy_asset.append(update_community_energy_assets(community_centroid_string, action_key,actions_to_generation_systems))

    updated_community_energy_asset=assign_incremental_ids_to_community_assets(community_energy_asset=updated_community_energy_asset)
                                   #create new context (id=2) with context_parent=bd.get("id")
    community_context['building_asset_context']=assign_incremental_ids(new_buildings_asset_contexts)
    #update community assets and nodes (Alberto)
    if 'community_energy_asset' in community_context and not community_context['community_energy_asset']:
        # If it's an empty list, replace it with `updated_community_energy_asset`
        community_context_updated['community_energy_asset'] = updated_community_energy_asset
    else:
        community_context_updated['community_energy_asset']=[]
        # If it's not empty, append every asset from `updated_community_energy_asset`
        for asset in updated_community_energy_asset:
            community_context_updated['community_energy_asset'].append(asset)
    # datetime object containing current date and time
    community_context_updated['creation_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    community_context_updated['name'] =name_of_actions_applied
    community_context_updated['description'] = name_of_actions_applied+ f'with goal {goal}'
    return community_context_updated
