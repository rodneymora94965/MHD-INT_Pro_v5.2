# historial.py
# MHD-INT v5.1 - Sistema de historial de simulaciones
# Licencia AGPL-3.0

import pandas as pd
import os
from datetime import datetime

ARCHIVO_HISTORIAL = "historial_simulaciones.csv"

# CAMBIO (ago-2026): se agrega sesion_id. Necesario para el despliegue
# como demo/beta pública en Streamlit Cloud: TODOS los visitantes
# comparten el mismo historial_simulaciones.csv en el disco del
# servidor -- sin esta columna, cualquiera que abra "Ver historial"
# vería (y podría borrar) las simulaciones de todos los demás
# visitantes. sesion_id=None (comportamiento viejo) sigue andando para
# uso local de un solo usuario.
COLUMNAS = [
    "timestamp", "sesion_id", "planeta", "t_max_gyr", "dt_yr",
    "modelo_termico", "modelo_atmosfera",
    "B_final_gauss", "MHI_total", "atm_perdida",
    "T_cmb_final_K", "Rm_final",
]


def inicializar_historial():
    """Crea el archivo de historial si no existe. Si existe pero es de
    una version anterior sin sesion_id, la agrega vacia (compatible
    hacia atras con historiales locales viejos)."""
    if not os.path.exists(ARCHIVO_HISTORIAL):
        df = pd.DataFrame(columns=COLUMNAS)
        df.to_csv(ARCHIVO_HISTORIAL, index=False)
        return df
    df = pd.read_csv(ARCHIVO_HISTORIAL)
    if "sesion_id" not in df.columns:
        df["sesion_id"] = None
    return df


def guardar_simulacion(resultado, params, mhi=None, sesion_id=None):
    """
    Guarda una simulacion en el historial.
    resultado: ResultadoSimulacion ya calculado.
    params: dict con planeta, t_max_gyr, dt_yr, modelo_termico, modelo_atmosfera.
    mhi: dict ya calculado por calcular_mhi() (opcional). Si no se pasa, se
         recalcula aqui -- se prefiere pasarlo para no calcularlo dos veces.
    sesion_id: identificador de la sesion de Streamlit que genero esta
               simulacion (ver sesion.py). None = comportamiento viejo,
               sin aislar por usuario (uso local de un solo usuario).
    """
    df = inicializar_historial()
    if mhi is None and resultado.tiene_serie():
        from habitabilidad import calcular_mhi
        mhi = calcular_mhi(resultado)

    nueva_fila = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sesion_id": sesion_id,
        "planeta": params.get("planeta", resultado.nombre_planeta),
        "t_max_gyr": params.get("t_max_gyr", 5.0),
        "dt_yr": params.get("dt_yr", 10000),
        "modelo_termico": params.get("modelo_termico", False),
        "modelo_atmosfera": params.get("modelo_atmosfera", False),
        "B_final_gauss": resultado.B_final_gauss if resultado.es_valido() else None,
        "MHI_total": mhi["mhi_total"] if mhi else None,
        "atm_perdida": getattr(resultado, "atm_perdida", False),
        "se_estrello": resultado.se_estrello if resultado.es_valido() else None,
        "T_cmb_final_K": getattr(resultado, "T_cmb_final_K", 0.0),
        "Rm_final": getattr(resultado, "Rm_final", 0.0),
    }
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_csv(ARCHIVO_HISTORIAL, index=False)
    return nueva_fila


def cargar_historial(sesion_id=None):
    """Carga el historial como DataFrame.
    sesion_id=None (default): historial completo -- SOLO para uso
        local de un usuario o para el propio Roney auditando el
        deploy. NO usar este default en una pantalla pública.
    sesion_id="algo": solo las filas de esa sesion -- lo que debe usar
        cualquier pantalla que un visitante de la demo pueda ver."""
    df = inicializar_historial()
    if sesion_id is None:
        return df
    if "sesion_id" not in df.columns:
        return df.iloc[0:0]
    return df[df["sesion_id"] == sesion_id].reset_index(drop=True)


def borrar_historial(sesion_id=None):
    """Elimina historial.
    sesion_id=None (default): borra TODO el archivo -- destructivo,
        solo para uso local de un usuario. En una demo pública, cada
        visitante debe borrar unicamente su propia sesion_id.
    sesion_id="algo": borra solo las filas de esa sesion, conserva el
        resto."""
    if sesion_id is None:
        if os.path.exists(ARCHIVO_HISTORIAL):
            os.remove(ARCHIVO_HISTORIAL)
        inicializar_historial()
        return
    df = inicializar_historial()
    if "sesion_id" in df.columns:
        df = df[df["sesion_id"] != sesion_id]
    df.to_csv(ARCHIVO_HISTORIAL, index=False)
