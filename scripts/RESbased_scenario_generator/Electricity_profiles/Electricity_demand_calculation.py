# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 13:51:16 2024

Vincenzo Ezio Santovito
@author: vinsan

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
"""

import json
import pandas as pd
import numpy as np
import os
import random
import matplotlib.pyplot as plt

# Function to compare the UI usuario answer and those from LPG in the case of no exact match
def are_dicts_similar(dict1, dict2, threshold):
    common_elements = sum(1 for key, value in dict1.items() if key in dict2 and dict2[key] == value)
    return common_elements >= threshold


def LPG_electricity_profile_generator(ruta_jsons, ruta_csvs, answer):
    # ruta_base = os.path.join(os.getcwd(), "Electricity_profiles_vinsan")
    # ruta_jsons = os.path.join(os.getcwd(), "Unique_Usuarios")
    # ruta_csvs = os.path.join(os.getcwd(), "Electricity_Profiles_Averaged_Duplicates")
    
    usuarios = {}
    demandas = {}
    # answer = {"usuario": 
    #     {"number_of_family_members": 4, 
    #       "number_of_people_working": 1, 
    #       "number_of_people_students": 2,
    #       "number_of_people_retired": None,
    #       "number_of_toddler": None,
    #       "number_of_children": 2,
    #       "number_of_adult_young": None,
    #       "number_of_adult": 2,
    #       "number_of_senior": None}  #This is the hosuehold characteristics coming from the UI
    # }
    json_files = [archivo for archivo in os.listdir(ruta_jsons) if archivo.endswith('.json')]
    csv_files = [archivo for archivo in os.listdir(ruta_csvs) if archivo.endswith('.csv')]
    
    # Storing all the households in a proper dictionary
    for json_file in json_files:
        with open(ruta_jsons+"\\"+json_file) as file:
            usuario = json.load(file)                    #.json of a specific household
            json_name = os.path.splitext(json_file)[0]   #.json file name without the extension
            usuarios[json_name] = usuario                # Dictionary containing all the types of households (The key is CHR_)
    
    # Storing all the Electricity Consumption Profiles in a dictionary of dataframes in which the access key is the household ID
    for csv_file in csv_files:
        demanda = pd.read_csv(os.path.join(ruta_csvs, csv_file))
        csv_name = os.path.splitext(csv_file)[0]
        demandas[csv_name] = demanda
    
    # Now I imagine I have a household specification as received from the UI answers. I import it as a .json and compare it with the available 
    # usuarios and assign it to the corresponding Electricity Consumption. In case no exact match is found I have three options:
    # 1. A random profile is assigned among those available
    # 2. The closest profile is assigned (Is it possible? I have to check)
    # 3. Average of all the available profiles is assigned (does it make sense?) 
    

    profile = np.zeros(8760)
    n = 0
    
    for key1,value1 in usuarios.items():
        for key2,value2 in demandas.items():
            if key1 == answer:
                profile = demandas[key2]['Consumption [kWh]']
                
    if profile.sum() == 0:  # This means the assignment did not work as no available usuario matches the answer from the UI
            #Option1 - Random profile
            profile = random.choice(list(demandas.values()))['Consumption [kWh]']
            
            #Option2 - Similar profile
            for key1,value1 in usuarios.items():
                if are_dicts_similar(answer,value1,4) and value1["number_of_family_members"] == answer["number_of_family_members"]:
                    profile = demandas[key1]
                
            #Option3 - Average of all profiles
            for key in demandas:
                profile = profile + demandas[key]['Consumption [kWh]']
                n = n+1
            profile = profile/n
            
    
    # Ejemplo de plot
    # plt.plot(profile)

    return profile    