# termica.py
# MHD-INT v5.0 - Modelo Termico del Nucleo y Generacion de Dinamo
# Basado en Christensen & Aubert (2006), Christensen et al. (2009)
# Acoplamiento manto-nucleo (v5.0): factor stagnant-lid tipo Korenaga (2008)
# Licencia AGPL-3.0
#
# Fusiona el modelo termico simple del nucleo (v4.2) con el acoplamiento
# nucleo-manto (v5.0) en un solo modulo. Notas de implementacion:
#
#   1. k_manto y regimen_tectonico se asignan directamente desde los
#      parametros del constructor (unica fuente de verdad); no dependen de
#      overrides internos.
#
#   2. 'albedo' es un parametro real del constructor (default 0.3), leido
#      desde database.py a traves de engine.py, en vez de calcularse
#      internamente a partir de R_core/R_planeta.
#
#   3. self.R_planeta se guarda una sola vez en el __init__ principal.
#
#   4. LIMITACION CONOCIDA: engine.py llama a actualizar() con
#      L_estrella=1.0 (luminosidad solar) fijo para todos los planetas,
#      porque database.py todavia no tiene un dato de luminosidad estelar
#      por tipo espectral. Para estrellas G/K esto es razonable; para
#      enanas M sobreestima la temperatura superficial (T_sup) y por lo
#      tanto Q_CMB / q_conv. Resolverlo requiere agregar un modelo de
#      luminosidad estelar (relacion masa-luminosidad o tabla por tipo
#      espectral) -- pendiente para una version futura.

import numpy as np

YR_SEC = 365.25 * 24 * 3600
G = 6.67430e-11
MU_0 = 4.0 * np.pi * 1e-7
UA = 1.495978707e11
SIGMA_SB = 5.670374419e-8  # Constante de Stefan-Boltzmann


class NucleoTermico:
    """
    Modelo 1D de evolucion termica del nucleo planetario con acoplamiento
    al manto. Calcula el flujo de calor convectivo disponible (q_conv), el
    numero de Reynolds magnetico (Rm), y el campo magnetico generado en el
    nucleo (ley de escala de Christensen), atenuado a superficie.
    """

    def __init__(self,
                 M_planeta: float,          # kg
                 R_planeta: float,          # m
                 R_core: float,             # m (radio del nucleo)
                 rho_core: float,           # kg/m^3
                 T_cmb_inicial: float,      # K
                 T_manto_inicial: float,    # K (ver nota: ya no se usa en el balance v5.0, se conserva por compatibilidad de firma)
                 cp_core: float = 840.0,    # J/kg/K
                 H_radiogenic: float = 1.5e-12,  # W/kg
                 k_core: float = 40.0,      # W/m/K (ver nota: ya no se usa en el balance v5.0)
                 tau_regen_yr: float = 1e8, # anios
                 C_calib: float = 6.43e-5,  # calibrado para que la Tierra de ~0.31 G superficial
                 k_manto: float = 3.0,      # W/m/K, conductividad del manto
                 regimen_tectonico: int = 1,  # 1 = mobile lid (Tierra), 0 = stagnant lid (Venus/Marte)
                 albedo: float = 0.3):
        self.R_core = R_core
        self.R_planeta = R_planeta
        self.rho_core = rho_core
        self.cp = cp_core
        self.H_radio = H_radiogenic
        self.k_core = k_core
        self.tau_regen = tau_regen_yr * YR_SEC
        self.C_calib = C_calib
        self.k_manto = k_manto
        self.regimen_tectonico = regimen_tectonico
        self.albedo = albedo

        self.M_core = (4.0 / 3.0) * np.pi * (R_core ** 3) * rho_core

        self.T_cmb = T_cmb_inicial
        self.T_manto = T_manto_inicial  # vestigial tras v5.0; se conserva por compatibilidad

        self.q_conv_hist = []
        self.T_hist = []

    def actualizar(self, dt: float, a_ua: float, L_estrella: float = 1.0) -> tuple:
        """
        Actualiza la termodinamica del nucleo un paso temporal, con
        acoplamiento al manto (v5.0).

        Args:
            dt: paso de tiempo en segundos.
            a_ua: distancia orbital actual (UA).
            L_estrella: luminosidad estelar en luminosidades solares.
                        Ver LIMITACION CONOCIDA #4 en la cabecera del modulo.

        Returns:
            q_conv (float): flujo de calor convectivo disponible (W/m^2)
            T_cmb (float): nueva temperatura en el CMB (K)
        """
        a_m = a_ua * UA
        L_sol_W = 3.828e26
        L_estrella_W = L_estrella * L_sol_W
        F_estelar = L_estrella_W / (4.0 * np.pi * (a_m ** 2))

        T_sup = ((1.0 - self.albedo) * F_estelar / (4.0 * SIGMA_SB)) ** (1.0 / 4.0)
        T_sup = max(T_sup, 50.0)

        D_manto = self.R_planeta - self.R_core
        if D_manto <= 0:
            D_manto = 1e6  # evitar division por cero en configuraciones extremas

        factor_lid = 1.0 if self.regimen_tectonico == 1 else 0.35

        Q_CMB = (4.0 * np.pi * (self.R_planeta ** 2) *
                 self.k_manto * (self.T_cmb - T_sup) / D_manto * factor_lid)
        Q_CMB = max(Q_CMB, 0.0)

        Q_radio = self.H_radio * self.M_core
        Q_conv = max(0.0, Q_radio - Q_CMB)
        q_conv = Q_conv / (4.0 * np.pi * (self.R_core ** 2))

        dT_dt = (Q_radio - Q_CMB) / (self.M_core * self.cp)
        self.T_cmb += dT_dt * dt
        self.T_cmb = max(self.T_cmb, 1000.0)

        self.q_conv_hist.append(q_conv)
        self.T_hist.append(self.T_cmb)
        return q_conv, self.T_cmb

    def calcular_B_gen(self, q_conv: float) -> float:
        """
        Campo magnetico generado en el NUCLEO (Tesla), ley de escala de
        Christensen (2009): B ~ rho^(1/3) * (q_conv * R_core)^(2/3)
        """
        if q_conv <= 0:
            return 0.0
        B_nucleo = self.C_calib * (self.rho_core ** (1.0 / 3.0)) * ((q_conv * self.R_core) ** (2.0 / 3.0))
        return float(np.clip(B_nucleo, 0.0, 10.0))

    def calcular_Rm(self, q_conv: float, eta: float) -> float:
        """
        Numero de Reynolds magnetico (Rm = v_conv * R_core / eta).
        Umbral tipico de dinamo activo: Rm > ~40 (Christensen & Aubert).
        """
        if q_conv <= 0 or eta <= 0:
            return 0.0
        v_conv = (q_conv * self.R_core / self.rho_core) ** (1.0 / 3.0)
        return float(v_conv * self.R_core / eta)

    def atenuar_a_superficie(self, B_nucleo_tesla: float, R_p: float) -> float:
        """B_sup ~ B_nucleo * (R_core / R_p)^3"""
        factor = (self.R_core / R_p) ** 3
        return B_nucleo_tesla * factor
