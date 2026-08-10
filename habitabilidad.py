# ============================================================================
# HABITABILIDAD.PY — MHD-INT v3.4 (MHI v2)
# AUTOR: Roney Rigg Mora
#
# Índice de Habitabilidad Magnética y Planetaria (MHI).
# Versión 2 — parámetros ajustados basados en literatura:
# - UMBRAL_R_MP_PROTEGIDO = 5.0 (R_m > 5 R_p, protección significativa)
# - E_MAX_NORMALIZACION = 0.35 (excentricidad límite para estabilidad)
# - Q_TIDAL_BANDA_BAJA_W = 1e12 (flujo ~0.2 W/m² para planeta Tierra)
# - Q_TIDAL_BANDA_ALTA_W = 1e14 (flujo ~2 W/m², límite tipo Ío)
# - Pesos: escudo=0.40, órbita=0.20, campo=0.30, marea=0.10
#
# Referencias:
# - Kopparapu et al. (2013) - zona habitable y excentricidad
# - Heller & Barnes (2013) - habitabilidad de exolunas
# - Peale, Cassen & Reynolds (1979) - calentamiento por marea
# - Driscoll & Barnes (2015) - protección magnética
# ============================================================================

import numpy as np
from models import ResultadoSimulacion

UMBRAL_R_MP_PROTEGIDO = 5.0
E_MAX_NORMALIZACION = 0.35
Q_TIDAL_BANDA_BAJA_W = 1e12
Q_TIDAL_BANDA_ALTA_W = 1e14

PESO_ESCUDO = 0.40
PESO_ORBITA = 0.20
PESO_CAMPO = 0.30
PESO_MAREA = 0.10

UMBRAL_B_CAMPO_ACTIVO_GAUSS = 0.3


def _validar_resultado(resultado: ResultadoSimulacion):
    if not isinstance(resultado, ResultadoSimulacion):
        raise TypeError(f"calcular_mhi() espera un ResultadoSimulacion, recibió {type(resultado).__name__}")
    if not resultado.tiene_serie():
        raise ValueError(
            f"'{resultado.nombre_planeta}' no tiene serie temporal. "
            "Volvé a simular con incluir_serie=True para poder calcular el MHI."
        )


def calcular_mhi(resultado: ResultadoSimulacion) -> dict:
    _validar_resultado(resultado)
    serie = resultado.serie

    r_mp = np.array(serie.R_m_norm)
    tiempo_protegido = float(np.mean(r_mp >= UMBRAL_R_MP_PROTEGIDO) * 100.0)

    e_arr = np.array(serie.e) if serie.e else np.array([resultado.e_inicial])
    e_promedio = float(np.mean(e_arr))
    score_orbital = float(max(0.0, 100.0 * (1.0 - (e_promedio / E_MAX_NORMALIZACION))))

    b_gauss = np.array(serie.B_p_gauss)
    tiempo_campo_activo = float(np.mean(b_gauss >= UMBRAL_B_CAMPO_ACTIVO_GAUSS) * 100.0)

    q_arr = np.array(serie.Q_tidal_watts) if serie.Q_tidal_watts else np.array([0.0])
    q_promedio = float(np.mean(q_arr))
    if q_promedio < Q_TIDAL_BANDA_BAJA_W:
        score_marea = 60.0
    elif q_promedio <= Q_TIDAL_BANDA_ALTA_W:
        score_marea = 100.0
    else:
        score_marea = 20.0

    # NUEVO v5.0: si el planeta perdio la atmosfera (modelo_atmosfera activo)
    # o se estrello, el MHI se fuerza a 0 -- el escudo magnetico no sirve de
    # nada sin atmosfera que proteger.
    atm_perdida = getattr(resultado, "atm_perdida", False)
    if atm_perdida or resultado.se_estrello:
        mhi_bruto = 0.0
        penalizacion_obl = 0.0
    else:
        mhi_bruto = (
            PESO_ESCUDO * tiempo_protegido +
            PESO_ORBITA * score_orbital +
            PESO_CAMPO * tiempo_campo_activo +
            PESO_MAREA * score_marea
        )

        # NUEVO v5.1 (oblicuidad): oblicuidades > 60 grados (clima caotico)
        # o < 5 grados (posible efecto invernadero descontrolado) penalizan
        # el MHI. FIX (informe de revision, A.5): esta penalizacion SOLO se
        # aplica si eps_conocido=True -- es decir, solo para los 5 cuerpos
        # con dato real de oblicuidad (Tierra, Marte, Jupiter, Urano,
        # Venus). Para el resto (incluidos casi todos los exoplanetas), la
        # oblicuidad es un dato desconocido, no un dato bajo -- penalizar
        # por default=0 grados hubiera bajado el MHI de casi todo el
        # dataset ya validado sin ninguna base fisica real.
        eps_conocido = getattr(resultado, "eps_conocido", False)
        eps_final = resultado.eps_final_deg if eps_conocido else None
        if eps_conocido and (eps_final > 60.0 or eps_final < 5.0):
            penalizacion_obl = -20.0
        else:
            penalizacion_obl = 0.0

    mhi_total = mhi_bruto + penalizacion_obl

    return {
        "nombre_planeta": resultado.nombre_planeta,
        "mhi_total": float(np.clip(mhi_total, 0.0, 100.0)),
        # FIX v5.1.1: se expone mhi_bruto (suma de los 4 componentes
        # pesados, antes de penalizaciones) y penalizacion_obl_pts por
        # separado. Antes, la penalizacion se restaba de forma invisible
        # y ningun consumidor (donut, tabla del PDF) tenia como mostrarla
        # -- los componentes graficados sumaban mas que el total mostrado,
        # sin ninguna linea que explicara la diferencia.
        "mhi_bruto": mhi_bruto,
        "penalizacion_obl_pts": penalizacion_obl,
        "escudo_mag_pct": tiempo_protegido,
        "estabilidad_orb": score_orbital,
        "campo_activo_pct": tiempo_campo_activo,
        "score_marea": score_marea,
        "e_promedio": e_promedio,
        "q_promedio_w": q_promedio,
        "se_estrello": resultado.se_estrello,
        "atm_perdida": atm_perdida,
        "M_atm_final_kg": getattr(resultado, "M_atm_final_kg", 0.0),
        "eps_conocido": getattr(resultado, "eps_conocido", False),
        "eps_final_deg": getattr(resultado, "eps_final_deg", 0.0),
    }


def categoria_mhi(score: float) -> str:
    if score >= 80.0:
        return "Alta habitabilidad magnética"
    elif score >= 50.0:
        return "Habitabilidad moderada / límite"
    else:
        return "Estéril / atmósfera expuesta"


def tabla_mhi(resultados) -> list:
    filas = []
    for r in resultados:
        if not isinstance(r, ResultadoSimulacion) or not r.es_valido() or not r.tiene_serie():
            continue
        m = calcular_mhi(r)
        m["categoria"] = categoria_mhi(m["mhi_total"])
        filas.append(m)
    return filas
