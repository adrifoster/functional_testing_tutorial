"""Functional equations for fire behavior"""

import math


class FireEquations:

    @staticmethod
    def optimum_packing_ratio(SAV: float) -> float:
        """Calculates optimum packing ratio [unitless]
        Equation A6 in Thonicke et al. 2010
        Rothermel 1972 Eq. 37

        Args:
            SAV (float): surface area to volume ratio of fuel [/cm]

        Returns:
            float: optimum packing ratio [unitless]
        """
        if SAV < 0.0:
            return 0.0
        a, b = 0.200395, -0.8189
        return a * (SAV**b)

    @staticmethod
    def maximum_reaction_velocity(SAV: float) -> float:
        """Calculates maximum reaction velocity in /min

        From Equation 36 in Rothermel 1972; Fig. 12

        Args:
            SAV (float): fuel surface area to volume ratio [/cm]

        Returns:
            float: maximum reaction velocity [/min]
        """
        if SAV < 0.0:
            return 0.0
        return 1.0 / (0.0591 + 2.926 * (SAV**-1.5))

    @staticmethod
    def optimum_reaction_velocity(
        max_vel: float, SAV: float, beta_ratio: float
    ) -> float:
        """Calculates optimum reaction velocity in /min
        Reaction velocity (i.e. rate of fuel consumption) that would exist if the
        fuel were free of moisture and contained minerals at the same reaction
        concentration as alpha cellulose

        From Equation 38 in Rothermel 1972; Fig. 11

        Args:
            max_vel (float): maximum reaction velocity [/min]
            SAV (float): fuel surface area to volume ratio [/cm]
            beta_ratio (float): ratio of packing ratio to optimum packing ratio [0-1]

        Returns:
            float: optimum reaction velocity [/min]
        """
        a = 8.9033 * (SAV**-0.7913)
        a_beta = math.exp(a * (1.0 - beta_ratio))
        return max_vel * (beta_ratio**a) * a_beta

    @staticmethod
    def moisture_coefficient(moisture: float, MEF: float) -> float:
        """Calculates the moisture dampening coefficient for reaction intensity
        Based on Equation in table A1 Thonicke et al. 2010.

        Args:
            moisture (float): fuel moisture [m3/m3]
            MEF (float): fuel moisture of extinction [m3/m3]

        Returns:
            float: moisture dampening coefficient [unitless]
        """
        if MEF < 0.0:
            return 0.0
        mw_weight = moisture / MEF
        coeff = 1.0 - 2.59 * mw_weight + 5.11 * (mw_weight**2) - 3.52 * (mw_weight**3)
        return max(0.0, coeff)

    @staticmethod
    def reaction_intensity(
        fuel_loading: float,
        SAV: float,
        beta_ratio: float,
        moisture: float,
        MEF: float,
        fuel_energy: float,
        mineral_dampening: float,
    ) -> float:
        """Calculates reaction intensity in kJ/m2/min

        Rate of energy release per unit area within the flaming front

        Args:
            fuel_loading (float): net fuel loading [kg/m2]
            SAV (float): fuel surface area to volume ratio [/cm]
            beta_ratio (float): ratio of packing ratio to optimum packing ratio [0-1]
            moisture (float): fuel moisture [m3/m3]
            MEF (float): fuel moisture of extinction [m3/m3]
            fuel_energy (float): heat content of fuel [kJ/kg]
            mineral_dampening (float): mineral-dampening coefficient [unitless]

        Returns:
            float: reaction intensity [kJ/m2/min]
        """
        max_vel = FireEquations.maximum_reaction_velocity(SAV)
        opt_vel = FireEquations.optimum_reaction_velocity(max_vel, SAV, beta_ratio)
        moist_coeff = FireEquations.moisture_coefficient(moisture, MEF)
        return opt_vel * fuel_loading * fuel_energy * moist_coeff * mineral_dampening

    @staticmethod
    def heat_of_preignition(fuel_moisture: float) -> float:
        """Calculates heat of pre-ignition in kJ/kg

        Heat of pre-ignition is the heat required to bring a unit weight of fuel to
        ignition

        Equation A4 in Thonicke et al. 2010
        Rothermel EQ12 = 250 Btu/lb + 1116 Btu/lb * average_moisture
        conversion of Rothermel (1972) EQ12 in BTU/lb to current kJ/kg

        Args:
            fuel_moisture (float): fuel moisture [m3/m3]

        Returns:
            float: heat of preignition [kJ/kg]
        """
        Q_DRY = 581.0  # heat of pregnition of dry fuels
        return Q_DRY + 2594.0 * fuel_moisture

    @staticmethod
    def effective_heating_number(sav: float) -> float:
        """Calculates effective heating number [unitless]

        Proportion of a fuel particle that is heated to ignition temperature at the time
        flaming combustion starts

        Equation A3 in Thonicke et al. 2010

        Args:
            sav (float): fuel surface area to volume ratio [/cm]

        Returns:
            float: effective heating number [unitless]
        """
        if sav < 0.0:
            return 0.0
        return math.exp(-4.528 / sav)

    @staticmethod
    def wind_factor(wind_speed: float, beta_ratio: float, sav: float) -> float:
        """Calculates wind factor for the rate of spread equation [unitless]

        Accounts for effect of wind speed increasing rate of spread

        Args:
            wind_speed (float): wind speed [m/min]
            beta_ratio (float): relative packing ratio [unitless]
            sav (float): fuel surface area to volume ratio [/cm]

        Returns:
            float: wind factor [unitless]
        """

        # Equation A7 in Thonicke et al. 2010 per eqn 49 from Rothermel 1972
        b = 0.15988 * (sav**0.54)

        # Equation A8 in Thonicke et al. 2010 per eqn 48 from Rothermel 1972
        c = 7.47 * (math.exp(-0.8711 * (sav**0.55)))

        # Equation A9 in Thonicke et al. 2010 (appears to have typo, using coefficient
        # Eq. 50 Rothermel 1972)
        e = 0.715 * (math.exp(-0.01094 * sav))

        # Equation A5 in Thonicke et al. 2010
        # convert wind_speed (wind at elev relevant to fire) from m/min to ft/min for
        # Rothermel ROS Eq.
        return c * ((3.281 * wind_speed) ** b) * (beta_ratio ** (-e))

    @staticmethod
    def propagating_flux(beta: float, sav: float) -> float:
        """Calculates propagating flux ratio [unitless]
        Proportion of reaction intensity that heats adjacent fuel particles to ignition
        Equation A2 in Thonicke et al. 2010 and Eq. 42 Rothermel 1972

        Args:
            beta (float): packing ratio [unitless]
            sav (float): fuel surface area to volume ratio [/cm]

        Returns:
            float: propagating flux ratio [unitless]
        """
        return (math.exp((0.792 + 3.7597 * (sav**0.5)) * (beta + 0.1))) / (
            192.0 + 7.9095 * sav
        )

    @staticmethod
    def forward_rate_of_spread(
        bulk_density: float,
        epsilon: float,
        q_ig: float,
        i_r: float,
        xi: float,
        phi_wind: float,
    ) -> float:
        """Calculates forward rate of spread [m/min]
        Flaming front of a surface fire
        Equation 9. Thonicke et al. 2010

        Args:
            bulk_density (float): fulk bulk density [kg/m3]
            epsilon (float): effective heating number [unitless]
            q_ig (float): heat of preignition [kJ/kg]
            i_r (float): reaction intensity [kJ/m2/min]
            xi (float): propagating flux [unitless]
            phi_wind (float): wind factor [unitless]

        Returns:
            float: forward rate of spread [m/min]
        """

        if bulk_density <= 0.0 or epsilon <= 0.0 or q_ig <= 0.0:
            return 0.0

        return (i_r * xi * (1.0 + phi_wind)) / (bulk_density * epsilon * q_ig)

    @staticmethod
    def backward_rate_of_spread(ros_front: float, wind_speed: float) -> float:
        """Calculates backwards rate of spread [m/min]

        Equation 10 in Thonicke et al. 2010
        backward ROS from Can FBP System (1992)
        backward ROS wind not changed by vegetation

        Args:
            ros_front (float): forward rate of spread [m/min]
            wind_speed (float): wind speed [m/min]

        Returns:
            float: backwards rate of spread [m/min]
        """
        return ros_front * math.exp(-0.012 * wind_speed)

    @staticmethod
    def fire_duration(FDI: float, max_duration: float, duration_slope: float) -> float:
        """Calculates fire duration [min]
        Equation 14 in Thonicke et al. 2010

        Args:
            FDI (float): fire danger index [0-1]
            max_duration (float): maximum fire duration [min]
            duration_slope (float): slope of fire duration curve [unitless]

        Returns:
            float: fire duration [min]
        """
        return (max_duration + 1.0) / (
            1.0 + max_duration * math.exp(duration_slope * FDI)
        )

    @staticmethod
    def length_to_breadth_ratio(
        effective_windspeed: float, tree_fraction: float
    ) -> float:
        """Calculates length to breadth ratio of fire ellipse [unitless],
        used for calculating area burnt

        Args:
            effective_windspeed (float): effective windspeed [m/min]
            tree_fraction (float): tree fraction [0-1]

        Returns:
            float: length to bread ratio [unitless]
        """

        LB_THRESHOLD = 0.55

        windspeed_km_hr = effective_windspeed / 1000.0 * 60.0

        if windspeed_km_hr < 1.0:
            return 1.0

        if tree_fraction > LB_THRESHOLD:
            return 1.0 + 8.729 * ((1.0 - math.exp(-0.03 * windspeed_km_hr)) ** 2.155)
        else:
            return 1.1 * (windspeed_km_hr**0.464)

    @staticmethod
    def fire_size(
        length_to_breadth: float,
        ros_back: float,
        ros_forward: float,
        fire_duration: float,
    ) -> float:
        """Calculates fire size [m2]

         Eq 14 Arora and Boer JGR 2005 (area of an ellipse)

        Args:
            length_to_breadth (float): length to breadth ratio of fire ellipse [unitless]
            ros_back (float): backwards rate of spread [m/min]
            ros_forward (float): forward rate of spread [m/min]
            fire_duration (float): fire duration [min]

        Returns:
            float: fire size [m2]
        """

        PI = 3.14159265359

        if length_to_breadth < 0.0:
            return 0.0

        dist_back = ros_back * fire_duration
        dist_forward = ros_forward * fire_duration

        return (PI / (4.0 * length_to_breadth)) * ((dist_forward + dist_back) ** 2.0)

    @staticmethod
    def area_burnt(fire_size: float, num_ignitions: float, FDI: float) -> float:
        """Calculates area burnt [m2/km2/day]

        Args:
            fire_size (float): fire size [m2]
            num_ignitions (float): number of ignitions [/km2/day]
            FDI (float): fire danger index [0-1]

        Returns:
            float: area burnt [m2/km2/day]
        """
        return fire_size * num_ignitions * FDI

    @staticmethod
    def fire_intensity(fuel_consumed: float, ros: float, fuel_energy: float) -> float:
        """Calculates fire intensity [kW/m]
        Eq 15 Thonicke et al 2010

        Args:
            fuel_consumed (float): fuel consumed [kg/m2]
            ros (float): rate of spread [m/s]
            fuel_energy (float): heat content of fuel [kJ/kg]

        Returns:
            float: surface fireline intensity [kW/m]
        """
        return fuel_energy * fuel_consumed * ros

    @staticmethod
    def scorch_height(alpha_sh: float, fire_intensity: float) -> float:
        """Calculates scorch height [m]

        Equation 16 in Thonicke et al. 2010
        Van Wagner 1973 Eq. 8; Byram (1959)

        Args:
            alpha_sh (float): alpha parameter for scorch height equation
            fire_intensity (float): fire intensity [kW/m]

        Returns:
            float: scorch height [m]
        """
        if fire_intensity <= 0.0:
            return 0.0

        return alpha_sh * (fire_intensity**0.667)

    @staticmethod
    def crown_fraction_burnt(
        scorch_height: float, tree_height: float, crown_depth: float
    ) -> float:
        """Calculates fraction of the crown burnt for woody plants

        Equation 17 in Thonicke et al. 2010

        Args:
            scorch_height (float): scorch height [m]
            tree_height (float): tree height [m]
            crown_depth (float): crown depth [m]

        Returns:
            float: fraction of crown burnt [0-1]
        """
        if crown_depth <= 0.0:
            return 0.0

        fraction_burnt = (scorch_height - tree_height + crown_depth) / crown_depth
        return min(1.0, max(0.0, fraction_burnt))

    @staticmethod
    def bark_thickness(bark_scalar: float, dbh: float) -> float:
        """Calculates bark thickness [cm]

        Equation 21 in Thonicke et al 2010

        Args:
            bark_scalar (float): bark per dbh [cm/cm]
            dbh (float): diameter at breast height [cm]

        Returns:
            float: bark thickness [cm]
        """
        return bark_scalar * dbh

    @staticmethod
    def critical_residence_time(bark_thickness: float) -> float:
        """Calculates critical fire residence time for cambial damage [min]

        Equation 19 in Thonicke et al. 2010

        Args:
            bark_thickness (float): bark thickness [cm]

        Returns:
            float: critical fire residence time for cambial damage [min]
        """
        return 2.9 * bark_thickness**2.0

    @staticmethod
    def cambial_mortality(bark_scalar: float, dbh: float, tau_l: float) -> float:
        """Calculates rate of cambial damage mortality [0-1]
        Equation 19 in Thonicke et al. 2010

        Args:
            bark_scalar (float): cm bark per cm dbh [cm/cm]
            dbh (float): diameter at breast height [cm]
            tau_l (float): residence time of fire [min]

        Returns:
            float: rate of cambial damage mortality [0-1]
        """

        # calculate bark thickness based of bark scalar parameter and DBH
        bark_thickness = FireEquations.bark_thickness(bark_scalar, dbh)

        # calculate critical residence time for cambial damage [min]
        tau_c = FireEquations.critical_residence_time(bark_thickness)

        # relative residence time
        tau_r = tau_l / tau_c

        if tau_r >= 2.0:
            return 1.0
        if 0.22 < tau_r < 2.0:
            return 0.563 * tau_r - 0.125
        return 0.0

    @staticmethod
    def crown_fire_mortality(crown_kill: float, fraction_crown_burned: float) -> float:
        """Calculates rate of mortality from crown scorching [0-1]
        Equation 19 in Thonicke et al. 2010

        Args:
            crown_kill (float): parameter for crown kill cm bark per cm dbh [cm/cm]
            fraction_crown_burned (float): fraction of the crown burned [0-1]

        Returns:
            float: rate of mortality from crown scorching [0-1]
        """

        mortality = crown_kill * fraction_crown_burned**3.0
        return min(1.0, max(0.0, mortality))

    @staticmethod
    def total_fire_mortality(
        crown_fire_mort: float, cambial_damage_mort: float
    ) -> float:
        """Calculates rate of mortality from wildfire [0-1]
        Equation 18 in Thonicke et al. 2010

        Args:
            crown_fire_mort (float): mortality rate from crown scorching [0-1]
            cambial_damage_mort (float): mortality rate from cambial damage [0-1]

        Returns:
            float: rate of mortality from wildfire [0-1]
        """

        if crown_fire_mort >= 1.0 or cambial_damage_mort >= 1.0:
            return 1.0
        mortality = (
            crown_fire_mort
            + cambial_damage_mort
            - (crown_fire_mort * cambial_damage_mort)
        )
        return min(1.0, max(0.0, mortality))
