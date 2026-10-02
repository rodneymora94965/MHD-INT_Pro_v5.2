# eventos_ui.py
# MHD-INT -- pantalla de "Momentos capturables" de una corrida.
# Licencia: Comercial propietaria (dual con AGPL-3.0) -- va en las 3
# versiones igual que el resto de gráficos, no es exclusivo Pro.
#
# DECISIÓN: el "replay" NO vuelve a simular con dt más fino. Motivo:
# el integrador es de paso fijo (ver Científico Clase 8 en la sección
# Educación) y re-simular en alta resolución desde t=0 hasta un evento
# que ocurre varios Gyr adentro sería carísimo para una demo interactiva.
# En cambio, se reusa la serie que Streamlit ya calculó (limitada a
# ~2000 puntos por simular_planeta) y se hace zoom a la ventana del
# evento -- instantáneo, sin costo de cómputo extra, y se avisa en
# pantalla cuál es el límite de resolución real.

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from eventos_detector import detectar_eventos
from visualizacion_3d import render_orbita_3d

# Eventos donde tiene sentido repetir la órbita 3D (algo orbital pasa)
_EVENTOS_ORBITALES = {"colision", "circularizacion", "luna_perdida", "luna_escapa"}

# Qué variable de la serie graficar para cada tipo de evento no-orbital
_VARIABLE_POR_EVENTO = {
    "escudo_perdido": ("R_m_norm", "R_m (radios planetarios)"),
    "campo_debil": ("B_p_gauss", "Campo magnético (G)"),
    "atmosfera_perdida": ("M_atm_kg", "Masa atmosférica (kg)"),
    "dinamo_apagado": ("Rm_num", "Número de Reynolds magnético (Rm)"),
    "dinamo_encendido": ("Rm_num", "Número de Reynolds magnético (Rm)"),
    "pico_marea": ("Q_tidal_watts", "Calor de marea (W)"),
    "oblicuidad_alta": ("eps_deg", "Oblicuidad (°)"),
}


def _indices_ventana(serie, t_evento, ventana_myr):
    margen_gyr = ventana_myr / 1000.0
    t = np.asarray(serie.tiempos)
    mask = (t >= t_evento - margen_gyr) & (t <= t_evento + margen_gyr)
    idxs = np.where(mask)[0]
    if len(idxs) < 2:
        # ventana muy angosta para la resolución de la serie -- se
        # ensancha tomando algunos puntos alrededor del más cercano
        i_centro = int(np.argmin(np.abs(t - t_evento)))
        lo, hi = max(0, i_centro - 5), min(len(t), i_centro + 6)
        idxs = np.arange(lo, hi)
    return idxs


def render_eventos(resultado, nombre_planeta: str):
    st.markdown("### 🎬 Momentos capturables de esta corrida")
    st.caption(
        "En vez de ver los miles de millones de años completos, elegí un momento "
        "donde pasó algo y hacé zoom a esa ventana. Estos eventos usan los mismos "
        "umbrales que definen el MHI (ej. campo por debajo de 0.3 G = deja de contar "
        "como \"activo\" para habitabilidad) — es la misma vara que ya usa el resto "
        "de la app, no una nueva. Para umbrales más extremos pensados para contenido "
        "audiovisual (ej. campo casi en cero), ver 🎬 Taller de Contenido más abajo."
    )

    eventos = detectar_eventos(resultado)
    if not eventos:
        st.info(
            "No se detectó ningún evento capturable en esta corrida (ni pérdida de "
            "escudo/atmósfera, ni cambios de dínamo, ni circularización, ni colisión). "
            "Es un resultado real: significa que, con estos parámetros, el planeta se "
            "mantuvo estable durante todo el tiempo simulado."
        )
        return

    opciones = {f"{ev['t_gyr']:.3f} Gyr — {ev['titulo']}": ev for ev in eventos}
    elegido = st.selectbox("Eventos detectados en esta corrida", list(opciones.keys()))
    ev = opciones[elegido]
    st.markdown(f"**{ev['titulo']}** — {ev['descripcion']}")

    ventana_myr = st.slider("Ventana alrededor del evento (± millones de años)",
                             10, 1000, ev["ventana_sugerida_myr"], 10)

    idxs = _indices_ventana(resultado.serie, ev["t_gyr"], ventana_myr)
    st.caption(
        f"Mostrando {len(idxs)} puntos calculados entre "
        f"{resultado.serie.tiempos[idxs[0]]:.4f} y {resultado.serie.tiempos[idxs[-1]]:.4f} Gyr. "
        "La resolución es la de la corrida original (no se vuelve a simular con más "
        "detalle) — si necesitás más finura en esta ventana, corré de nuevo la "
        "simulación acotando el tiempo máximo cerca de este evento."
    )

    if ev["tipo"] in _EVENTOS_ORBITALES:
        render_orbita_3d(resultado, nombre_planeta, indices=idxs)
    else:
        campo, etiqueta_y = _VARIABLE_POR_EVENTO.get(ev["tipo"], (None, None))
        valores = getattr(resultado.serie, campo, None) if campo else None
        if not valores:
            st.warning("Esta corrida no guardó la variable necesaria para graficar este evento.")
            return
        t_ventana = [resultado.serie.tiempos[i] for i in idxs]
        y_ventana = [valores[i] for i in idxs]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t_ventana, y=y_ventana, mode="lines+markers",
                                  line=dict(color="#2E5C8A", width=2), marker=dict(size=4)))
        fig.add_vline(x=ev["t_gyr"], line_dash="dash", line_color="#B20710",
                      annotation_text="evento")
        fig.update_layout(
            title=ev["titulo"], xaxis_title="Tiempo (Gyr)", yaxis_title=etiqueta_y,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1A2E"), height=380,
        )
        st.plotly_chart(fig, use_container_width=True)
