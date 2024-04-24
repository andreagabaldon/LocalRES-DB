# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 13:17:08 2024
Dependencies:
    pillow                    10.2.0
    pandas                    2.2.0
    
Created on October 2023

@author: Andrea Gabaldon, Iciar Bernal 
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
@author: andgab, iciber
"""
from RESbased_scenario_generator import RESbased_generator_list_technologies
from RESbased_scenario_generator import DemandDefault
from RESbased_scenario_generator import baseline_pathway_simple
from energy_consumption import GenerationSystem

import os
import csv
import pandas as pd
import json


user_object='inputs_user.json'
def inner_RESbased_generator_list_technologies(user_object):
    try:
        #Input from users 
        file_path = os.path.join(os.getcwd(), 'data',user_object)
        # file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data',user_object)
        # Read the JSON data from the file
        with open(file_path, 'r') as file:
            inputs_users = json.load(file)
    except IOError:
        print("An error occured while reading the file.")
    
    return RESbased_generator_list_technologies(inputs_users)



def inputs_from_user(): #SEND THIS FUNCTION TO MAIN() 
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


#Retrive info from user
front_data, data = inputs_from_user()
#assign demand default profile
demand_profile=DemandDefault(data=data, front_data=front_data)
    
# Retrieve generation system information and building consumption
building_consumption_dict = GenerationSystem(data=data, demand_profile=demand_profile)
#generate baseline
baseline_simple=baseline_pathway_simple(data=data, front_data=front_data, demand_profile=demand_profile, building_consumption_dict=building_consumption_dict )

