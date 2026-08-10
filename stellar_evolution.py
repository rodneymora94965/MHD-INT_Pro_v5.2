import numpy as np
YR_SEC = 365.25 * 24 * 3600


class EstrellaEvolutiva:
    """
    CORRECCIÓN v4.1 (auditoría 2026-07-22, adenda A.4):
    Antes existían DOS tablas independientes estimando el campo magnético
    estelar de referencia por tipo espectral: estimar_B_estrella() en
    engine.py (escala Tesla, ej. G -> 1e-4 T) y _estimar_B_actual() aquí
    (escala relativa arbitraria, ej. G -> 1.0). Ninguna de las dos alimenta
    P_ram ni tau_mag en la física actual del motor — son vestigiales.

    Se elimina la tabla duplicada. Ahora B_actual se recibe como parámetro
    desde afuera (calculado una sola vez por estimar_B_estrella() en
    engine.py), en Tesla, consistente con el resto del modelo. Si en el
    futuro se decide usar B_estrella en algún cálculo físico (ej. escalar
    la presión de viento con el campo estelar real), ya queda en unidades
    correctas y con una sola fuente de verdad.
    """

    def __init__(self, nombre, masa_kg, tipo_espectral, edad_actual_gyr=4.6,
                 B_inicial_tesla=1.0e-4):
        self.nombre = nombre
        self.masa = masa_kg
        self.tipo = tipo_espectral.strip().upper()
        self.edad_actual = edad_actual_gyr
        self.omega_actual = 2.9e-6
        self.B_actual = B_inicial_tesla  # <-- antes: self._estimar_B_actual()
        self.rho_0 = None
        self.v_0 = None

    def set_viento_base(self, rho_sw_actual, v_sw_actual):
        self.rho_0 = rho_sw_actual
        self.v_0 = v_sw_actual

    def evolucionar(self, t_gyr, a_ua=None):
        if self.rho_0 is None or self.v_0 is None:
            raise ValueError("Debes llamar set_viento_base() antes de evolucionar().")
        if t_gyr <= 0:
            omega_t = self.omega_actual
            B_t = self.B_actual
            rho_t = self.rho_0
            v_t = self.v_0
        else:
            if self.tipo.startswith('M'):
                factor_rot = ((self.edad_actual + t_gyr) / self.edad_actual) ** -0.3
            else:
                factor_rot = ((self.edad_actual + t_gyr) / self.edad_actual) ** -0.5
            omega_t = self.omega_actual * factor_rot
            omega_t = max(omega_t, 0.1 * self.omega_actual)
            if self.tipo.startswith('M'):
                B_t = self.B_actual
            else:
                B_t = self.B_actual * (omega_t / self.omega_actual)
            rho_t = self.rho_0 * (omega_t / self.omega_actual) ** 2.0
            v_t = self.v_0 * (omega_t / self.omega_actual) ** 0.3
        if a_ua is not None and a_ua > 0:
            rho_t = rho_t / (a_ua ** 2)
        return omega_t, B_t, rho_t, v_t
