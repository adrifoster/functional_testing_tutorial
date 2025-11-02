"""Holds concrete fire weather class using Nesterov Index"""

import numpy as np
from fire_model.fire_weather_class import FireWeather

# constants
DEWPOINT_A = 17.62  # dewpoint temperature constant a
DEWPOINT_B = 243.12  # dewpoint temperature constant b


class NesterovFireWeather(FireWeather):
    """Concrete fire weather class using a Nesterov index calculation."""

    MIN_PRECIP_THRESH = (
        3.0  # threshold for precipitation above which to zero NI [mm/day]
    )

    def __init__(self) -> None:
        """init method"""
        super().__init__()
        self.fire_weather_index = 0.0

    def update_index(self, temp_c: float, precip: float, rh: float) -> None:
        """Updates Nesterov Index

        Args:
            temp_c (float): daily averaged temperature [degrees C]
            precip (float): daily precipitation [mm]
            rh (float): daily relative humidity [%]
        """
        rh_clamped = np.clip(rh, 0.0, 100.0)

        if precip > self.MIN_PRECIP_THRESH:
            self.fire_weather_index = 0.0
        else:
            t_dew = self.dewpoint(temp_c, rh_clamped)
            self.fire_weather_index += self.calc_nesterov_index(temp_c, t_dew)

    @staticmethod
    def dewpoint(tempc: float, rh: float) -> float:
        """Calculates dewpoint from input air temperature and relative humidity
        Uses Equation 8 from Lawrence 2005, https://doi.org/10.1175/BAMS-86-2-225

        Args:
            tempc (float): air temperature [degrees C]
            rh (float): relative humidity [%]

        Returns:
            float: dewpoint temperature [degrees C]
        """

        yipsolon = np.log(max(1.0, rh) / 100.0) + (DEWPOINT_A * tempc) / (
            DEWPOINT_B + tempc
        )
        return (DEWPOINT_B * yipsolon) / (DEWPOINT_A - yipsolon)

    @staticmethod
    def calc_nesterov_index(tempc: float, tdew: float) -> float:
        """Calculates current day's Nesterov Index for given input values

        Args:
            tempC (float): daily averaged temperature [degrees C]
            tdew (float): daily dewpoint temperature [degrees C]

        Returns:
            float: Nesterov Index (>=0)
        """

        nesterov_index = (tempc - tdew) * tempc
        return max(0.0, nesterov_index)
