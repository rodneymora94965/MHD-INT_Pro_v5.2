# comparador.py
# MHD-INT PRO v5.2 — Capa 3: Comparador de planetas lado a lado
# Licencia: Comercial propietaria (dual con AGPL-3.0)
#
# ⚠️ ESTE MÓDULO NO PERTENECE AL REPOSITORIO PÚBLICO AGPL.
# Simula dos planetas y los compara: ΔB, ΔMHI, Δa, Δe, veredicto de
# habitabilidad y videos lado a lado.
#
# DECISIÓN: las dos simulaciones corren EN SECUENCIA (Streamlit no es
# multi-hilo por sesión); barra de progreso combinada.

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from engine import simular_planeta
from database import PLANETAS
from habitabilidad import calcular_mhi, categoria_mhi
from exportar_video import construir_json_video
from video_mpl import generar_video_desde_dict

COLOR_B   = '#E50914'
COLOR_A   = '#00C9FF'
COLOR_E   = '#92FE9D'
COLOR_ATM = '#FFA500'
COLOR_BG  = '#FFFFFF'  # CAMBIO (ago-2026): tema claro -- antes '#0A0A0F'

DT_COMPARADOR = 10000.0


def calcular_deltas(rA, rB, mhiA=None, mhiB=None) -> dict:
    """Diferencias (A − B). delta_MHI positivo => A más habitable."""
    deltas = {}
    if rA.es_valido() and rB.es_valido():
        deltas["delta_B_gauss"]    = rA.B_final_gauss - rB.B_final_gauss
        deltas["delta_a_ua"]       = rA.a_final_ua - rB.a_final_ua
        deltas["delta_e"]          = rA.e_final - rB.e_final
        deltas["delta_P_rot_dias"] = rA.P_rot_final_dias - rB.P_rot_final_dias
    if mhiA is not None and mhiB is not None:
        deltas["delta_MHI"] = mhiA["mhi_total"] - mhiB["mhi_total"]
    return deltas


def _render_video(resultado, params, cache_key):
    """Genera (una sola vez, cacheado) y muestra el video de un planeta."""
    if resultado is None or not resultado.tiene_serie():
        return
    if cache_key not in st.session_state:
        try:
            datos_json = construir_json_video(
                resultado,
                planeta=params["planeta"],
                t_max_gyr=params["t_max_gyr"],
                dt_yr=params["dt_yr"],
            )
            with st.spinner("🎨 Renderizando video..."):
                buffer = generar_video_desde_dict(datos_json, fps=20)
            st.session_state[cache_key] = {
                "bytes": buffer.getvalue(),
                "formato": getattr(buffer, "formato_real", "mp4"),
            }
        except Exception as exc:
            st.warning(f"No se pudo generar el video: {exc}")
            return
    vid = st.session_state[cache_key]
    fmt = vid["formato"]
    if fmt == "gif":
        # FIX: st.video() no soporta GIF (solo mp4/ogv/m4v/webm) -- un GIF
        # es una imagen animada, se muestra con st.image(), no st.video().
        # Este es justamente el camino que se activa cuando ffmpeg no está
        # disponible (típico en Streamlit Cloud sin packages.txt) -- era
        # el que estaba fallando.
        st.caption("ℹ️ ffmpeg no disponible — GIF en vez de MP4.")
        st.image(vid["bytes"])
    else:
        # FIX: el parámetro de st.video() se llama "format", no "mime_type"
        # (ese nombre nunca existió en la API de Streamlit).
        st.video(vid["bytes"], format="video/mp4")


def _tarjeta_planeta(resultado, mhi, params, etiqueta):
    """Tarjeta compacta de un planeta para la vista de comparación."""
    if resultado is None:
        st.info("Sin simular.")
        return
    st.markdown(f"#### {etiqueta} · {resultado.nombre_planeta}")
    if not resultado.es_valido():
        st.error(f"Simulación inválida: {resultado.error}")
        return

    estado_txt = "💥 Estrellado" if resultado.se_estrello else \
                 "❌ Sin atmósfera" if resultado.atm_perdida else \
                 "✅ Estable"
    st.caption(f"Estado: **{estado_txt}**")

    c1, c2 = st.columns(2)
    c1.metric("B final", f"{resultado.B_final_gauss:.3f} G")
    c2.metric("a final", f"{resultado.a_final_ua:.4f} UA")
    c1.metric("e final", f"{resultado.e_final:.4f}")
    c2.metric("P_rot final", f"{resultado.P_rot_final_dias:.2f} d")

    if mhi is not None:
        st.metric("MHI", f"{mhi['mhi_total']:.0f} / 100", categoria_mhi(mhi['mhi_total']))
        if mhi.get("penalizacion_obl_pts", 0.0) != 0.0:
            st.caption(f"↳ incluye penalización por oblicuidad: {mhi['penalizacion_obl_pts']:+.0f} pts")

    _render_video(resultado, params, cache_key=f"comp_video_{etiqueta}")


def render_comparador():
    """UI completa del modo Comparador (Capa 3)."""
    st.subheader("⚡ Comparador lado a lado")
    st.caption(
        "Simulá dos planetas y compará su evolución, MHI y video en la misma "
        "pantalla. Para una comparación justa, usá el mismo tiempo en ambos."
    )

    col_cfg_A, col_cfg_B = st.columns(2)
    config = {}
    for etiqueta, col in zip(["A", "B"], [col_cfg_A, col_cfg_B]):
        with col:
            icono = "🅰️" if etiqueta == "A" else "🅱️"
            st.markdown(f"### {icono} Planeta {etiqueta}")
            planeta = st.selectbox("Planeta", list(PLANETAS.keys()), key=f"comp_planeta_{etiqueta}")
            t_max = st.slider("Tiempo (Gyr)", 0.1, 10.0, 5.0, 0.1, key=f"comp_tmax_{etiqueta}")
            usar_termico = st.checkbox("Modelo térmico", False, key=f"comp_termico_{etiqueta}")
            usar_atmosfera = st.checkbox("Atmósfera (escape XUV)", False, key=f"comp_atm_{etiqueta}")
            config[etiqueta] = {
                "planeta": planeta,
                "t_max_gyr": t_max,
                "usar_termico": usar_termico,
                "usar_atmosfera": usar_atmosfera,
            }

    st.caption("Los cambios de configuración se aplican al hacer click en **Comparar**.")

    if st.button("⚡ Comparar", type="primary"):
        barra = st.progress(0.0, text="Simulando planeta A...")
        resultados = {}

        params_extra_A = {
            "modelo_termico": config["A"]["usar_termico"],
            "modelo_atmosfera": config["A"]["usar_atmosfera"],
        }
        resultados["A"] = simular_planeta(
            config["A"]["planeta"], t_max_gyr=config["A"]["t_max_gyr"],
            dt_yr=DT_COMPARADOR, incluir_serie=True, parametros_extra=params_extra_A,
        )
        barra.progress(0.5, text="Simulando planeta B...")

        params_extra_B = {
            "modelo_termico": config["B"]["usar_termico"],
            "modelo_atmosfera": config["B"]["usar_atmosfera"],
        }
        resultados["B"] = simular_planeta(
            config["B"]["planeta"], t_max_gyr=config["B"]["t_max_gyr"],
            dt_yr=DT_COMPARADOR, incluir_serie=True, parametros_extra=params_extra_B,
        )
        barra.progress(1.0, text="Comparación lista.")
        barra.empty()

        st.session_state["comp_resultado_A"] = resultados["A"]
        st.session_state["comp_resultado_B"] = resultados["B"]
        st.session_state["comp_params_A"] = {
            "planeta": config["A"]["planeta"], "t_max_gyr": config["A"]["t_max_gyr"], "dt_yr": DT_COMPARADOR,
        }
        st.session_state["comp_params_B"] = {
            "planeta": config["B"]["planeta"], "t_max_gyr": config["B"]["t_max_gyr"], "dt_yr": DT_COMPARADOR,
        }
        st.session_state.pop("comp_video_A", None)
        st.session_state.pop("comp_video_B", None)

    if "comp_resultado_A" in st.session_state and "comp_resultado_B" in st.session_state:
        rA = st.session_state["comp_resultado_A"]
        rB = st.session_state["comp_resultado_B"]

        mhiA = calcular_mhi(rA) if rA.es_valido() and rA.tiene_serie() else None
        mhiB = calcular_mhi(rB) if rB.es_valido() and rB.tiene_serie() else None
        deltas = calcular_deltas(rA, rB, mhiA, mhiB)

        st.markdown("---")
        st.markdown("### 📊 Diferencias (A − B)")

        d1, d2, d3, d4 = st.columns(4)
        if "delta_B_gauss" in deltas:
            d1.metric("Δ B final", f"{deltas['delta_B_gauss']:+.3f} G")
            d3.metric("Δ a final", f"{deltas['delta_a_ua']:+.4f} UA")
            d4.metric("Δ e final", f"{deltas['delta_e']:+.4f}")
        if "delta_MHI" in deltas:
            d2.metric("Δ MHI", f"{deltas['delta_MHI']:+.1f}",
                      "A más habitable" if deltas['delta_MHI'] > 0 else
                      "B más habitable" if deltas['delta_MHI'] < 0 else "Empate")

        if mhiA is not None and mhiB is not None:
            if mhiA["mhi_total"] > mhiB["mhi_total"]:
                st.success(f"🏆 **{rA.nombre_planeta} (A)** es más habitable: "
                           f"MHI {mhiA['mhi_total']:.0f} vs {mhiB['mhi_total']:.0f} de {rB.nombre_planeta} (B).")
            elif mhiB["mhi_total"] > mhiA["mhi_total"]:
                st.success(f"🏆 **{rB.nombre_planeta} (B)** es más habitable: "
                           f"MHI {mhiB['mhi_total']:.0f} vs {mhiA['mhi_total']:.0f} de {rA.nombre_planeta} (A).")
            else:
                st.info("⚖️ Empate en MHI.")

        st.markdown("---")
        vA, vB = st.columns(2)
        with vA:
            _tarjeta_planeta(rA, mhiA, st.session_state["comp_params_A"], "A")
        with vB:
            _tarjeta_planeta(rB, mhiB, st.session_state["comp_params_B"], "B")

        with st.expander("🔬 Ver comparación detallada"):
            filas = []
            for r, et, mhi in [(rA, "A", mhiA), (rB, "B", mhiB)]:
                if r.es_valido():
                    filas.append({
                        "Lado": et,
                        "Planeta": r.nombre_planeta,
                        "B_final_G": round(r.B_final_gauss, 4),
                        "a_final_UA": round(r.a_final_ua, 4),
                        "e_final": round(r.e_final, 5),
                        "P_rot_final_d": round(r.P_rot_final_dias, 3),
                        "MHI": round(mhi["mhi_total"], 1) if mhi else None,
                        "Penalización oblicuidad": round(mhi["penalizacion_obl_pts"], 1) if mhi else None,
                        "atm_perdida": r.atm_perdida,
                        "se_estrello": r.se_estrello,
                    })
            st.dataframe(pd.DataFrame(filas))
