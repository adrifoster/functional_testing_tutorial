"""Base FireWeather class."""

from abc import ABC, abstractmethod


class FireWeather(ABC):
    """
    Abstract base class representing fire weather conditions.

    Attributes
    ----------
    fire_weather_index : float
        Fire weather index (e.g., indicator of fire danger).
    effective_windspeed : float
        Effective wind speed [m/min], adjusted for vegetation cover.
    """

    # class constants for wind attenuation
    WIND_ATTEN_TREED = 0.4
    WIND_ATTEN_GRASS = 0.6

    def __init__(self) -> None:
        """class init method"""
        self.fire_weather_index: float = 0.0
        self.effective_windspeed: float = 0.0

    @abstractmethod
    def update_index(self, temp_c: float, precip: float, rh: float) -> None:
        """Update fire weather index (to be implemented by subclasses)."""

    def update_effective_windspeed(
        self,
        wind_speed: float,
        tree_fraction: float,
        grass_fraction: float,
        bare_fraction: float,
    ) -> None:
        """Calculate effective wind speed corrected for vegetation cover.

        Args:
            wind_speed (float): wind speed [m/min]
            tree_fraction (float): tree fraction [0-1]
            grass_fraction (float): grass fraction [0-1]
            bare_fraction (float): bare ground fraction [0-1]
        """
        self.effective_windspeed = wind_speed * (
            tree_fraction * self.WIND_ATTEN_TREED
            + (grass_fraction + bare_fraction) * self.WIND_ATTEN_GRASS
        )
