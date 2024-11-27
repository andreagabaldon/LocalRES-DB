# Dummy data example

## About 
This is an example of a context created in the LocalRES Planning tool using City Energy Analyst. The following items explain how it was obtained
#### City Energy Analyst software
The City Energy Analyst (CEA) is an open-source tool designed to support the planning and optimization of urban energy systems. Developed for use by urban planners, architects, and engineers, it provides a suite of tools to analyze and improve energy efficiency and sustainability in cities. CEA enables users to simulate energy demand for heating, cooling, and electricity in buildings, assess renewable energy potential, and optimize district energy systems and their economic performance. By integrating spatial data, building physics, and advanced analytics, it facilitates informed decision-making for reducing energy consumption, lowering greenhouse gas emissions, and enhancing the overall energy resilience of urban areas.

Visit their [project page](https://www.cityenergyanalyst.com/)

#### Data inputs to city Energy Analyst
User-defined standards are set:

| STANDARD    | Description        | YEAR_START | YEAR_END |
|-------------|--------------------|------------|----------|
| Before1945  | From 1000 to 1945  | 1000       | 1945     |
| Before1969  | From 1946 to 1969  | 1946       | 1969     |
| Before1979  | From 1970 to 1979  | 1970       | 1979     |
| Before1989  | From 1980 to 1989  | 1980       | 1989     |
| Before1999  | From 1990 to 1999  | 1990       | 1999     |
| Before2010  | From 2000 to 2010  | 2000       | 2010     |
| Post2010    | From 2011 to 2023  | 2011       | 2023     |

For example for the envelope assemblies the following values are set:

| STANDARD    | type_cons        | type_leak       | type_win   | type_roof | type_part | type_wall | type_floor | type_base  | type_shade   | Es   | Hs_ag | Hs_bg | Ns   | void_deck | wwr_north | wwr_south | wwr_east | wwr_west |
|-------------|------------------|-----------------|-----------|-----------|-----------|-----------|------------|------------|--------------|-------|-------|-------|-------|-----------|-----------|-----------|----------|----------|
| Before1945  | CONSTRUCTION_AS2 | TIGHTNESS_AS3   | WINDOW_AS2| ROOF45    | WALL_I_45 | WALL_E_45 | FLOOR_I_45 | FLOOR_B_45 | SHADING_AS3  | 0.82  | 0.82  | 0     | 0.82  | 0         | 0.15      | 0.15      | 0.15     | 0.15     |
| Before1969  | CONSTRUCTION_AS2 | TIGHTNESS_AS3   | WINDOW_AS2| ROOF69    | WALL_I_69 | WALL_E_69 | FLOOR_I_69 | FLOOR_B_69 | SHADING_AS3  | 0.82  | 0.82  | 0     | 0.82  | 0         | 0.15      | 0.15      | 0.15     | 0.15     |
| Before1979  | CONSTRUCTION_AS2 | TIGHTNESS_AS3   | WINDOW_AS2| ROOF79    | WALL_I_79 | WALL_E_79 | FLOOR_I_79 | FLOOR_B_79 | SHADING_AS3  | 0.82  | 0.82  | 0     | 0.82  | 0         | 0.15      | 0.15      | 0.15     | 0.15     |
| Before1989  | CONSTRUCTION_AS2 | TIGHTNESS_AS2   | WINDOW_AS2| ROOF89    | WALL_I_89 | WALL_E_89 | FLOOR_I_89 | FLOOR_B_89 | SHADING_AS3  | 0.82  | 0.82  | 0     | 0.82  | 0         | 0.15      | 0.15      | 0.15     | 0.15     |
| Before1999  | CONSTRUCTION_AS2 | TIGHTNESS_AS2   | WINDOW_AS2| ROOF99    | WALL_I_99 | WALL_E_99 | FLOOR_I_99 | FLOOR_B_99 | SHADING_AS2  | 0.82  | 0.82  | 0     | 0.82  | 0         | 0.15      | 0.15      | 0.15     | 0.15     |
| Before2010  | CONSTRUCTION_AS2 | TIGHTNESS_AS2   | WINDOW_AS2| ROOF10    | WALL_I_10 | WALL_E_10 | FLOOR_I_10 | FLOOR_B_10 | SHADING_AS2  | 0.82  | 0.82  | 0     | 0.82  | 0         | 0.15      | 0.15      | 0.15     | 0.15     |
| Post2010    | CONSTRUCTION_AS2 | TIGHTNESS_AS2   | WINDOW_AS2| ROOF11    | WALL_I_11 | WALL_E_11 | FLOOR_I_11 | FLOOR_B_11 | SHADING_AS2  | 0.82  | 0.82  | 0     | 0.82  | 0         | 0.15      | 0.15      | 0.15     | 0.15     |

They are based on the construction year and construction code standards from Spain.

For each building a user defined standard is set, as well as usage (which will set default schedules), height, or number of floors-  

- Building B01:
  - height agove ground (height_ag): 3
  - floors above ground (floors_ag):1
  - construction: 1986, standard user defined 'before 1989'
  - usage: restaurant
- Building B02: 
  - height agove ground (height_ag): 12
  - floors above ground (floors_ag):2
  - construction: 1986, standard user defined 'before 1989'
  - usage: gym
- Building B03:
  - height agove ground (height_ag): 12
  - floors above ground (floors_ag):2
  - construction: 1817, standard user defined 'before 1945'
  - usage: office
- Building B04:
  - height agove ground (height_ag): 12
  - floors above ground (floors_ag):2
  - construction: 1890, standard user defined 'before 1945'
  - usage: library
This is an example created with CEA. Further developments have been made for the generation of demand estimation with our own tools (ThermaGrid API). More information is included in the RESbased_Scenario_generator module.

## Database structure

The database structure is the following: 

## License
License: GNU GPLv3  
The GNU General Public License is a free, copyleft license for software and other kinds of works.
GNU General Public License Version 3

You may copy, distribute and modify the software as long as you track changes/dates in source files. Any modifications to or software including (via compiler) GPL-licensed code must also be made available under the GPL along with build & install instructions. This means, you must:

- Include original
- State Changes
- Disclose source
- Include the same license -- to make sure it remains free software for all its users.
- Include copyright
- Include install instructions

You cannot: sublicense or hold liable.

## Disclaimer
The content of this repository reflects only the authors' view and the European Union is not responsible for any use that may be made of the information it contains. The LocalRES consortium does not guarantee the accuracy of the data included in this repository and is not responsible for any third-party use of its contents. 
