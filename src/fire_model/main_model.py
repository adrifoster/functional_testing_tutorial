"""Main methods for fire model"""

import numpy as np
from fire_model.fire_weather_class import FireWeather
from fire_model.fuel_class import Fuel
from fire_model.fire_equations import FireEquations
from fire_model.fuel_types import FuelType


def daily_fire_model(
    tempc: float,
    precip: float,
    rh: float,
    wind_speed: float,
    num_ignitions: float,
    tree_fraction: float,
    grass_fraction: float,
    bare_fraction: float,
    fdi_alpha: float,
    leaf_litter: float,
    twig_litter: float,
    small_branch_litter: float,
    large_branch_litter: float,
    trunk_litter: float,
    live_grass: float,
    max_duration: float,
    duration_slope: float,
    fuel: Fuel,
    fire_weather: FireWeather,
) -> tuple[float, float, float]:
    """Drives daily fire model

    Args:
        tempc (float): air temperature [degC]
        precip (float): precipitation [mm]
        rh (float): relative humidity [%]
        wind_speed (float): wind speed [m/min]
        num_ignitions (float): daily ignitions [count/km2/day]
        tree_fraction (float): tree fraction [0-1]
        grass_fraction (float): grass fraction [0-1]
        bare_fraction (float): bare fraction [0-1]
        fdi_alpha (float): parameter scaling weather index to fire danger index
        leaf_litter (float): leaf litter [kgC/m2]
        twig_litter (float): twig litter [kgC/m2]
        small_branch_litter (float): small branch litter [kgC/m2]
        large_branch_litter (float): large branch litter [kgC/m2]
        trunk_litter (float): trunk litter [kgC/m2]
        live_grass (float): live grass [kgC/m2]
        max_duration (float): maximum fire duration [min]
        duration_slope (float): slope of fire duration curve [unitless]
        fuel (Fuel): Fuel instance
        fire_weather (FireWeather): FireWeather instance

    Returns:
        tuple[float, float, float]: area burnt, fire intensity, rate of spread
    """

    # update fire weather for day
    update_fire_weather(
        tempc,
        precip,
        rh,
        wind_speed,
        tree_fraction,
        grass_fraction,
        bare_fraction,
        fdi_alpha,
        fire_weather,
    )

    # update fuel characteristics
    update_fuel_characteristics(
        leaf_litter,
        twig_litter,
        small_branch_litter,
        large_branch_litter,
        trunk_litter,
        live_grass,
        fuel,
        fire_weather,
    )

    # rate of spread
    ros_front, ros_back = calculate_rate_of_spread(wind_speed, fuel, fire_weather)

    # fire intensity
    fire_intensity = calculate_surface_fire_intensity(ros_front, fuel)

    # area burnt
    area_burnt = calculate_area_burnt(
        fire_weather,
        num_ignitions,
        max_duration,
        duration_slope,
        tree_fraction,
        ros_back,
        ros_front,
    )

    return area_burnt, fire_intensity, ros_front


def update_fire_weather(
    tempc: float,
    precip: float,
    rh: float,
    wind_speed: float,
    tree_fraction: float,
    grass_fraction: float,
    bare_fraction: float,
    fdi_alpha: float,
    fire_weather: FireWeather,
) -> None:
    """Update the fire weather index and calculate effective windspeed based on
    vegetation characteristics

    Args:
        tempc (float): daily averaged temperature [degrees C]
        precip (float): daily precipitation [mm]
        rh (float): daily relative humidity [%]
        wind_speed (float): wind speed [m/min]
        tree_fraction (float): tree fraction [0-1]
        grass_fraction (float): grass fraction [0-1]
        bare_fraction (float): bare ground fraction [0-1]
        fdi_alpha (float): parameter scaling weather index to fire danger index
        fire_weather (FireWeather): FireWeather class instance
    """

    # update fire weather index
    fire_weather.update_index(tempc, precip, rh)

    # update effective wind speed
    fire_weather.update_effective_windspeed(
        wind_speed, tree_fraction, grass_fraction, bare_fraction
    )

    # update fire danger
    fire_weather.update_fire_danger_index(fdi_alpha)


def update_fuel_characteristics(
    leaf_litter: float,
    twig_litter: float,
    small_branch_litter: float,
    large_branch_litter: float,
    trunk_litter: float,
    live_grass: float,
    fuel: Fuel,
    fire_weather: FireWeather,
) -> None:
    """Updates fuel characteristics

    Args:
        leaf_litter (float): leaf litter [kgC/m2]
        twig_litter (float): twig litter [kgC/m2]
        small_branch_litter (float): small branch litter [kgC/m2]
        large_branch_litter (float): large branch litter [kgC/m2]
        trunk_litter (float): trunk litter [kgC/m2]
        live_grass (float): live grasses [kgC/m2]
        fuel (Fuel): Fuel instance
        fire_weather (FireWeather): FireWeather instance
    """

    # update fuel loading [kgC/m2]
    fuel.update_loading(
        leaf_litter,
        twig_litter,
        small_branch_litter,
        large_branch_litter,
        trunk_litter,
        live_grass,
    )

    # sum up fuel classes and calculate fractional loading for each
    fuel.sum_loading()
    fuel.calculate_fractional_loading()

    # calculate fuel moisture [m3/m3]
    fuel.update_fuel_moisture(fire_weather)

    # calculate geometric properties
    fuel.average_bulk_density_no_trunks()
    fuel.average_sav_no_trunks()


def calculate_rate_of_spread(
    wind_speed: float, fuel: Fuel, fire_weather: FireWeather
) -> tuple[float, float]:
    """Calculates potential rate of spread based on fuel and fire weather characteristics

    Args:
        wind_speed (float): wind speed [m/min]
        fuel (Fuel): Fuel instance
        fire_weather (FireWeather): FireWeather instance

    Returns:
        tuple[float, float]: forward rate of spread, backwards rate of spread [m/min]
    """
    if fuel.non_trunk_loading <= 0.0:
        return 0.0, 0.0

    # fraction of fuel array volume occupied by fuel, i.e. compactness of fuel bed [unitless]
    beta = fuel.bulk_density_notrunks / fuel.params.particle_density

    # optimum packing ratio [unitless]
    beta_op = FireEquations.optimum_packing_ratio(fuel.bulk_density_notrunks)

    # relative packing ratio [unitless]
    if beta_op < 0.0:
        beta_ratio = 0.0
    else:
        beta_ratio = beta / beta_op

    # remove mineral content from fuel load per Thonicke 2010
    mineral_fuel_loading = fuel.non_trunk_loading * (1.0 - fuel.params.miner_total)

    # reaction intensity [kJ/m2/min]
    i_r = FireEquations.reaction_intensity(
        mineral_fuel_loading / 0.45,
        fuel.sav_notrunks,
        beta_ratio,
        fuel.average_moisture_notrunks,
        fuel.mef_notrunks,
        fuel.params.fuel_energy,
        fuel.params.mineral_dampening,
    )

    # heat of preignition [kJ/kg]
    q_ig = FireEquations.heat_of_preignition(fuel.average_moisture_notrunks)

    # effective heating number [unitless]
    eps = FireEquations.effective_heating_number(fuel.sav_notrunks)

    # wind factor [unitless]
    phi_wind = FireEquations.wind_factor(
        fire_weather.effective_windspeed, beta_ratio, fuel.sav_notrunks
    )

    # propagating flux [unitless]
    xi = FireEquations.propagating_flux(beta, fuel.sav_notrunks)

    # forward rate of spread [m/min]
    ros_front = FireEquations.forward_rate_of_spread(
        fuel.bulk_density_notrunks, eps, q_ig, i_r, xi, phi_wind
    )

    # backwards rate of spread [m/min]
    # backward ROS wind not changed by vegetation - so use wind, not effective_windspeed
    ros_back = FireEquations.backward_rate_of_spread(ros_front, wind_speed)

    return ros_front, ros_back


def calculate_surface_fire_intensity(rate_of_spread: float, fuel: Fuel) -> float:
    """Calculates surface fireline intensity [kW/m]

    Args:
        rate_of_spread (float): forward rate of spread [m/min]
        fuel (Fuel): Fuel instance

    Returns:
        float: surface fireline intensity [kW/m]
    """

    # calculate potential fuel burnt at current moisture level
    fuel.calculate_fraction_burnt()
    fuel_consumed = fuel.calculate_fuel_consumed()

    # sum of all minus trunks
    total_fuel_consumed_no_trunks = (
        np.sum(fuel_consumed) - fuel_consumed[FuelType.TRUNKS.value]
    )

    # fire intensity [kW/m]
    return FireEquations.fire_intensity(
        total_fuel_consumed_no_trunks / 0.45,
        rate_of_spread / 60.0,
        fuel.params.fuel_energy,
    )


def calculate_area_burnt(
    fire_weather: FireWeather,
    num_ignitions: float,
    max_duration: float,
    duration_slope: float,
    tree_fraction: float,
    ros_back: float,
    ros_front: float,
) -> float:
    """Calculates area burnt for each patch of a site

    Args:
        fire_weather (FireWeather): FireWeather instance
        num_ignitions (float): number of ignitions [count/km2/day]
        max_duration (float): maximum fire duration [min]
        duration_slope (float): slope of fire duration curve [unitless]
        tree_fraction (float): tree fraction [0-1]
        ros_back (float): rate of backwards spread [m/min]
        ros_front (float): rate of forwards spread [m/min]

    Returns:
        float: burned area m2/km2
    """

    # fire duration [min]
    fire_duration = FireEquations.fire_duration(
        fire_weather.fire_danger_index, max_duration, duration_slope
    )

    # length-to-breadth ratio of fire ellipse [unitless]
    length_to_breadth = FireEquations.length_to_breadth_ratio(
        fire_weather.effective_windspeed, tree_fraction
    )

    # fire size [m2]
    fire_size = FireEquations.fire_size(
        length_to_breadth, ros_back, ros_front, fire_duration
    )

    return FireEquations.area_burnt(
        fire_size, num_ignitions, fire_weather.fire_danger_index
    )
