# app_streamlit_pro.py
# MHD-INT PRO — Edición comercial (v5.2)
# Licencia: Comercial propietaria (dual con AGPL-3.0)
#
# ⚠️ ESTE ARCHIVO NO PERTENECE AL REPOSITORIO PÚBLICO AGPL.
# Es el entry point de la distribución comercial (nivel Básico/Profesional/
# Código Fuente). Importa el motor físico público (engine.py, database.py,
# etc.) y añade las capas premium: video nativo (Capa 1), donut MHI + gauge
# Rm (Capa 2), comparador (Capa 3), exportación PDF/figuras (Capa 4).
# Para la versión pública, usar app_streamlit.py (v5.0).
#
# FIX v5.2 (revisión previa a release):
# 1) El video_key de los modos "Simulación" y "Sintético" solo incluía 2-3
#    parámetros (planeta/t_max/dt en Simulación; masa/radio/t_max en
#    Sintético). Cambiar torques, modelo térmico, atmósfera, distancia
#    orbital, excentricidad, etc. y volver a simular NO invalidaba el video
#    cacheado -- se mostraba el video de la corrida anterior como si
#    correspondiera a la nueva. Se reemplaza por una clave derivada de un
#    hash estable de TODOS los parámetros relevantes (_clave_video()).
# 2) El donut de MHI y el centro numérico mostraban una inconsistencia
#    cuando había penalización por oblicuidad (mhi_bruto de los 4
#    componentes != mhi_total). Se separa explícitamente: el donut grafica
#    la composición de mhi_bruto (los 4 componentes pesados, que sí suman
#    100% entre sí) y el MHI final se muestra aparte, con la penalización
#    (si aplica) anotada en texto -- nunca se hace pasar una cosa por otra.

import streamlit as st
import json
import hashlib
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ---- Motor físico PÚBLICO (AGPL) — se importa, no se modifica ----
from engine import simular_planeta, UA, M_SOL, R_TIERRA
from database import PLANETAS
from sensibilidad_runner import analisis_sensibilidad, analisis_sensibilidad_extendido
from validacion import validar_todos
from habitabilidad import calcular_mhi, categoria_mhi
from mapa_mhi import generar_mapa_mhi
from historial import guardar_simulacion, cargar_historial, borrar_historial
from exportar_video import construir_json_video

# ---- Módulos COMERCIALES (privados, no están en el repo AGPL) ----
from video_mpl import generar_video_desde_dict       # Capa 1: video nativo
from comparador import render_comparador              # Capa 3: comparador
from disco_ui import render_disco_protoplanetario     # Capa 3: disco protoplanetario
from educacion_ui import render_educacion             # sección educativa
from modificador_ui import render_modificador_sistemas  # modificador de sistemas
from reporte_pdf import generar_reporte_pdf           # Capa 4: PDF ejecutivo
from pack_figuras import generar_pack_figuras          # Capa 4: pack de figuras
from glosario_terminos import GLOSARIO_TERMINOS       # diccionario de terminos, compartido con Standard/O.S.
from etiquetas_columnas import ETIQUETAS_HISTORIAL, ETIQUETAS_MAPA_MHI, con_nombres_legibles
from sesion import obtener_sesion_id

st.set_page_config(page_title="MHD-INT PRO v5.2", layout="wide", page_icon="assets/logo_mhd_int.png")


def _clave_video(planeta: str, params_extra: dict, t_max_gyr: float, dt_yr: float, prefijo: str = "video") -> str:
    """
    Clave de cache estable y ÚNICA por combinación real de parámetros de
    simulación. Reemplaza las claves parciales que causaban que se
    mostrara un video de una corrida anterior con parámetros distintos.
    json.dumps(sort_keys=True) + hash corto: determinista entre reruns de
    Streamlit (no usa id()/hash() de Python, que cambian entre procesos).
    """
    payload = {
        "planeta": planeta,
        "t_max_gyr": round(float(t_max_gyr), 6),
        "dt_yr": round(float(dt_yr), 6),
        "params_extra": params_extra or {},
    }
    huella = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]
    return f"{prefijo}_{huella}"


# ============================================================================
# Estilo Premium (CSS) — identidad visual MHD-INT
# ============================================================================
st.markdown("""
<style>
/* CAMBIO (ago-2026): paleta profesional/atenuada -- ver misma nota en
   app_streamlit.py. Azul corporativo #2E5C8A en vez de rojo saturado,
   sin mayúsculas/glow en botones. */
.stApp {
    background: linear-gradient(180deg, #FFFFFF 0%, #F4F6FA 100%);
    color: #1A1A2E;
}
[data-testid="stSidebar"] {
    background: rgba(244, 246, 250, 0.92) !important;
    backdrop-filter: blur(12px) !important;
    border-right: 1px solid rgba(30, 60, 90, 0.12) !important;
}
.stButton > button {
    background: #2E5C8A !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 0.4rem 1rem !important;
    box-shadow: 0 1px 4px rgba(30, 60, 90, 0.2) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #24486E !important;
    box-shadow: 0 2px 8px rgba(30, 60, 90, 0.3) !important;
}
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(30, 60, 90, 0.12) !important;
    border-radius: 12px !important;
    padding: 14px !important;
    box-shadow: 0 2px 8px rgba(20, 20, 40, 0.05) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: #2E5C8A !important;
    box-shadow: 0 2px 10px rgba(46, 92, 138, 0.12) !important;
}
[data-testid="stMetric"] label, [data-testid="stMetricValue"] {
    color: #1A1A2E !important;
}
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #2E5C8A, #4F9C6D) !important;
    border-radius: 20px !important;
    height: 8px !important;
}
h1 {
    font-family: 'Courier New', monospace !important;
    letter-spacing: 1.5px !important;
    color: #1A1A2E !important;
    font-size: 1.9rem !important;
    border-bottom: 3px solid #2E5C8A;
    padding-bottom: 6px;
    display: inline-block;
}
h2, h3 {
    color: #1A1A2E !important;
    font-weight: 600 !important;
}
[data-testid="stExpanderHeader"] {
    color: #2E5C8A !important;
    font-weight: 600 !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Versión, edición y nivel de licencia
# ============================================================================
VERSION_PRO = "5.2"

# NIVEL controla qué funcionalidades se muestran. Este mismo archivo se
# usa para Standard y para Pro -- la versión AGPL/Open Source NO usa este
# archivo (usa app_streamlit.py del repo público, más simple, sin ninguna
# capa comercial). Esquema de precios vigente: AGPL gratis / Standard $49
# / Pro $199.
NIVEL = "PRO"   # "STANDARD" | "PRO"
PRECIO_NIVEL = {"STANDARD": "$49", "PRO": "$199"}

# ============================================================================
# Verificación de licencia (ver licencia.py). Se corta la ejecución acá
# mismo si no hay una licencia válida para este NIVEL -- todo lo que
# sigue abajo (dashboard completo) nunca llega a renderizarse.
# ============================================================================
from licencia import verificar_licencia, LicenciaInvalida

try:
    LICENCIA = verificar_licencia(NIVEL)
except LicenciaInvalida:
    st.error(
        "🔒 **Licencia no válida.**\n\n"
        "No se encontró una licencia válida para esta aplicación. "
        "Verificá que el archivo `license.json` esté en la misma carpeta "
        "que el ejecutable. Si compraste MHD-INT y no tenés ese archivo, "
        "escribinos a través de Ko-fi (ko-fi.com/solariscoremhd)."
    )
    st.stop()

col_logo, col_titulo = st.columns([1, 3])
with col_logo:
    st.image("assets/logo_mhd_int.png", width=90)
with col_titulo:
    st.caption(f"by Solaris Core · versión {VERSION_PRO} · {NIVEL} ({PRECIO_NIVEL[NIVEL]})")

# Marca blanca (logo/nombre de cliente en el PDF ejecutivo): el esquema de
# precios anterior la ligaba al nivel "Código Fuente" ($33k), que ya no
# existe en el esquema nuevo (AGPL / Standard $49 / Pro $199). No hay
# decisión de negocio tomada sobre en qué nivel va -- queda DESACTIVADA
# por defecto para no regalar de más ni quitar de menos sin que Roney lo
# decida. Para activarla en PRO alcanza con descomentar el bloque de abajo.
BRANDING_CLIENTE = None
# if NIVEL == "PRO":
#     BRANDING_CLIENTE = {
#         "logo_path": "assets/logo_cliente.png",
#         "nombre_cliente": "Nombre del Cliente",
#     }

# Paleta corporativa (usada por render_reporte_comercial)
COLOR_B   = '#E50914'
COLOR_A   = '#00C9FF'
COLOR_E   = '#92FE9D'
COLOR_ATM = '#FFA500'
COLOR_BG  = '#FFFFFF'  # CAMBIO (ago-2026): tema claro -- antes '#0A0A0F'


# ============================================================================
# FUNCIÓN PREMIUM: reporte comercial completo (Capas 1, 2 y 4)
# ============================================================================
def render_reporte_comercial(resultado, params: dict, usar_termico: bool,
                             usar_atmosfera: bool, video_key: str = None):
    """
    Renderiza el reporte premium: cabecera, video nativo, slider de
    inspección, donut MHI, gauge Rm, estado térmico/atmósfera, evolución de
    oblicuidad, gráficas personalizables, historial y exportación ejecutiva.

    video_key ahora se espera generado con _clave_video() por el llamador,
    para que dependa de TODOS los parámetros de la simulación (ver fix v5.2
    en el encabezado del archivo).
    """
    planeta = params.get("planeta", resultado.nombre_planeta)

    # ---- Cabecera ----
    col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
    with col_h1:
        estado_txt = "💥 Estrellado" if resultado.se_estrello else \
                     "❌ Sin atmósfera" if resultado.atm_perdida else \
                     "✅ Estable"
        st.markdown(f"## 🪐 {resultado.nombre_planeta}")
        st.caption(f"Estado final: **{estado_txt}** · "
                   f"{params.get('t_max_gyr', 5.0):.1f} Gyr simulados")
    with col_h2:
        delta_B = resultado.B_final_gauss - resultado.B_inicial_gauss
        st.metric("B final", f"{resultado.B_final_gauss:.3f} G",
                  delta=f"{delta_B:+.3f} G")
    with col_h3:
        mhi = None
        if resultado.es_valido() and resultado.tiene_serie():
            mhi = calcular_mhi(resultado)
            st.metric("MHI", f"{mhi['mhi_total']:.0f}",
                      delta=categoria_mhi(mhi['mhi_total']))

    if not resultado.tiene_serie():
        st.json(resultado.resumen_dict())
        return

    st.markdown("---")

    # ---- Video + panel de inspección (Capa 1) ----
    col_video, col_panel = st.columns([3, 2])

    with col_video:
        st.markdown("### 🎞️ Evolución temporal")

        if video_key is None:
            # Fallback defensivo si algún llamador no pasa video_key: se
            # construye igual con la función centralizada, nunca con una
            # clave parcial hecha a mano.
            video_key = _clave_video(planeta, params, params.get("t_max_gyr", 5.0), params.get("dt_yr", 10000))

        if video_key not in st.session_state:
            try:
                datos_json = construir_json_video(
                    resultado,
                    planeta=planeta,
                    t_max_gyr=params.get("t_max_gyr", 5.0),
                    dt_yr=params.get("dt_yr", 10000),
                )
                with st.spinner("🎨 Renderizando video..."):
                    buffer = generar_video_desde_dict(datos_json, fps=20)
                st.session_state[video_key] = {
                    "bytes": buffer.getvalue(),
                    "formato": getattr(buffer, "formato_real", "mp4"),
                }
            except Exception as exc:
                st.warning(f"No se pudo generar el video: {exc}")

        if video_key in st.session_state:
            vid = st.session_state[video_key]
            fmt = vid["formato"]
            mime = "image/gif" if fmt == "gif" else "video/mp4"
            if fmt == "gif":
                # FIX: st.video() no soporta GIF (solo mp4/ogv/m4v/webm) --
                # un GIF es una imagen animada, se muestra con st.image().
                # Este es el camino que se activa cuando ffmpeg no está
                # disponible (tipico en Streamlit Cloud sin packages.txt).
                st.info("ℹ️ ffmpeg no disponible — se generó GIF en vez de MP4.")
                st.image(vid["bytes"])
            else:
                # FIX: el parametro se llama "format", no "mime_type" (ese
                # nombre nunca existio en la API de Streamlit -- por esto
                # crasheaba con TypeError en Streamlit Cloud).
                st.video(vid["bytes"], format="video/mp4")

            dc1, dc2 = st.columns(2)
            with dc1:
                st.download_button(
                    f"⬇️ Video ({fmt.upper()})",
                    data=vid["bytes"],
                    file_name=f"{planeta}_evolucion.{fmt}",
                    mime=mime,
                    key=f"dl_video_{video_key}",
                )
            with dc2:
                try:
                    json_str = json.dumps(
                        construir_json_video(resultado, planeta,
                                             params.get("t_max_gyr", 5.0),
                                             params.get("dt_yr", 10000)),
                        ensure_ascii=False, indent=2,
                    )
                    st.download_button(
                        "⬇️ Datos (JSON)",
                        data=json_str,
                        file_name=f"{planeta}_data.json",
                        mime="application/json",
                        key=f"dl_json_{video_key}",
                    )
                except Exception:
                    pass

        serie = resultado.serie
        n_puntos = len(serie.tiempos)
        st.markdown("#### 🔍 Inspeccionar instante")
        frame_idx = st.slider(
            "Frame", 0, n_puntos - 1, 0,
            help="Mové el slider para ver el estado del planeta en cualquier instante.",
            key=f"slider_frame_{video_key}",
        )
        st.caption(f"**t = {serie.tiempos[frame_idx]:.4f} Gyr**")

    with col_panel:
        st.markdown("### 📊 Estado en el frame seleccionado")
        serie = resultado.serie
        st.metric("Distancia orbital", f"{serie.a_ua[frame_idx]:.4f} UA")
        st.metric("Campo magnético", f"{serie.B_p_gauss[frame_idx]:.3f} G")
        st.metric("Excentricidad", f"{serie.e[frame_idx]:.5f}")

        if getattr(resultado, "eps_conocido", False) and serie.eps_deg and len(serie.eps_deg) > frame_idx:
            st.metric("Oblicuidad", f"{serie.eps_deg[frame_idx]:.1f}°")

        if usar_atmosfera and serie.M_atm_kg and len(serie.M_atm_kg) > frame_idx:
            atm_tierras = serie.M_atm_kg[frame_idx] / 5.15e18
            if resultado.atm_perdida:
                st.metric("Masa atm.", "❌ Perdida")
            else:
                st.metric("Masa atm.", f"{atm_tierras:.4f} Tierras")

        if usar_termico and serie.Rm_num and len(serie.Rm_num) > frame_idx:
            rm_val = serie.Rm_num[frame_idx]
            if rm_val > 40:
                st.success(f"✅ Dínamo activo (Rm = {rm_val:.1f})")
            else:
                st.warning(f"⚠️ Dínamo inactivo (Rm = {rm_val:.1f})")

    # ---- Donut MHI (Capa 2) ----
    st.markdown("---")
    st.markdown("### 🛡️ Índice de Habitabilidad Magnética (MHI)")

    if mhi is not None:
        col_donut, col_mhi_metrics = st.columns([1, 2])

        with col_donut:
            # FIX v5.2: el donut grafica los 4 componentes pesados, que
            # suman exactamente mhi_bruto (no mhi_total si hay
            # penalización). El centro muestra mhi_bruto etiquetado como
            # tal; el MHI final (post-penalización) se muestra aparte en
            # las métricas, nunca mezclado en la misma cifra.
            valores = [
                mhi["escudo_mag_pct"] * 0.40,
                mhi["campo_activo_pct"] * 0.30,
                mhi["estabilidad_orb"] * 0.20,
                mhi["score_marea"] * 0.10,
            ]
            colores = [COLOR_B, COLOR_A, COLOR_E, COLOR_ATM]
            fig_donut = go.Figure(data=[go.Pie(
                labels=["Escudo", "Campo", "Órbita", "Marea"],
                values=valores, hole=0.65,
                marker=dict(colors=colores, line=dict(color=COLOR_BG, width=2)),
                textinfo='label+percent', textfont_size=11,
                hovertemplate="%{label}<br>Aporte: %{value:.1f} pts<extra></extra>",
            )])
            centro_label = "MHI bruto" if mhi.get("penalizacion_obl_pts", 0.0) != 0.0 else "MHI"
            fig_donut.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1A1A2E'),
                annotations=[dict(
                    text=f"<b>{mhi['mhi_bruto']:.0f}</b><br>{centro_label}",
                    x=0.5, y=0.5, font_size=20, showarrow=False,
                )],
                height=280,
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_mhi_metrics:
            m1, m2 = st.columns(2)
            m1.metric("Escudo activo", f"{mhi['escudo_mag_pct']:.1f}% del tiempo")
            m1.metric("Dínamo activo", f"{mhi['campo_activo_pct']:.1f}% del tiempo")
            m2.metric("Excentricidad prom.", f"{mhi['e_promedio']:.4f}")
            m2.metric("Calor marea medio", f"{mhi['q_promedio_w']:.2e} W")

            penal = mhi.get("penalizacion_obl_pts", 0.0)
            if penal != 0.0:
                st.metric("MHI final (con penalización)", f"{mhi['mhi_total']:.0f} / 100",
                          delta=f"{penal:+.0f} pts por oblicuidad")
                st.caption(
                    f"El donut muestra la composición antes de la penalización "
                    f"(ε final = {mhi['eps_final_deg']:.1f}°, fuera del rango 5°–60°)."
                )

            if mhi["atm_perdida"]:
                st.error("⚠️ Atmósfera perdida. MHI forzado a 0.")
            if mhi["se_estrello"]:
                st.error("💥 Planeta estrellado. MHI forzado a 0.")

    # ---- Gauge Rm (Capa 2, solo si modelo térmico activo) ----
    if usar_termico and resultado.tiene_serie() and resultado.Rm_final > 0:
        col_gauge, col_gauge_info = st.columns([1, 1])
        with col_gauge:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=resultado.Rm_final,
                number={'font': {'color': '#F0F0F0', 'size': 32}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#F0F0F0',
                             'tickfont': {'color': '#F0F0F0'}},
                    'bar': {'color': COLOR_A if resultado.Rm_final > 40 else COLOR_B},
                    'bgcolor': "rgba(255,255,255,0.05)",
                    'steps': [
                        {'range': [0, 40], 'color': 'rgba(229, 9, 20, 0.15)'},
                        {'range': [40, 100], 'color': 'rgba(0, 201, 255, 0.15)'},
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.8, 'value': 40,
                    },
                },
                title={'text': "Reynolds magnético<br><span style='font-size:0.7em;color:#92FE9D'>Umbral dínamo: 40</span>"}
            ))
            fig_gauge.update_layout(
                height=220,
                margin=dict(l=10, r=10, t=50, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        with col_gauge_info:
            st.markdown("#### 🔥 Estado térmico del núcleo")
            c1, c2 = st.columns(2)
            c1.metric("T CMB (K)", f"{resultado.T_cmb_final_K:.0f}")
            c2.metric("B generado (G)", f"{resultado.B_gen_final_gauss:.3f}")

    # ---- Estado de la atmósfera ----
    if usar_atmosfera and resultado.tiene_serie():
        st.markdown("---")
        st.markdown("### 🌍 Estado de la Atmósfera")
        c1, c2 = st.columns(2)
        M_atm_tierras = resultado.M_atm_final_kg / 5.15e18
        c1.metric("Masa atmosférica", f"{M_atm_tierras:.4f} Tierras")
        if resultado.atm_perdida:
            c2.metric("Atmósfera", "❌ PERDIDA")
            st.error("⚠️ Foto-evaporación completa. MHI = 0.")
        else:
            c2.metric("Atmósfera", "✅ Retenida")

    # ---- Evolución de oblicuidad ----
    eps_conocido_res = getattr(resultado, "eps_conocido", False)
    if eps_conocido_res and resultado.tiene_serie() and len(resultado.serie.eps_deg) > 0:
        st.markdown("---")
        st.markdown("### 🌍 Evolución de la Oblicuidad")
        df_eps = pd.DataFrame({
            "t_Gyr": resultado.serie.tiempos,
            "eps_deg": resultado.serie.eps_deg,
        })
        fig_eps = go.Figure()
        fig_eps.add_trace(go.Scatter(
            x=df_eps["t_Gyr"], y=df_eps["eps_deg"], mode="lines",
            name="Oblicuidad (°)", line=dict(color=COLOR_ATM, width=3),
        ))
        fig_eps.add_hline(y=60, line_dash="dash", line_color="red",
                          annotation_text="Límite caótico (60°)")
        fig_eps.add_hline(y=5, line_dash="dash", line_color="blue",
                          annotation_text="Límite estéril (5°)")
        fig_eps.update_layout(
            xaxis_title="Tiempo (Gyr)", yaxis_title="Oblicuidad (grados)",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1A1A2E'),
        )
        st.plotly_chart(fig_eps, use_container_width=True)

        eps_final_res = resultado.eps_final_deg
        if eps_final_res > 60:
            st.warning(f"⚠️ Oblicuidad extrema ({eps_final_res:.1f}°). Clima caótico. Penalización de -20 en el MHI.")
        elif eps_final_res < 5:
            st.warning(f"⚠️ Oblicuidad muy baja ({eps_final_res:.1f}°). Riesgo de invernadero descontrolado. Penalización de -20 en el MHI.")
        else:
            st.success(f"✅ Oblicuidad estable ({eps_final_res:.1f}°). Clima habitable.")
    elif resultado.tiene_serie():
        st.caption("ℹ️ Oblicuidad no disponible como dato conocido para este cuerpo — no se muestra la evolución para evitar sugerir un dato que no existe.")

    # ---- Gráficas personalizables ----
    st.markdown("---")
    st.markdown("### 📈 Gráficas personalizables")
    serie = resultado.serie
    df = pd.DataFrame({
        "t_Gyr": serie.tiempos,
        "a_ua": serie.a_ua,
        "B_gauss": serie.B_p_gauss,
        "w_p": serie.w_p,
        "e": serie.e,
        "T_cmb_K": serie.T_cmb_K,
        "B_gen_gauss": serie.B_gen_gauss,
        "Rm": serie.Rm_num,
        "M_atm_kg": serie.M_atm_kg,
        "eps_deg": serie.eps_deg,
    })
    ETIQUETAS_VARIABLES = {
        "a_ua": "Distancia orbital a (UA)",
        "B_gauss": "Campo magnético B (G)",
        "w_p": "Velocidad de rotación ω (rad/s)",
        "e": "Excentricidad e",
        "T_cmb_K": "Temp. núcleo-manto T_cmb (K)",
        "B_gen_gauss": "Campo generado por dínamo (G)",
        "Rm": "Número de Reynolds magnético Rm",
        "M_atm_kg": "Masa atmosférica (kg)",
        "eps_deg": "Oblicuidad ε (°)" + ("" if eps_conocido_res else " [no conocida — valor interno]"),
    }
    vars_disponibles = list(ETIQUETAS_VARIABLES.keys())
    vars_seleccionadas = st.multiselect(
        "Variables a graficar", vars_disponibles,
        default=["a_ua", "B_gauss"],
        format_func=lambda v: ETIQUETAS_VARIABLES[v],
        key=f"multiplot_{video_key}",
    )
    if not vars_seleccionadas:
        st.info("Elegí al menos una variable para graficar.")
    else:
        fig = go.Figure()
        for var in vars_seleccionadas:
            fig.add_trace(go.Scatter(
                x=df["t_Gyr"], y=df[var], mode="lines",
                name=ETIQUETAS_VARIABLES[var],
            ))
        fig.update_layout(
            xaxis_title="Tiempo (Gyr)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1A1A2E'),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Guardar en historial ----
    st.markdown("---")
    col_hist1, col_hist2 = st.columns([1, 3])
    with col_hist1:
        if st.button("📜 Guardar en Historial", type="primary", key=f"btn_hist_{video_key}"):
            try:
                fila = guardar_simulacion(resultado, params, mhi=mhi, sesion_id=obtener_sesion_id())
                st.success(f"✅ Simulación guardada ({fila['timestamp']})")
            except Exception as exc:
                st.error(f"Error al guardar: {exc}")
    with col_hist2:
        st.caption("Guarda esta simulación en tu historial personal.")

    # ---- Exportación ejecutiva (Capa 4, EXCLUSIVO PRO) ----
    if NIVEL == "PRO":
        st.markdown("---")
        st.markdown("### 📤 Exportación ejecutiva")
        st.caption("Generá y descargá el reporte PDF y el pack de figuras en alta resolución (300 dpi).")

        exp_key = video_key

        col_pdf, col_fig = st.columns(2)

        with col_pdf:
            pdf_cache_key = f"pdf_{exp_key}"
            if st.button("📄 Generar Reporte PDF", key=f"gen_pdf_{exp_key}"):
                with st.spinner("Generando PDF..."):
                    try:
                        st.session_state[pdf_cache_key] = generar_reporte_pdf(
                            resultado, mhi, params, branding=BRANDING_CLIENTE)
                    except Exception as exc:
                        st.session_state[pdf_cache_key] = None
                        st.error(f"No se pudo generar el PDF: {exc}")
            if st.session_state.get(pdf_cache_key):
                st.download_button(
                    "⬇️ Descargar Reporte PDF",
                    data=st.session_state[pdf_cache_key],
                    file_name=f"{resultado.nombre_planeta}_reporte.pdf",
                    mime="application/pdf",
                    key=f"dl_pdf_{exp_key}",
                )

        with col_fig:
            fig_cache_key = f"fig_{exp_key}"
            if st.button("🖼️ Generar Pack de Figuras", key=f"gen_fig_{exp_key}"):
                with st.spinner("Generando figuras (300 dpi)..."):
                    try:
                        st.session_state[fig_cache_key] = generar_pack_figuras(resultado)
                    except Exception as exc:
                        st.session_state[fig_cache_key] = None
                        st.error(f"No se pudo generar el pack de figuras: {exc}")
            if st.session_state.get(fig_cache_key):
                st.download_button(
                    "⬇️ Descargar Pack de Figuras (ZIP)",
                    data=st.session_state[fig_cache_key],
                    file_name=f"{resultado.nombre_planeta}_figuras.zip",
                    mime="application/zip",
                    key=f"dl_fig_{exp_key}",
                )


# ============================================================================
# Sidebar
# ============================================================================
_modos_disponibles = ["📚 Educación", "Simulación", "Sintético", "Mapa MHI", "Sensibilidad", "Validación"]
if NIVEL == "PRO":
    # Comparador y Disco Protoplanetario son exclusivos Pro -- Standard
    # no importa esos módulos ni ve las opciones en el menú.
    _modos_disponibles.append("⚡ Comparador")
    _modos_disponibles.append("🌌 Disco Protoplanetario (Beta)")
    _modos_disponibles.append("🧪 Modificador de Sistemas")
_modos_disponibles.append("📖 Glosario")

# ---- Sidebar reorganizado: logo arriba, identidad/licencia, navegación
# en el medio, herramientas (historial) abajo -- jerarquía de lectura de
# arriba hacia abajo en vez de todo mezclado. ----
st.sidebar.image("assets/logo_mhd_int.png", width=70)
st.sidebar.caption(f"MHD-INT {VERSION_PRO} · {NIVEL} · by Solaris Core")
st.sidebar.caption(f"🔑 Licenciado a: {LICENCIA['comprador']}")
st.sidebar.markdown("---")
st.sidebar.markdown("**Navegación**")
modo = st.sidebar.radio("Modo", _modos_disponibles, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("**Herramientas**")

# ---- Historial ----
if st.sidebar.button("📂 Ver historial de simulaciones"):
    st.session_state["mostrar_historial"] = not st.session_state.get("mostrar_historial", False)

if st.session_state.get("mostrar_historial", False):
    st.subheader("📜 Historial de simulaciones")
    st.caption("Solo se muestran las simulaciones de tu sesión actual.")
    _mi_sesion = obtener_sesion_id()
    df_hist = cargar_historial(sesion_id=_mi_sesion)
    if df_hist.empty:
        st.info("Aún no hay simulaciones guardadas en esta sesión.")
    else:
        st.dataframe(con_nombres_legibles(df_hist.sort_values("timestamp", ascending=False), ETIQUETAS_HISTORIAL))
        csv = con_nombres_legibles(df_hist, ETIQUETAS_HISTORIAL).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Descargar mi historial (CSV)",
            data=csv,
            file_name="historial_completo.csv",
            mime="text/csv",
        )
    if st.button("🗑️ Borrar mi historial"):
        st.session_state["confirmar_borrado_historial"] = True
    if st.session_state.get("confirmar_borrado_historial", False):
        st.warning("¿Confirmás borrar tu historial de esta sesión? Esta acción no se puede deshacer.")
        cb1, cb2 = st.columns(2)
        if cb1.button("Sí, borrar el mío"):
            borrar_historial(sesion_id=_mi_sesion)
            st.session_state["confirmar_borrado_historial"] = False
            st.success("Tu historial fue borrado.")
            st.rerun()
        if cb2.button("Cancelar"):
            st.session_state["confirmar_borrado_historial"] = False
    st.markdown("---")

# ============================================================================
# MODO: Simulación  (resultado PREMIUM)
# ============================================================================
if modo == "📚 Educación":
    render_educacion()

elif modo == "Simulación":
    planeta = st.sidebar.selectbox("Planeta", list(PLANETAS.keys()))
    t_max = st.sidebar.slider("Tiempo máximo (Gyr)", 0.1, 10.0, 5.0, 0.1)
    dt = st.sidebar.select_slider("Paso (años)", options=[1000, 5000, 10000, 50000, 100000], value=10000)

    st.sidebar.subheader("⚙️ Control de torques (experimentos)")
    torque_mag = st.sidebar.checkbox("Torque magnético", True)
    torque_tide = st.sidebar.checkbox("Marea estelar", True)
    torque_lunar = st.sidebar.checkbox("Marea lunar", True)

    st.sidebar.subheader("🧠 Modelo de dínamo y atmósfera")
    usar_termico = st.sidebar.checkbox(
        "Activar modelo térmico (Christensen 2009)", value=False,
        help="Balance energético real del núcleo (Q_CMB, manto)."
    )
    usar_atmosfera = st.sidebar.checkbox(
        "Activar pérdida atmosférica (escape XUV)", value=False,
        help="Simula la foto-evaporación de la atmósfera (Owen & Jackson 2012)."
    )
    if usar_atmosfera and dt > 1000:
        st.sidebar.warning("⚠️ Con atmósfera activa se recomienda dt ≤ 1000 años.")

    if st.sidebar.button("Simular"):
        with st.spinner("Simulando..."):
            params_extra = {
                "torque_magnetico": torque_mag,
                "torque_marea_estelar": torque_tide,
                "torque_lunar": torque_lunar,
                "modelo_termico": usar_termico,
                "modelo_atmosfera": usar_atmosfera,
            }
            resultado = simular_planeta(planeta, t_max_gyr=t_max, dt_yr=dt,
                                        incluir_serie=True, parametros_extra=params_extra)
        st.session_state["ultimo_resultado"] = resultado
        st.session_state["ultimos_params"] = {
            "planeta": planeta, "t_max_gyr": t_max, "dt_yr": dt,
            "modelo_termico": usar_termico, "modelo_atmosfera": usar_atmosfera,
        }
        st.session_state["ultimo_usar_termico"] = usar_termico
        st.session_state["ultimo_usar_atmosfera"] = usar_atmosfera
        # FIX v5.2: clave de video calculada con TODOS los parámetros que
        # afectan la física (params_extra completo), no solo planeta/t_max/dt.
        st.session_state["ultimo_video_key"] = _clave_video(planeta, params_extra, t_max, dt)

    if "ultimo_resultado" in st.session_state:
        resultado = st.session_state["ultimo_resultado"]
        usar_termico_res = st.session_state.get("ultimo_usar_termico", False)
        usar_atmosfera_res = st.session_state.get("ultimo_usar_atmosfera", False)
        render_reporte_comercial(
            resultado,
            st.session_state.get("ultimos_params", {}),
            usar_termico_res,
            usar_atmosfera_res,
            video_key=st.session_state.get("ultimo_video_key"),
        )

# ============================================================================
# MODO: Sintético  (resultado PREMIUM)
# ============================================================================
elif modo == "Sintético":
    st.subheader("🧬 Diseña tu propio planeta")
    st.caption("Parte de la Tierra como base; los parámetros no listados abajo "
               "(perfil de viento estelar) quedan con el valor terrestre.")

    # ------------------------------------------------------------------
    # MEJORA #5 — Presets rápidos
    # Valores tomados directo de database.py (Tierra/Venus/Marte reales).
    # El preset "Júpiter" es una aproximación DENTRO del rango de los
    # sliders (masa tope 10 M⊕, radio tope 3 R⊕, distancia tope 2.5 UA) --
    # el Júpiter real (318 M⊕, 11 R⊕, 5.2 UA) excede esos rangos. Se marca
    # explícitamente como no-a-escala, mismo criterio que ya usa el motor
    # para no hacer pasar un dato estimado por uno medido.
    # ------------------------------------------------------------------
    PRESETS_SINTETICO = {
        "🌍 Tierra": {
            "sint_masa": 1.0, "sint_radio": 1.0, "sint_a_ua": 1.0,
            "sint_B_inicial_G": 0.31, "sint_tipo_planeta": "Terrestre",
            "sint_P_rot_dias": 0.9973, "sint_e_inicial": 0.0167,
            "sint_tipo_estrella": "G2V", "sint_edad_estrella": 4.6,
            "sint_eps_inicial_deg": 23.44,
            "sint_inercia": 0.33, "sint_difusividad": 1.2, "sint_k2_sobre_q": 0.015,
        },
        "🟠 Venus": {
            "sint_masa": 0.8151, "sint_radio": 0.9499, "sint_a_ua": 0.723,
            "sint_B_inicial_G": 0.0001, "sint_tipo_planeta": "Terrestre",
            # NOTA: el período real de Venus es 243.02 días RETRÓGRADOS.
            # El slider de este modo solo admite magnitud (siempre calcula
            # w_p_inicial positivo) -- no hay forma de cargar el sentido
            # retrógrado desde acá. Se carga la magnitud real; el sentido
            # queda prógrado por limitación de la UI, no por error de dato.
            "sint_P_rot_dias": 243.02, "sint_e_inicial": 0.0068,
            "sint_tipo_estrella": "G2V", "sint_edad_estrella": 4.6,
            "sint_eps_inicial_deg": 2.64,
            "sint_inercia": 0.33, "sint_difusividad": 1.3, "sint_k2_sobre_q": 0.015,
        },
        "🔴 Marte": {
            "sint_masa": 0.1075, "sint_radio": 0.5320, "sint_a_ua": 1.524,
            "sint_B_inicial_G": 0.0001, "sint_tipo_planeta": "Terrestre",
            "sint_P_rot_dias": 1.0259, "sint_e_inicial": 0.0934,
            "sint_tipo_estrella": "G2V", "sint_edad_estrella": 4.6,
            "sint_eps_inicial_deg": 25.19,
            "sint_inercia": 0.36, "sint_difusividad": 1.4, "sint_k2_sobre_q": 0.015,
        },
        "🟣 Júpiter (aprox., no a escala)": {
            "sint_masa": 10.0, "sint_radio": 3.0, "sint_a_ua": 2.5,
            "sint_B_inicial_G": 4.2, "sint_tipo_planeta": "Gigante gaseoso",
            "sint_P_rot_dias": 0.4135, "sint_e_inicial": 0.0489,
            "sint_tipo_estrella": "G2V", "sint_edad_estrella": 4.6,
            "sint_eps_inicial_deg": 3.13,
            "sint_inercia": 0.25, "sint_difusividad": 2.5, "sint_k2_sobre_q": 1.0e-5,
        },
    }
    DEFAULTS_SINTETICO = PRESETS_SINTETICO["🌍 Tierra"]
    for _k, _v in DEFAULTS_SINTETICO.items():
        st.session_state.setdefault(_k, _v)

    cols_preset = st.columns(len(PRESETS_SINTETICO))
    for _col, (_label, _valores) in zip(cols_preset, PRESETS_SINTETICO.items()):
        if _col.button(_label, key=f"preset_btn_{_label}", use_container_width=True):
            for _k, _v in _valores.items():
                st.session_state[_k] = _v
            st.rerun()
    if "🟣" in "".join(PRESETS_SINTETICO.keys()):
        st.caption(
            "El preset de Júpiter usa el tope de cada slider (masa, radio, "
            "distancia) para dar el 'sabor' de un gigante gaseoso -- el "
            "Júpiter real (318 masas terrestres, 5.2 UA) excede el rango "
            "de este modo. No lo tomes como una réplica exacta."
        )

    col1, col2 = st.columns(2)
    with col1:
        masa = st.slider("Masa (masas terrestres)", 0.1, 10.0, step=0.1, key="sint_masa")
        radio = st.slider("Radio (radios terrestres)", 0.5, 3.0, step=0.05, key="sint_radio")
        a_ua = st.slider("Distancia orbital (UA)", 0.02, 2.5, step=0.01, key="sint_a_ua")
        B_inicial_G = st.slider("Campo magnético inicial (Gauss)", 0.0, 5.0, step=0.01, key="sint_B_inicial_G")
        tipo_planeta = st.selectbox(
            "Tipo de planeta",
            ["Terrestre", "SuperTierra", "Gigante gaseoso", "Hot Jupiter", "SubNeptuno"],
            key="sint_tipo_planeta",
        )
    with col2:
        P_rot_dias = st.slider("Período de rotación inicial (días)", 0.1, 365.0, step=0.1, key="sint_P_rot_dias")
        e_inicial = st.slider("Excentricidad inicial", 0.0, 0.8, step=0.01, key="sint_e_inicial")
        tipo_estrella = st.selectbox("Tipo espectral de la estrella", ["G2V", "G5V", "K5V", "F8V", "M5V"], key="sint_tipo_estrella")
        edad_estrella = st.slider("Edad de la estrella (Gyr)", 0.5, 10.0, step=0.1, key="sint_edad_estrella")
        t_max = st.slider("Tiempo de simulación (Gyr)", 0.5, 10.0, 5.0, 0.5, key="sint_t_max")
        eps_inicial_deg = st.slider(
            "Oblicuidad inicial (grados)", 0.0, 180.0, step=0.1, key="sint_eps_inicial_deg",
            help="Inclinación del eje de rotación. Como lo elegís vos, cuenta como dato 'conocido'."
        )

    # ------------------------------------------------------------------
    # MEJORA #1 — Parámetros internos avanzados (EXCLUSIVO PRO)
    # Confirmado contra engine.py: inercia, difusividad y k2_sobre_q se
    # leen todos vía self.parametros.get(...) / override explícito, así
    # que llegan al motor por el mismo mecanismo genérico de
    # parametros_extra que ya usan M/R_p/a_inicial -- sin tocar engine.py.
    # ------------------------------------------------------------------
    if NIVEL == "PRO":
        with st.expander("⚙️ Parámetros internos avanzados (opcional)"):
            st.caption(
                "Por defecto el motor asigna estos valores según el tipo de "
                "planeta. Tocalos solo si sabés lo que estás simulando."
            )
            ci1, ci2, ci3 = st.columns(3)
            inercia = ci1.slider(
                "Momento de inercia (I/MR²)", 0.20, 0.40, step=0.01, key="sint_inercia",
                help="0.33 = Tierra (núcleo denso concentrado). 0.25 = gigante gaseoso (masa más distribuida).",
            )
            difusividad = ci2.slider(
                "Difusividad magnética (η)", 0.5, 3.0, step=0.1, key="sint_difusividad",
                help="1.2 = Tierra. 2.5 = Júpiter. Afecta qué tan rápido decae el campo magnético.",
            )
            k2_sobre_q = ci3.number_input(
                "k2/Q (acoplamiento de marea)", min_value=1.0e-6, max_value=0.05,
                step=1.0e-4, format="%.6f", key="sint_k2_sobre_q",
                help="0.015 = rocoso típico. 1e-5 = gigante gaseoso. El motor ya elige uno de estos dos "
                     "según el radio si no lo tocás; acá lo podés fijar a mano.",
            )
    else:
        # Standard no ve los sliders, pero el preset elegido ya cargó
        # valores físicamente coherentes en session_state -- se siguen
        # usando esos (sin exponer el control manual), no un default
        # arbitrario.
        inercia = st.session_state.get("sint_inercia", DEFAULTS_SINTETICO["sint_inercia"])
        difusividad = st.session_state.get("sint_difusividad", DEFAULTS_SINTETICO["sint_difusividad"])
        k2_sobre_q = st.session_state.get("sint_k2_sobre_q", DEFAULTS_SINTETICO["sint_k2_sobre_q"])

    # ------------------------------------------------------------------
    # MEJORA #6 — Parámetros térmicos del núcleo (EXCLUSIVO PRO)
    # Confirmado contra engine.py: R_core, T_cmb_inicial_K y
    # T_manto_inicial_K se leen con self.parametros.get(clave, default) --
    # llegan por el mismo parametros_extra genérico, sin tocar engine.py.
    # Antes, el modo Sintético ni siquiera tenía el toggle de modelo
    # térmico (quedaba hardcodeado a False al renderizar el reporte).
    # ------------------------------------------------------------------
    if NIVEL == "PRO":
        usar_termico_sint = st.checkbox(
            "🔥 Activar modelo térmico (Christensen 2009)", value=False, key="sint_usar_termico",
            help="Habilita el gauge de Reynolds magnético y el balance térmico del núcleo.",
        )
        if usar_termico_sint:
            with st.expander("🔥 Parámetros térmicos del núcleo (opcional)", expanded=True):
                ct_a, ct_b, ct_c = st.columns(3)
                R_core_frac = ct_a.slider(
                    "R_core / R_p", 0.20, 0.70, 0.55, 0.01, key="sint_R_core_frac",
                    help="0.55 = Tierra. 0.14 = Júpiter (núcleo pequeño relativo al planeta).",
                )
                T_cmb_inicial_K = ct_b.slider(
                    "T_CMB inicial (K)", 1000.0, 20000.0, 4000.0, 100.0, key="sint_T_cmb_inicial_K",
                    help="Temperatura núcleo-manto inicial. 4000 K ≈ Tierra.",
                )
                T_manto_inicial_K = ct_c.slider(
                    "T_manto inicial (K)", 500.0, 10000.0, 2000.0, 100.0, key="sint_T_manto_inicial_K",
                )
        else:
            R_core_frac, T_cmb_inicial_K, T_manto_inicial_K = 0.55, 4000.0, 2000.0
    else:
        usar_termico_sint = False
        R_core_frac, T_cmb_inicial_K, T_manto_inicial_K = 0.55, 4000.0, 2000.0

    # ------------------------------------------------------------------
    # MEJORA #2 — Atmósfera personalizada (Standard + Pro)
    # Confirmado contra engine.py: M_atm_inicial y eficiencia_escape se
    # leen igual, vía parametros_extra. Mismo caso que el térmico: el
    # modo Sintético no tenía el toggle, quedaba hardcodeado a False.
    # ------------------------------------------------------------------
    usar_atmosfera_sint = st.checkbox(
        "🌍 Activar pérdida atmosférica (escape XUV)", value=False, key="sint_usar_atmosfera",
        help="Simula foto-evaporación (Owen & Jackson 2012). Con esto activo se recomienda dt bajo.",
    )
    if usar_atmosfera_sint:
        with st.expander("🌍 Parámetros de atmósfera (opcional)", expanded=True):
            ca1, ca2 = st.columns(2)
            M_atm_inicial_tierras = ca1.slider(
                "Masa atmósfera inicial (masas terrestres)", 0.0, 100.0, 1.0, 0.1, key="sint_M_atm_tierras",
                help="1.0 = Tierra. 0 = sin atmósfera (como Marte, aprox.). Valores altos = mundo tipo Venus.",
            )
            eficiencia_escape = ca2.slider(
                "Eficiencia de escape", 0.0, 1.0, 0.15, 0.01, key="sint_eficiencia_escape",
                help="0.15 = Tierra. 0.5 = Marte (escapa más rápido por menor gravedad).",
            )
    else:
        M_atm_inicial_tierras, eficiencia_escape = 1.0, 0.15

    # ------------------------------------------------------------------
    # MEJORA #3 — Luna personalizada (EXCLUSIVO PRO)
    # Depende del fix de estado global (ya aplicado y verificado a
    # engine.py) para poder usarse sin corromper LUNAS["Tierra"]. No
    # requiere NINGÚN cambio adicional a engine.py: usa el mismo mecanismo
    # `lunas_personalizadas` que ya existía en simular_planeta().
    #
    # k2 y Q_p de la Luna NUNCA aparecen por separado en la física
    # (calcular_torque_lunar solo usa la razón k2/Q_p) -- exponer los dos
    # como sliders independientes daría una falsa sensación de dos grados
    # de libertad donde físicamente hay uno solo. Se expone la razón.
    #
    # CAMBIO DE COMPORTAMIENTO POR DEFECTO: antes, cualquier planeta
    # sintético con "Marea lunar" tildado (default True) heredaba en
    # silencio la Luna real de la Tierra (self.lunas_db.get("Tierra") la
    # encuentra si no se manda un override). Con este toggle en OFF por
    # defecto, ahora el planeta sintético NO tiene luna a menos que se
    # pida explícitamente.
    # ------------------------------------------------------------------
    if NIVEL == "PRO":
        usar_luna_sint = st.checkbox(
            "🌙 Añadir luna personalizada", value=False, key="sint_usar_luna",
            help="Si lo dejás apagado, el planeta sintético no tiene luna (antes heredaba en "
                 "silencio la Luna real de la Tierra si 'Marea lunar' estaba activo).",
        )
        if usar_luna_sint:
            with st.expander("🌙 Parámetros de la luna (opcional)", expanded=True):
                cl1, cl2, cl3 = st.columns(3)
                masa_luna_tierras = cl1.slider(
                    "Masa de la luna (masas terrestres)", 0.0, 0.1, 0.0123, 0.001, key="sint_masa_luna",
                    help="0.0123 = Luna real. 0 = sin luna (equivalente a apagar el toggle).",
                )
                distancia_luna_ua = cl2.slider(
                    "Distancia inicial (UA)", 0.001, 0.01, 0.00257, 0.0001, key="sint_distancia_luna",
                    format="%.5f",
                    help="0.00257 UA = distancia Tierra-Luna real. Piso subido de 0.0001 a 0.001: por "
                         "debajo de eso el integrador del motor (paso fijo de 10.000 años) no resuelve "
                         "la órbita de una luna tan cercana y el resultado se vuelve numéricamente "
                         "inestable -- confirmado con pruebas, no es solo cautela.",
                )
                k2_qp_luna = cl3.slider(
                    "k2/Q_p (acoplamiento planeta-luna)", 0.001, 0.1, 0.025, 0.001, key="sint_k2qp_luna",
                    format="%.3f",
                    help="0.025 = razón real Tierra-Luna (k2=0.3, Q_p=12). Solo importa la razón, "
                         "no los valores individuales.",
                )
        else:
            masa_luna_tierras, distancia_luna_ua, k2_qp_luna = 0.0, 0.00257, 0.025
    else:
        # Standard: sin luna personalizada. Mismo default "sin luna" que
        # Pro usa cuando el toggle está apagado -- no hereda la Luna real
        # en silencio (ver CAMBIO DE COMPORTAMIENTO arriba).
        usar_luna_sint = False
        masa_luna_tierras, distancia_luna_ua, k2_qp_luna = 0.0, 0.00257, 0.025

    st.subheader("⚙️ Control de torques (opcional)")
    ct1, ct2, ct3 = st.columns(3)
    tm_on = ct1.checkbox("Torque magnético", True, key="sint_tmag")
    tt_on = ct2.checkbox("Marea estelar", True, key="sint_ttide")
    tl_on = ct3.checkbox(
        "Marea lunar", True, key="sint_tluna",
        help="Solo aísla si la marea lunar afecta la ROTACIÓN del planeta. La órbita de la luna "
             "(si hay una) evoluciona igual esté esto tildado o no.",
    )

    if st.button("🚀 Simular planeta sintético", type="primary"):
        M_TIERRA = 5.972e24
        M_ATM_TIERRA_KG = 5.15e18
        w_p_inicial = 2 * np.pi / (P_rot_dias * 24 * 3600)
        masa_estelar_kg = {
            "G2V": 1.00 * M_SOL, "G5V": 0.97 * M_SOL, "K5V": 0.69 * M_SOL,
            "F8V": 1.20 * M_SOL, "M5V": 0.12 * M_SOL,
        }
        densidad_nucleo = 11000.0 if tipo_planeta in ("Gigante gaseoso", "Hot Jupiter") else 10000.0
        R_p_metros = radio * R_TIERRA
        params_extra = {
            "M": masa * M_TIERRA,
            "R_p": R_p_metros,
            "a_inicial": a_ua * UA,
            "w_p_inicial": w_p_inicial,
            "B_p_inicial": B_inicial_G * 1e-4,
            "e_inicial": e_inicial,
            "tipo_planeta": tipo_planeta,
            "densidad_nucleo": densidad_nucleo,
            "torque_magnetico": tm_on,
            "torque_marea_estelar": tt_on,
            "torque_lunar": tl_on,
            "eps_inicial_deg": eps_inicial_deg,
            "eps_conocido": True,
            # MEJORA #1 — parámetros internos avanzados
            "inercia": inercia,
            "difusividad": difusividad,
            "k2_sobre_q": k2_sobre_q,
            # MEJORA #6 — térmicos del núcleo (el motor los ignora si
            # modelo_termico=False, pero se envían siempre para que
            # activar/desactivar el checkbox no pierda lo que el usuario cargó)
            "modelo_termico": usar_termico_sint,
            "R_core": R_core_frac * R_p_metros,
            "T_cmb_inicial_K": T_cmb_inicial_K,
            "T_manto_inicial_K": T_manto_inicial_K,
            # MEJORA #2 — atmósfera personalizada
            "modelo_atmosfera": usar_atmosfera_sint,
            "M_atm_inicial": M_atm_inicial_tierras * M_ATM_TIERRA_KG,
            "eficiencia_escape": eficiencia_escape,
        }
        estrella_personalizada = {
            "masa_kg": masa_estelar_kg[tipo_estrella],
            "tipo_espectral": tipo_estrella,
            "edad_gyr": edad_estrella,
        }
        # MEJORA #3 — luna personalizada. Se manda SIEMPRE de forma
        # explícita (con masa=0.0 si el toggle está apagado) para no
        # depender del fallback silencioso de self.lunas_db.get("Tierra").
        # "Tierra" es la clave correcta acá porque simular_planeta() se
        # llama con ese nombre fijo en todo el modo Sintético (ver
        # llamada más abajo) -- gracias al fix de engine.py, esto pisa la
        # entrada SOLO dentro de esta instancia de MotorMHD, sin tocar
        # LUNAS["Tierra"] global.
        masa_luna_kg = masa_luna_tierras * M_TIERRA
        lunas_personalizadas = {
            "Tierra": {
                "masa": masa_luna_kg,
                "a_luna_inicial": distancia_luna_ua * UA,
                "k2": k2_qp_luna,
                "Q_p": 1.0,  # solo importa la razon k2/Q_p; Q_p=1.0 hace que k2 SEA la razon
            }
        }
        with st.spinner("Simulando..."):
            resultado = simular_planeta(
                "Tierra", t_max_gyr=t_max, dt_yr=10000.0,
                incluir_serie=True, parametros_extra=params_extra,
                estrella_personalizada=estrella_personalizada,
                lunas_personalizadas=lunas_personalizadas,
            )
        st.session_state["ultimo_resultado_sint"] = resultado
        st.session_state["ultimos_params_sint"] = {
            "planeta": f"Sintético ({tipo_planeta})",
            "t_max_gyr": t_max, "dt_yr": 10000.0,
        }
        # MEJORA #2/#6: antes render_reporte_comercial() recibía
        # usar_termico/usar_atmosfera hardcodeados en False para el modo
        # Sintético -- aunque el motor hubiera corrido esos modelos, el
        # gauge Rm y el panel de atmósfera nunca se mostraban. Ahora se
        # guarda el estado real de los checkboxes.
        st.session_state["ultimo_usar_termico_sint"] = usar_termico_sint
        st.session_state["ultimo_usar_atmosfera_sint"] = usar_atmosfera_sint
        # MEJORA #3: se guarda el radio del planeta (en UA) para poder
        # avisar si la luna terminó "chocando" -- el motor la frena en
        # a_luna = R_p sin ninguna bandera propia de colisión, así que el
        # aviso se arma acá comparando contra el resultado.
        st.session_state["ultimo_tenia_luna_sint"] = masa_luna_tierras > 0.0
        st.session_state["ultimo_R_p_ua_sint"] = R_p_metros / UA
        # FIX v5.2: la clave de video ahora depende del payload completo
        # (params_extra + estrella_personalizada), no solo masa/radio/t_max.
        # Antes, cambiar la distancia orbital, el campo inicial, la
        # excentricidad o la estrella sin tocar masa/radio/t_max mostraba
        # el video de la corrida anterior.
        payload_sint = dict(params_extra)
        payload_sint["estrella_personalizada"] = estrella_personalizada
        payload_sint["lunas_personalizadas"] = lunas_personalizadas
        st.session_state["ultimo_video_key_sint"] = _clave_video(
            "Tierra_sintetico", payload_sint, t_max, 10000.0, prefijo="video_sint",
        )

    if "ultimo_resultado_sint" in st.session_state:
        resultado = st.session_state["ultimo_resultado_sint"]
        if not resultado.es_valido():
            st.error(f"Simulación inválida: {resultado.error}")
        else:
            # MEJORA #3: aviso de colisión lunar -- el motor frena a_luna en
            # R_p (ver calcular_recesion_lunar / a_luna_nuevo en engine.py)
            # pero no expone una bandera de "la luna chocó". Se reconstruye
            # acá comparando el a_luna final contra el radio del planeta.
            if st.session_state.get("ultimo_tenia_luna_sint") and resultado.tiene_serie():
                r_p_ua = st.session_state.get("ultimo_R_p_ua_sint", 0.0)
                a_luna_final = getattr(resultado, "a_luna_final_ua", None)
                if a_luna_final is not None and r_p_ua > 0 and a_luna_final <= r_p_ua * 1.01:
                    st.warning(
                        "🌙💥 La luna migró hacia adentro hasta chocar contra el planeta "
                        f"(distancia final ≈ radio del planeta, {a_luna_final:.6f} UA). "
                        "El motor la frena ahí pero no la elimina del sistema."
                    )
                # MEJORA #3: chequeo de estabilidad numérica. El integrador
                # de engine.py usa paso fijo (10.000 años); confirmado con
                # pruebas que ciertas combinaciones de luna (masa alta +
                # distancia corta + acoplamiento fuerte + rotación lenta del
                # planeta) hacen que el paso sea demasiado grande frente al
                # período orbital real de la luna, y el resultado diverge
                # numéricamente -- sin que motor.es_valido() lo detecte (el
                # estado queda con w_p de miles de rad/s, físicamente
                # imposible, pero "válido" para el motor). Se agrega acá un
                # chequeo defensivo independiente del rango del slider,
                # porque el límite de estabilidad no es una recta prolija
                # (encontramos zona caótica entre 0.0005-0.0009 UA con
                # ciertos parámetros) y no hay garantía de haber cubierto
                # todas las combinaciones posibles con la sola restricción
                # del slider.
                w_final_abs = abs(getattr(resultado, "w_final", 0.0))
                if w_final_abs > 1e-2:  # periodo de rotacion final < ~10 minutos
                    st.error(
                        "⚠️ Esta combinación de luna produjo una inestabilidad numérica "
                        "en el integrador (el motor usa paso fijo de 10.000 años, y esta "
                        "combinación de masa/distancia/acoplamiento requiere resolución "
                        "mucho más fina). El resultado no es físicamente confiable -- "
                        "probá con una luna más liviana, más lejana, o un acoplamiento "
                        "k2/Q_p más débil."
                    )

            render_reporte_comercial(
                resultado,
                st.session_state["ultimos_params_sint"],
                usar_termico=st.session_state.get("ultimo_usar_termico_sint", False),
                usar_atmosfera=st.session_state.get("ultimo_usar_atmosfera_sint", False),
                video_key=st.session_state.get("ultimo_video_key_sint"),
            )

# ============================================================================
# MODO: Mapa MHI  (idéntico al público)
# ============================================================================
elif modo == "Mapa MHI":
    st.subheader("🗺️ Mapa de calor MHI: distancia orbital × campo inicial")
    st.caption("El resto de los parámetros del planeta base queda fijo tal como está en la base de datos.")
    planeta_base = st.sidebar.selectbox("Planeta base", list(PLANETAS.keys()))
    a_min, a_max = st.sidebar.slider("Rango de distancia orbital (UA)", 0.01, 5.0, (0.5, 2.0), 0.01)
    B_min, B_max = st.sidebar.slider("Rango de campo inicial (Gauss)", 0.0, 5.0, (0.0, 2.0), 0.1)
    resolucion = st.sidebar.slider("Resolución de la malla (N×N)", 3, 25, 10, 1)
    t_max_mapa = st.sidebar.slider("Tiempo de simulación (Gyr)", 0.5, 10.0, 5.0, 0.5, key="t_max_mapa")
    total_sims = resolucion * resolucion
    st.sidebar.caption(f"⚠️ Esto va a correr {total_sims} simulaciones.")

    if st.sidebar.button("🔥 Generar mapa"):
        barra = st.progress(0.0, text="Simulando...")
        def _actualizar(frac):
            barra.progress(min(frac, 1.0), text=f"Simulando... {frac*100:.0f}%")
        with st.spinner("Generando mapa MHI..."):
            df_mapa = generar_mapa_mhi(
                planeta_base, (a_min, a_max), (B_min, B_max),
                n_pasos_a=resolucion, n_pasos_B=resolucion,
                t_max_gyr=t_max_mapa, progress_callback=_actualizar,
            )
        barra.empty()
        fallidas = df_mapa["MHI_total"].isna().sum()
        if fallidas > 0:
            st.warning(f"{fallidas} de {len(df_mapa)} combinaciones no se pudieron simular.")
        pivot = df_mapa.pivot(index="B_G", columns="a_ua", values="MHI_total")
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values, x=pivot.columns, y=pivot.index,
            colorscale="Viridis", zmin=0, zmax=100,
            colorbar=dict(title="MHI"),
        ))
        fig.update_layout(
            title=f"MHI de {planeta_base} — variando a y B_p inicial",
            xaxis_title="Distancia orbital (UA)",
            yaxis_title="Campo magnético inicial (Gauss)",
            width=800, height=550,
        )
        st.plotly_chart(fig, use_container_width=True)
        validos = df_mapa["MHI_total"].dropna()
        if not validos.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("MHI mínimo", f"{validos.min():.1f}")
            c2.metric("MHI máximo", f"{validos.max():.1f}")
            c3.metric("MHI promedio", f"{validos.mean():.1f}")
        with st.expander("Ver datos crudos"):
            st.dataframe(con_nombres_legibles(df_mapa, ETIQUETAS_MAPA_MHI))
        st.download_button("Descargar CSV", con_nombres_legibles(df_mapa, ETIQUETAS_MAPA_MHI).to_csv(index=False),
                           file_name=f"mapa_mhi_{planeta_base}.csv")

# ============================================================================
# MODO: Sensibilidad  (idéntico al público)
# ============================================================================
elif modo == "Sensibilidad":
    planeta = st.sidebar.selectbox("Planeta", list(PLANETAS.keys()))
    tipo_sens = st.sidebar.radio("Tipo de análisis",
                                  ["Básica (k2_sobre_q + densidad_nucleo)",
                                   "Extendida (1 parámetro a elección)"])
    if tipo_sens.startswith("Básica"):
        n_runs = st.sidebar.slider("Número de corridas", 10, 500, 100, 10)
        if st.sidebar.button("Ejecutar sensibilidad"):
            df = analisis_sensibilidad(planeta, n_runs=n_runs)
            st.dataframe(df)
            if not df.empty:
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=df["B_final_gauss"], nbinsx=30, name="B final"))
                st.plotly_chart(fig, use_container_width=True)
    else:
        param = st.sidebar.selectbox("Parámetro a variar", [
            "a_inicial", "B_p_inicial", "M", "R_p", "w_p_inicial",
            "densidad_nucleo", "difusividad", "k2_sobre_q",
        ])
        unidad = {"a_inicial": "UA", "B_p_inicial": "Gauss"}.get(param, "SI (mismas unidades que database.py)")
        st.sidebar.caption(f"Unidad: {unidad}")
        val_min = st.sidebar.number_input("Valor mínimo", value=0.1)
        val_max = st.sidebar.number_input("Valor máximo", value=2.0)
        n_runs = st.sidebar.slider("Número de puntos", 5, 200, 30, 5)
        if st.sidebar.button("Ejecutar sensibilidad extendida"):
            with st.spinner("Simulando..."):
                df = analisis_sensibilidad_extendido(planeta, param, (val_min, val_max), n_runs=n_runs)
            st.dataframe(df)
            df_ok = df[df["error"].isna()] if "error" in df.columns else df
            if not df_ok.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_ok[param], y=df_ok["B_final_gauss"],
                                         mode="lines+markers", name="B final (G)"))
                fig.update_layout(
                    title=f"Sensibilidad de B_final a {param}",
                    xaxis_title=f"{param} ({unidad})",
                    yaxis_title="B final (Gauss)",
                )
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# MODO: Validación  (idéntico al público)
# ============================================================================
elif modo == "Validación":
    st.subheader("✅ Validación contra datos reales")
    st.caption(
        "Compara lo que simula el motor contra mediciones reales de cada "
        "cuerpo (sondas espaciales, observaciones). Un error relativo por "
        "debajo del 5% se considera aprobado."
    )

    # ------------------------------------------------------------------
    # MEJORA: antes esta pantalla mostraba el diccionario crudo de
    # validacion.py con st.json() -- nombres de variable internos
    # (P_rot_dias, a_ua, B_gauss, error_relativo_pct...) sin ningún
    # contexto, pensados para debugging, no para un usuario básico. Se
    # reemplaza por una vista agrupada por planeta con nombres en
    # español y unidades explícitas.
    # ------------------------------------------------------------------
    ETIQUETAS_METRICAS_VALIDACION = {
        "P_rot_dias": ("Período de rotación", "días"),
        "a_ua": ("Distancia orbital", "UA"),
        "B_gauss": ("Campo magnético", "Gauss"),
        "e": ("Excentricidad orbital", ""),
        "sentido_rotacion": ("Sentido de rotación", ""),
    }

    if st.sidebar.button("Validar todo"):
        st.session_state["resultados_validacion"] = validar_todos()

    if "resultados_validacion" in st.session_state:
        resultados = st.session_state["resultados_validacion"]
        n_aprobados = sum(1 for r in resultados if r["aprueba"])
        st.metric("Cuerpos aprobados", f"{n_aprobados} / {len(resultados)}")
        st.markdown("---")

        for r in resultados:
            estado_icono = "✅" if r["aprueba"] else "❌"
            with st.expander(f"{estado_icono} {r['nombre']}", expanded=not r["aprueba"]):
                if r["error_simulacion"]:
                    st.error(f"La simulación no pudo completarse: {r['error_simulacion']}")
                    continue
                if not r["metricas"]:
                    st.info("Sin métricas para este cuerpo.")
                    continue

                filas = []
                for clave, m in r["metricas"].items():
                    etiqueta, unidad = ETIQUETAS_METRICAS_VALIDACION.get(clave, (clave, ""))
                    fila = {
                        "Métrica": etiqueta + (f" ({unidad})" if unidad else ""),
                        "Simulado": m["simulado"],
                        "Real (referencia)": m["real"],
                        "Diferencia": (
                            f"{m['error_relativo_pct']}%"
                            if m.get("error_relativo_pct") is not None
                            else "—"
                        ),
                        "¿Aprueba?": "✅" if m["aprueba"] else "❌",
                    }
                    filas.append(fila)
                st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)

        with st.expander("Ver datos técnicos completos (JSON)"):
            st.caption("Para revisión técnica o reportar un problema.")
            st.json(resultados)

# ============================================================================
# MODO: Comparador lado a lado  (Capa 3 — comercial)
# ============================================================================
elif modo == "⚡ Comparador":
    render_comparador()

elif modo == "🌌 Disco Protoplanetario (Beta)":
    render_disco_protoplanetario()

elif modo == "🧪 Modificador de Sistemas":
    render_modificador_sistemas()

# ============================================================================
# MODO: Glosario
# ============================================================================
elif modo == "📖 Glosario":
    st.subheader("Diccionario de términos")
    st.caption(
        "Qué significa cada variable y sigla que aparece en los gráficos, "
        "informes y validaciones de MHD-INT."
    )
    for seccion, terminos in GLOSARIO_TERMINOS.items():
        with st.expander(seccion, expanded=True):
            for _clave, (titulo, definicion) in terminos.items():
                st.markdown(f"**{titulo}**  \n{definicion}")
                st.markdown("---")
