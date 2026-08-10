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
from mapa_mhi import generar_mapa_mhi
from historial import guardar_simulacion, cargar_historial, borrar_historial
from exportar_video import construir_json_video  # exportacion JSON para IAs de video
from glosario_terminos import GLOSARIO_TERMINOS  # diccionario de terminos, compartido con Standard/Pro
from etiquetas_columnas import ETIQUETAS_HISTORIAL, ETIQUETAS_MAPA_MHI, con_nombres_legibles
from educacion_ui import render_educacion  # sección educativa
from sesion import obtener_sesion_id

st.set_page_config(page_title="MHD-INT v5.0", layout="wide", page_icon="assets/logo_mhd_int.png")

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
# ===================================================================
VERSION_PUBLICA = "5.0"

col_logo, col_titulo = st.columns([1, 3])
with col_logo:
    st.image("assets/logo_mhd_int.png", width=90)
with col_titulo:
    st.caption(f"by Solaris Core · versión {VERSION_PUBLICA}")
# ===================================================================

# ===================================================================
# NUEVO: banner de "version de prueba" (sin bloqueo real -- decision
# explicita de Roney en vez del mecanismo de 30 dias). Solo informativo,
# para entregar a Kike/Gisela/Giancarlo. No limita ninguna funcionalidad
# ni cuenta tiempo ni usos. Para pasar a version completa, alcanza con
# poner EDICION = "COMPLETA" (o borrar el bloque).
# ===================================================================
EDICION = "PRUEBA"  # cambiar a "COMPLETA" para quitar el banner

if EDICION == "PRUEBA":
    st.info(
        "🧪 **Versión de prueba de MHD-INT.** Simulación científica sin límite de "
        "tiempo ni de usos en esta edición. Para la versión completa, contactá a Roney.",
        icon="🧪",
    )
# ===================================================================

st.sidebar.image("assets/logo_mhd_int.png", width=70)
modo = st.sidebar.radio("Modo", ["📚 Educación", "Simulación", "Sintético", "Mapa MHI", "Sensibilidad", "Validación", "📖 Glosario"])

st.sidebar.markdown("---")
st.sidebar.caption(f"MHD-INT v{VERSION_PUBLICA} · by Solaris Core")

# ==================== Historial de simulaciones ====================
# La confirmacion de borrado usa st.session_state en dos pasos
# independientes, que sobreviven entre reruns de Streamlit.
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
# ==================================================================================================

if modo == "📚 Educación":
    render_educacion()

elif modo == "Simulación":
    planeta = st.sidebar.selectbox("Planeta", list(PLANETAS.keys()))
    t_max = st.sidebar.slider("Tiempo máximo (Gyr)", 0.1, 10.0, 5.0, 0.1)
    dt = st.sidebar.select_slider("Paso (años)", options=[1000, 5000, 10000, 50000, 100000], value=10000)

    # ==================== MEJORA v4.1: experimentos controlados ====================
    # Permite aislar el efecto de cada torque sobre la rotación (depuración /
    # fines didácticos). Los 3 activos por defecto = comportamiento normal.
    st.sidebar.subheader("⚙️ Control de torques (experimentos)")
    torque_mag = st.sidebar.checkbox("Torque magnético", True)
    torque_tide = st.sidebar.checkbox("Marea estelar", True)
    torque_lunar = st.sidebar.checkbox("Marea lunar", True)
    # ================================================================================

    # ==================== NUEVO v4.2 + v5.0: modelo termico + atmosfera ====================
    st.sidebar.subheader("🧠 Modelo de dínamo y atmósfera")
    usar_termico = st.sidebar.checkbox(
        "Activar modelo térmico (Christensen 2009)",
        value=False,
        help="Balance energético real del núcleo (Q_CMB, manto). Desactivado = interruptor empírico (v4.1)."
    )
    usar_atmosfera = st.sidebar.checkbox(
        "Activar pérdida atmosférica (escape XUV)",
        value=False,
        help="Simula la foto-evaporación de la atmósfera (Owen & Jackson 2012). Si se pierde, el MHI será 0."
    )
    if usar_atmosfera and dt > 1000:
        st.sidebar.warning("⚠️ Con atmósfera activa se recomienda dt ≤ 1000 años para evitar inestabilidad numérica.")
    # ========================================================================================

    if st.sidebar.button("Simular"):
        with st.spinner("Simulando..."):
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

        st.subheader("Resultado")
        st.json(resultado.resumen_dict())

        mhi = None
        # ==================== BLOQUE MHI (reconectado) ====================
        if resultado.es_valido() and resultado.tiene_serie():
            st.markdown("### 🛡️ Índice de Habitabilidad Magnética y Planetaria (MHI)")
            mhi = calcular_mhi(resultado)
            m1, m2, m3 = st.columns([1.5, 1, 1])
            m1.metric("MHI", f"{mhi['mhi_total']:.1f} / 100", categoria_mhi(mhi['mhi_total']))
            m1.progress(int(mhi["mhi_total"]) / 100)
            m2.metric("Escudo activo", f"{mhi['escudo_mag_pct']:.1f}% del tiempo")
            m2.metric("Dínamo activo", f"{mhi['campo_activo_pct']:.1f}% del tiempo")
            m3.metric("Excentricidad promedio", f"{mhi['e_promedio']:.4f}")
            m3.metric("Calor de marea medio", f"{mhi['q_promedio_w']:.2e} W")
        # ====================================================================

        # ==================== NUEVO v4.2: estado térmico del núcleo ====================
        if usar_termico_res and resultado.tiene_serie():
            st.markdown("### 🔥 Estado térmico del núcleo")
            c1, c2, c3 = st.columns(3)
            c1.metric("T CMB (K)", f"{resultado.T_cmb_final_K:.0f}")
            c2.metric("B generado (G)", f"{resultado.B_gen_final_gauss:.3f}")
            c3.metric("Rm (dínamo activo si > 40)", f"{resultado.Rm_final:.1f}")
            if resultado.Rm_final > 40:
                st.success("✅ Dínamo activo (Rm > 40)")
            else:
                st.warning("⚠️ Dínamo inactivo (Rm ≤ 40)")
        # ==================================================================================

        # ==================== NUEVO v5.0: estado de la atmósfera ====================
        if usar_atmosfera_res and resultado.tiene_serie():
            st.markdown("### 🌍 Estado de la Atmósfera")
            c1, c2 = st.columns(2)
            M_atm_tierras = resultado.M_atm_final_kg / 5.15e18
            c1.metric("Masa atmosférica (Tierras)", f"{M_atm_tierras:.4f}")
            if resultado.atm_perdida:
                c2.metric("Atmósfera", "❌ PERDIDA", delta="Estéril")
                st.error("⚠️ El planeta ha perdido su atmósfera por foto-evaporación. MHI = 0.")
            else:
                c2.metric("Atmósfera", "✅ Retenida", delta="Protegida")
        # ================================================================================

        # ==================== NUEVO v5.1: evolución de la oblicuidad ====================
        # Solo se muestra si el planeta tiene dato real de oblicuidad
        # (eps_conocido=True) -- ver fix A.5 del informe de revision. Para
        # exoplanetas sin dato, no tiene sentido mostrar un grafico de algo
        # que arranca en 0 grados por falta de informacion, no por fisica.
        eps_conocido_res = getattr(resultado, "eps_conocido", False)
        if eps_conocido_res and resultado.tiene_serie() and len(resultado.serie.eps_deg) > 0:
            st.markdown("### 🌍 Evolución de la Oblicuidad")
            df_eps = pd.DataFrame({
                "t_Gyr": resultado.serie.tiempos,
                "eps_deg": resultado.serie.eps_deg,
            })
            fig_eps = go.Figure()
            fig_eps.add_trace(go.Scatter(
                x=df_eps["t_Gyr"], y=df_eps["eps_deg"], mode="lines",
                name="Oblicuidad (°)", line=dict(color="orange", width=3),
            ))
            fig_eps.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="Límite caótico (60°)")
            fig_eps.add_hline(y=5, line_dash="dash", line_color="blue", annotation_text="Límite estéril (5°)")
            fig_eps.update_layout(
                xaxis_title="Tiempo (Gyr)", yaxis_title="Oblicuidad (grados)",
                legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
            )
            st.plotly_chart(fig_eps, use_container_width=True)

            eps_final_res = resultado.eps_final_deg
            if eps_final_res > 60:
                st.warning(f"⚠️ Oblicuidad extrema ({eps_final_res:.1f}°). Clima caótico. Penalización de -20 en el MHI.")
            elif eps_final_res < 5:
                st.warning(f"⚠️ Oblicuidad muy baja ({eps_final_res:.1f}°). Riesgo de invernadero descontrolado. Penalización de -20 en el MHI.")
            else:
                st.success(f"✅ Oblicuidad estable ({eps_final_res:.1f}°). Clima habitable.")
        # ==================================================================================

        # ==================== Guardar en Historial ====================
        st.markdown("---")
        col_hist1, col_hist2 = st.columns([1, 3])
        with col_hist1:
            if st.button("📜 Guardar en Historial", type="primary"):
                try:
                    fila = guardar_simulacion(resultado, st.session_state["ultimos_params"], mhi=mhi, sesion_id=obtener_sesion_id())
                    st.success(f"✅ Simulación guardada en historial ({fila['timestamp']})")
                except Exception as exc:
                    st.error(f"Error al guardar: {exc}")
        with col_hist2:
            st.caption("Guarda esta simulación en tu historial personal. Útil para comparar configuraciones y llevar trazabilidad.")
        # ===========================================================================================

        # ==================== NUEVO: Exportar para IA de Video ====================
        # FIX: usa st.session_state (mismo patrón que "Guardar en Historial") para
        # no depender del estado momentáneo del botón "Simular".
        st.markdown("### 📹 Exportar para IA de Video")
        st.caption("JSON con la serie temporal completa, pensado para consumirse desde Manim, "
                   "Blender, Sora u otras herramientas de generación de video.")
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
                    label="📊 Descargar JSON (Datos)",
                    data=json_str,
                    file_name=f"{params_json['planeta']}_data.json",
                    mime="application/json",
                )
                st.caption(
                    f"{datos_json['meta']['puntos_exportados']} de "
                    f"{datos_json['meta']['puntos_originales']} puntos "
                    f"(submuestreado a un máximo de {2000})."
                )
            except Exception as exc:
                st.error(f"No se pudo generar el JSON: {exc}")
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
                "a_ua": "Distancia orbital a (UA)",
                "B_gauss": "Campo magnético B (G)",
                "w_p": "Velocidad de rotación ω (rad/s)",
                "e": "Excentricidad e",
                "T_cmb_K": "Temp. núcleo-manto T_cmb (K)",
                "B_gen_gauss": "Campo generado por dínamo (G)",
                "Rm": "Número de Reynolds magnético Rm",
                "M_atm_kg": "Masa atmosférica (kg)",
                "eps_deg": "Oblicuidad ε (°)",
            }

            vars_disponibles = list(ETIQUETAS_VARIABLES.keys())
            vars_seleccionadas = st.multiselect(
                "Variables a graficar",
                vars_disponibles,
                default=["a_ua", "B_gauss"],
                format_func=lambda v: ETIQUETAS_VARIABLES[v],
            )

            with st.expander("➕ Línea de umbral (opcional)"):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    var_umbral = st.selectbox(
                        "Variable", ["(ninguna)"] + vars_disponibles,
                        format_func=lambda v: v if v == "(ninguna)" else ETIQUETAS_VARIABLES[v],
                    )
                with col_u2:
                    valor_umbral = st.number_input("Valor del umbral", value=0.0, format="%.6g")

            vista_panel = st.checkbox("Vista de panel (un gráfico por variable)", value=False)

            if not vars_seleccionadas:
                st.info("Elegí al menos una variable para graficar.")
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
                fig_panel.update_xaxes(title_text="Tiempo (Gyr)")
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
                if var_umbral != "(ninguna)" and var_umbral in vars_seleccionadas:
                    fig.add_hline(y=valor_umbral, line_dash="dash", line_color="red",
                                  annotation_text=f"Umbral {ETIQUETAS_VARIABLES[var_umbral]}")
                fig.update_layout(
                    xaxis_title="Tiempo (Gyr)",
                    yaxis=dict(title=ETIQUETAS_VARIABLES[escala_principal]),
                    yaxis2=dict(title="(otra escala)", overlaying="y", side="right"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
                )
                st.plotly_chart(fig, use_container_width=True)

elif modo == "Sintético":
    # ==================== MEJORA v4.1 (Mejora 2) ====================
    # Parte del planeta "Tierra" en database.py como base y sobrescribe
    # solo los campos que el usuario cambia; lo que no se toca (perfil de
    # viento estelar rho_sw/v_sw, difusividad del núcleo, inercia) queda
    # con el valor terrestre. Es una simplificación deliberada: no hay
    # forma físicamente derivada de "inventar" esos valores para un
    # planeta que no existe, así que se documenta el supuesto en vez de
    # ocultarlo.
    st.subheader("🧬 Diseña tu propio planeta")
    st.caption("Parte de la Tierra como base; los parámetros no listados abajo "
               "(difusividad del núcleo, perfil de viento estelar) quedan con el valor terrestre.")

    col1, col2 = st.columns(2)
    with col1:
        masa = st.slider("Masa (masas terrestres)", 0.1, 10.0, 1.0, 0.1)
        radio = st.slider("Radio (radios terrestres)", 0.5, 3.0, 1.0, 0.05)
        a_ua = st.slider("Distancia orbital (UA)", 0.02, 2.5, 1.0, 0.01)
        B_inicial_G = st.slider("Campo magnético inicial (Gauss)", 0.0, 5.0, 0.3, 0.01)
        tipo_planeta = st.selectbox("Tipo de planeta",
                                     ["Terrestre", "SuperTierra", "Gigante gaseoso", "Hot Jupiter", "SubNeptuno"])
    with col2:
        P_rot_dias = st.slider("Período de rotación inicial (días)", 0.1, 365.0, 1.0, 0.1)
        e_inicial = st.slider("Excentricidad inicial", 0.0, 0.8, 0.0167, 0.01)
        tipo_estrella = st.selectbox("Tipo espectral de la estrella", ["G2V", "G5V", "K5V", "F8V", "M5V"])
        edad_estrella = st.slider("Edad de la estrella (Gyr)", 0.5, 10.0, 4.6, 0.1)
        t_max = st.slider("Tiempo de simulación (Gyr)", 0.5, 10.0, 5.0, 0.5)
        eps_inicial_deg = st.slider(
            "Oblicuidad inicial (grados)", 0.0, 180.0, 23.44, 0.1,
            help="Inclinación del eje de rotación. 23.44° para la Tierra, 98° para Urano. "
                 "Como lo elegís vos mismo, cuenta como dato 'conocido' para la penalización del MHI."
        )

    st.subheader("⚙️ Control de torques (opcional)")
    ct1, ct2, ct3 = st.columns(3)
    tm_on = ct1.checkbox("Torque magnético", True, key="sint_tmag")
    tt_on = ct2.checkbox("Marea estelar", True, key="sint_ttide")
    tl_on = ct3.checkbox("Marea lunar", True, key="sint_tluna")
    st.caption("La Tierra sintética no trae Luna propia (LUNAS solo tiene la Tierra real); "
               "este toggle queda sin efecto salvo que agregues una luna en database.py.")

    if st.button("🚀 Simular planeta sintético", type="primary"):
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

        with st.spinner("Simulando..."):
            resultado = simular_planeta(
                "Tierra",
                t_max_gyr=t_max,
                dt_yr=10000.0,
                incluir_serie=True,
                parametros_extra=params_extra,
                estrella_personalizada=estrella_personalizada,
            )

        if not resultado.es_valido():
            st.error(f"Simulación inválida: {resultado.error}")
        else:
            st.subheader("📊 Resultados")
            st.json(resultado.resumen_dict())

            if resultado.tiene_serie():
                mhi = calcular_mhi(resultado)
                st.markdown("### 🛡️ Índice de Habitabilidad (MHI)")
                cm1, cm2, cm3 = st.columns(3)
                cm1.metric("MHI Total", f"{mhi['mhi_total']:.1f} / 100", categoria_mhi(mhi['mhi_total']))
                cm2.metric("Escudo activo", f"{mhi['escudo_mag_pct']:.1f}%")
                cm3.metric("Campo activo", f"{mhi['campo_activo_pct']:.1f}%")

                serie = resultado.serie
                df_s = pd.DataFrame({"t_Gyr": serie.tiempos, "a_ua": serie.a_ua, "B_gauss": serie.B_p_gauss})
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_s["t_Gyr"], y=df_s["a_ua"], mode="lines", name="a (UA)"))
                fig.add_trace(go.Scatter(x=df_s["t_Gyr"], y=df_s["B_gauss"], mode="lines", name="B (G)", yaxis="y2"))
                fig.update_layout(
                    xaxis_title="Tiempo (Gyr)",
                    yaxis=dict(title="a (UA)"),
                    yaxis2=dict(title="B (G)", overlaying="y", side="right"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
                )
                st.plotly_chart(fig, use_container_width=True)
    # ================================================================================

elif modo == "Mapa MHI":
    # ==================== MEJORA v4.1 (Mejora 1) ====================
    st.subheader("🗺️ Mapa de calor MHI: distancia orbital × campo inicial")
    st.caption("El resto de los parámetros del planeta base (masa, radio, estrella) "
               "queda fijo tal como está en la base de datos.")

    planeta_base = st.sidebar.selectbox("Planeta base", list(PLANETAS.keys()))
    a_min, a_max = st.sidebar.slider("Rango de distancia orbital (UA)", 0.01, 5.0, (0.5, 2.0), 0.01)
    B_min, B_max = st.sidebar.slider("Rango de campo inicial (Gauss)", 0.0, 5.0, (0.0, 2.0), 0.1)
    resolucion = st.sidebar.slider("Resolución de la malla (N×N)", 3, 25, 10, 1)
    t_max_mapa = st.sidebar.slider("Tiempo de simulación (Gyr)", 0.5, 10.0, 5.0, 0.5, key="t_max_mapa")

    total_sims = resolucion * resolucion
    st.sidebar.caption(f"⚠️ Esto va a correr {total_sims} simulaciones. "
                        f"Con resoluciones altas puede tardar varios minutos.")

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
            st.warning(f"{fallidas} de {len(df_mapa)} combinaciones no se pudieron simular "
                       f"(quedaron como NaN en el mapa, no se ocultaron).")

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
            estrellados = df_mapa["se_estrello"].sum() if df_mapa["se_estrello"].notna().any() else 0
            st.caption(f"💥 Se estrellaron: {estrellados} / {len(df_mapa)} combinaciones "
                       f"({estrellados/len(df_mapa)*100:.1f}%)")

        with st.expander("Ver datos crudos"):
            st.dataframe(con_nombres_legibles(df_mapa, ETIQUETAS_MAPA_MHI))
        st.download_button("Descargar CSV", con_nombres_legibles(df_mapa, ETIQUETAS_MAPA_MHI).to_csv(index=False),
                           file_name=f"mapa_mhi_{planeta_base}.csv")
    # ================================================================================

elif modo == "Sensibilidad":
    planeta = st.sidebar.selectbox("Planeta", list(PLANETAS.keys()))
    tipo_sens = st.sidebar.radio("Tipo de análisis", ["Básica (k2_sobre_q + densidad_nucleo)", "Extendida (1 parámetro a elección)"])

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
        # ==================== MEJORA v4.1 (Mejora 3) ====================
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
            errores = df[df["error"].notna()] if "error" in df.columns else pd.DataFrame()
            if not errores.empty:
                st.warning(f"{len(errores)} de {len(df)} corridas no dieron resultado válido (ver columna 'error').")
        # ==================================================================

elif modo == "Validación":
    if st.sidebar.button("Validar todo"):
        resultados = validar_todos()
        st.json(resultados)

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
