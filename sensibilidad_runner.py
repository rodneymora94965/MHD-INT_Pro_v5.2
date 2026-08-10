"""
sensibilidad_runner.py (antes: mcmc_runner.py)

CORRECCIÓN v4.1 (auditoría 2026-07-22, hallazgo #6):
Este módulo NO implementa MCMC (Markov Chain Monte Carlo). MCMC requiere una
cadena con criterio de aceptación/rechazo (ej. Metropolis-Hastings) para
muestrear una distribución posterior condicionada a datos observacionales.

Lo que este módulo hace es muestreo Monte Carlo simple: perturbaciones
gaussianas independientes sobre k2_sobre_q y densidad_nucleo, sin cadena,
sin verosimilitud, sin distribución posterior. Es un análisis de
sensibilidad/incertidumbre paramétrica legítimo y útil, pero el nombre
original prometía una metodología distinta a la implementada — el mismo
patrón de "nombre que promete más de lo que hay" identificado y cerrado
en el proyecto TUM.

Se renombra el archivo y la función interna se mantiene igual
(analisis_sensibilidad) para no romper compatibilidad con quien ya la usa.
"""
import numpy as np
import pandas as pd
from engine import simular_planeta, UA
from database import PLANETAS


# Parámetros que necesitan conversión de unidades al pasarlos como
# parametros_extra (el motor trabaja en SI: metros, Tesla, radianes/seg).
# Cualquier otro parámetro se pasa tal cual (ya está en las unidades del
# diccionario PLANETAS en database.py).
_CONVERSIONES = {
    "a_inicial": lambda ua: ua * UA,          # UA -> metros
    "B_p_inicial": lambda gauss: gauss * 1e-4,  # Gauss -> Tesla
}


def analisis_sensibilidad_extendido(nombre_planeta: str,
                                     param_a_variar: str,
                                     rango: tuple,
                                     n_runs: int = 50,
                                     t_max_gyr: float = 5.0,
                                     dt_yr: float = 50000.0) -> pd.DataFrame:
    """
    MEJORA v4.1 (Mejora 3): generaliza analisis_sensibilidad para variar
    UN parámetro cualquiera del planeta en un rango, en vez de solo
    k2_sobre_q y densidad_nucleo con perturbación gaussiana fija.

    Args:
        nombre_planeta: debe existir en database.PLANETAS.
        param_a_variar: nombre del campo en PLANETAS[nombre_planeta] a
            variar. Ej: 'a_inicial' (en UA), 'B_p_inicial' (en Gauss),
            'M', 'R_p', 'w_p_inicial', 'densidad_nucleo', 'k2_sobre_q', etc.
            Usar las unidades "humanas" para 'a_inicial' y 'B_p_inicial'
            (UA y Gauss respectivamente); el resto en las unidades SI que
            ya usa database.py.
        rango: (min, max) del parámetro, en las unidades indicadas arriba.
        n_runs: cantidad de puntos entre min y max (linspace).

    Returns:
        DataFrame con una fila por corrida: el valor del parámetro variado
        + las métricas finales de la simulación.
    """
    if nombre_planeta not in PLANETAS:
        raise KeyError(f"'{nombre_planeta}' no está en la base de datos.")

    valores = np.linspace(rango[0], rango[1], n_runs)
    convertir = _CONVERSIONES.get(param_a_variar, lambda x: x)

    resultados = []
    for val in valores:
        extra = {param_a_variar: convertir(val)}
        try:
            r = simular_planeta(nombre_planeta, t_max_gyr=t_max_gyr, dt_yr=dt_yr,
                                 incluir_serie=False, parametros_extra=extra)
        except Exception as e:
            resultados.append({param_a_variar: val, "error": str(e)})
            continue
        if not (r.es_valido() and not np.isnan(r.B_final_gauss) and
                not np.isinf(r.B_final_gauss) and r.a_final_ua > 0.001):
            resultados.append({param_a_variar: val, "error": "resultado inválido/no físico"})
            continue
        resultados.append({
            param_a_variar: val,
            "B_final_gauss": r.B_final_gauss,
            "a_final_ua": r.a_final_ua,
            "P_rot_final_dias": r.P_rot_final_dias,
            "e_final": r.e_final,
            "campo_protegido": r.campo_protegido,
            "se_estrello": r.se_estrello,
            "error": None,
        })

    return pd.DataFrame(resultados)


def analisis_sensibilidad(nombre_planeta: str,
                           t_max_gyr: float = 5.0,
                           dt_yr: float = 50000.0,
                           n_runs: int = 100,
                           seed: int = 42) -> pd.DataFrame:
    """
    Muestreo Monte Carlo simple (NO MCMC) de la sensibilidad del resultado
    final a incertidumbre en k2_sobre_q y densidad_nucleo. Cada corrida es
    independiente; no hay cadena ni criterio de aceptación/rechazo.
    """
    if nombre_planeta not in PLANETAS:
        raise KeyError(f"'{nombre_planeta}' no está en la base de datos.")

    rng = np.random.default_rng(seed)
    datos = PLANETAS[nombre_planeta]
    R_p = datos.get('R_p')
    R_TIERRA = 6.371e6
    k2_Q_base = datos.get('k2_sobre_q', 0.015 if R_p < 3.0 * R_TIERRA else 1.0e-5)
    rho_core_base = datos.get('densidad_nucleo', 10000.0)

    resultados = []
    for _ in range(n_runs):
        k2_sobre_q = float(np.clip(k2_Q_base * (1.0 + 0.3 * rng.standard_normal()), 1e-6, 0.05))
        rho_core = float(np.clip(rho_core_base * (1.0 + 0.1 * rng.standard_normal()), 5000, 15000))
        extra = {'k2_sobre_q': k2_sobre_q, 'densidad_nucleo': rho_core}
        r = simular_planeta(nombre_planeta, t_max_gyr=t_max_gyr, dt_yr=dt_yr,
                             incluir_serie=False, parametros_extra=extra)
        if (r.es_valido() and not np.isnan(r.B_final_gauss) and
                not np.isinf(r.B_final_gauss) and r.a_final_ua > 0.001):
            resultados.append({
                'B_final_gauss': r.B_final_gauss,
                'a_final_ua': r.a_final_ua,
                'P_rot_final_dias': r.P_rot_final_dias,
                'e_final': r.e_final,
                'campo_protegido': r.campo_protegido,
                'se_estrello': r.se_estrello,
                'k2_sobre_q_usado': k2_sobre_q,
                'rho_core_usado': rho_core,
            })

    return pd.DataFrame(resultados)
