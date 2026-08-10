import numpy as np
from numba import njit

# ============================================================================
# CORRECCIÓN v4.1 (integración Cambio 1, 2026-07-24):
# G agregado como constante de módulo. Necesario porque
# calcular_torque_tide_estelar() la usa directamente (Numba con
# nopython=True requiere que sea constante de módulo, no un argumento
# pasado desde engine.py, para poder compilar la función). El resto de las
# funciones del archivo siguen recibiendo G como parámetro explícito (no se
# tocó su firma, para no romper las llamadas ya existentes en engine.py).
# ============================================================================
G = 6.67430e-11


@njit(fastmath=True)
def calcular_presion_ram_numba(a, rho_sw, v_sw, UA):
    factor_escala = (UA / a) ** 2
    return rho_sw * (v_sw ** 2) * factor_escala


@njit(fastmath=True)
def calcular_radio_alfven_numba(a, B_p, P_ram, R_p, MU_0):
    if P_ram <= 0:
        return R_p
    termino = (B_p ** 2) / (2.0 * MU_0 * P_ram)
    R_alfven = R_p * (termino) ** (1.0 / 6.0)
    if R_alfven > a * 0.9:
        return a * 0.9
    return R_alfven


@njit(fastmath=True)
def calcular_torque_magnetico_numba(a, w_p, B_p, P_ram, R_p, w_estrella, MU_0):
    R_alfven = calcular_radio_alfven_numba(a, B_p, P_ram, R_p, MU_0)
    if R_alfven < 1e-12:
        R_alfven = 1e-12
    delta_w = w_p - w_estrella
    B_alfven = B_p * (R_p / R_alfven) ** 3
    tau_0 = 1.2e-3
    tau_mag_mag = tau_0 * (B_alfven ** 2 / MU_0) * (R_alfven ** 3)
    if delta_w > 0:
        tau_mag = -tau_mag_mag
    elif delta_w < 0:
        tau_mag = tau_mag_mag
    else:
        tau_mag = 0.0
    if tau_mag > 1e22:
        return 1e22
    if tau_mag < -1e22:
        return -1e22
    return tau_mag


@njit(fastmath=True)
def calcular_calor_marea_numba(a, e, R_p, M_estrella, k2_sobre_q, G):
    if a <= 0 or e <= 0:
        return 0.0
    n = np.sqrt(G * M_estrella / a ** 3)
    return (21.0 / 2.0) * k2_sobre_q * (R_p ** 5) * (n ** 5) * (e ** 2) / G


@njit(fastmath=True)
def calcular_de_dt_numba(a, e, R_p, M, M_estrella, k2_sobre_q, G):
    if e <= 1e-8 or a <= 0:
        return 0.0
    n = np.sqrt(G * M_estrella / a ** 3)
    return -(21.0 / 2.0) * k2_sobre_q * (M_estrella / M) * ((R_p / a) ** 5) * n * e


@njit(fastmath=True)
def calcular_elsasser_numba(B_p, w_p, rho_core, eta, MU_0):
    w_seguro = max(abs(w_p), 1e-20)
    denominador = MU_0 * rho_core * w_seguro * eta
    if denominador == 0:
        return 1e6
    return (B_p ** 2) / denominador


@njit(fastmath=True)
def calcular_radio_magnetosferico_numba(B_p, P_ram, MU_0):
    if P_ram <= 0:
        return 1.0
    termino = (B_p ** 2) / (2.0 * MU_0 * P_ram)
    return min(termino ** (1.0 / 6.0), 100.0)


@njit(fastmath=True)
def corregir_radio_ohmico_numba(R_m_puro, E_p, ALPHA):
    return R_m_puro * (1.0 + ALPHA * np.tanh(E_p - 1.0))


@njit(fastmath=True)
def calcular_migracion_orbital_numba(a, tiempo_migracion, YR_SEC):
    if tiempo_migracion <= 0:
        return 0.0
    da_dt = -a / tiempo_migracion
    return da_dt


# ============================================================================
# NUEVO v4.1 (Cambio 1, fusionado desde AGREGAR_a_numba_functions.py):
# Torque de marea sólida de la estrella sobre la rotación planetaria
# (Hut 1981). Domina sobre el torque magnético para a < 0.1 UA (Hot
# Jupiters). Usa la G de módulo definida arriba -- no recibe G como
# parámetro porque, a diferencia de las funciones anteriores, así se
# escribió originalmente en el snippet y así la llama engine.py
# (calcular_torque_tide_estelar(k2_Q, M_star, R_p, a, omega_p, n), 6
# argumentos, sin G).
# ============================================================================
@njit(fastmath=True)
def calcular_torque_tide_estelar(k2_Q, M_star, R_p, a, omega_p, n):
    tau0 = 1.5 * k2_Q * G * (M_star ** 2) * (R_p ** 5) / (a ** 6)
    diff = omega_p - n
    if abs(diff) < 1e-15:
        return 0.0
    return -tau0 * np.sign(diff)
