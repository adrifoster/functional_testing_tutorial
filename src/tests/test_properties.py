#!/usr/bin/env python3

import math
import pytest
import copy


from fire_model import FireEquations
import numpy as np
import matplotlib.pyplot as plt
from fire_model.fire_equations import FireEquations
from fire_model.fuel_class import Fuel
from fire_model.testing.synthetic_fuel_models import (
    FuelModelsArray,
    HARD_CODED_FUEL_MODELS,
)
from fire_model.testing.testing_shr import initialize_from_synthetic
import hypothesis.strategies as st
import hypothesis.extra.numpy as npst
from hypothesis import given
from fire_model.fire_params import FireParams
from fire_model.fuel_class import Fuel

betas = st.floats(min_value=1e-3, max_value=0.02, allow_nan=False, allow_infinity=False)
beta_ratios = st.floats(min_value=0, max_value=5, allow_nan=False, allow_infinity=False)
savs = st.floats(min_value=5, max_value=120, allow_nan=False, allow_infinity=False)


@st.composite
def fuels(draw: st.DrawFn) -> Fuel:
    # read in parameter file
    params = FireParams.from_yaml("parameter_files/fire_parameters.yaml")
    fuel = Fuel(params)

    all_synthetic_fuels = FuelModelsArray()
    valid_fuel_ids = tuple(f[0] for f in HARD_CODED_FUEL_MODELS)

    fuel_id = draw(st.sampled_from(valid_fuel_ids))
    fuel = initialize_from_synthetic(fuel, all_synthetic_fuels, fuel_id)
    return fuel


@given(
    beta=betas,
    sav=savs,
    factor=st.floats(min_value=1, max_value=5, allow_nan=False, allow_infinity=False),
)
def test_propagating_flux_increases_with_beta_sav(
    beta: float, sav: float, factor: float
) -> None:
    actual = FireEquations.propagating_flux(beta, sav)
    sav_2x = FireEquations.propagating_flux(beta, sav * factor)
    beta_2x = FireEquations.propagating_flux(beta * factor, sav)

    # Are all flux values positive?
    assert actual > 0
    assert sav_2x > 0
    assert beta_2x > 0

    # Does the flux increase monotonically with beta and SAV?
    assert sav_2x >= actual
    assert beta_2x >= actual


@given(data=st.data(), fuel=fuels())
def test_calculate_fraction_burnt(data: st.DataObject, fuel: Fuel) -> None:
    # this is a dependent draw since we need to generate an array of the right size
    effmoist = data.draw(
        npst.arrays(
            dtype=fuel.effective_moisture.dtype,
            shape=fuel.effective_moisture.size,
            elements={"min_value": 0, "max_value": 1},
        )
    )

    fuel.effective_moisture = effmoist.copy()
    fuel.calculate_fraction_burnt()
    assert (fuel.frac_burnt >= 0).all()
    assert (fuel.frac_burnt <= 1).all()

    # metamorphic test
    perturb_fuel = copy.deepcopy(fuel)
    perturb = data.draw(
        npst.arrays(
            dtype=fuel.effective_moisture.dtype,
            shape=fuel.effective_moisture.size,
            elements=dict(
                min_value=0,
                max_value=(1 - effmoist.max()),
                allow_nan=False,
                allow_infinity=False,
            ),
        )
    )
    perturb_fuel.effective_moisture = effmoist + perturb
    fuel.calculate_fraction_burnt()
    assert (perturb_fuel.frac_burnt >= 0).all()
    assert (perturb_fuel.frac_burnt <= 1).all()
    assert (perturb_fuel.frac_burnt <= fuel.frac_burnt).all()


@given(
    beta_ratio=st.floats(
        min_value=0.1, max_value=5, allow_nan=False, allow_infinity=False
    ),
    sav=savs,
)
def test_property_reaction_velocity(beta_ratio: float, sav: float):
    """tests that the maximum is at 1. does NOT catch the bug."""
    max_vel = FireEquations.maximum_reaction_velocity(sav)
    vel = FireEquations.optimum_reaction_velocity(max_vel, sav, beta_ratio)

    vel_at_1 = FireEquations.optimum_reaction_velocity(max_vel, sav, 1)
    assert max_vel == vel_at_1
    # peak appears to be at 1
    assert vel <= max_vel


@given(sav=savs)
def test_property_reaction_velocity_sav_variation(sav):
    """ This doesn't find the bug! """
    beta_ratios = np.arange(0.1, 5, 0.1)
    max_vel = FireEquations.maximum_reaction_velocity(sav)
    velocities = np.array(
        [
            FireEquations.optimum_reaction_velocity(max_vel, sav, beta)
            for beta in beta_ratios
        ]
    )

    idx = np.argmax(velocities)
    area_lt_1 = np.trapz(velocities[:idx], beta_ratios[:idx])
    area_gt_1 = np.trapz(velocities[idx:], beta_ratios[idx:])
    assert area_gt_1 > area_lt_1


@given(sav=savs.filter(lambda x: x > 15))
def test_property_reaction_velocity_sav_variation(sav):
    """ This 'silly' test captures the error immediately. """
    # looking at the expected image; the value for σ of 15 is > 1 for β ratio = 5
    # assert sav > 15
    max_vel = FireEquations.maximum_reaction_velocity(sav)
    vel = FireEquations.optimum_reaction_velocity(max_vel, sav, 5)
    assert vel > 0.5
