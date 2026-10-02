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
from concurrent.futures import ProcessPoolExecutor, as_completed
from engine import simular_planeta, UA
from database import PLANETAS
from habitabilidad import calcular_mhi
from progreso_util import invocar_callback  # Sugerencia 4: logs en vivo (fracción 0-1 + mensaje opcional)


def _simular_punto_mapa(args: tuple) -> dict:
    """
    Simula UN punto de la malla (a, B_p). Función de MÓDULO (no un
    closure/lambda de generar_mapa_mhi) a propósito -- ProcessPoolExecutor
    necesita "picklear" la función para mandarla a cada proceso hijo, y
    eso solo funciona con funciones importables por nombre desde el
    módulo, no con funciones anidadas.

    Reproduce EXACTAMENTE la misma lógica que tenía el loop secuencial
    (mismo manejo de errores, mismos valores por defecto en cada caso)
    -- ver generar_mapa_mhi() más abajo para el porqué de cada rama.
    """
    planeta_base, a_ua, B_G, t_max_gyr, dt_yr, max_puntos_serie = args
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
            fila.update({"MHI_total": 0.0, "se_estrello": r.se_estrello,
                         "campo_protegido": False})
    except Exception:
        fila.update({"MHI_total": np.nan, "se_estrello": None, "campo_protegido": None})
    return fila


def generar_mapa_mhi(planeta_base: str,
                      rango_a_ua: tuple,
                      rango_B_gauss: tuple,
                      n_pasos_a: int = 10,
                      n_pasos_B: int = 10,
                      t_max_gyr: float = 5.0,
                      dt_yr: float = 50000.0,
                      max_puntos_serie: int = 200,
                      progress_callback=None,
                      paralelo: bool = True,
                      max_workers: int = None) -> pd.DataFrame:
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
        paralelo: si True (default), usa ProcessPoolExecutor -- una
            malla de 25x25 (625 simulaciones) baja de 10+ minutos a
            1-2 en una máquina de 4+ núcleos. Si False, corre secuencial
            (más lento, pero sin el overhead de arrancar procesos --
            útil para grillas chicas o debugging).
        max_workers: cantidad de procesos: None = os.cpu_count().

    Returns:
        DataFrame con columnas: a_ua, B_G, MHI_total, se_estrello,
        campo_protegido. MHI_total = NaN si la simulación fue inválida
        o lanzó una excepción (no se descarta la fila, queda marcada).
    """
    if planeta_base not in PLANETAS:
        raise KeyError(f"'{planeta_base}' no está en la base de datos.")

    a_vals = np.linspace(rango_a_ua[0], rango_a_ua[1], n_pasos_a)
    B_vals = np.linspace(rango_B_gauss[0], rango_B_gauss[1], n_pasos_B)
    puntos = [(planeta_base, float(a_ua), float(B_G), t_max_gyr, dt_yr, max_puntos_serie)
              for a_ua in a_vals for B_G in B_vals]
    total = max(len(puntos), 1)

    if not paralelo or total <= 4:
        # Grillas chiquitas: el overhead de arrancar procesos (sobre todo
        # en Windows, que usa "spawn" -- cada worker reimporta todo el
        # proyecto desde cero) puede pesar más que la simulación en sí.
        # No vale la pena paralelizar 4 puntos o menos.
        resultados = []
        for i, args in enumerate(puntos, start=1):
            resultados.append(_simular_punto_mapa(args))
            if progress_callback:
                a_ua, B_G = args[1], args[2]
                invocar_callback(
                    progress_callback, i / total,
                    f"Calculando MHI del punto {i}/{total} (a={a_ua:.3f} UA, B={B_G:.3f} G)...",
                )
        return pd.DataFrame(resultados)

    resultados = [None] * len(puntos)
    contador = 0
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futuros = {executor.submit(_simular_punto_mapa, args): i
                   for i, args in enumerate(puntos)}
        for futuro in as_completed(futuros):
            idx = futuros[futuro]
            resultados[idx] = futuro.result()
            contador += 1
            if progress_callback:
                a_ua, B_G = puntos[idx][1], puntos[idx][2]
                invocar_callback(
                    progress_callback, contador / total,
                    f"Calculando MHI del punto {contador}/{total} (a={a_ua:.3f} UA, B={B_G:.3f} G)...",
                )

    return pd.DataFrame(resultados)


if __name__ == "__main__":
    df = generar_mapa_mhi("Tierra", (0.5, 2.0), (0.0, 2.0), n_pasos_a=15, n_pasos_B=15)
    df.to_csv("mapa_mhi_Tierra.csv", index=False)
    print(f"Guardado: mapa_mhi_Tierra.csv ({len(df)} simulaciones, "
          f"{df['MHI_total'].isna().sum()} fallidas)")
