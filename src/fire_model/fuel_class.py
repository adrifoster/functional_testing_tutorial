"""Fuel class"""

import numpy as np
from fire_model.fire_weather_class import FireWeather
from fire_model.nesterov_fire_weather import NesterovFireWeather
from fire_model.fuel_types import NUM_FUEL_CLASSES, FuelType
from fire_model.fire_params import FireParams


class Fuel:
    """
    Holds arrays for loading, effective moisture, fractional loading and burnt fractions,
    as well as computed aggregate properties for non-trunk fuel classes.
    """

    def __init__(self, params: FireParams) -> None:
        self.params = params
        self.loading = np.zeros(NUM_FUEL_CLASSES, dtype=float)
        self.effective_moisture = np.zeros(NUM_FUEL_CLASSES, dtype=float)
        self.frac_loading = np.zeros(NUM_FUEL_CLASSES, dtype=float)
        self.frac_burnt = np.zeros(NUM_FUEL_CLASSES, dtype=float)
        self.non_trunk_loading = 0.0
        self.average_moisture_notrunks = 0.0
        self.bulk_density_notrunks = 0.0
        self.sav_notrunks = 0.0
        self.mef_notrunks = 0.0

    def update_loading(
        self,
        leaf_litter: float,
        twig_litter: float,
        small_branch_litter: float,
        large_branch_litter: float,
        trunk_litter: float,
        live_grass: float,
    ) -> None:
        """
        Set loading for each fuel type from inputs.
        """
        self.loading[FuelType.DEAD_LEAVES.value] = float(leaf_litter)
        self.loading[FuelType.TWIGS.value] = float(twig_litter)
        self.loading[FuelType.SMALL_BRANCHES.value] = float(small_branch_litter)
        self.loading[FuelType.LARGE_BRANCHES.value] = float(large_branch_litter)
        self.loading[FuelType.LIVE_GRASS.value] = float(live_grass)
        self.loading[FuelType.TRUNKS.value] = float(trunk_litter)

    def sum_loading(self) -> None:
        """Compute non_trunk_loading (sum of all fuel loadings except trunks)."""
        mask = np.ones(NUM_FUEL_CLASSES, dtype=bool)
        mask[FuelType.TRUNKS.value] = False
        self.non_trunk_loading = float(np.sum(self.loading[mask]))

    def calculate_fractional_loading(self) -> None:
        """
        Calculate frac_loading for each fuel class excluding trunks,
        normalized by non_trunk_loading. If non_trunk_loading is ~0, zero everything.
        """
        self.sum_loading()
        if self.non_trunk_loading > 0.0:
            mask = np.ones(NUM_FUEL_CLASSES, dtype=bool)
            mask[FuelType.TRUNKS.value] = False
            self.frac_loading[:] = 0.0
            self.frac_loading[mask] = self.loading[mask] / self.non_trunk_loading
            self.frac_loading[~mask] = 0.0
        else:
            self.frac_loading.fill(0.0)
            self.non_trunk_loading = 0.0

    def update_fuel_moisture(
        self,
        sav_fuel: np.ndarray,
        drying_ratio: float,
        fire_weather: FireWeather,
    ) -> None:
        """
        Update fuel moisture using the provided fire weather strategy object.
        """
        total_loading = self.non_trunk_loading + self.loading[FuelType.TRUNKS.value]
        if total_loading > 0.0:

            moisture = self.compute_moisture(sav_fuel, drying_ratio, fire_weather)
            # moisture_of_extinction per class and effective_moisture = moisture / MEF
            moisture_of_extinction = np.array(
                [self.moisture_of_extinction(s) for s in sav_fuel], dtype=float
            )
            # protect division by zero of MEF (shouldn't happen for sav>0)
            self.effective_moisture = moisture / moisture_of_extinction

            # compute weighted averages excluding trunks
            self.average_moisture_notrunks = 0.0
            self.mef_notrunks = 0.0
            for i in range(NUM_FUEL_CLASSES):
                if (i + 1) != FuelType.TRUNKS.value:
                    self.average_moisture_notrunks += self.frac_loading[i] * moisture[i]
                    self.mef_notrunks += (
                        self.frac_loading[i] * moisture_of_extinction[i]
                    )
        else:
            self.effective_moisture.fill(0.0)
            self.average_moisture_notrunks = 0.0
            self.mef_notrunks = 0.0

    def compute_moisture(
        self, sav_fuel: np.ndarray, drying_ratio: float, fire_weather
    ) -> np.ndarray:
        """
        Compute fuel moisture based on fire weather type.

        Args:
            sav_fuel (np.ndarray): surface area to volume ratio of all fuel classes
            drying_ratio (float): drying ratio
            fire_weather: a FireWeather instance providing fire_weather_index
        Returns:
            np.ndarray: fuel moisture for all classes
        """
        if isinstance(fire_weather, NesterovFireWeather):
            return self._compute_moisture_nesterov(
                sav_fuel, drying_ratio, fire_weather.fire_weather_index
            )
        else:
            raise NotImplementedError(
                f"Moisture computation not implemented for {type(fire_weather)}"
            )

    def _compute_moisture_nesterov(
        self, sav_fuel: np.ndarray, drying_ratio: float, NI: float
    ) -> np.ndarray:
        """Compute fuel moisture using the Nesterov Index."""
        moisture = np.zeros_like(sav_fuel)

        for i in range(len(sav_fuel)):
            if i == FuelType.LIVE_GRASS.value:
                alpha_FMC = sav_fuel[FuelType.TWIGS.value] / drying_ratio
            else:
                alpha_FMC = sav_fuel[i] / drying_ratio
            moisture[i] = np.exp(-alpha_FMC * NI)

        self.effective_moisture[:] = moisture
        return moisture

    @staticmethod
    def moisture_of_extinction(sav: float) -> float:
        """Calculates moisture of extinction based on input surface area to volume ratio

        MEF (moisure of extinction) depends on compactness of fuel, depth, particle size,
        wind, and slope

        Equation here is Eq. 27 from Peterson and Ryan (1986) "Modeling Postfire Conifer
        Mortality for Long-Range Planning"

        Args:
            sav (float): fuel surface area to volume ratio [/cm]

        Returns:
            float: moisture of extinction [m3/m3]
        """

        # constants
        MEF_a = 0.524
        MEF_b = 0.066
        return MEF_a - MEF_b * np.log(sav)

    def average_bulk_density_no_trunks(self) -> None:
        """Calculate average bulk density excluding trunks. If non_trunk_loading ~ 0,
        fall back to simple mean of bulk_density
        """
        bd = self.params.bulk_density
        if self.non_trunk_loading > 0.0:
            mask = np.ones(NUM_FUEL_CLASSES, dtype=bool)
            mask[FuelType.TRUNKS.value] = False
            self.bulk_density_notrunks = float(
                np.sum(self.frac_loading[mask] * bd[mask])
            )
        else:
            self.bulk_density_notrunks = float(np.sum(bd) / NUM_FUEL_CLASSES)

    def average_sav_no_trunks(self) -> None:
        """Calculate average SAV excluding trunks. If non_trunk_loading ~ 0,
        fall back to simple mean of bulk_density

        Args:
            sav_fuel (np.ndarray): input SAV of fuel types
        """
        sav = self.params.sav
        if self.non_trunk_loading > 0.0:
            mask = np.ones(NUM_FUEL_CLASSES, dtype=bool)
            mask[FuelType.TRUNKS.value] = False
            self.sav_notrunks = float(np.sum(self.frac_loading[mask] * sav[mask]))
        else:
            self.sav_notrunks = float(np.sum(sav) / NUM_FUEL_CLASSES)

    def calculate_fraction_burnt(self) -> None:
        """Calculates the fraction burnt for all fuel classes"""

        MAX_GRASS_FRAC = 0.8  # maximum fraction burnt for live grasses

        frac_burnt = np.zeros(NUM_FUEL_CLASSES)
        relative_moisture = self.effective_moisture

        val_low = (
            self.params.low_moisture_coeff
            - self.params.low_moisture_slope * relative_moisture
        )
        val_mid = (
            self.params.mid_moisture_coeff
            - self.params.mid_moisture_slope * relative_moisture
        )

        # masks for four regimes
        dry_mask = relative_moisture <= self.params.min_moisture
        low_mask = (relative_moisture > self.params.min_moisture) & (
            relative_moisture <= self.params.mid_moisture
        )
        mid_mask = (relative_moisture > self.params.mid_moisture) & (
            relative_moisture <= 1.0
        )

        # very dry
        frac_burnt[dry_mask] = 1.0
        frac_burnt[low_mask] = np.clip(val_low[low_mask], 0.0, 1.0)
        frac_burnt[mid_mask] = np.clip(val_mid[mid_mask], 0.0, 1.0)

        # grass limitation
        live_idx = FuelType.LIVE_GRASS.value
        frac_burnt[live_idx] = min(MAX_GRASS_FRAC, frac_burnt[live_idx])

        # mineral reduction
        frac_burnt *= 1.0 - self.params.miner_total

        self.frac_burnt = frac_burnt

    def calculate_fuel_consumed(self) -> np.ndarray:
        """Calculates fuel consumed [kgC/m2]

        Returns:
            np.ndarray: fuel consumed [kgC/m2]
        """
        return self.frac_burnt * self.loading

    def calculate_residence_time(self) -> float:
        """Compute fireline residence time (tau_l) in minutes, capped"""
        MAX_RESIDENCE_TIME = 8.0  # minutes

        # boolean mask to exclude trunks
        mask = np.arange(NUM_FUEL_CLASSES) != FuelType.TRUNKS.value

        # compute term only for non-trunks
        term = (
            39.4
            / 0.45
            / 10.0  # kgC/m2 to g/cm2
            * (self.frac_loading[mask] * self.non_trunk_loading)
            * (1.0 - np.sqrt(1.0 - self.frac_burnt[mask]))
        )

        tau_l = np.sum(term)

        # cap at maximum residence time
        return min(MAX_RESIDENCE_TIME, tau_l)
