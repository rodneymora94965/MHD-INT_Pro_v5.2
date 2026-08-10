# exportar_video.py
# MHD-INT v5.1.1 - Exportacion JSON para IAs de video (Manim, Blender, Sora)
# Licencia AGPL-3.0
#
# Implementa el esquema descrito en el documento de spec de Roney
# (JSON_salida_IAs_video v1.0, jul-2026). Se agrego como funcion aparte
# (no directamente en app_streamlit.py) para poder testearla y reusarla
# sin depender de la interfaz.
#
# FIX v5.1.1: el esquema JSON se definio (jul-2026) antes de que existiera
# la oblicuidad como variable dinamica (v5.1). eps_deg nunca se agrego al
# payload por punto, asi que cualquier consumidor de este JSON (incluida
# la Capa 1 de video de MHD-INT Pro) no tenia forma de graficar oblicuidad
# real -- quedaba silenciosamente en 0 para todos los frames. Se agrega
# aqui el campo por punto y la bandera eps_conocido en meta, siguiendo el
# mismo principio que el resto del archivo: el consumidor debe poder
# distinguir "el dato es 0" de "el dato no es conocido/valido".

import numpy as np

M_ATM_TIERRA_KG = 5.15e18  # masa de la atmosfera terrestre (ver database.py / atmosfera.py)
MAX_PUNTOS_DEFAULT = 2000


def _submuestrear_indices(n_total: int, max_puntos: int) -> list:
    """
    Devuelve los indices a conservar para no exceder max_puntos, manteniendo
    siempre el primer y el ultimo punto de la serie.
    """
    if n_total <= max_puntos:
        return list(range(n_total))
    idx = np.linspace(0, n_total - 1, max_puntos)
    return sorted(set(int(round(i)) for i in idx))


def construir_json_video(resultado, planeta: str, t_max_gyr: float, dt_yr: float,
                          max_puntos: int = MAX_PUNTOS_DEFAULT) -> dict:
    """
    Construye el dict que se serializa como JSON para IAs de video, según
    el esquema documentado. resultado debe tener tiene_serie()=True.

    Nota: si el modelo termico y/o de atmosfera estaban DESACTIVADOS en la
    simulacion, los campos B_gen_Gauss, Rm, T_cmb_K, M_atm_Tierras van a
    salir en 0.0 para todos los pasos -- eso es consistente con el resto
    del proyecto (no se inventa un valor si el modelo no corrio), no es un
    bug de esta exportacion.
    """
    if not resultado.tiene_serie():
        raise ValueError(
            f"'{resultado.nombre_planeta}' no tiene serie temporal. "
            "Volvé a simular con incluir_serie=True para poder exportar."
        )

    serie = resultado.serie
    n_total = len(serie)
    indices = _submuestrear_indices(n_total, max_puntos)

    serie_temporal = []
    for i in indices:
        w_p = serie.w_p[i]
        P_rot_dias = float(2.0 * np.pi / abs(w_p) / (24 * 3600)) if abs(w_p) > 1e-20 else None

        serie_temporal.append({
            "t_Gyr": round(float(serie.tiempos[i]), 6),
            "a_ua": round(float(serie.a_ua[i]), 6),
            "B_p_Gauss": round(float(serie.B_p_gauss[i]), 6),
            "B_gen_Gauss": round(float(serie.B_gen_gauss[i]), 6) if serie.B_gen_gauss else 0.0,
            "Rm": round(float(serie.Rm_num[i]), 3) if serie.Rm_num else 0.0,
            "T_cmb_K": round(float(serie.T_cmb_K[i]), 2) if serie.T_cmb_K else 0.0,
            "M_atm_Tierras": round(float(serie.M_atm_kg[i]) / M_ATM_TIERRA_KG, 6) if serie.M_atm_kg else 0.0,
            "e": round(float(serie.e[i]), 6),
            "w_p_rad_s": float(serie.w_p[i]),
            "P_rot_dias": round(P_rot_dias, 6) if P_rot_dias is not None else None,
            "eps_deg": round(float(serie.eps_deg[i]), 3) if serie.eps_deg else 0.0,
        })

    return {
        "meta": {
            "planeta": planeta,
            "t_max_gyr": t_max_gyr,
            "dt_yr": dt_yr,
            "se_estrello": bool(resultado.se_estrello),
            "atm_perdida": bool(getattr(resultado, "atm_perdida", False)),
            # NUEVO v5.1.1: distingue "eps_deg trae un valor dinamico interno
            # del integrador" de "eps_deg es un dato con respaldo observacional
            # o fijado a proposito por el usuario". Ver nota eps_conocido en
            # habitabilidad.py y models.py (v5.1).
            "eps_conocido": bool(getattr(resultado, "eps_conocido", False)),
            "puntos_originales": n_total,
            "puntos_exportados": len(indices),
        },
        "serie_temporal": serie_temporal,
    }
