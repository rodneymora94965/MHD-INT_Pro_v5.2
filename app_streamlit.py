import streamlit as st
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from engine import simular_planeta, UA, M_SOL, R_TIERRA
from database import PLANETAS
from sensibilidad_runner import analisis_sensibilidad, analisis_sensibilidad_extendido
from validacion import validar_todos
from habitabilidad import calcular_mhi, categoria_mhi
from estilo_app import metric_categoria, calidad_mhi
from mapa_mhi import generar_mapa_mhi
from historial import guardar_simulacion, cargar_historial, borrar_historial
from exportar_video import construir_json_video  # exportacion JSON para IAs de video
from glosario_terminos import obtener_glosario  # diccionario de terminos (ES/EN), compartido con Standard/Pro
from etiquetas_columnas import ETIQUETAS_HISTORIAL, ETIQUETAS_MAPA_MHI, con_nombres_legibles
from educacion_ui import render_educacion  # sección educativa
from ruta_aprendizaje_ui import render_ruta_aprendizaje  # ruta de aprendizaje curada
from biblioteca_fotos_ui import render_biblioteca_fotos  # biblioteca de fotos astronómicas
from sesion import obtener_sesion_id
from visualizacion_3d import render_orbita_3d
from eventos_ui import render_eventos
from i18n import t, selector_idioma
from contenido_i18n import nombre_cuerpo, tipo_visible, categoria_visible

VERSION_PUBLICA = "5.2.2"  # (definida arriba: la usa el título de la pestaña)

st.set_page_config(page_title=t("libre.pagina"), layout="wide", page_icon="assets/logo_mhd_int.png")

# ===================================================================
# Estilo Premium (CSS Injectado)
# Usa selectores [data-testid="..."], estables y documentados
# oficialmente por Streamlit (evita clases internas autogeneradas
# como .css-1d391kg, que cambian entre versiones).
# ===================================================================
st.markdown("""
<style>
    /* ===============================================================
       CAMBIO (ago-2026): paleta profesional/atenuada, reemplaza el
       rojo saturado tipo streaming y los botones "gritones" (mayúsculas
       + glow) por un estilo más cercano a dashboard técnico (tipo
       Cisco Packet Tracer / Boson NetSim): menos intensidad de color,
       menos efectos, jerarquía visual más clara.
       =============================================================== */
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
# ===================================================================

# ===================================================================
# NUEVO: logo del proyecto + numero de version PUBLICO.
# DECISION DE PRODUCTO (Roney, jul-2026): de cara al usuario, todo lo
# construido sobre v4.1 (nucleo termico v4.2, atmosfera v5.0, oblicuidad
# v5.1) se presenta bajo un unico numero: "v5.0". Los sub-numeros
# internos (v4.2 / v5.0 / v5.1) siguen existiendo en el codigo y en los
# CAMBIOS_*.md para trazabilidad tecnica, pero no se muestran en la
# interfaz -- para el usuario final es una sola version, la 5.0.
# ACTUALIZACION (Roney, sep-2026): la version publica pasa a 5.2 para
# alinearse con el paquete Pro v5.2. Mismo criterio: un unico numero.
# ===================================================================
# (VERSION_PUBLICA se define más arriba, antes de set_page_config)

col_logo, col_titulo = st.columns([1, 3])
with col_logo:
    st.image("assets/logo_mhd_int.png", width=90)
with col_titulo:
    st.caption(t("libre.cabecera", v=VERSION_PUBLICA))
# ===================================================================

# ===================================================================
# NUEVO: banner de "version de prueba" (sin bloqueo real -- decision
# explicita de Roney en vez del mecanismo de 30 dias). Solo informativo,
# para entregar a Kike/Gisela/Giancarlo. No limita ninguna funcionalidad
# ni cuenta tiempo ni usos. Para pasar a version completa, alcanza con
# poner EDICION = "COMPLETA" (o borrar el bloque).
# ===================================================================
# oct-2026: la edicion publica de GitHub es la "versión libre" (AGPL-3.0).
EDICION = "LIBRE"

if EDICION == "LIBRE":
    st.info(
        t("libre.banner"),
        icon="🔭",
    )
# ===================================================================

selector_idioma()  # 🌐 ES / EN, arriba de todo
st.sidebar.image("assets/logo_mhd_int.png", width=70)
# i18n: los modos son IDs internos estables; el texto visible lo pone format_func.
# Nunca se compara contra texto traducido (trampa #1).
modo = st.sidebar.radio(t("sidebar.modo"), ["ruta_aprendizaje", "educacion", "simulacion", "sintetico", "mapa_mhi", "sensibilidad", "validacion", "biblioteca_fotos", "glosario"],
                        format_func=lambda mid: t(f"menu.{mid}"))

st.sidebar.markdown("---")
st.sidebar.caption(f"MHD-INT v{VERSION_PUBLICA} · by Solaris Core")

# ==================== Historial de simulaciones ====================
# La confirmacion de borrado usa st.session_state en dos pasos
# independientes, que sobreviven entre reruns de Streamlit.
if st.sidebar.button(t("historial.btn")):
    st.session_state["mostrar_historial"] = not st.session_state.get("mostrar_historial", False)

if st.session_state.get("mostrar_historial", False):
    st.subheader(t("historial.titulo"))
    st.caption(t("historial.caption"))
    _mi_sesion = obtener_sesion_id()
    df_hist = cargar_historial(sesion_id=_mi_sesion)
    if df_hist.empty:
        st.info(t("historial.vacio"))
    else:
        st.dataframe(con_nombres_legibles(df_hist.sort_values("timestamp", ascending=False), ETIQUETAS_HISTORIAL))
        csv = con_nombres_legibles(df_hist, ETIQUETAS_HISTORIAL).to_csv(index=False).encode("utf-8")
        st.download_button(
            label=t("historial.descargar"),
            data=csv,
            file_name="historial_completo.csv",
            mime="text/csv",
        )
        if st.button(t("historial.borrar")):
            st.session_state["confirmar_borrado_historial"] = True

        if st.session_state.get("confirmar_borrado_historial", False):
            st.warning(t("historial.confirmar"))
            cb1, cb2 = st.columns(2)
            if cb1.button(t("historial.si")):
                borrar_historial(sesion_id=_mi_sesion)
                st.session_state["confirmar_borrado_historial"] = False
                st.success(t("historial.borrado"))
                st.rerun()
            if cb2.button(t("historial.cancelar")):
                st.session_state["confirmar_borrado_historial"] = False
    st.markdown("---")
# ==================================================================================================

if "primera_visita_vista" not in st.session_state:
    st.session_state["primera_visita_vista"] = False

if not st.session_state["primera_visita_vista"] and modo != "ruta_aprendizaje":
    _col_banner, _col_cerrar = st.columns([5, 1])
    with _col_banner:
        st.info(t("bienvenida.texto"))
    with _col_cerrar:
        if st.button(t("bienvenida.cerrar"), key="cerrar_banner_primera_visita"):
            st.session_state["primera_visita_vista"] = True
            st.rerun()

if modo == "ruta_aprendizaje":
    st.session_state["primera_visita_vista"] = True
    render_ruta_aprendizaje()

elif modo == "educacion":
    render_educacion()

elif modo == "simulacion":
    planeta = st.sidebar.selectbox(t("sim.planeta"), list(PLANETAS.keys()), format_func=nombre_cuerpo)
    t_max = st.sidebar.slider(t("sim.t_max"), 0.1, 10.0, 5.0, 0.1)
    dt = st.sidebar.select_slider(t("sim.dt"), options=[1000, 5000, 10000, 50000, 100000], value=10000)

    # ==================== MEJORA v4.1: experimentos controlados ====================
    # Permite aislar el efecto de cada torque sobre la rotación (depuración /
    # fines didácticos). Los 3 activos por defecto = comportamiento normal.
    st.sidebar.subheader(t("sim.torques"))
    torque_mag = st.sidebar.checkbox(t("sim.torque_mag"), True)
    torque_tide = st.sidebar.checkbox(t("sim.torque_estelar"), True)
    torque_lunar = st.sidebar.checkbox(t("sim.torque_lunar"), True)
    # ================================================================================

    # ==================== NUEVO v4.2 + v5.0: modelo termico + atmosfera ====================
    st.sidebar.subheader(t("sim.dinamo"))
    usar_termico = st.sidebar.checkbox(
        t("libre.termico"),
        value=False,
        help=t("libre.termico.ayuda")
    )
    usar_atmosfera = st.sidebar.checkbox(
        t("sim.atmosfera"),
        value=False,
        help=t("libre.atm.ayuda")
    )
    if usar_atmosfera and dt > 1000:
        st.sidebar.warning(t("libre.atm.dt"))
    # ========================================================================================

    if st.sidebar.button(t("sim.boton")):
        with st.spinner(t("lab.sim.simulando")):
            params_extra = {
                "torque_magnetico": torque_mag,
                "torque_marea_estelar": torque_tide,
                "torque_lunar": torque_lunar,
                "modelo_termico": usar_termico,
                "modelo_atmosfera": usar_atmosfera,
            }
            resultado = simular_planeta(planeta, t_max_gyr=t_max, dt_yr=dt, incluir_serie=True,
                                         parametros_extra=params_extra)
        # El resultado se guarda en session_state para que sobreviva a
        # reruns posteriores (por ejemplo, al clickear "Guardar en
        # Historial"). Streamlit reevalua st.sidebar.button("Simular") como
        # False en cualquier rerun que no sea el del propio clic, asi que si
        # el bloque de resultados dependiera solo de ese boton, el boton de
        # guardar (y todo lo demas) desaparecería antes de poder usarse.
        st.session_state["ultimo_resultado"] = resultado
        st.session_state["ultimos_params"] = {
            "planeta": planeta, "t_max_gyr": t_max, "dt_yr": dt,
            "modelo_termico": usar_termico, "modelo_atmosfera": usar_atmosfera,
        }
        st.session_state["ultimo_usar_termico"] = usar_termico
        st.session_state["ultimo_usar_atmosfera"] = usar_atmosfera

    if "ultimo_resultado" in st.session_state:
        resultado = st.session_state["ultimo_resultado"]
        usar_termico_res = st.session_state.get("ultimo_usar_termico", False)
        usar_atmosfera_res = st.session_state.get("ultimo_usar_atmosfera", False)

        st.subheader(t("libre.resultado"))
        st.json(resultado.resumen_dict())

        mhi = None
        # ==================== BLOQUE MHI (reconectado) ====================
        if resultado.es_valido() and resultado.tiene_serie():
            st.markdown(t("libre.mhi.titulo"))
            mhi = calcular_mhi(resultado)
            m1, m2, m3 = st.columns([1.5, 1, 1])
            metric_categoria(m1, "MHI", f"{mhi['mhi_total']:.1f} / 100", categoria_visible(mhi['mhi_total']), calidad_mhi(mhi['mhi_total']))
            m1.progress(int(mhi["mhi_total"]) / 100)
            m2.metric(t("rep.mhi.escudo"), t("pdf.del_tiempo", v=format(mhi['escudo_mag_pct'], ".1f")))
            m2.metric(t("rep.mhi.dinamo"), t("pdf.del_tiempo", v=format(mhi['campo_activo_pct'], ".1f")))
            m3.metric(t("libre.mhi.exc"), f"{mhi['e_promedio']:.4f}")
            m3.metric(t("libre.mhi.marea"), f"{mhi['q_promedio_w']:.2e} W")
        # ====================================================================

        # ==================== NUEVO v4.2: estado térmico del núcleo ====================
        if usar_termico_res and resultado.tiene_serie():
            st.markdown(t("libre.term.titulo"))
            c1, c2, c3 = st.columns(3)
            c1.metric(t("rep.term.cmb"), f"{resultado.T_cmb_final_K:.0f}")
            c2.metric(t("rep.term.bgen"), f"{resultado.B_gen_final_gauss:.3f}")
            c3.metric(t("libre.term.rm"), f"{resultado.Rm_final:.1f}")
            if resultado.Rm_final > 40:
                st.success(t("libre.term.activo"))
            else:
                st.warning(t("libre.term.inactivo"))
        # ==================================================================================

        # ==================== NUEVO v5.0: estado de la atmósfera ====================
        if usar_atmosfera_res and resultado.tiene_serie():
            st.markdown(t("rep.atm.titulo"))
            c1, c2 = st.columns(2)
            M_atm_tierras = resultado.M_atm_final_kg / 5.15e18
            c1.metric(t("libre.atm.masa"), f"{M_atm_tierras:.4f}")
            if resultado.atm_perdida:
                metric_categoria(c2, t("rep.atm.atmosfera"), t("rep.atm.perdida"), t("libre.atm.esteril"), "malo")
                st.error(t("libre.atm.error"))
            else:
                metric_categoria(c2, t("rep.atm.atmosfera"), t("rep.atm.retenida"), t("libre.atm.protegida"), "bueno")
        # ================================================================================

        # ==================== NUEVO v5.1: evolución de la oblicuidad ====================
        # Solo se muestra si el planeta tiene dato real de oblicuidad
        # (eps_conocido=True) -- ver fix A.5 del informe de revision. Para
        # exoplanetas sin dato, no tiene sentido mostrar un grafico de algo
        # que arranca en 0 grados por falta de informacion, no por fisica.
        eps_conocido_res = getattr(resultado, "eps_conocido", False)
        if eps_conocido_res and resultado.tiene_serie() and len(resultado.serie.eps_deg) > 0:
            st.markdown(t("rep.obl.titulo"))
            df_eps = pd.DataFrame({
                "t_Gyr": resultado.serie.tiempos,
                "eps_deg": resultado.serie.eps_deg,
            })
            fig_eps = go.Figure()
            fig_eps.add_trace(go.Scatter(
                x=df_eps["t_Gyr"], y=df_eps["eps_deg"], mode="lines",
                name=t("col.serie.eps_deg"), line=dict(color="orange", width=3),
            ))
            fig_eps.add_hline(y=60, line_dash="dash", line_color="red", annotation_text=t("rep.obl.limite"))
            fig_eps.update_layout(
                xaxis_title=t("cat.ev.col.tiempo"), yaxis_title=t("rep.obl.eje_y"),
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
            )
            st.plotly_chart(fig_eps, use_container_width=True)

            eps_final_res = resultado.eps_final_deg
            if eps_final_res > 60:
                st.warning(t("rep.obl.extrema", eps=format(eps_final_res, ".1f")))
            else:
                st.success(t("rep.obl.ok", eps=format(eps_final_res, ".1f")))
        # ==================================================================================

        # ---- Órbita en 3D ----
        with st.expander(t("rep.orbita3d"), expanded=False):
            render_orbita_3d(resultado, planeta)

        # ---- Momentos capturables ----
        with st.expander(t("rep.momentos"), expanded=False):
            render_eventos(resultado, planeta)

        # ==================== Guardar en Historial ====================
        st.markdown("---")
        col_hist1, col_hist2 = st.columns([1, 3])
        with col_hist1:
            if st.button(t("rep.hist.boton"), type="primary"):
                try:
                    fila = guardar_simulacion(resultado, st.session_state["ultimos_params"], mhi=mhi, sesion_id=obtener_sesion_id())
                    st.success(t("libre.hist.ok", ts=fila['timestamp']))
                except Exception as exc:
                    st.error(t("rep.hist.error", error=exc))
        with col_hist2:
            st.caption(t("libre.hist.caption"))
        # ===========================================================================================

        # ==================== NUEVO: Exportar para IA de Video ====================
        # FIX: usa st.session_state (mismo patrón que "Guardar en Historial") para
        # no depender del estado momentáneo del botón "Simular".
        st.markdown(t("libre.video.titulo"))
        st.caption(t("libre.video.caption"))
        if resultado.tiene_serie():
            try:
                params_json = st.session_state["ultimos_params"]
                datos_json = construir_json_video(
                    resultado,
                    planeta=params_json["planeta"],
                    t_max_gyr=params_json["t_max_gyr"],
                    dt_yr=params_json["dt_yr"],
                )
                json_str = json.dumps(datos_json, ensure_ascii=False, indent=2)
                st.download_button(
                    label=t("libre.video.descargar"),
                    data=json_str,
                    file_name=f"{params_json['planeta']}_data.json",
                    mime="application/json",
                )
                st.caption(
                    t("libre.video.puntos", p=datos_json['meta']['puntos_exportados'], o=datos_json['meta']['puntos_originales'], m=2000)
                )
            except Exception as exc:
                st.error(t("libre.video.error", error=exc))
        # ============================================================================

        if resultado.tiene_serie():
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
                "a_ua": t("rep.var.a_ua"),
                "B_gauss": t("rep.var.B_gauss"),
                "w_p": t("rep.var.w_p"),
                "e": t("rep.var.e"),
                "T_cmb_K": t("rep.var.T_cmb_K"),
                "B_gen_gauss": t("rep.var.B_gen_gauss"),
                "Rm": t("rep.var.Rm"),
                "M_atm_kg": t("ev.var.M_atm_kg"),
                "eps_deg": t("rep.var.eps_deg"),
            }

            vars_disponibles = list(ETIQUETAS_VARIABLES.keys())
            vars_seleccionadas = st.multiselect(
                t("rep.graf.vars"),
                vars_disponibles,
                default=["a_ua", "B_gauss"],
                format_func=lambda v: ETIQUETAS_VARIABLES[v],
            )

            with st.expander(t("libre.umbral.titulo")):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    var_umbral = st.selectbox(
                        t("libre.variable"), ["__ninguna__"] + vars_disponibles,
                        format_func=lambda v: t("libre.ninguna") if v == "__ninguna__" else ETIQUETAS_VARIABLES[v],
                    )
                with col_u2:
                    valor_umbral = st.number_input(t("libre.umbral.valor"), value=0.0, format="%.6g")

            vista_panel = st.checkbox(t("libre.panel"), value=False)

            if not vars_seleccionadas:
                st.info(t("rep.graf.ninguna"))
            elif vista_panel:
                from plotly.subplots import make_subplots
                n = len(vars_seleccionadas)
                filas = (n + 1) // 2
                fig_panel = make_subplots(rows=filas, cols=2 if n > 1 else 1,
                                           subplot_titles=[ETIQUETAS_VARIABLES[v] for v in vars_seleccionadas])
                for idx, var in enumerate(vars_seleccionadas):
                    fila, col = idx // 2 + 1, idx % 2 + 1
                    fig_panel.add_trace(
                        go.Scatter(x=df["t_Gyr"], y=df[var], mode="lines", name=ETIQUETAS_VARIABLES[var]),
                        row=fila, col=col,
                    )
                    if var_umbral == var:
                        fig_panel.add_hline(y=valor_umbral, line_dash="dash", line_color="red",
                                             row=fila, col=col)
                fig_panel.update_layout(showlegend=False, height=300 * filas)
                fig_panel.update_xaxes(title_text=t("cat.ev.col.tiempo"))
                st.plotly_chart(fig_panel, use_container_width=True)
            else:
                fig = go.Figure()
                # Si mezclan escalas muy distintas, la primera variable va al eje
                # izquierdo y el resto (si son de otra magnitud) al eje derecho.
                escala_principal = vars_seleccionadas[0]
                for var in vars_seleccionadas:
                    mismo_eje = (var == escala_principal) or (
                        df[var].abs().max() > 0
                        and df[escala_principal].abs().max() > 0
                        and 0.01 < (df[var].abs().max() / df[escala_principal].abs().max()) < 100
                    )
                    fig.add_trace(go.Scatter(
                        x=df["t_Gyr"], y=df[var], mode="lines",
                        name=ETIQUETAS_VARIABLES[var],
                        yaxis="y" if mismo_eje else "y2",
                    ))
                if var_umbral != "__ninguna__" and var_umbral in vars_seleccionadas:
                    fig.add_hline(y=valor_umbral, line_dash="dash", line_color="red",
                                  annotation_text=t("libre.umbral.anot", v=ETIQUETAS_VARIABLES[var_umbral]))
                fig.update_layout(
                    xaxis_title=t("cat.ev.col.tiempo"),
                    yaxis=dict(title=ETIQUETAS_VARIABLES[escala_principal]),
                    yaxis2=dict(title=t("libre.otra_escala"), overlaying="y", side="right"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
                )
                st.plotly_chart(fig, use_container_width=True)

elif modo == "sintetico":
    # ==================== MEJORA v4.1 (Mejora 2) ====================
    # Parte del planeta "Tierra" en database.py como base y sobrescribe
    # solo los campos que el usuario cambia; lo que no se toca (perfil de
    # viento estelar rho_sw/v_sw, difusividad del núcleo, inercia) queda
    # con el valor terrestre. Es una simplificación deliberada: no hay
    # forma físicamente derivada de "inventar" esos valores para un
    # planeta que no existe, así que se documenta el supuesto en vez de
    # ocultarlo.
    st.subheader(t("sint.titulo"))
    st.caption(t("libre.sint.caption"))

    col1, col2 = st.columns(2)
    with col1:
        masa = st.slider(t("sint.masa"), 0.1, 10.0, 1.0, 0.1)
        radio = st.slider(t("sint.radio"), 0.5, 3.0, 1.0, 0.05)
        a_ua = st.slider(t("col.mapa.a_ua"), 0.02, 2.5, 1.0, 0.01)
        B_inicial_G = st.slider(t("mapa.fig.y"), 0.0, 5.0, 0.3, 0.01)
        tipo_planeta = st.selectbox(t("sint.tipo_planeta"),
                                     ["Terrestre", "SuperTierra", "Gigante gaseoso", "Hot Jupiter", "SubNeptuno"],
                                     format_func=tipo_visible)
    with col2:
        P_rot_dias = st.slider(t("col.res.P_rot_inicial_dias"), 0.1, 365.0, 1.0, 0.1)
        e_inicial = st.slider(t("col.res.e_inicial"), 0.0, 0.8, 0.0167, 0.01)
        tipo_estrella = st.selectbox(t("sint.tipo_estrella"), ["G2V", "G5V", "K5V", "F8V", "M5V"])
        edad_estrella = st.slider(t("sint.edad"), 0.5, 10.0, 4.6, 0.1)
        t_max = st.slider(t("mapa.t_max"), 0.5, 10.0, 5.0, 0.5)
        eps_inicial_deg = st.slider(
            t("sint.eps"), 0.0, 180.0, 23.44, 0.1,
            help=t("libre.sint.eps.ayuda")
        )

    st.subheader(t("sint.torques.titulo"))
    ct1, ct2, ct3 = st.columns(3)
    tm_on = ct1.checkbox(t("sim.torque_mag"), True, key="sint_tmag")
    tt_on = ct2.checkbox(t("sim.torque_estelar"), True, key="sint_ttide")
    tl_on = ct3.checkbox(t("sim.torque_lunar"), True, key="sint_tluna")
    st.caption(t("libre.sint.luna"))

    if st.button(t("sint.simular"), type="primary"):
        M_TIERRA = 5.972e24
        w_p_inicial = 2 * np.pi / (P_rot_dias * 24 * 3600)

        masa_estelar_kg = {
            "G2V": 1.00 * M_SOL, "G5V": 0.97 * M_SOL, "K5V": 0.69 * M_SOL,
            "F8V": 1.20 * M_SOL, "M5V": 0.12 * M_SOL,
        }
        # Mismo criterio que usa engine.py internamente para distinguir
        # núcleo rocoso vs gaseoso (ver __init__ / k2_sobre_q).
        densidad_nucleo = 11000.0 if tipo_planeta in ("Gigante gaseoso", "Hot Jupiter") else 10000.0

        params_extra = {
            "M": masa * M_TIERRA,
            "R_p": radio * R_TIERRA,
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
        }
        estrella_personalizada = {
            "masa_kg": masa_estelar_kg[tipo_estrella],
            "tipo_espectral": tipo_estrella,
            "edad_gyr": edad_estrella,
        }

        with st.spinner(t("lab.sim.simulando")):
            resultado = simular_planeta(
                "Tierra",
                t_max_gyr=t_max,
                dt_yr=10000.0,
                incluir_serie=True,
                parametros_extra=params_extra,
                estrella_personalizada=estrella_personalizada,
            )

        if not resultado.es_valido():
            st.error(t("comp.invalida", error=resultado.error))
        else:
            st.subheader(t("libre.resultados"))
            st.json(resultado.resumen_dict())

            if resultado.tiene_serie():
                mhi = calcular_mhi(resultado)
                st.markdown(t("libre.mhi.titulo2"))
                cm1, cm2, cm3 = st.columns(3)
                metric_categoria(cm1, "MHI Total", f"{mhi['mhi_total']:.1f} / 100", categoria_visible(mhi['mhi_total']), calidad_mhi(mhi['mhi_total']))
                cm2.metric(t("rep.mhi.escudo"), f"{mhi['escudo_mag_pct']:.1f}%")
                cm3.metric(t("pdf.c.campo"), f"{mhi['campo_activo_pct']:.1f}%")

                serie = resultado.serie
                df_s = pd.DataFrame({"t_Gyr": serie.tiempos, "a_ua": serie.a_ua, "B_gauss": serie.B_p_gauss})
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_s["t_Gyr"], y=df_s["a_ua"], mode="lines", name=t("cat.col.a")))
                fig.add_trace(go.Scatter(x=df_s["t_Gyr"], y=df_s["B_gauss"], mode="lines", name="B (G)", yaxis="y2"))
                fig.update_layout(
                    xaxis_title=t("cat.ev.col.tiempo"),
                    yaxis=dict(title=t("cat.col.a")),
                    yaxis2=dict(title="B (G)", overlaying="y", side="right"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
                )
                st.plotly_chart(fig, use_container_width=True)
    # ================================================================================

elif modo == "mapa_mhi":
    # ==================== MEJORA v4.1 (Mejora 1) ====================
    st.subheader(t("mapa.titulo"))
    st.caption(t("libre.mapa.caption"))

    planeta_base = st.sidebar.selectbox(t("mapa.planeta"), list(PLANETAS.keys()), format_func=nombre_cuerpo)
    a_min, a_max = st.sidebar.slider(t("mapa.rango_a"), 0.01, 5.0, (0.5, 2.0), 0.01)
    B_min, B_max = st.sidebar.slider(t("mapa.rango_b"), 0.0, 5.0, (0.0, 2.0), 0.1)
    resolucion = st.sidebar.slider(t("mapa.resolucion"), 3, 25, 10, 1)
    t_max_mapa = st.sidebar.slider(t("mapa.t_max"), 0.5, 10.0, 5.0, 0.5, key="t_max_mapa")

    total_sims = resolucion * resolucion
    st.sidebar.caption(t("libre.mapa.aviso", n=total_sims))

    if st.sidebar.button(t("mapa.boton")):
        barra = st.progress(0.0, text=t("lab.sim.simulando"))

        def _actualizar(frac, mensaje=None):
            barra.progress(min(frac, 1.0), text=mensaje or t("mapa.simulando_pct", pct=format(frac*100, ".0f")))

        with st.spinner(t("mapa.generando")):
            df_mapa = generar_mapa_mhi(
                planeta_base, (a_min, a_max), (B_min, B_max),
                n_pasos_a=resolucion, n_pasos_B=resolucion,
                t_max_gyr=t_max_mapa, progress_callback=_actualizar,
            )
        barra.empty()

        fallidas = df_mapa["MHI_total"].isna().sum()
        if fallidas > 0:
            st.warning(t("libre.mapa.fallidas", f=fallidas, n=len(df_mapa)))

        pivot = df_mapa.pivot(index="B_G", columns="a_ua", values="MHI_total")
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values, x=pivot.columns, y=pivot.index,
            colorscale="Viridis", zmin=0, zmax=100,
            colorbar=dict(title="MHI"),
        ))
        fig.update_layout(
            title=t("mapa.fig.titulo", planeta=nombre_cuerpo(planeta_base)),
            xaxis_title=t("col.mapa.a_ua"),
            yaxis_title=t("mapa.fig.y"),
            width=800, height=550,
        )
        st.plotly_chart(fig, use_container_width=True)

        validos = df_mapa["MHI_total"].dropna()
        if not validos.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric(t("mapa.min"), f"{validos.min():.1f}")
            c2.metric(t("mapa.max"), f"{validos.max():.1f}")
            c3.metric(t("mapa.prom"), f"{validos.mean():.1f}")
            estrellados = df_mapa["se_estrello"].sum() if df_mapa["se_estrello"].notna().any() else 0
            st.caption(t("libre.mapa.estrellados", e=estrellados, n=len(df_mapa), pct=format(estrellados/len(df_mapa)*100, ".1f")))

        with st.expander(t("mapa.crudos")):
            st.dataframe(con_nombres_legibles(df_mapa, ETIQUETAS_MAPA_MHI))
        st.download_button(t("mapa.csv"), con_nombres_legibles(df_mapa, ETIQUETAS_MAPA_MHI).to_csv(index=False),
                           file_name=f"mapa_mhi_{planeta_base}.csv")
    # ================================================================================

elif modo == "sensibilidad":
    planeta = st.sidebar.selectbox(t("sim.planeta"), list(PLANETAS.keys()), format_func=nombre_cuerpo)
    tipo_sens = st.sidebar.radio(t("sens.tipo"), ["basica", "extendida"],
                                    format_func=lambda x: t(f"sens.tipo.{x}"))

    if tipo_sens == "basica":
        n_runs = st.sidebar.slider(t("sens.n_corridas"), 10, 500, 100, 10)
        if st.sidebar.button(t("sens.boton")):
            df = analisis_sensibilidad(planeta, n_runs=n_runs)
            st.dataframe(df)
            if not df.empty:
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=df["B_final_gauss"], nbinsx=30, name=t("comp.m.b")))
                st.plotly_chart(fig, use_container_width=True)

    else:
        # ==================== MEJORA v4.1 (Mejora 3) ====================
        param = st.sidebar.selectbox(t("sens.param"), [
            "a_inicial", "B_p_inicial", "M", "R_p", "w_p_inicial",
            "densidad_nucleo", "difusividad", "k2_sobre_q",
        ])
        unidad = {"a_inicial": t("libre.u.ua"), "B_p_inicial": t("sens.u.gauss")}.get(param, t("sens.u.si"))
        st.sidebar.caption(t("sens.unidad", unidad=unidad))
        val_min = st.sidebar.number_input(t("sens.vmin"), value=0.1)
        val_max = st.sidebar.number_input(t("sens.vmax"), value=2.0)
        n_runs = st.sidebar.slider(t("sens.n_puntos"), 5, 200, 30, 5)
        if st.sidebar.button(t("sens.boton_ext")):
            with st.spinner(t("lab.sim.simulando")):
                df = analisis_sensibilidad_extendido(planeta, param, (val_min, val_max), n_runs=n_runs)
            st.dataframe(df)
            df_ok = df[df["error"].isna()] if "error" in df.columns else df
            if not df_ok.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_ok[param], y=df_ok["B_final_gauss"],
                                          mode="lines+markers", name=t("lab.cmp.b_final")))
                fig.update_layout(
                    title=t("sens.fig.titulo", param=param),
                    xaxis_title=f"{param} ({unidad})",
                    yaxis_title=t("lab.bar.eje_y"),
                )
                st.plotly_chart(fig, use_container_width=True)
            errores = df[df["error"].notna()] if "error" in df.columns else pd.DataFrame()
            if not errores.empty:
                st.warning(t("libre.sens.fallidas", n=len(errores), m=len(df)))
        # ==================================================================

elif modo == "validacion":
    if st.sidebar.button(t("val.boton")):
        resultados = validar_todos()
        st.json(resultados)

elif modo == "biblioteca_fotos":
    render_biblioteca_fotos()

elif modo == "glosario":
    st.subheader(t("glosario.titulo"))
    st.caption(
        t("glosario.caption")
    )
    for seccion, terminos in obtener_glosario().items():
        with st.expander(seccion, expanded=True):
            for _clave, (titulo, definicion) in terminos.items():
                st.markdown(f"**{titulo}**  \n{definicion}")
                st.markdown("---")
