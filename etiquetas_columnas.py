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

# Usadas por exportar_csv.py (serie_a_dataframe / resumen_a_dataframe).
ETIQUETAS_SERIE_TEMPORAL = {
    "planeta": "Planeta",
    "tiempos": "Tiempo (Gyr)",
    "a_ua": "Distancia orbital (UA)",
    "w_p": "Velocidad angular (rad/s)",
    "B_p_gauss": "Campo magnético (G)",
    "E_p": "Número de Elsasser",
    "R_m_norm": "Reynolds magnético (normalizado)",
    "tau_mag": "Torque magnético (N·m)",
    "tiempo_migracion": "Tiempo de migración",
    "e": "Excentricidad",
    "Q_tidal_watts": "Disipación de marea (W)",
    "a_luna_ua": "Distancia de la luna (UA)",
    "T_cmb_K": "Temp. núcleo-manto (K)",
    "B_gen_gauss": "Campo generado en el núcleo (G)",
    "Rm_num": "Reynolds magnético (núcleo)",
    "q_conv": "Flujo convectivo",
    "M_atm_kg": "Masa de atmósfera (kg)",
    "atm_perdida": "Atmósfera perdida",
    "eps_deg": "Oblicuidad (°)",
}

ETIQUETAS_RESUMEN_SIMULACION = {
    "planeta": "Planeta",
    "nombre_planeta": "Nombre interno",
    "a_inicial_ua": "Distancia inicial (UA)",
    "a_final_ua": "Distancia final (UA)",
    "w_inicial": "Velocidad angular inicial (rad/s)",
    "w_final": "Velocidad angular final (rad/s)",
    "B_inicial_gauss": "Campo magnético inicial (G)",
    "B_final_gauss": "Campo magnético final (G)",
    "P_rot_inicial_dias": "Período de rotación inicial (días)",
    "P_rot_final_dias": "Período de rotación final (días)",
    "E_p_final": "Número de Elsasser final",
    "R_m_norm_final": "Reynolds magnético final (normalizado)",
    "tau_mag_final": "Torque magnético final (N·m)",
    "tiempo_migracion_final": "Tiempo de migración final",
    "campo_protegido": "Campo magnético protector",
    "se_estrello": "Se estrelló contra la estrella",
    "e_inicial": "Excentricidad inicial",
    "e_final": "Excentricidad final",
    "Q_tidal_final_watts": "Disipación de marea final (W)",
    "a_luna_inicial_ua": "Distancia inicial de la luna (UA)",
    "a_luna_final_ua": "Distancia final de la luna (UA)",
    "recesion_lunar_cm_anio": "Recesión lunar (cm/año)",
    "T_cmb_final_K": "Temp. núcleo-manto final (K)",
    "B_gen_final_gauss": "Campo generado final (G)",
    "Rm_final": "Reynolds magnético final (núcleo)",
    "q_conv_final": "Flujo convectivo final",
    "M_atm_final_kg": "Masa de atmósfera final (kg)",
    "atm_perdida": "Atmósfera perdida",
    "eps_final_deg": "Oblicuidad final (°)",
    "eps_conocido": "Oblicuidad con respaldo observacional",
    "error": "Error",
}


def con_nombres_legibles(df, mapeo: dict):
    """Devuelve una COPIA del DataFrame con las columnas conocidas
    renombradas para mostrar/exportar. Las columnas que no estén en
    el mapeo se dejan tal cual (para no ocultar datos nuevos que
    todavía no se agregaron al diccionario)."""
    return df.rename(columns=mapeo)
