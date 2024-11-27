# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 11:52:35 2024

@author: andgab
"""

import numpy as np


class BuildingEnergyAsset:
    def __init__(self, generation_system_id, pmaxmin_scalar,pmaxmax_scalar, building_asset_context_id, name):
        self.generation_system_id = generation_system_id
        self.pmaxmin_scalar= pmaxmin_scalar
        self.pmaxmax_scalar=pmaxmax_scalar
        self.building_asset_context_id = building_asset_context_id
        self.name = name

        # Initialize time series data placeholders for input1, input2, output1, and output2
        self.input1 = []  # Represents electricity or other input1
        self.input2 = []  # Represents air or other input2
        self.output1 = []  # Represents heating demand or other output1
        self.output2 = []  # Empty by default


    def add_PV_profile(self,pvprofile):
        self.input1 = pvprofile

    def calculate_inputs_and_outputs(self, demand, fuel_yield1, fuel_yield2, type="heat_pump"):
        """
        General method to calculate input1, input2 (e.g., electricity and air)
        based on demand and fuel_yield. You can specify the input_type as 'electricity' or another.
        """
        for d in demand:
            if type == "heat_pump":
                input1_value = d / fuel_yield1
                input2_value = (fuel_yield1 - 1) * input1_value
            else:
                input1_value = d / fuel_yield1
                input2_value=[]
                if fuel_yield2 is not None:
                    output2_value = d*fuel_yield2
                    self.output2 = output2_value

            self.input1.append(input1_value)
            self.input2.append(input2_value)

        # Store demand in output1 or output2 based on the context
        self.output1 = demand  # This could represent heating demand or another output


    def to_dict(self):
        """Convert the object to a dictionary matching the required JSON structure."""
        return {
                "id_temp": None,
                "generation_system_id": self.generation_system_id,
                "pmaxmin_scalar": self.pmaxmin_scalar,
                "availability_ts_id": None,
                "pmax_scalar": None,
                "pmaxmax_scalar": self.pmaxmax_scalar,
                "building_asset_context_id": self.building_asset_context_id,
                "availability_ts": {
                    "temp_id": None,
                    "name": self.name,
                    "value_input1": self.input1,
                    "value_input2": self.input2,
                    "value_output1": self.output1,
                    "value_output2": self.output2,
                    "testcase": "TC_0"
                }
            }



class BuildingConsumption:
    """
    Represents building consumption dict
    Attributes:
        building (dict): Detailed information about the building.
        building_consumption (dict): Information about the building's energy consumption.
    """
    
    def __init__(self, building_consumption_id_temp,elec_consumption):
        self.building_consumption_id_temp = building_consumption_id_temp
        hours_in_year = 8760  # 8760 hours for a year-long hourly model
        # Initialize time series data placeholders for input1, input2, output1, and output2
        self.heat_consumption = [0] * hours_in_year  # Empty by default
        self.dhw_consumption = [0] * hours_in_year # Empty by default
        # Check if elec_consumption is None, if so, fill with zeros
        if elec_consumption is None:
            self.elec_consumption = [0] * hours_in_year
        else:
            self.elec_consumption = elec_consumption
        self.cool_consumption = [0] * hours_in_year  # Empty by default

    def to_dict(self):
        return {
                "id": self.building_consumption_id_temp,
                "heat_consumption": self.heat_consumption,
                "dhw_consumption": self.dhw_consumption,
                "elec_consumption": self.elec_consumption,
                "cool_consumption": self.cool_consumption
        }

    def re_calculate_consumption(self, demand, fuel_yield1, type="heat_consumption"):
        """
               General method to calculate consumption based on demand and fuel_yield1.
               Parameters:
                   demand (list): A list of demand values.
                   fuel_yield1 (float): A yield value to adjust consumption.
                   type (str): The type of consumption to update (default is 'heat_consumption').
               """
        hours_in_year = 8760  # 8760 hours for a year-long hourly model

        # If demand is None or fuel_yield1 is None, set consumption to zeros
        if demand is None or fuel_yield1 is None:
            output = [0] * hours_in_year
        else:
            if fuel_yield1 == 0:
                raise ValueError("fuel_yield1 cannot be zero.")  # Prevent division by zero

            # Calculate consumption based on demand and fuel_yield1
            output = [x / fuel_yield1 for x in demand]

        # Assign the output to the appropriate consumption type
        if type == "heat_consumption":
            self.heat_consumption = output
        elif type == "dhw_consumption":
            self.dhw_consumption = output
        elif type == "cool_consumption":
            self.cool_consumption = output


import json
import os



class FinalEnergy:
    def __init__(self, id):
        self.id = id
        self.name = None
        self.final = False
        self._hourly_data = [0] * 8760  # Using a leading underscore to indicate this is "private" and a method is assigned
                                        #to recalculate monthly and yearly data every time hourly data is changed
        self.monthly_data = [0] * 12
        self.yearly_data = 0
        self.recalculate()  # Initial calculation

    @property
    def hourly_data(self):
        return self._hourly_data

    @hourly_data.setter
    def hourly_data(self, new_hourly_data):
        #the setter is used: e.g. energy_instance.hourly_data = new_hourly_data  # This triggers the setter
        if len(new_hourly_data) != 8760:
            raise ValueError("Hourly data must have 8760 entries.")
        self._hourly_data =  [0 if value is None else value for value in new_hourly_data]
        self.recalculate()  # Recalculate monthly and yearly data when hourly data changes

    def recalculate(self):
        """ Recalculate the monthly and yearly data whenever hourly data is changed """
        self.monthly_data = self.calculate_monthly(self._hourly_data)
        self.yearly_data = sum(self._hourly_data)

    def calculate_monthly(self, hourly_data):
        # Define the number of hours per month in a non-leap year
        hours_per_month = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
        monthly_data = []
        start = 0
        for hours in hours_per_month:
            monthly_data.append(sum(hourly_data[start:start + hours]))
            start += hours
        return monthly_data

    def final_energy_to_dic(self):
        return {
            "name": self.name,
            "final": self.final,
            "hour": self._hourly_data[:],  # return a copy of the list
            "month": self.monthly_data[:],  # return a copy of the list
            "year": self.yearly_data
        }

    def add_new_consumption(self, consumption):
        """
        Adds new fuels or electricity consumption to the current _hourly_data for the energy carrier
        :param consumption: List of 8760 values representing the new consumption to add.
        """
        if len(consumption) != 8760:
            raise ValueError("Consumption data must have 8760 entries.")
        # Add each hour's consumption to the existing _hourly_data
        self._hourly_data =[self._hourly_data[i] + (consumption[i] if consumption[i] is not None else 0) for i in range(8760)]
        # Recalculate monthly and yearly values after adding new consumption
        self.recalculate()



class BuildingKPIs:
    def __init__(self, final_energy_instance, kpi_data):
        """
        Initialize the BuildingKPIs object with the FinalEnergy instance and KPI data such as PEF_total, PEF_nren, etc.
        :param final_energy_instance: The FinalEnergy object for a specific energy carrier.
        :param kpi_data: A dictionary containing the external KPI factors for that energy carrier.For each energy carrier,
        you store the values for pef_tot, pef_nren, f_co2_eq_g_kwh, etc.
        For each energy carrier, the hourly KPIs will be calculated as products of FinalEnergy._hourly_data
        and the external factor.
        # Monthly and yearly values will also be calculated based on the hourly values.
        """
        self.final_energy = final_energy_instance
        self.energy_carrier_name=final_energy_instance.name
        self.energy_carrier_id = kpi_data['energy_carrier_id']
        self.pef_tot = kpi_data.get('pef_tot', 0.0)  # Default to 0 if None
        self.pef_nren = kpi_data.get('pef_nren', 0.0)  # Default to 0 if None
        self.f_co2_eq_g_kwh = kpi_data.get('f_co2_eq_g_kwh', 0.0)  # Default to 0 if None
        self.pef_ren = kpi_data.get('pef_ren', 0.0)  # Default to 0 if None

        if kpi_data.get('non_h_costs_eur_kwh', 0.0) == None:
            self.non_h_costs_eur_kwh = 0
        else:
            self.non_h_costs_eur_kwh=kpi_data.get('non_h_costs_eur_kwh', 0.0)  # Default to 0 if None

        if  kpi_data.get('house_costs_eur_kwh', 0.0)== None:
            self.house_costs_eur_kwh = 0  # Default to 0 if None
        else:
            self.house_costs_eur_kwh = kpi_data.get('house_costs_eur_kwh', 0.0)  # Default to 0 if None

        # Calculate the KPIs (hourly, monthly, yearly)
        self.calculate_kpis()

    def calculate_kpis(self):
        """
        Calculate the KPIs based on FinalEnergy's hourly data and the provided external factors.
        """
        # Perform element-wise calculation
        hourly_data = self.final_energy._hourly_data
        self.PEF_total = [hourly_data[i] * self.pef_tot for i in range(len(hourly_data))] #kWh
        self.PEF_nren = [hourly_data[i] * self.pef_nren for i in range(len(hourly_data))] #kWh
        self.PEF_ren = [hourly_data[i] * self.pef_ren for i in range(len(hourly_data))] #kWh
        self.co2 = [hourly_data[i] * self.f_co2_eq_g_kwh for i in range(len(hourly_data))] #g
        self.non_h_costs = [hourly_data[i] * self.non_h_costs_eur_kwh for i in range(len(hourly_data))] #euros
        self.household_costs = [hourly_data[i] * self.house_costs_eur_kwh for i in range(len(hourly_data))] #euros
        # Monthly KPIs in appropriate units (MWh, tonnes, k€)
        self.PEF_total_monthly = [value * 1e-3 for value in
                                  self.calculate_monthly(self.PEF_total)]  # Convert kWh to MWh
        self.PEF_nren_monthly = [value * 1e-3 for value in self.calculate_monthly(self.PEF_nren)]  # Convert kWh to MWh
        self.PEF_ren_monthly = [value * 1e-3 for value in self.calculate_monthly(self.PEF_ren)]  # Convert kWh to MWh
        self.co2_monthly = [value * 1e-6 for value in self.calculate_monthly(self.co2)]  # Convert grams to tonnes
        self.non_h_costs_monthly = [value * 1e-3 for value in
                                    self.calculate_monthly(self.non_h_costs)]  # Convert € to k€
        self.household_costs_monthly = [value * 1e-3 for value in
                                        self.calculate_monthly(self.household_costs)]  # Convert € to k€

        # Yearly KPIs in appropriate units (MWh, tonnes, k€)
        self.PEF_total_yearly = sum(self.PEF_total) * 1e-3  # Convert kWh to MWh
        self.PEF_nren_yearly = sum(self.PEF_nren) * 1e-3  # Convert kWh to MWh
        self.PEF_ren_yearly = sum(self.PEF_ren) * 1e-3  # Convert kWh to MWh
        self.co2_yearly = sum(self.co2) * 1e-6  # Convert grams to tonnes
        self.non_h_costs_yearly = sum(self.non_h_costs) * 1e-3  # Convert € to k€
        self.household_costs_yearly = sum(self.household_costs) * 1e-3  # Convert € to k€

    def calculate_monthly(self, hourly_data):
        """
        Calculate monthly data from hourly data. Based on the assumption of non-leap year.
        :param hourly_data: Array of hourly data (8760 values)
        :return: Monthly data (12 values)
        """
        hours_per_month = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
        monthly_data = []
        start = 0
        for hours in hours_per_month:
            monthly_data.append(sum(hourly_data[start:start + hours]))
            start += hours
        return monthly_data

    def to_dict(self):
        """
        Return the KPIs as a dictionary, including hourly, monthly, and yearly values.
        """

        return {
            "energy_carrier_name":self.energy_carrier_name,
            "energy_carrier_id": self.energy_carrier_id,
            "PEF_total_hourly": self.PEF_total.tolist(),
            "PEF_total_monthly": self.PEF_total_monthly,
            "PEF_total_yearly": self.PEF_total_yearly,
            "PEF_nren_hourly": self.PEF_nren.tolist(),
            "PEF_nren_monthly": self.PEF_nren_monthly,
            "PEF_nren_yearly": self.PEF_nren_yearly,
            "PEF_ren_hourly": self.PEF_ren.tolist(),
            "PEF_ren_monthly": self.PEF_ren_monthly,
            "PEF_ren_yearly": self.PEF_ren_yearly,
            "co2_hourly": self.co2.tolist(),
            "co2_monthly": self.co2_monthly,
            "co2_yearly": self.co2_yearly,
            "non_h_costs_hourly": self.non_h_costs.tolist(),
            "non_h_costs_monthly": self.non_h_costs_monthly,
            "non_h_costs_yearly": self.non_h_costs_yearly,
            "household_costs_hourly": self.household_costs.tolist(),
            "household_costs_monthly": self.household_costs_monthly,
            "household_costs_yearly": self.household_costs_yearly
        }
