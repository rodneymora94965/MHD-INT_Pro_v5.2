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
from i18n import t
from visualizacion_3d import render_orbita_3d

# Eventos donde tiene sentido repetir la órbita 3D (algo orbital pasa)
_EVENTOS_ORBITALES = {"colision", "circularizacion", "luna_perdida", "luna_escapa"}

# Qué variable de la serie graficar para cada tipo de evento no-orbital
_VARIABLE_POR_EVENTO = {
    "escudo_perdido": ("R_m_norm", "ev.var.R_m_norm"),
    "campo_debil": ("B_p_gauss", "ev.var.B_p_gauss"),
    "atmosfera_perdida": ("M_atm_kg", "ev.var.M_atm_kg"),
    "dinamo_apagado": ("Rm_num", "ev.var.Rm_num"),
    "dinamo_encendido": ("Rm_num", "ev.var.Rm_num"),
    "pico_marea": ("Q_tidal_watts", "ev.var.Q_tidal_watts"),
    "oblicuidad_alta": ("eps_deg", "ev.var.eps_deg"),
}


def _indices_ventana(serie, t_evento, ventana_myr):
    margen_gyr = ventana_myr / 1000.0
    tiempos = np.asarray(serie.tiempos)
    mask = (tiempos >= t_evento - margen_gyr) & (tiempos <= t_evento + margen_gyr)
    idxs = np.where(mask)[0]
    if len(idxs) < 2:
        # ventana muy angosta para la resolución de la serie -- se
        # ensancha tomando algunos puntos alrededor del más cercano
        i_centro = int(np.argmin(np.abs(tiempos - t_evento)))
        lo, hi = max(0, i_centro - 5), min(len(tiempos), i_centro + 6)
        idxs = np.arange(lo, hi)
    return idxs


def _titulo(ev):
    """Título del evento en el idioma activo (si no hay traducción, el original)."""
    return t(f"evd.{ev['tipo']}.titulo", defecto=ev["titulo"])


def _descripcion(ev):
    return t(f"evd.{ev['tipo']}.desc", defecto=ev["descripcion"], **ev.get("args", {}))


def render_eventos(resultado, nombre_planeta: str):
    st.markdown(t("ev.titulo"))
    st.caption(t("ev.caption"))

    eventos = detectar_eventos(resultado)
    if not eventos:
        st.info(t("ev.ninguno"))
        return

    # El valor del selector es el índice del evento (no su texto): así cambiar de
    # idioma no desarma la selección. Solo el texto mostrado se traduce.
    elegido = st.selectbox(t("ev.selector"), list(range(len(eventos))),
                           format_func=lambda i: f"{eventos[i]['t_gyr']:.3f} Gyr — {_titulo(eventos[i])}",
                           key=f"ev_sel_{nombre_planeta}_{len(eventos)}")
    ev = eventos[elegido]
    st.markdown(f"**{_titulo(ev)}** — {_descripcion(ev)}")

    ventana_myr = st.slider(t("ev.ventana"),
                             10, 1000, ev["ventana_sugerida_myr"], 10,
                             key=f"ev_vent_{nombre_planeta}_{elegido}_{ev['tipo']}")

    idxs = _indices_ventana(resultado.serie, ev["t_gyr"], ventana_myr)
    st.caption(t("ev.mostrando", n=len(idxs),
                 t0=f"{resultado.serie.tiempos[idxs[0]]:.4f}",
                 t1=f"{resultado.serie.tiempos[idxs[-1]]:.4f}"))

    if ev["tipo"] in _EVENTOS_ORBITALES:
        render_orbita_3d(resultado, nombre_planeta, indices=idxs)
    else:
        campo, clave_y = _VARIABLE_POR_EVENTO.get(ev["tipo"], (None, None))
        etiqueta_y = t(clave_y) if clave_y else None
        valores = getattr(resultado.serie, campo, None) if campo else None
        if not valores:
            st.warning(t("ev.sin_variable"))
            return
        t_ventana = [resultado.serie.tiempos[i] for i in idxs]
        y_ventana = [valores[i] for i in idxs]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t_ventana, y=y_ventana, mode="lines+markers",
                                  line=dict(color="#2E5C8A", width=2), marker=dict(size=4)))
        fig.add_vline(x=ev["t_gyr"], line_dash="dash", line_color="#B20710",
                      annotation_text=t("ev.grafico.evento"))
        fig.update_layout(
            title=_titulo(ev), xaxis_title=t("ev.grafico.eje_x"), yaxis_title=etiqueta_y,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1A2E"), height=380,
        )
        st.plotly_chart(fig, use_container_width=True)
