"""
mapa_mhi.py

MEJORA v4.1 (Mejora 1): mapa de calor 2D del Índice de Habitabilidad
Magnética y Planetaria (MHI) variando distancia orbital (a) y campo
magnético inicial (B_p), con el resto de los parámetros del planeta
base fijos tal como están en database.py.

CORRECCIÓN sobre el paquete original: el pseudocódigo pedía
incluir_serie=False para ahorrar tiempo, pero calcular_mhi() necesita
la serie temporal (R_m_norm, e, B_p_gauss, Q_tidal_watts) para poder
calcular el índice. Se deja incluir_serie=True con max_puntos_serie
bajo (200 por defecto) para no disparar el costo de memoria en una
grilla de decenas o cientos de simulaciones.

Script independiente (no depende de streamlit): se puede correr por
línea de comandos y guarda un CSV. app_streamlit.py lo importa para
mostrarlo como mapa de calor en el modo "Mapa MHI".
"""
import numpy as np
import pandas as pd
from engine import simular_planeta, UA
from database import PLANETAS
from habitabilidad import calcular_mhi


def generar_mapa_mhi(planeta_base: str,
                      rango_a_ua: tuple,
                      rango_B_gauss: tuple,
                      n_pasos_a: int = 10,
                      n_pasos_B: int = 10,
                      t_max_gyr: float = 5.0,
                      dt_yr: float = 50000.0,
                      max_puntos_serie: int = 200,
                      progress_callback=None) -> pd.DataFrame:
    """
    Genera un mapa de MHI variando distancia orbital (a) y campo
    magnético inicial (B_p). El resto de los parámetros del planeta
    (masa, radio, estrella, tipo, etc.) quedan como están en
    database.PLANETAS[planeta_base] — no se tocan.

    Args:
        planeta_base: debe existir en database.PLANETAS.
        rango_a_ua: (min, max) en UA.
        rango_B_gauss: (min, max) en Gauss.
        n_pasos_a, n_pasos_B: resolución de la malla (total = producto).
        t_max_gyr, dt_yr: igual que simular_planeta.
        max_puntos_serie: puntos de serie por simulación (bajo, para
            no acumular demasiada memoria en grillas grandes).
        progress_callback: opcional, function(fraccion_completada: float),
            para conectar a una barra de progreso (ej. en Streamlit).

    Returns:
        DataFrame con columnas: a_ua, B_G, MHI_total, se_estrello,
        campo_protegido. MHI_total = NaN si la simulación fue inválida
        o lanzó una excepción (no se descarta la fila, queda marcada).
    """
    if planeta_base not in PLANETAS:
        raise KeyError(f"'{planeta_base}' no está en la base de datos.")

    a_vals = np.linspace(rango_a_ua[0], rango_a_ua[1], n_pasos_a)
    B_vals = np.linspace(rango_B_gauss[0], rango_B_gauss[1], n_pasos_B)
    total = max(len(a_vals) * len(B_vals), 1)

    resultados = []
    contador = 0
    for a_ua in a_vals:
        for B_G in B_vals:
            extra = {
                "a_inicial": float(a_ua) * UA,
                "B_p_inicial": float(B_G) * 1e-4,
            }
            fila = {"a_ua": round(float(a_ua), 4), "B_G": round(float(B_G), 4)}
            try:
                r = simular_planeta(
                    planeta_base, t_max_gyr=t_max_gyr, dt_yr=dt_yr,
                    incluir_serie=True, max_puntos_serie=max_puntos_serie,
                    parametros_extra=extra,
                )
                if r.es_valido() and r.tiene_serie():
                    mhi = calcular_mhi(r)
                    fila.update({
                        "MHI_total": round(mhi["mhi_total"], 2),
                        "se_estrello": r.se_estrello,
                        "campo_protegido": r.campo_protegido,
                    })
                else:
                    # Simulación corrió pero sin serie válida (ej. se
                    # estrelló antes del primer punto registrado): MHI 0,
                    # no NaN, porque sabemos que no hay habitabilidad.
                    fila.update({"MHI_total": 0.0, "se_estrello": r.se_estrello,
                                 "campo_protegido": False})
            except Exception:
                # Falla real del motor con esta combinación de parámetros:
                # se marca NaN (no 0.0) para no confundir "no habitable"
                # con "no se pudo calcular".
                fila.update({"MHI_total": np.nan, "se_estrello": None, "campo_protegido": None})

            resultados.append(fila)
            contador += 1
            if progress_callback:
                progress_callback(contador / total)

    return pd.DataFrame(resultados)


if __name__ == "__main__":
    df = generar_mapa_mhi("Tierra", (0.5, 2.0), (0.0, 2.0), n_pasos_a=15, n_pasos_B=15)
    df.to_csv("mapa_mhi_Tierra.csv", index=False)
    print(f"Guardado: mapa_mhi_Tierra.csv ({len(df)} simulaciones, "
          f"{df['MHI_total'].isna().sum()} fallidas)")
