"""Helper functions for testing code"""

import pandas as pd
import numpy as np
from fire_model.fuel_class import Fuel
from fire_model.testing.synthetic_fuel_models import FuelModelsArray


def read_weather_data(
    file_path: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Reads in weahter data

    Args:
        file_path (str): full path to file

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: temperature,
        precipitation, relative humidity, wind
    """
    weather_data = pd.read_csv(file_path, index_col=[0])
    return (
        weather_data.temp_degC,
        weather_data.precip,
        weather_data.RH,
        weather_data.wind,
    )


def initialize_from_synthetic(
    fuel: Fuel, fuel_models_array: FuelModelsArray, fuel_model_index: int
) -> Fuel:
    """Initialize a Fuel objecting using an input synthetic fuel model

    Args:
        fuel (Fuel): fuel instance
        fuel_models_array (FuelModelsArray): input synthetic fule models array
        fuel_model_index (int): synthetic fuel model index

    Returns:
        Fuel: updated fuel object
    """

    # get fuel model position in array
    idx = fuel_models_array.fuel_model_position(fuel_model_index)

    # fuel model data
    leaf_litter = fuel_models_array.fuel_models[idx].hr1_loading
    twig_litter = fuel_models_array.fuel_models[idx].hr10_loading

    # small vs. large branches based on parameter file
    small_branch_fraction = fuel.params.cwd_frac[1] / (
        fuel.params.cwd_frac[1] + fuel.params.cwd_frac[2]
    )
    large_branch_fraction = fuel.params.cwd_frac[2] / (
        fuel.params.cwd_frac[1] + fuel.params.cwd_frac[2]
    )

    small_branch_litter = (
        fuel_models_array.fuel_models[idx].hr100_loading * small_branch_fraction
    )
    large_branch_litter = (
        fuel_models_array.fuel_models[idx].hr100_loading * large_branch_fraction
    )

    grass_litter = fuel_models_array.fuel_models[idx].live_herb_loading

    fuel.update_loading(
        leaf_litter,
        twig_litter,
        small_branch_litter,
        large_branch_litter,
        0.0,
        grass_litter,
    )

    fuel.sum_loading()
    fuel.calculate_fractional_loading()

    # calculate geometric properties
    fuel.average_bulk_density_no_trunks()
    fuel.average_sav_no_trunks()

    return fuel
