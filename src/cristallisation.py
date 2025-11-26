"""
Crystallization kinetics and batch crystallizer simulation.
Includes solubility, nucleation/growth kinetics, and population balance equation solving.
"""

import numpy as np
from scipy.integrate import odeint
import config


def solubility_saccharose(T):
    """
    Calculate solubility of saccharose in water using empirical correlation.
    C* = a + bT + cT² + dT³

    Parameters:
    -----------
    T : float or array-like
        Temperature in °C

    Returns:
    --------
    float or array : Solubility in g saccharose / 100g solution
    """
    a = config.SOLUBILITY_COEFFS['a']
    b = config.SOLUBILITY_COEFFS['b']
    c = config.SOLUBILITY_COEFFS['c']
    d = config.SOLUBILITY_COEFFS['d']

    C_star = a + b * T + c * T**2 + d * T**3

    return C_star


def supersaturation(C, T):
    """
    Calculate relative supersaturation.
    S = (C - C*) / C*

    Parameters:
    -----------
    C : float
        Actual concentration (g/100g solution)
    T : float
        Temperature (°C)

    Returns:
    --------
    float : Relative supersaturation (dimensionless)
    """
    C_star = solubility_saccharose(T)
    S = (C - C_star) / C_star
    return max(S, 0)  # Supersaturation cannot be negative


def nucleation_rate(S, m_T):
    """
    Calculate nucleation rate using power law model.
    B = kb * S^b * mT^j

    Parameters:
    -----------
    S : float
        Relative supersaturation
    m_T : float
        Third moment of CSD (related to total crystal mass)

    Returns:
    --------
    float : Nucleation rate (nuclei/m³/s)
    """
    if S <= 0:
        return 0

    kb = config.NUCLEATION_KB
    b = config.NUCLEATION_B
    j = config.NUCLEATION_J

    B = kb * (S ** b) * (m_T ** j)

    return B


def growth_rate(S, T):
    """
    Calculate crystal growth rate using surface integration model.
    G = kg * S^g * exp(-Eg/RT)

    Parameters:
    -----------
    S : float
        Relative supersaturation
    T : float
        Temperature (°C)

    Returns:
    --------
    float : Growth rate (m/s)
    """
    if S <= 0:
        return 0

    kg = config.GROWTH_KG
    g = config.GROWTH_G
    Eg = config.GROWTH_EG
    R = config.R_GAS

    T_K = T + 273.15  # Convert to Kelvin

    G = kg * (S ** g) * np.exp(-Eg / (R * T_K))

    return G


class BatchCrystallizer:
    """
    Batch cooling crystallizer with population balance modeling using method of moments.
    """

    def __init__(self, volume, initial_concentration, initial_temperature):
        """
        Initialize batch crystallizer.

        Parameters:
        -----------
        volume : float
            Crystallizer volume (m³)
        initial_concentration : float
            Initial concentration (g saccharose / 100g solution)
        initial_temperature : float
            Initial temperature (°C)
        """
        self.volume = volume
        self.C_initial = initial_concentration
        self.T_initial = initial_temperature

        # Results storage
        self.time_profile = None
        self.T_profile = None
        self.C_profile = None
        self.S_profile = None
        self.moments_profile = None
        self.L50 = None
        self.CV = None
        self.yield_mass = None

    def cooling_profile(self, strategy, t, T_initial, T_final, duration):
        """
        Generate cooling profile.

        Parameters:
        -----------
        strategy : str
            Cooling strategy: 'linear', 'exponential', or 'optimal'
        t : float
            Current time (s)
        T_initial : float
            Initial temperature (°C)
        T_final : float
            Final temperature (°C)
        duration : float
            Total batch duration (s)

        Returns:
        --------
        float : Temperature at time t (°C)
        """
        if strategy == 'linear':
            alpha = (T_initial - T_final) / duration
            T = T_initial - alpha * t

        elif strategy == 'exponential':
            beta = -np.log((T_final - 20) / (T_initial - 20)) / duration
            T = T_final + (T_initial - T_final) * np.exp(-beta * t)

        elif strategy == 'optimal':
            # Maintain constant supersaturation by controlling temperature
            # This will be handled in the ODE system
            T = T_initial - (T_initial - T_final) * (t / duration) ** 0.7

        else:
            raise ValueError(f"Unknown cooling strategy: {strategy}")

        return max(min(T, T_initial), T_final)

    def pbe_ode_system(self, y, t, strategy, T_initial, T_final, duration):
        """
        ODE system for population balance using method of moments.

        Parameters:
        -----------
        y : array
            State vector [C, mu0, mu1, mu2, mu3]
            C: concentration, mu_i: i-th moment of CSD
        t : float
            Time (s)
        strategy : str
            Cooling strategy
        T_initial : float
            Initial temperature (°C)
        T_final : float
            Final temperature (°C)
        duration : float
            Total duration (s)

        Returns:
        --------
        array : Derivatives [dC/dt, dmu0/dt, dmu1/dt, dmu2/dt, dmu3/dt]
        """
        C, mu0, mu1, mu2, mu3 = y

        # Current temperature
        T = self.cooling_profile(strategy, t, T_initial, T_final, duration)

        # Supersaturation
        S = supersaturation(C, T)

        # Kinetics
        B = nucleation_rate(S, mu3)
        G = growth_rate(S, T)

        # Moments evolution
        dmu0_dt = B  # Nucleation creates new crystals
        dmu1_dt = G * mu0  # Growth increases first moment
        dmu2_dt = 2 * G * mu1  # Growth increases second moment
        dmu3_dt = 3 * G * mu2  # Growth increases third moment

        # Mass balance for concentration
        # dC/dt related to crystal growth (mass deposited)
        rho_crystal = config.SACCHAROSE_DENSITY  # kg/m³
        k_v = np.pi / 6  # Volume shape factor for spheres

        # Rate of mass deposition (kg/s/m³ of solution)
        dM_crystal_dt = rho_crystal * k_v * dmu3_dt

        # Convert to concentration change (g/100g solution decrease)
        # Approximate: solution density ~ 1200 kg/m³
        rho_solution = 1200  # kg/m³

        # dC/dt in g/100g per second
        dC_dt = -(dM_crystal_dt / rho_solution) * 100

        return [dC_dt, dmu0_dt, dmu1_dt, dmu2_dt, dmu3_dt]

    def run_batch(self, strategy, T_final, duration):
        """
        Run batch crystallization simulation.

        Parameters:
        -----------
        strategy : str
            Cooling strategy: 'linear', 'exponential', or 'optimal'
        T_final : float
            Final temperature (°C)
        duration : float
            Batch duration (s)

        Returns:
        --------
        dict : Crystallization results
        """
        # Initial conditions [C, mu0, mu1, mu2, mu3]
        # Start with no crystals (seed crystals can be added if needed)
        y0 = [self.C_initial, 1e6, 1e-6, 1e-12, 1e-18]  # Small seed population

        # Time points
        t = np.linspace(0, duration, 200)

        # Solve ODE system
        solution = odeint(
            self.pbe_ode_system,
            y0,
            t,
            args=(strategy, self.T_initial, T_final, duration)
        )

        # Extract profiles
        self.time_profile = t
        self.C_profile = solution[:, 0]
        self.moments_profile = solution[:, 1:]

        # Temperature profile
        self.T_profile = np.array([
            self.cooling_profile(strategy, ti, self.T_initial, T_final, duration)
            for ti in t
        ])

        # Supersaturation profile
        self.S_profile = np.array([
            supersaturation(self.C_profile[i], self.T_profile[i])
            for i in range(len(t))
        ])

        # Final CSD characteristics
        mu0_final = self.moments_profile[-1, 0]
        mu1_final = self.moments_profile[-1, 1]
        mu2_final = self.moments_profile[-1, 2]
        mu3_final = self.moments_profile[-1, 3]

        # Mean crystal size (L50)
        if mu2_final > 0:
            self.L50 = mu3_final / mu2_final  # m
        else:
            self.L50 = 0

        # Coefficient of variation
        if mu1_final > 0 and mu0_final > 0:
            L_mean = mu1_final / mu0_final
            L_variance = (mu2_final / mu0_final) - L_mean**2
            if L_variance > 0 and L_mean > 0:
                self.CV = np.sqrt(L_variance) / L_mean
            else:
                self.CV = 0
        else:
            self.CV = 0

        # Mass yield
        C_final = self.C_profile[-1]
        C_sat_final = solubility_saccharose(T_final)
        if self.C_initial > C_sat_final:
            self.yield_mass = (self.C_initial - C_final) / (self.C_initial - C_sat_final)
        else:
            self.yield_mass = 0

        return {
            'strategy': strategy,
            'L50': self.L50,
            'L50_microns': self.L50 * 1e6,  # Convert to μm
            'CV': self.CV,
            'yield': self.yield_mass,
            'final_concentration': C_final,
            'final_temperature': T_final,
            'time': self.time_profile,
            'T_profile': self.T_profile,
            'C_profile': self.C_profile,
            'S_profile': self.S_profile,
            'moments': self.moments_profile
        }

    def calculate_CSD(self, n_bins=50):
        """
        Calculate crystal size distribution from moments.

        Parameters:
        -----------
        n_bins : int
            Number of size bins

        Returns:
        --------
        tuple : (L_bins, n_distribution)
            L_bins: crystal sizes (m)
            n_distribution: number density (nuclei/m³/m)
        """
        if self.moments_profile is None:
            raise ValueError("Must run batch simulation first")

        # Use final moments
        mu0 = self.moments_profile[-1, 0]
        mu1 = self.moments_profile[-1, 1]
        mu2 = self.moments_profile[-1, 2]

        # Assume log-normal distribution
        if mu0 > 0 and mu1 > 0:
            L_mean = mu1 / mu0
            L_std = np.sqrt(max(mu2 / mu0 - L_mean**2, 0))

            # Generate size bins
            L_max = L_mean + 4 * L_std
            L_bins = np.linspace(0, L_max, n_bins)

            # Log-normal distribution
            if L_std > 0:
                # Avoid division by zero by using np.errstate
                with np.errstate(divide='ignore', invalid='ignore'):
                    n_distribution = (mu0 / (L_bins * L_std * np.sqrt(2 * np.pi))) * \
                                     np.exp(-(np.log(L_bins / L_mean))**2 / (2 * (L_std / L_mean)**2))
                # Handle division by zero at L=0
                n_distribution[0] = 0
                # Replace any inf/nan with 0
                n_distribution = np.nan_to_num(n_distribution, nan=0.0, posinf=0.0, neginf=0.0)
            else:
                n_distribution = np.zeros_like(L_bins)
                # Delta function at L_mean
                idx = np.argmin(np.abs(L_bins - L_mean))
                n_distribution[idx] = mu0

            return L_bins, n_distribution
        else:
            return np.zeros(n_bins), np.zeros(n_bins)

    def size_crystallizer(self, residence_time_target=None):
        """
        Calculate required crystallizer volume based on residence time.

        Parameters:
        -----------
        residence_time_target : float, optional
            Target residence time (s). If None, uses batch duration.

        Returns:
        --------
        float : Required volume (m³)
        """
        if residence_time_target is None:
            residence_time_target = config.CRYSTALLIZATION_TIME

        # Volume based on batch size and density
        batch_mass = config.BATCH_SIZE  # kg
        solution_density = 1200  # kg/m³ (approximate)

        volume_required = batch_mass / solution_density

        return volume_required

    def size_cooling_coil(self, T_cooling_water=15):
        """
        Calculate heat transfer area required for cooling coil.

        Parameters:
        -----------
        T_cooling_water : float
            Cooling water temperature (°C)

        Returns:
        --------
        dict : Cooling coil sizing results
            - area: Heat transfer area (m²)
            - Q_total: Total heat to remove (kJ)
            - Q_avg: Average cooling power (kW)
            - LMTD: Log-mean temperature difference (K)
        """
        if self.T_profile is None:
            raise ValueError("Must run batch simulation first")

        # Heat removal calculation
        batch_mass = config.BATCH_SIZE  # kg
        cp_solution = 3500  # J/(kg·K) - approximate for sugar solution

        # Total heat to be removed
        delta_T = self.T_initial - self.T_profile[-1]
        Q_total = batch_mass * cp_solution * delta_T  # J

        # Average cooling rate
        duration = self.time_profile[-1]
        Q_avg = Q_total / duration  # W

        # Heat transfer coefficient for cooling coil
        U_coil = 500  # W/(m²·K) - typical for jacketed vessel

        # LMTD calculation
        delta_T_initial = self.T_initial - T_cooling_water
        delta_T_final = self.T_profile[-1] - T_cooling_water

        if delta_T_final > 0:
            LMTD = (delta_T_initial - delta_T_final) / np.log(delta_T_initial / delta_T_final)
        else:
            LMTD = delta_T_initial

        # Area calculation
        A_coil = Q_avg / (U_coil * LMTD)

        return {
            'area': A_coil,
            'Q_total': Q_total / 1000,  # kJ
            'Q_avg': Q_avg / 1000,  # kW
            'LMTD': LMTD
        }

    def calculate_agitation_power(self):
        """
        Calculate agitation power requirement for crystallizer.

        Uses standard correlations for power number and tip speed.

        Returns:
        --------
        dict : Agitation sizing results
            - power: Power requirement (kW)
            - impeller_diameter: Impeller diameter (m)
            - rotation_speed: Rotational speed (rpm)
            - tip_speed: Tip speed (m/s)
        """
        # Typical design parameters for crystallizers
        # Tank diameter (from volume)
        D_tank = (4 * self.volume / (np.pi * 1.5)) ** (1/3)  # Assume H/D = 1.5

        # Impeller diameter (typically D_impeller = 0.33 * D_tank)
        D_impeller = 0.33 * D_tank

        # Rotation speed for gentle mixing in crystallizers (to avoid attrition)
        # Typical tip speed: 2-3 m/s for crystallization
        tip_speed_target = 2.5  # m/s
        N = tip_speed_target / (np.pi * D_impeller)  # rev/s
        N_rpm = N * 60  # rpm

        # Power number (Np) for pitched blade turbine ~ 1.5
        Np = 1.5

        # Solution properties
        rho = 1200  # kg/m³ (sugar solution density)
        mu = 0.01  # Pa·s (dynamic viscosity of concentrated sugar solution)

        # Reynolds number
        Re = rho * N * D_impeller**2 / mu

        # Power calculation: P = Np * rho * N^3 * D^5
        P = Np * rho * (N ** 3) * (D_impeller ** 5)  # W

        # Safety factor for motor sizing
        P_motor = P * 1.5 / 1000  # kW (with 50% safety margin)

        return {
            'power': P_motor,
            'power_actual': P / 1000,  # kW
            'impeller_diameter': D_impeller,
            'tank_diameter': D_tank,
            'rotation_speed': N_rpm,
            'tip_speed': tip_speed_target,
            'reynolds_number': Re
        }

    def calculate_residence_time(self):
        """
        Calculate hydraulic residence time for continuous equivalent.

        For batch operation, this is simply the batch duration.
        For economic analysis, also calculate throughput.

        Returns:
        --------
        dict : Residence time analysis
            - batch_duration: Batch time (hours)
            - residence_time: Effective residence time (hours)
            - throughput: Annual throughput (tonnes/year)
            - batches_per_day: Number of batches per day
        """
        if self.time_profile is None:
            raise ValueError("Must run batch simulation first")

        batch_duration_hours = self.time_profile[-1] / 3600  # hours

        # Assume 2 hours for emptying, cleaning, filling
        turnaround_time = 2  # hours
        total_cycle_time = batch_duration_hours + turnaround_time

        # Batches per day
        batches_per_day = 24 / total_cycle_time

        # Annual production (assuming 330 operating days/year)
        batch_mass = config.BATCH_SIZE  # kg
        yield_fraction = self.yield_mass if self.yield_mass else 0.5
        crystals_per_batch = batch_mass * (self.C_initial - self.C_profile[-1]) / 100  # kg

        annual_production = crystals_per_batch * batches_per_day * 330 / 1000  # tonnes/year

        return {
            'batch_duration': batch_duration_hours,
            'turnaround_time': turnaround_time,
            'total_cycle_time': total_cycle_time,
            'residence_time': batch_duration_hours,  # For batch, same as duration
            'batches_per_day': batches_per_day,
            'crystals_per_batch': crystals_per_batch,
            'annual_throughput': annual_production
        }
