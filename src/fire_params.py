"""Parameters for fire methods"""

from dataclasses import dataclass
import yaml
import numpy as np
from fuel_types import NUM_FUEL_CLASSES, NUM_CWD_CLASSES


@dataclass
class FireParams:
    """Encapsulate the parameter arrays and scalars"""

    bulk_density: np.ndarray
    sav: np.ndarray
    min_moisture: np.ndarray
    mid_moisture: np.ndarray
    mid_moisture_coeff: np.ndarray
    mid_moisture_slope: np.ndarray
    low_moisture_coeff: np.ndarray
    low_moisture_slope: np.ndarray
    cwd_frac: np.ndarray
    miner_total: float
    mineral_dampening: float
    fuel_energy: float
    max_duration: float
    duration_slope: float
    metadata: dict | None = None  # optional metadata

    @classmethod
    def zeros(cls) -> "FireParams":
        """Zeroes all arrays for the parameter class

        Returns:
            FireParams: FireParams with all zeros
        """
        z1 = np.zeros(NUM_FUEL_CLASSES, dtype=float)
        z2 = np.zeros(NUM_CWD_CLASSES, dtype=float)
        return cls(
            bulk_density=z1.copy(),
            sav=z1.copy(),
            min_moisture=z1.copy(),
            mid_moisture=z1.copy(),
            mid_moisture_coeff=z1.copy(),
            mid_moisture_slope=z1.copy(),
            low_moisture_coeff=z1.copy(),
            low_moisture_slope=z1.copy(),
            cwd_frac=z2.copy(),
            miner_total=0.0,
            mineral_dampening=0.0,
            fuel_energy=0.0,
            max_duration=0.0,
            duration_slope=0.0,
        )

    @classmethod
    def from_yaml(cls, path: str) -> "FireParams":
        """Load FireParams with metadata from a YAML file.

        Args:
            path (str): path to YAML file

        Returns:
            FireParams: FireParams
        """
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        def extract_array(key):
            entry = data[key]
            return (
                np.array(entry["value"], dtype=float)
                if isinstance(entry["value"], list)
                else float(entry["value"])
            )

        meta = {
            k: {kk: vv for kk, vv in v.items() if kk != "value"}
            for k, v in data.items()
        }

        return cls(
            bulk_density=extract_array("bulk_density"),
            sav=extract_array("sav"),
            min_moisture=extract_array("min_moisture"),
            mid_moisture=extract_array("mid_moisture"),
            mid_moisture_coeff=extract_array("mid_moisture_coeff"),
            mid_moisture_slope=extract_array("mid_moisture_slope"),
            low_moisture_coeff=extract_array("low_moisture_coeff"),
            low_moisture_slope=extract_array("low_moisture_slope"),
            miner_total=extract_array("miner_total"),
            cwd_frac=extract_array("cwd_frac"),
            mineral_dampening=extract_array("mineral_dampening"),
            fuel_energy=extract_array("fuel_energy"),
            max_duration=extract_array("max_duration"),
            duration_slope=extract_array("duration_slope"),
            metadata=meta,
        )

    def describe(self):
        """Print a summary table of parameters with metadata."""
        print(f"{'Parameter':<20} {'Value':<20} {'Units':<10} {'Description'}")
        print("-" * 70)
        for key, val in self.metadata.items():
            value = getattr(self, key)
            units = val.get("units", "")
            desc = val.get("description", "")
            print(f"{key:<20} {str(value):<20} {units:<10} {desc}")
