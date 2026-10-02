# visualizacion_3d.py
# MHD-INT -- Opción 1: visualización 3D con Plotly (Scatter3d + frames).
# Licencia AGPL-3.0 (sin dependencias nuevas: usa lo que ya trae plotly).
#
# DECISIÓN IMPORTANTE, por honestidad científica (mismo criterio que el
# resto del proyecto): el motor de MHD-INT integra a(t) y e(t) a escala
# de Gyr -- NO integra la posición orbital rápida del planeta (eso
# requeriría pasos de tiempo de horas/días, millones de veces más caros
# computacionalmente). Por eso esta animación anima dos cosas distintas
# y las etiqueta como tales:
#   1) La FORMA y TAMAÑO de la órbita (elipse con a_ua[i], e[i]) --
#      esto SÍ es el resultado real simulado (migración, circularización).
#   2) La posición del planeta avanzando sobre esa elipse cuadro a
#      cuadro -- esto es una animación ilustrativa para dar sensación
#      de movimiento, NO la fase orbital real en cada instante de Gyr.
# El caption en pantalla aclara la diferencia -- no se presenta como
# si fuera una posición orbital calculada.

import numpy as np
import plotly.graph_objects as go
import streamlit as st

COLOR_ESTRELLA = "#FFD54A"
COLOR_ORBITA = "#2E5C8A"
COLOR_PLANETA = "#4F9C6D"
# NUEVO (multi-luna, ago-2026): paleta para varias lunas -- se recicla si
# hay más lunas que colores (ciclo con módulo). El primer color coincide
# con el COLOR_LUNA de antes, para que una sola luna se vea igual que
# siempre.
COLORES_LUNAS = ["#8A94A6", "#C97B4A", "#4AAFC9", "#C94A8A", "#9BC94A"]

N_FRAMES_MAX = 60          # cuadros de la animación (independiente de cuántos puntos tenga la serie)
PASOS_POR_ORBITA = 48      # resolución de la elipse dibujada en cada cuadro


def _elipse(a: float, e: float, n=PASOS_POR_ORBITA):
    """Puntos (x, y) de una elipse kepleriana con semieje mayor a y
    excentricidad e, con el foco (la estrella) en el origen."""
    theta = np.linspace(0, 2 * np.pi, n)
    r = a * (1 - e ** 2) / (1 + e * np.cos(theta))
    return r * np.cos(theta), r * np.sin(theta)


def render_orbita_3d(resultado, nombre_planeta: str, indices=None):
    """resultado: ResultadoSimulacion con .serie ya calculada
    (resultado.tiene_serie() == True).
    indices: sub-lista opcional de índices de la serie a animar (para
    "repetir" solo la ventana de un evento en vez de la corrida
    completa -- ver eventos_ui.py). Si es None, se usa toda la serie
    sub-muestreada a N_FRAMES_MAX cuadros, como antes."""
    serie = resultado.serie
    n_puntos = len(serie.tiempos)
    if n_puntos < 2:
        st.info("No hay suficientes puntos en la serie para animar la órbita.")
        return

    if indices is not None:
        idxs = np.asarray(indices)
        if len(idxs) > N_FRAMES_MAX:
            idxs = idxs[np.linspace(0, len(idxs) - 1, N_FRAMES_MAX).astype(int)]
    else:
        # Sub-muestreo a N_FRAMES_MAX cuadros como mucho, para que la
        # animación no quede pesada en simulaciones largas.
        idxs = np.linspace(0, n_puntos - 1, min(N_FRAMES_MAX, n_puntos)).astype(int)

    # NUEVO (multi-luna, ago-2026): antes esto miraba solo serie.a_luna_ua
    # (escalar, primera luna). Ahora usa serie.a_lunas_ua (lista por
    # paso de tiempo, todas las lunas) si está disponible -- resultados
    # viejos (ya serializados antes de este cambio, ej. sesiones .mhd
    # cargadas) no tienen ese campo, así que se cae de vuelta a
    # a_luna_ua envuelta en una lista de 1 elemento.
    lunas_serie = getattr(serie, "a_lunas_ua", None)
    if not lunas_serie and getattr(serie, "a_luna_ua", None):
        lunas_serie = [[v] if v > 0 else [] for v in serie.a_luna_ua]
    n_lunas = max((len(lunas_serie[i]) for i in idxs), default=0) if lunas_serie else 0
    tiene_luna = n_lunas > 0

    # Nombres de cada luna, para la leyenda -- vienen de resultado.lunas
    # (resumen final, mismo orden que self.lunas en engine.py). Si no
    # está disponible (resultado viejo), se usan nombres genéricos.
    nombres_lunas = [l.get("nombre", f"Luna {i+1}") for i, l in enumerate(getattr(resultado, "lunas", []))]
    if len(nombres_lunas) < n_lunas:
        nombres_lunas += [f"Luna {i+1}" for i in range(len(nombres_lunas), n_lunas)]

    frames = []
    for k, i in enumerate(idxs):
        a_i, e_i = serie.a_ua[i], serie.e[i]
        x_orb, y_orb = _elipse(a_i, e_i)

        # Posición del planeta: avanza un ángulo fijo por cuadro. Es
        # una animación ilustrativa de movimiento, no la fase orbital
        # real en el tiempo Gyr de ese punto (ver nota arriba).
        theta_planeta = (k / len(idxs)) * 2 * np.pi * 3  # varias vueltas visuales
        r_planeta = a_i * (1 - e_i ** 2) / (1 + e_i * np.cos(theta_planeta))
        x_p = r_planeta * np.cos(theta_planeta)
        y_p = r_planeta * np.sin(theta_planeta)

        datos_frame = [
            go.Scatter3d(x=x_orb, y=y_orb, z=np.zeros_like(x_orb),
                          mode="lines", line=dict(color=COLOR_ORBITA, width=3), name="Órbita"),
            go.Scatter3d(x=[0], y=[0], z=[0], mode="markers",
                         marker=dict(size=14, color=COLOR_ESTRELLA), name="Estrella"),
            go.Scatter3d(x=[x_p], y=[y_p], z=[0], mode="markers",
                         marker=dict(size=8, color=COLOR_PLANETA), name=nombre_planeta),
        ]
        if tiene_luna and i < len(lunas_serie):
            # Cada luna gira a una velocidad angular DISTINTA (múltiplo
            # de theta_planeta con un offset por índice) solo para que
            # se separen visualmente en el dibujo -- no representa sus
            # velocidades orbitales reales relativas entre sí (ver
            # mismo caveat que ya existía para theta_planeta arriba).
            for j, a_luna_i in enumerate(lunas_serie[i]):
                if a_luna_i <= 0:
                    continue
                r_luna = a_luna_i * 20  # escalado solo visual, ver caption
                theta_luna = theta_planeta * (6 + j * 2)
                x_l = x_p + r_luna * np.cos(theta_luna)
                y_l = y_p + r_luna * np.sin(theta_luna)
                color_j = COLORES_LUNAS[j % len(COLORES_LUNAS)]
                nombre_j = nombres_lunas[j] if j < len(nombres_lunas) else f"Luna {j+1}"
                datos_frame.append(go.Scatter3d(x=[x_l], y=[y_l], z=[0], mode="markers",
                                                 marker=dict(size=4, color=color_j), name=nombre_j))

        frames.append(go.Frame(data=datos_frame, name=str(k)))

    fig = go.Figure(data=frames[0].data, frames=frames)

    lim = max(serie.a_ua[i] * 1.3 for i in idxs)
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="UA", range=[-lim, lim], backgroundcolor="rgba(0,0,0,0)"),
            yaxis=dict(title="UA", range=[-lim, lim], backgroundcolor="rgba(0,0,0,0)"),
            zaxis=dict(title="", range=[-lim, lim], showticklabels=False, backgroundcolor="rgba(0,0,0,0)"),
            aspectmode="cube",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1A1A2E"),
        height=520,
        margin=dict(l=0, r=0, t=30, b=0),
        updatemenus=[dict(
            type="buttons", showactive=False,
            buttons=[
                dict(label="▶️ Reproducir", method="animate",
                     args=[None, dict(frame=dict(duration=120, redraw=True), fromcurrent=True)]),
                dict(label="⏸️ Pausar", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
            ],
        )],
        sliders=[dict(
            steps=[dict(method="animate", args=[[str(k)], dict(mode="immediate",
                        frame=dict(duration=0, redraw=True))], label=f"{serie.tiempos[idxs[k]]:.2f}")
                   for k in range(len(idxs))],
            currentvalue=dict(prefix="t = ", suffix=" Gyr"),
        )],
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "La **forma y el tamaño de la órbita** en cada cuadro son el resultado real "
        "simulado (migración orbital, circularización por marea). El **movimiento del "
        "planeta girando** es ilustrativo, para dar sensación de órbita — el motor no "
        "integra la posición orbital rápida (horas/días), solo la evolución lenta de "
        "sus parámetros a escala de miles de millones de años."
        + (" La(s) distancia(s) de la(s) luna(s) están reescaladas para que se vean "
           "(no a escala real), y giran a velocidades solo ilustrativas -- no reflejan "
           "sus velocidades orbitales reales entre sí." if tiene_luna else "")
    )
