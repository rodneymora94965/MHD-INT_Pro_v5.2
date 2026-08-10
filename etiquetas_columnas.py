# ===================================================================
# etiquetas_columnas.py
# Traduce nombres internos de columnas (los que usa el motor y los
# archivos CSV guardados en disco) a nombres legibles SOLO para lo
# que ve el usuario -- tablas en pantalla y CSV/Excel descargados.
#
# IMPORTANTE: nunca tocar el CSV guardado en disco (historial_
# simulaciones.csv) con estos nombres. Si se renombran ahí, dejan
# de coincidir con COLUMNAS en historial.py y se rompe la carga de
# historiales viejos. Este módulo solo se usa al mostrar/exportar,
# nunca al guardar.
# ===================================================================

ETIQUETAS_HISTORIAL = {
    "timestamp": "Fecha y hora",
    "planeta": "Planeta",
    "t_max_gyr": "Tiempo simulado (Gyr)",
    "dt_yr": "Paso de tiempo (años)",
    "modelo_termico": "Modelo térmico activo",
    "modelo_atmosfera": "Modelo de atmósfera activo",
    "B_final_gauss": "Campo magnético final (G)",
    "MHI_total": "Índice de habitabilidad magnética (MHI)",
    "atm_perdida": "Atmósfera perdida",
    "se_estrello": "Se estrelló contra la estrella",
    "T_cmb_final_K": "Temp. núcleo-manto final (K)",
    "Rm_final": "Reynolds magnético final (Rm)",
}

ETIQUETAS_MAPA_MHI = {
    "a_ua": "Distancia orbital (UA)",
    "B_G": "Campo magnético inicial (G)",
    "MHI_total": "Índice de habitabilidad magnética (MHI)",
    "se_estrello": "Se estrelló contra la estrella",
    "campo_protegido": "Campo magnético protector",
}


def con_nombres_legibles(df, mapeo: dict):
    """Devuelve una COPIA del DataFrame con las columnas conocidas
    renombradas para mostrar/exportar. Las columnas que no estén en
    el mapeo se dejan tal cual (para no ocultar datos nuevos que
    todavía no se agregaron al diccionario)."""
    return df.rename(columns=mapeo)
