import os
import json
from scripts.RESbased_scenario_generator.RESbased_scenario_generator import res_based_generator_list_technologies, generate_geojson, fetch_geojson, baseline_pathway_simple, baseline_pathway_intermediate, demand_statistics, demand_thermagrid
# , generate_geojson
from scripts.KPI_module.energy_consumption import generation_system_function
from scripts.RESbased_scenario_generator.get_new_context import resbased_generator_context_creation
from scripts.KPI_module.key_performance_indicators import recalculate_indicators, get_indicators_from_baseline, aggregate_demand_profiles, community_KPIs



def generate_baseline_pathway_simple(data, front_data):
    #calculate electricity and heat demand
    demand_profile=demand_statistics(data=data, front_data=front_data)
    #calculate energy consumption based on the technology
    building_consumption_dict = generation_system_function(data=data, front_data=front_data, demand_profile=demand_profile)
    #create baseline object
    baseline=baseline_pathway_simple(data=data, front_data=front_data, demand_profile=demand_profile, building_consumption_dict=building_consumption_dict )
     # calculate kpis per building
    citizen_KPIs_per_building = get_indicators_from_baseline(front_data, data, building_consumption_dict,
                                                             demand_profile)
    # calculate total aggregated demand
    total_demand = aggregate_demand_profiles(demand_profile)
    # calculate total community indicators
    community_indicators = community_KPIs(citizen_KPIs_per_building, total_demand)

    return baseline, community_indicators


def generate_baseline_pathway_intermediate(data, front_data):
    geojson_object=generate_geojson(front_data=front_data)
    geojson_file = fetch_geojson(geojson_object=geojson_object)
    demand_profile=demand_thermagrid(front_data=front_data, geojson_file=geojson_file)
    #calculate energy consumption based on the technology
    building_consumption_dict = generation_system_function(data=data, front_data=front_data, demand_profile=demand_profile)
    #create baseline object
    baseline = baseline_pathway_intermediate(front_data=front_data, data=data, geojson_file=geojson_file, demand_profile=demand_profile, building_consumption_dict=building_consumption_dict )
    #calculate kpis per building
    citizen_KPIs_per_building = get_indicators_from_baseline(front_data, data, building_consumption_dict, demand_profile)
    #calculate total aggregated demand
    total_demand = aggregate_demand_profiles(demand_profile)
    #calculate total community indicators
    community_indicators = community_KPIs(citizen_KPIs_per_building, total_demand)

    return  baseline, community_indicators


def generate_resbased_generator_list_technologies(front_data):
    list_technologies = res_based_generator_list_technologies(inputs_users=front_data)
    return list_technologies


def get_new_context(goal, community_context,recommendations_dic):
    new_context=resbased_generator_context_creation(goal,community_context,recommendations_dic)
    return new_context

def calculate_indicators(community_context):
    citizen_KPIs_per_building, demand_profiles_context=recalculate_indicators(community_context)
    #calculate total aggregated demand
    total_demand = aggregate_demand_profiles(demand_profiles_context)
    #calculate total community indicators
    community_indicators = community_KPIs(citizen_KPIs_per_building, total_demand)
    return citizen_KPIs_per_building, community_indicators

current_path=os.path.dirname(os.path.abspath(__file__))
# choose simple (1) or intermmediate (2) pathway (the latter being the one with higher user inputs)
pathway=2
#import path
if pathway==2:
    #inputs from use in the simple pathway
    front_data={
        "num_building": 3,
        "common_profile": 3,
        "building_use_id": 2
    }
    #the databse uses front_data to obtain the following information from the database:
    example_of_output_database_simple = os.path.join(current_path, 'scripts','KPI_module','data',
                                     'inputs_database.json')

    # Load the JSON file to take the info from the database
    with open(example_of_output_database_simple, 'r') as file:
        data = json.load(file)
    #obtain the baseline and community indicators for the LocalRES database structure
    baseline, community_indicators= generate_baseline_pathway_simple(data, front_data)
else:
    #inputs from user in the intermediate pathway are given per building
    example_of_output_database_int_front = os.path.join(current_path, 'scripts','KPI_module','data',
                                     'int_inputs_user.json')
    #structure of those inputs can be seen in:
    with open(example_of_output_database_int_front, 'r') as file:
        front_data = json.load(file)
    #the database uses front_data to obtain the following information from the database:
    example_of_output_database_int = os.path.join(current_path, 'scripts','KPI_module','data',
                                     'int_inputs_database.json')

    # Load the JSON file to take the info from the database
    with open(example_of_output_database_int, 'r') as file:
        data = json.load(file)
    #obtain the baseline and community indicators for the LocalRES database structure
    baseline, community_indicators= generate_baseline_pathway_intermediate(data, front_data)


# user chooses a goal in the user-interface and based on the location of the chosen community country is passed:
#     goals={
#             "1": "Higher rate of renewable energy",
#             "2": "Higher efficiency",
#             "3": "Energy self-sufficiency",
#             "4": "Decarbonisation of H&C",
#             "5": "Electrification",
#             "6": "E-mobility",
#         }

inputs_user_goals={"goals": "3",
                   "country": "ES"
                   }
recommendations_dic=generate_resbased_generator_list_technologies (front_data=inputs_user_goals)
#the baseline context is obtained from the API database


with open(os.path.join(current_path, 'scripts','data_example',
                                     'dummy_data_example.json'), 'r') as file:
    community_context = json.load(file)


new_context=get_new_context(goal=inputs_user_goals["goals"],community_context=community_context, recommendations_dic=recommendations_dic)
##Optimise results with an optimisation engine (not open source in LocalRES project):
output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts','data_example', 'dummy_data_example_output.json')
with open(output_file_path, 'w') as json_file:
    json.dump(new_context, json_file, indent=4)
