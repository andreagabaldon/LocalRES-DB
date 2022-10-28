DROP TABLE IF EXISTS building_asset_context;
DROP TABLE IF EXISTS building_consumption;
DROP TABLE IF EXISTS building;
DROP TABLE IF EXISTS building_energy_asset;
DROP TABLE IF EXISTS community_energy_asset;
DROP TABLE IF EXISTS time_serie;
DROP TABLE IF EXISTS multi_time_serie;
DROP TABLE IF EXISTS node;
DROP TABLE IF EXISTS transformation_action;
DROP TABLE IF EXISTS context;
DROP TABLE IF EXISTS building_statistics_profile;
DROP TABLE IF EXISTS demand_profile;
DROP TABLE IF EXISTS building_use;
DROP TABLE IF EXISTS generation_system_profile;
DROP TABLE IF EXISTS generation_system;
DROP TABLE IF EXISTS national_energy_carrier_production;
DROP TABLE IF EXISTS energy_carrier;
DROP TABLE IF EXISTS system_type;
DROP TABLE IF EXISTS country_weather_data;
DROP TABLE IF EXISTS country_statistics;
DROP TABLE IF EXISTS country;
DROP TABLE IF EXISTS climatic_region;

-- DICTIONARIES AND STATIC DATA
CREATE TABLE climatic_region (
    id SERIAL NOT NULL CONSTRAINT climatic_region_pk PRIMARY KEY,
    name character varying NOT NULL
);

CREATE TABLE country (
    id SERIAL NOT NULL CONSTRAINT country_pk PRIMARY KEY,
    name character varying NOT NULL,
    geom geometry(GEOMETRY,4326) NOT NULL
);

CREATE TABLE country_statistics (
    id SERIAL NOT NULL CONSTRAINT country_statistics_pk PRIMARY KEY,
    country_id int NOT NULL,
    gdp_base float NOT NULL,
    gdp_growth float NOT NULL,
    population int NOT NULL,
    population_growth int NOT NULL,
    building_retrofitting_rate int NOT NULL,
    e_cars_fleet int NOT NULL,
    avg_cars_per_city int NOT NULL,
    CONSTRAINT country_statistics_country_fk 
        FOREIGN key (country_id) 
        REFERENCES country(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE country_weather_data (
    id SERIAL NOT NULL CONSTRAINT country_weather_data_pk PRIMARY KEY,
    country_id int NOT NULL,
    climatic_region_id int NOT NULL,
    hdh float[] NOT NULL,
    cdh float[] NOT NULL,
    reference_temperature_heating_in_c float NOT NULL,
    reference_temperature_cooling_in_c float NOT NULL,
    temp_ambient_air_in_c float[] NOT NULL,
    temp_mains_water_in_c float[] NOT NULL,
    temp_ground_in_c float[] NOT NULL,
    humidity_in_percent float[] NOT NULL,    
    CONSTRAINT country_weather_data_country_fk 
        FOREIGN key (country_id) 
        REFERENCES country(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT country_weather_data_climatic_region_fk 
        FOREIGN key (climatic_region_id) 
        REFERENCES climatic_region(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE system_type (
    id SERIAL NOT NULL CONSTRAINT system_type_pk PRIMARY KEY,
    name character varying NOT NULL
);

CREATE TABLE energy_carrier (
    id SERIAL NOT NULL CONSTRAINT energy_carrier_pk PRIMARY KEY,
    name character varying NOT NULL,
    final boolean NOT NULL
);

CREATE TABLE national_energy_carrier_production (
    id SERIAL NOT NULL CONSTRAINT national_energy_carrier_production_pk PRIMARY KEY,
    energy_carrier_id int NOT NULL,
    country_id int NOT NULL,
    pef_tot float NOT NULL,
    pef_nren float NOT NULL,
    pef_ren float NOT NULL,
    hourly_price float NOT NULL,
    co2_equiv_content float NOT NULL,
    CONSTRAINT national_energy_carrier_production_energy_carrier_fk 
        FOREIGN key (energy_carrier_id) 
        REFERENCES energy_carrier(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT national_energy_carrier_production_country_fk 
        FOREIGN key (country_id) 
        REFERENCES country(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE generation_system (
    id SERIAL NOT NULL CONSTRAINT generation_system_pk PRIMARY KEY,
    name character varying NOT NULL,
    fuel_yield float NOT NULL,
    energy_carrier_input_1_id int NULL,
    energy_carrier_input_2_id int NULL,
    energy_carrier_output_1_id int NULL,
    energy_carrier_output_2_id int NULL,  
    CONSTRAINT generation_system_energy_carrier_energy_carrier_input_1_fk 
        FOREIGN key (energy_carrier_input_1_id) 
        REFERENCES energy_carrier(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT generation_system_energy_carrier_energy_carrier_input_2_fk 
        FOREIGN key (energy_carrier_input_2_id) 
        REFERENCES energy_carrier(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT generation_system_energy_carrier_energy_carrier_output_1_fk 
        FOREIGN key (energy_carrier_output_1_id) 
        REFERENCES energy_carrier(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT generation_system_energy_carrier_energy_carrier_output_2_fk 
        FOREIGN key (energy_carrier_output_2_id) 
        REFERENCES energy_carrier(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE generation_system_profile (
    id SERIAL NOT NULL CONSTRAINT generation_system_profile_pk PRIMARY KEY,
    electricity_system_id int NOT NULL,
    heating_system_id int NOT NULL,
    cooling_system_id int NOT NULL,
    dhw_system_id int NOT NULL,    
    CONSTRAINT generation_system_profile_electricity_system_fk 
        FOREIGN key (electricity_system_id) 
        REFERENCES generation_system(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT generation_system_profile_heating_system_fk 
        FOREIGN key (heating_system_id) 
        REFERENCES generation_system(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT generation_system_profile_cooling_system_fk
        FOREIGN key (cooling_system_id) 
        REFERENCES generation_system(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT generation_system_profile_dhw_system_fk 
        FOREIGN key (dhw_system_id) 
        REFERENCES generation_system(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE building_use (
    id SERIAL NOT NULL CONSTRAINT building_use_pk PRIMARY KEY,
    name character varying NOT NULL
);

CREATE TABLE demand_profile (
    id SERIAL NOT NULL CONSTRAINT demand_profile_pk PRIMARY KEY,
    electricity_demand float[] NOT NULL,
    heating_demand float[] NOT NULL,
    cooling_demand float[] NOT NULL,
    dhw_demand float[] NOT NULL  
);

CREATE TABLE building_statistics_profile (
    id SERIAL NOT NULL CONSTRAINT building_statistics_profile_pk PRIMARY KEY,
    building_use_id int NOT NULL,
    demand_profile_id int NOT NULL,
    generation_system_profile_id int NULL,
    country_id int NOT NULL,
    construction_min_year int NULL,
    construction_max_year int NULL,
    CONSTRAINT building_statistics_profile_building_use_fk
        FOREIGN key (building_use_id) 
        REFERENCES building_use(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT building_statistics_profile_demand_profile_fk
        FOREIGN key (demand_profile_id) 
        REFERENCES demand_profile(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT building_statistics_profile_generation_system_profile_fk
        FOREIGN key (generation_system_profile_id) 
        REFERENCES generation_system_profile(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT building_statistics_profile_country_fk
        FOREIGN key (country_id) 
        REFERENCES country(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- END DICTIONARIES AND STATIC DATA


CREATE TABLE context (
    id SERIAL NOT NULL CONSTRAINT context_pk PRIMARY KEY,
    context_parent int NULL,
    name character varying NOT NULL,
    start_date date NOT NULL,
    timestep_count int NOT NULL,
    timestep_duration int NOT NULL,
    author character varying NOT NULL,
    creation_date date NOT NULL,
    description character varying NOT NULL,
    CONSTRAINT context_context_fk 
        FOREIGN key (context_parent) 
        REFERENCES context(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION   
);

CREATE TABLE transformation_action (
    id SERIAL NOT NULL CONSTRAINT transformation_action_pk PRIMARY KEY,
    context_id int,
    param1 float NOT NULL,
    param2 float NOT NULL,
    param3 float NOT NULL,
    param4 float NOT NULL,
    param5 float NOT NULL,    
    CONSTRAINT transformation_action_context_fk 
        FOREIGN key (context_id) 
        REFERENCES context(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE node (
    id SERIAL NOT NULL CONSTRAINT node_pk PRIMARY KEY,
    context_id int,
    name character varying NOT NULL,
    geom geometry(POINT,4326) NOT NULL,
    CONSTRAINT node_context_fk 
        FOREIGN key (context_id) 
        REFERENCES context(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE multi_time_serie (
    id SERIAL NOT NULL CONSTRAINT multi_time_serie_pk PRIMARY KEY,
    name character varying NOT NULL
);

CREATE TABLE time_serie (
    id SERIAL NOT NULL CONSTRAINT time_serie_pk PRIMARY KEY,
    multi_time_serie_id int NOT NULL,
    value float[] NOT NULL,
    testcase character varying NOT NULL,
    CONSTRAINT time_serie_multi_time_serie_fk
        FOREIGN key (multi_time_serie_id) 
        REFERENCES multi_time_serie(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE community_energy_asset (
    id SERIAL NOT NULL CONSTRAINT community_energy_asset_pk PRIMARY KEY,
    availability_ts_id int NOT NULL,
    input_node_id int NOT NULL,
    output_node_id int NULL,
    generation_system_id int NOT NULL,
    pmax_scalar float NOT NULL,
    pmaxmin_scalar float NOT NULL,
    pmaxmax_scalar float NOT NULL,    
    CONSTRAINT community_energy_asset_multi_time_serie_fk
        FOREIGN key (availability_ts_id) 
        REFERENCES multi_time_serie(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT community_energy_asset_input_node_fk
        FOREIGN key (input_node_id) 
        REFERENCES node(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT community_energy_asset_output_node_fk
        FOREIGN key (output_node_id) 
        REFERENCES node(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT community_energy_asset_generation_system_fk
        FOREIGN key (generation_system_id) 
        REFERENCES generation_system(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE building_energy_asset (
    id SERIAL NOT NULL CONSTRAINT building_energy_asset_pk PRIMARY KEY,
    availability_ts_id int NOT NULL,
    generation_system_id int NOT NULL,
    pmax_scalar float NOT NULL,
    pmaxmin_scalar float NOT NULL,
    pmaxmax_scalar float NOT NULL,    
    CONSTRAINT building_energy_asset_multi_time_serie_fk
        FOREIGN key (availability_ts_id) 
        REFERENCES multi_time_serie(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT building_energy_asset_generation_system_fk
        FOREIGN key (generation_system_id) 
        REFERENCES generation_system(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE building (
    id SERIAL NOT NULL CONSTRAINT building_pk PRIMARY KEY,
    geom geometry(GEOMETRY,4326) NOT NULL,
    area float NOT NULL,
    height float NOT NULL,
    building_statistics_profile_id int NULL,
    CONSTRAINT building_building_statistics_profile_fk
        FOREIGN key (building_statistics_profile_id) 
        REFERENCES building_statistics_profile(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE building_consumption (
    id SERIAL NOT NULL CONSTRAINT building_consumption_pk PRIMARY KEY,
    elec_consumption float[],
    heat_consumption float[],
    cool_consumption float[],
    dhw_consumption float[]
);

CREATE TABLE building_asset_context (
    id SERIAL NOT NULL CONSTRAINT building_asset_context_pk PRIMARY KEY,
    context_id int NULL,
    building_consumption_id int NOT NULL,
    generation_system_profile_id int NOT NULL,
    building_id int NOT NULL,
    building_energy_asset_id int NOT NULL,
    CONSTRAINT building_asset_context_context_fk 
        FOREIGN key (context_id) 
        REFERENCES context(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT building_asset_context_building_consumption_fk 
        FOREIGN key (building_consumption_id) 
        REFERENCES building_consumption(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT building_asset_context_generation_system_profile_fk
        FOREIGN key (generation_system_profile_id) 
        REFERENCES generation_system_profile(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT building_asset_context_building_fk
        FOREIGN key (building_id) 
        REFERENCES building(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT building_asset_context_building_energy_asset_fk
        FOREIGN key (building_energy_asset_id) 
        REFERENCES building_energy_asset(id) 
        ON UPDATE NO ACTION ON DELETE NO ACTION
);
