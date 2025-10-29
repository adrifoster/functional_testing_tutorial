import os
import numpy as np
import pandas as pd
from fuel_class import Fuel
from nesterov_fire_weather import NesterovFireWeather
from fire_params import FireParams
from testing.synthetic_fuel_models import FuelModelsArray
from testing.testing_shr import *
    
def main():
    
    # weather data file
    data_file = os.path.join('~/Documents/04_Code/functional_testing_tutorial/data/weather_data.csv')
    
    # get fire parameters
    params = FireParams.from_yaml("../parameter_files/fire_parameters.yaml")
    
    # initialize synthetic fuel data
    fuel_models = [102, 183, 164, 104, 163]
    
    all_synthetic_fuels = FuelModelsArray()
    fuels = []
    for fuel_model in fuel_models:
        
        # initialize fuel
        fuel = Fuel(params)
        fuel = initialize_from_synthetic(fuel, all_synthetic_fuels, fuel_model)
        
        # sum up fuel and calculate loading
        fuel.sum_loading()
        fuel.calculate_fractional_loading()
        
        # calculate geometric properties
        fuel.average_bulk_density_no_trunks()
        fuel.average_sav_no_trunks()
        
        # save to array
        fuels.append(fuel)
    
    # read in weather data
    tempC, precip, rh, wind = read_weather_data(data_file)
    
    # set up fire weather class
    fire_weather = NesterovFireWeather()    
    
    n_days = len(tempC)
    nesterov_index = []
    for i in range(n_days):
        fire_weather.update_index(tempC[i], precip[i], rh[i])
        nesterov_index.append(fire_weather.fire_weather_index)
        
if __name__ == "__main__":
    main()
