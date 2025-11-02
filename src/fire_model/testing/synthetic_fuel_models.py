"""Synthetic fuel model definitions"""

from dataclasses import dataclass, field
from typing import List, Optional

# constants
USTONS_TO_KG = 907.185
ACRES_TO_M2 = 4046.86
USTONS_ACRE_TO_KGC_M2 = USTONS_TO_KG / ACRES_TO_M2 * 0.45
FT_TO_M = 0.3048


@dataclass
class SyntheticFuelModel:
    """Holds values for synthetic fuel models from Scott & Burgan 2005"""

    fuel_model_index: int
    carrier: str
    fuel_model_name: str = ""
    wind_adj_factor: float = 0.0
    hr1_loading: float = 0.0
    hr10_loading: float = 0.0
    hr100_loading: float = 0.0
    live_herb_loading: float = 0.0
    live_woody_loading: float = 0.0
    fuel_depth: float = 0.0

    def __post_init__(self):
        self.hr1_loading *= USTONS_ACRE_TO_KGC_M2
        self.hr10_loading *= USTONS_ACRE_TO_KGC_M2
        self.hr100_loading *= USTONS_ACRE_TO_KGC_M2
        self.live_herb_loading *= USTONS_ACRE_TO_KGC_M2
        self.live_woody_loading *= USTONS_ACRE_TO_KGC_M2
        self.fuel_depth *= FT_TO_M


HARD_CODED_FUEL_MODELS = [
    (1, "GR", "short grass", 0.36, 0.7, 0.0, 0.0, 0.0, 0.0, 1.0),
    (2, "GR", "timber and grass understory", 0.36, 2.0, 1.0, 0.5, 0.5, 0.0, 1.0),
    (3, "GR", "tall grass", 0.44, 3.0, 0.0, 0.0, 0.0, 0.0, 2.5),
    (4, "SH", "chapparal", 0.55, 5.0, 4.0, 2.0, 0.0, 5.0, 6.0),
    (5, "SH", "brush", 0.42, 1.0, 0.5, 0.0, 0.0, 2.0, 2.0),
    (6, "SH", "dormant brush", 0.44, 1.5, 2.5, 2.0, 0.0, 0.0, 2.5),
    (7, "SH", "southern rough", 0.44, 1.1, 1.9, 1.0, 0.0, 0.4, 2.5),
    (8, "TL", "compact timber litter", 0.28, 1.5, 1.0, 2.5, 0.0, 0.0, 0.2),
    (9, "TL", "hardwood litter", 0.28, 2.9, 0.4, 0.2, 0.0, 0.0, 0.2),
    (10, "TU", "timber and litter understorey", 0.46, 3.0, 2.0, 5.0, 0.0, 2.0, 1.0),
    (11, "SB", "light slash", 0.36, 1.5, 4.5, 5.5, 0.0, 0.0, 1.0),
    (12, "SB", "medium slash", 0.43, 4.0, 14.0, 16.5, 0.0, 0.0, 2.3),
    (13, "SB", "heavy slash", 0.46, 7.0, 23.0, 28.1, 0.0, 0.0, 3.0),
    (101, "GR", "short, sparse dry climate grass", 0.31, 0.1, 0.0, 0.0, 0.3, 0.0, 0.4),
    (102, "GR", "low load dry climate grass", 0.36, 0.1, 0.0, 0.0, 1.0, 0.0, 1.0),
    (
        103,
        "GR",
        "low load very coarse humid climate grass",
        0.42,
        0.1,
        0.4,
        0.0,
        1.5,
        0.0,
        2.0,
    ),
    (104, "GR", "moderate load dry climate grass", 0.42, 0.3, 0.0, 0.0, 1.9, 0.0, 2.0),
    (105, "GR", "low load humid climate grass", 0.39, 0.4, 0.0, 0.0, 2.5, 0.0, 1.5),
    (
        106,
        "GR",
        "moderate load humid climate grass",
        0.39,
        0.1,
        0.0,
        0.0,
        3.4,
        0.0,
        1.5,
    ),
    (107, "GR", "high load dry climate grass", 0.46, 1.0, 0.0, 0.0, 5.4, 0.0, 3.0),
    (108, "GR", "high load humid climate grass", 0.49, 0.5, 1.0, 0.0, 7.3, 0.0, 4.0),
    (
        109,
        "GR",
        "very high load humid climate grass-shrub",
        0.52,
        1.0,
        1.0,
        0.0,
        9.0,
        0.0,
        5.0,
    ),
    (121, "GS", "low load dry climate grass-shrub", 0.35, 0.2, 0.0, 0.0, 0.5, 0.7, 0.9),
    (
        122,
        "GS",
        "moderate load dry climate grass-shrub",
        0.39,
        0.5,
        0.5,
        0.0,
        0.6,
        1.0,
        1.5,
    ),
    (
        123,
        "GS",
        "moderate load humid climate grass-shrub",
        0.41,
        0.3,
        0.3,
        0.0,
        1.5,
        1.3,
        1.8,
    ),
    (
        124,
        "GS",
        "high load humid climate grass-shrub",
        0.42,
        1.9,
        0.3,
        0.1,
        3.4,
        7.1,
        2.1,
    ),
    (141, "SH", "low load dry climate shrub", 0.36, 0.3, 0.3, 0.0, 0.2, 1.3, 1.0),
    (142, "SH", "moderate load dry climate shrub", 0.36, 1.4, 2.4, 0.8, 0.0, 3.9, 1.0),
    (
        143,
        "SH",
        "moderate load humid climate shrub",
        0.44,
        0.5,
        3.0,
        0.0,
        0.0,
        6.2,
        2.4,
    ),
    (
        144,
        "SH",
        "low load humid climate timber-shrub",
        0.46,
        0.9,
        1.2,
        0.2,
        0.0,
        2.6,
        3.0,
    ),
    (145, "SH", "high load dry climate shrub", 0.55, 3.6, 2.1, 0.0, 0.0, 2.9, 6.0),
    (146, "SH", "low load humid climate shrub", 0.42, 2.9, 1.5, 0.0, 0.0, 1.4, 2.0),
    (147, "SH", "very high load dry climate shrub", 0.55, 3.5, 5.3, 2.2, 0.0, 3.4, 6.0),
    (148, "SH", "high load humid climate shrub", 0.46, 2.1, 3.4, 0.9, 0.0, 4.4, 3.0),
    (
        149,
        "SH",
        "very high load humid climate shrub",
        0.50,
        4.5,
        2.5,
        0.0,
        1.6,
        7.0,
        4.4,
    ),
    (
        161,
        "TU",
        "light load dry climate timber-grass-shrub",
        0.33,
        0.2,
        0.9,
        1.5,
        0.2,
        0.9,
        0.6,
    ),
    (
        162,
        "TU",
        "moderate load humid climate timber-shrub",
        0.36,
        1.0,
        1.8,
        1.3,
        0.0,
        0.2,
        1.0,
    ),
    (
        163,
        "TU",
        "moderate load humid climate timber-grass-shrub",
        0.38,
        1.1,
        0.2,
        0.2,
        0.3,
        0.7,
        1.3,
    ),
    (164, "TU", "dwarf conifer with understory", 0.32, 4.5, 0.0, 0.0, 0.0, 2.0, 0.5),
    (
        165,
        "TU",
        "very high load dry climate timber-shrub",
        0.33,
        4.0,
        4.0,
        3.0,
        0.0,
        3.0,
        1.0,
    ),
    (181, "TL", "low load compact conifer litter", 0.28, 1.0, 2.2, 3.6, 0.0, 0.0, 0.2),
    (182, "TL", "low load broadleaf litter", 0.28, 1.4, 2.3, 2.2, 0.0, 0.0, 0.2),
    (183, "TL", "moderate load conifer litter", 0.29, 0.5, 2.2, 2.8, 0.0, 0.0, 0.3),
    (184, "TL", "small downed logs", 0.31, 0.5, 1.5, 4.2, 0.0, 0.0, 0.4),
    (185, "TL", "high load conifer litter", 0.33, 1.2, 2.5, 4.4, 0.0, 0.0, 0.6),
    (186, "TL", "moderate load broadleaf litter", 0.29, 2.4, 1.2, 1.2, 0.0, 0.0, 0.3),
    (187, "TL", "large downed logs", 0.31, 0.3, 1.4, 8.1, 0.0, 0.0, 0.4),
    (188, "TL", "long-needle litter", 0.29, 5.0, 1.4, 1.1, 0.0, 0.0, 0.3),
    (189, "TL", "very high load broadleaf litter", 0.33, 6.7, 3.3, 4.2, 0.0, 0.0, 0.6),
    (201, "SB", "low load activity fuel", 0.36, 1.5, 3.0, 11.1, 0.0, 0.0, 1.0),
    (
        202,
        "SB",
        "moderate load activity fuel or low load blowdown",
        0.36,
        4.5,
        4.3,
        4.0,
        0.0,
        0.0,
        1.0,
    ),
    (
        203,
        "SB",
        "high load activity fuel or moderate load blowdown",
        0.38,
        5.5,
        2.8,
        3.0,
        0.0,
        0.0,
        1.2,
    ),
    (204, "SB", "high load blowdown", 0.45, 5.3, 3.5, 5.3, 0.0, 0.0, 2.7),
]


@dataclass
class FuelModelsArray:
    """Holds an array of synthetic fuel models"""

    fuel_models: List[SyntheticFuelModel] = field(default_factory=list)

    def __post_init__(self):
        for model in HARD_CODED_FUEL_MODELS:
            fm = SyntheticFuelModel(*model[:10])
            self.fuel_models.append(fm)

    def fuel_model_position(self, fuel_model_index: int) -> int:
        """Get position in array of input fuel model index

        Args:
            fuel_model_index (int): fuel model index

        Raises:
            ValueError: can't find the index

        Returns:
            int: output array index
        """
        for i, fm in enumerate(self.fuel_models):
            if fm.fuel_model_index == fuel_model_index:
                return i
        raise ValueError(f"Cannot find fuel model index {fuel_model_index}")
