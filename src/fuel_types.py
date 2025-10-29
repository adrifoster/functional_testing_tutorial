"""Fuel types class"""

from enum import Enum, unique


@unique
class FuelType(Enum):
    """Enumeration of available fuel classes."""

    TWIGS = 0
    SMALL_BRANCHES = 1
    LARGE_BRANCHES = 2
    TRUNKS = 3
    DEAD_LEAVES = 4
    LIVE_GRASS = 5


NUM_FUEL_CLASSES = len(FuelType)
NUM_CWD_CLASSES = NUM_FUEL_CLASSES - 2
