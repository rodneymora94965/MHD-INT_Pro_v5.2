# eventos_detector.py
# MHD-INT -- detecta momentos capturables en una simulación ya calculada,
# para poder "repetir" ese tramo con más resolución en vez de mostrar
# los Gyr completos. NO inventa física nueva: solo lee series que el
# motor ya calcula y usa los mismos umbrales que habitabilidad.py, para
# no introducir un segundo criterio de "protegido" o "dínamo activo"
# que pueda desincronizarse del que realmente usa el cálculo del MHI.
# Licencia AGPL-3.0

import numpy as np

UMBRAL_R_MP_PROTEGIDO = 5.0    # mismo valor que habitabilidad.py
UMBRAL_B_CAMPO_ACTIVO_GAUSS = 0.3
UMBRAL_RM_DINAMO = 40.0
UMBRAL_E_CIRCULAR = 0.01
UMBRAL_ECCENTRICO_INICIAL_FACTOR = 3.0  # e cayó a menos de 1/3 de su valor inicial
UMBRAL_ATM_PERDIDA_FRACCION = 0.05      # M_atm cayó a <5% del valor inicial
UMBRAL_OBL_CAOTICA_ALTA = 60.0
UMBRAL_OBL_CAOTICA_BAJA = 5.0


def _cruces(valores, umbral, hacia_abajo=True):
    """Índices donde la serie cruza el umbral (de un lado al otro)."""
    v = np.asarray(valores, dtype=float)
    if hacia_abajo:
        cruzo = (v[:-1] >= umbral) & (v[1:] < umbral)
    else:
        cruzo = (v[:-1] < umbral) & (v[1:] >= umbral)
    return list(np.where(cruzo)[0] + 1)


def detectar_eventos(resultado) -> list:
    """Devuelve una lista de eventos capturables, cada uno con:
    tipo, titulo, t_gyr, indice, descripcion, ventana_sugerida_myr.
    Vacía si la simulación no tiene serie o no cruzó ningún umbral."""
    if not resultado.tiene_serie():
        return []
    serie = resultado.serie
    eventos = []

    # 1) Pérdida del escudo magnético (R_m cruza 5 R_planeta hacia abajo)
    for i in _cruces(serie.R_m_norm, UMBRAL_R_MP_PROTEGIDO, hacia_abajo=True):
        eventos.append(dict(
            tipo="escudo_perdido", titulo="🛡️ Pérdida del escudo magnético",
            t_gyr=serie.tiempos[i], indice=i,
            descripcion=(f"La magnetopausa cae por debajo de {UMBRAL_R_MP_PROTEGIDO:.0f} "
                         f"radios planetarios — deja de proteger significativamente."),
            ventana_sugerida_myr=200,
        ))

    # 2) Campo por debajo del umbral de "campo activo" (0.3 G)
    for i in _cruces(serie.B_p_gauss, UMBRAL_B_CAMPO_ACTIVO_GAUSS, hacia_abajo=True):
        eventos.append(dict(
            tipo="campo_debil", titulo="🧲 Campo magnético cae por debajo del umbral activo",
            t_gyr=serie.tiempos[i], indice=i,
            descripcion=f"B cae por debajo de {UMBRAL_B_CAMPO_ACTIVO_GAUSS} G.",
            ventana_sugerida_myr=200,
        ))

    # 3) Atmósfera: cae a menos del 5% de la masa atmosférica inicial
    if serie.M_atm_kg and serie.M_atm_kg[0] > 0:
        m0 = serie.M_atm_kg[0]
        for i in _cruces(serie.M_atm_kg, m0 * UMBRAL_ATM_PERDIDA_FRACCION, hacia_abajo=True):
            eventos.append(dict(
                tipo="atmosfera_perdida", titulo="💨 Pérdida de atmósfera",
                t_gyr=serie.tiempos[i], indice=i,
                descripcion=f"La masa atmosférica cae por debajo del {UMBRAL_ATM_PERDIDA_FRACCION*100:.0f}% de su valor inicial.",
                ventana_sugerida_myr=300,
            ))

    # 4) Dínamo: Rm cruza 40 (activo <-> inactivo), en cualquier dirección
    if serie.Rm_num:
        for i in _cruces(serie.Rm_num, UMBRAL_RM_DINAMO, hacia_abajo=True):
            eventos.append(dict(
                tipo="dinamo_apagado", titulo="⚡ El dínamo se apaga",
                t_gyr=serie.tiempos[i], indice=i,
                descripcion=f"Rm cae por debajo de {UMBRAL_RM_DINAMO:.0f} — el núcleo deja de generar campo activamente.",
                ventana_sugerida_myr=200,
            ))
        for i in _cruces(serie.Rm_num, UMBRAL_RM_DINAMO, hacia_abajo=False):
            eventos.append(dict(
                tipo="dinamo_encendido", titulo="⚡ El dínamo se enciende",
                t_gyr=serie.tiempos[i], indice=i,
                descripcion=f"Rm supera {UMBRAL_RM_DINAMO:.0f} — el núcleo empieza a generar campo activamente.",
                ventana_sugerida_myr=200,
            ))

    # 5) Circularización: e cae a menos de 1/3 de su valor inicial (y < 0.01)
    if serie.e and serie.e[0] > 0:
        e0 = serie.e[0]
        umbral_e = min(UMBRAL_E_CIRCULAR, e0 / UMBRAL_ECCENTRICO_INICIAL_FACTOR)
        cruces_e = _cruces(serie.e, umbral_e, hacia_abajo=True)
        if cruces_e:
            i = cruces_e[0]
            eventos.append(dict(
                tipo="circularizacion", titulo="⭕ La órbita se circulariza",
                t_gyr=serie.tiempos[i], indice=i,
                descripcion=f"La excentricidad cae de {e0:.3f} a menos de {umbral_e:.4f} por fricción de marea.",
                ventana_sugerida_myr=500,
            ))

    # 6) Pico de calor de marea
    if serie.Q_tidal_watts and any(q > 0 for q in serie.Q_tidal_watts):
        i_pico = int(np.argmax(serie.Q_tidal_watts))
        if 0 < i_pico < len(serie.tiempos) - 1:  # no es solo el punto inicial
            eventos.append(dict(
                tipo="pico_marea", titulo="🌋 Pico de calor de marea",
                t_gyr=serie.tiempos[i_pico], indice=i_pico,
                descripcion=f"Máxima disipación de marea: {serie.Q_tidal_watts[i_pico]:.2e} W (tipo Ío).",
                ventana_sugerida_myr=100,
            ))

    # 7) Luna: se estrella (a_luna -> 0) o escapa (crece mucho)
    if serie.a_luna_ua and any(v > 0 for v in serie.a_luna_ua):
        a_luna0 = next((v for v in serie.a_luna_ua if v > 0), None)
        if a_luna0:
            for i in _cruces(serie.a_luna_ua, a_luna0 * 0.02, hacia_abajo=True):
                eventos.append(dict(
                    tipo="luna_perdida", titulo="🌑 La luna se estrella contra el planeta",
                    t_gyr=serie.tiempos[i], indice=i,
                    descripcion="La distancia orbital de la luna colapsa hacia el planeta.",
                    ventana_sugerida_myr=50,
                ))
            for i in _cruces(serie.a_luna_ua, a_luna0 * 5.0, hacia_abajo=False):
                eventos.append(dict(
                    tipo="luna_escapa", titulo="🌒 La luna escapa",
                    t_gyr=serie.tiempos[i], indice=i,
                    descripcion="La distancia orbital de la luna crece varias veces su valor inicial.",
                    ventana_sugerida_myr=300,
                ))

    # 8) Oblicuidad entra en régimen caótico (solo si hay dato real, eps_conocido)
    if getattr(resultado, "eps_conocido", False) and serie.eps_deg:
        for i in _cruces(serie.eps_deg, UMBRAL_OBL_CAOTICA_ALTA, hacia_abajo=False):
            eventos.append(dict(
                tipo="oblicuidad_alta", titulo="🌪️ Oblicuidad entra en régimen caótico (alto)",
                t_gyr=serie.tiempos[i], indice=i,
                descripcion=f"La oblicuidad supera {UMBRAL_OBL_CAOTICA_ALTA:.0f}°.",
                ventana_sugerida_myr=500,
            ))

    # 9) Colisión con la estrella (fin de la simulación con se_estrello)
    if getattr(resultado, "se_estrello", False):
        eventos.append(dict(
            tipo="colision", titulo="💥 El planeta cae en la estrella",
            t_gyr=serie.tiempos[-1], indice=len(serie.tiempos) - 1,
            descripcion="El semieje orbital cruza el umbral de colisión (a < 0.01 UA). "
                        "No se modela el impacto en sí ni su efecto sobre la estrella.",
            ventana_sugerida_myr=50,
        ))

    eventos.sort(key=lambda ev: ev["t_gyr"])
    return eventos
