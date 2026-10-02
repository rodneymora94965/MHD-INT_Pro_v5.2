# sanity_check.py
# MHD-INT — Chequeo de coherencia física de datos de exoplanetas
# Licencia AGPL-3.0. Lógica pura, sin streamlit.
#
# Valida que masa/radio/semieje/período de un planeta sean físicamente
# plausibles ANTES de integrarlo a database.py -- pero solo con
# ADVERTENCIAS, nunca bloqueando: un dato raro puede ser real (los
# exoplanetas conocidos incluyen casos extremos de verdad). Bloquea
# únicamente cuando el dato es imposible por definición (masa o radio
# negativos o cero), que es corrupción de datos, no rareza física.
#
# RANGO DE DENSIDAD: el rango típico "manual de libro" es ~0.3-25 g/cm³,
# pero hay exoplanetas confirmados fuera de ese rango -- Kepler-51b/c/d
# ("algodón de azúcar") tienen densidades medidas de ~0.1 g/cm³. El piso
# se bajó a 0.05 g/cm³ (margen bajo el caso extremo real conocido) para
# no marcar como sospechoso un dato que podría ser genuino.
DENSIDAD_MIN_G_CM3 = 0.05
DENSIDAD_MAX_G_CM3 = 25.0
KEPLER_TOLERANCIA = 0.30  # 30% de margen -- es un chequeo grueso, no una validación orbital fina

UA_M = 1.495978707e11
MSUN_KG = 1.98847e30
M_TIERRA_KG = 5.972e24
R_TIERRA_M = 6.371e6


def _densidad_g_cm3(masa_kg: float, radio_m: float) -> float:
    volumen_m3 = (4.0 / 3.0) * 3.141592653589793 * radio_m ** 3
    densidad_kg_m3 = masa_kg / volumen_m3
    return densidad_kg_m3 / 1000.0  # kg/m^3 -> g/cm^3


def _periodo_kepler_anios(a_m: float, m_estrella_kg: float) -> float:
    """Tercera ley de Kepler, forma simplificada P²=a³/M (P en años,
    a en UA, M en masas solares) -- ignora la masa del planeta a
    propósito, es despreciable frente a la de la estrella en el 99% de
    los casos y esto es un chequeo grueso, no una validación orbital fina."""
    a_ua = a_m / UA_M
    m_sol = m_estrella_kg / MSUN_KG
    if m_sol <= 0:
        return float("nan")
    return (a_ua ** 3 / m_sol) ** 0.5


def validar_coherencia(datos_planeta: dict, masa_estrella_kg: float = None) -> dict:
    """
    Valida coherencia física de un planeta. NO modifica datos_planeta.

    datos_planeta: dict con al menos M (kg), R_p (m), a_inicial (m);
        opcionalmente periodo_dias para el chequeo de Kepler.
    masa_estrella_kg: si se da, habilita el chequeo de la 3ª ley de
        Kepler contra periodo_dias (si también está presente).

    Returns:
        dict con:
        - "coherente": bool -- False SOLO si hay un valor imposible
          (masa/radio/semieje <= 0). Esto sí bloquea, es dato corrupto.
        - "advertencias": list[str] -- rarezas físicas que NO bloquean,
          para que quien revisa decida si el dato es real o un error.
    """
    advertencias = []

    M = datos_planeta.get("M")
    R_p = datos_planeta.get("R_p")
    a_inicial = datos_planeta.get("a_inicial")

    # ---- Bloqueo real: valores imposibles, no raros ----
    if M is None or M <= 0:
        return {"coherente": False, "advertencias": ["Masa (M) ausente, negativa o cero -- dato inválido."]}
    if R_p is None or R_p <= 0:
        return {"coherente": False, "advertencias": ["Radio (R_p) ausente, negativo o cero -- dato inválido."]}
    if a_inicial is not None and a_inicial <= 0:
        return {"coherente": False, "advertencias": ["Semieje (a_inicial) negativo o cero -- dato inválido."]}

    # ---- Advertencias: raro pero puede ser real, no bloquea ----
    densidad = _densidad_g_cm3(M, R_p)
    if densidad < DENSIDAD_MIN_G_CM3:
        advertencias.append(
            f"Densidad muy baja ({densidad:.3f} g/cm³, mínimo esperado "
            f"{DENSIDAD_MIN_G_CM3} g/cm³) -- revisar unidades de M/R_p. "
            f"Puede ser real: Kepler-51b/c/d miden ~0.1 g/cm³."
        )
    elif densidad > DENSIDAD_MAX_G_CM3:
        advertencias.append(
            f"Densidad muy alta ({densidad:.3f} g/cm³, máximo esperado "
            f"{DENSIDAD_MAX_G_CM3} g/cm³) -- revisar unidades de M/R_p."
        )

    if masa_estrella_kg and a_inicial and datos_planeta.get("periodo_dias"):
        periodo_esperado_anios = _periodo_kepler_anios(a_inicial, masa_estrella_kg)
        periodo_real_anios = datos_planeta["periodo_dias"] / 365.25
        if periodo_esperado_anios and periodo_esperado_anios == periodo_esperado_anios:  # not NaN
            error_rel = abs(periodo_real_anios - periodo_esperado_anios) / periodo_esperado_anios
            if error_rel > KEPLER_TOLERANCIA:
                advertencias.append(
                    f"Período reportado ({periodo_real_anios:.3f} años) se aleja "
                    f"{error_rel * 100:.0f}% del esperado por la 3ª ley de Kepler "
                    f"({periodo_esperado_anios:.3f} años) para a={a_inicial / UA_M:.4f} UA "
                    f"y M_estrella={masa_estrella_kg / MSUN_KG:.3f} M☉ -- revisar semieje, "
                    f"período o masa estelar."
                )

    return {"coherente": True, "advertencias": advertencias}
