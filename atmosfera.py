# atmosfera.py
# MHD-INT v5.0 - Modelo de Atmosfera y Escape (Owen & Jackson 2012)
# Licencia AGPL-3.0
#
# El umbral de "atmosfera perdida" (M_atm_critica) se define como una
# fraccion configurable de la masa atmosferica INICIAL de cada planeta
# (10% por defecto), no de la masa del planeta. Esto es mas robusto: no
# depende de que la masa/gravedad de cada planeta este calibrada para dar
# exactamente 1 bar de presion superficial con una formula fija.

import numpy as np

YR_SEC = 365.25 * 24 * 3600
G = 6.67430e-11
UA = 1.495978707e11


class Atmosfera:
    """
    Modelo 1D de evolucion de masa atmosferica por escape hidrodinamico.

    Ecuacion de Owen & Jackson (2012):
        dM_atm/dt = -eta * (pi * R_p^3 * F_XUV) / (G * M_p)
    """

    def __init__(self,
                 M_atm_inicial: float,        # kg
                 M_planeta: float,            # kg
                 R_planeta: float,            # m
                 F_XUV_inicial: float,        # W/m^2 (flujo XUV de referencia a 1 UA)
                 distancia_ua: float,         # UA (distancia inicial)
                 eficiencia_escape: float = 0.15,
                 tipo_estrella: str = "G2V",
                 fraccion_critica: float = 0.10):  # NUEVO: umbral como % de M_atm_inicial
        self.M_atm = M_atm_inicial
        self.M_atm_inicial = M_atm_inicial
        self.M_planeta = M_planeta
        self.R_p = R_planeta
        self.eta = eficiencia_escape
        self.distancia_ua = distancia_ua

        self.F_XUV_0 = F_XUV_inicial / (distancia_ua ** 2)

        if tipo_estrella.upper().startswith('M'):
            self.beta = 0.8  # enanas M: XUV saturado por mas tiempo (Loyd et al. 2020)
        else:
            self.beta = 1.5  # tipo solar (decaimiento tipo Skumanich)

        # CORREGIDO: umbral relativo a la masa atmosferica inicial de ESTE
        # planeta, no a la masa del planeta (ver nota de modulo).
        self.M_atm_critica = fraccion_critica * M_atm_inicial

        self.perdida_total = False
        self.M_atm_hist = [M_atm_inicial]

    def actualizar(self, t_gyr: float, dt: float, a_ua: float) -> float:
        """
        Args:
            t_gyr: tiempo actual en Gyr.
            dt: paso de tiempo en segundos.
            a_ua: distancia orbital actual en UA.
        Returns:
            M_atm_actual (float): masa atmosferica en kg.
        """
        if self.perdida_total:
            return 0.0

        t_0 = 0.01  # Gyr, edad de referencia
        factor_tiempo = 1.0 if t_gyr <= t_0 else (t_gyr / t_0) ** (-self.beta)

        F_XUV_actual = self.F_XUV_0 * factor_tiempo / (a_ua ** 2)
        F_XUV_actual = max(F_XUV_actual, 1e-5)

        dM_dt = -self.eta * (np.pi * (self.R_p ** 3) * F_XUV_actual) / (G * self.M_planeta)

        self.M_atm = max(self.M_atm + dM_dt * dt, 0.0)

        if self.M_atm < self.M_atm_critica:
            self.perdida_total = True
            self.M_atm = 0.0

        self.M_atm_hist.append(self.M_atm)
        return self.M_atm

    def get_presion_superficial(self) -> float:
        """Estima presion superficial (bar), asumiendo atmosfera uniforme."""
        if self.M_atm <= 0:
            return 0.0
        g = G * self.M_planeta / (self.R_p ** 2)
        P_pascal = self.M_atm * g / (4.0 * np.pi * (self.R_p ** 2))
        return P_pascal / 1e5

    def get_frac_atm_restante(self) -> float:
        """Fraccion de masa atmosferica restante (0 a 1)."""
        if self.M_atm_inicial <= 0:
            return 0.0
        return self.M_atm / self.M_atm_inicial
