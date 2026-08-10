# disco_ui.py
# MHD-INT PRO v5.9 — Capa 3: pantalla del Disco Protoplanetario
# Licencia: Comercial propietaria (dual con AGPL-3.0)
#
# ⚠️ ESTE MÓDULO NO PERTENECE AL REPOSITORIO PÚBLICO AGPL.
#
# Separado de disco_protoplanetario.py a propósito: ese archivo es
# física pura (sin streamlit), este es solo la pantalla que lo llama.
# Así el módulo de física se puede seguir auditando/testeando sin
# arrastrar la UI.

import streamlit as st
import plotly.graph_objects as go

from disco_protoplanetario import (
    DiscoProtoplanetario,
    LAMBDA_RANGO_SUGERIDO,
    ZETA_TILDE_RANGO_SUGERIDO,
)
from database_estrellas import ESTRELLAS_T_TAURI, listar_estrellas, obtener_estrella

COLOR_BETA = "#2E5C8A"
COLOR_MDOT = "#4F9C6D"


def render_disco_protoplanetario():
    st.markdown("### 🌌 Disco Protoplanetario — desalineación spin-disco")
    st.caption(
        "Evolución del ángulo β entre el eje de rotación de una estrella joven "
        "y el eje de su disco protoplanetario, por acoplamiento magnético + "
        "de acreción (Lai, Foucart & Lin 2011, Ec. 23)."
    )

    # ---- Advertencia SIEMPRE visible, no condicional (ver docstring de
    # advertencia_parametros_asumidos() en disco_protoplanetario.py) ----
    st.warning(
        "⚠️ **λ y ζ̃ son valores elegidos dentro de un rango plausible, no "
        "medidos ni derivados.** El propio paper (Lai, Foucart & Lin 2011) "
        "los describe como \"en gran medida sin restringir\". Este módulo "
        "explora un escenario plausible, no predice el β real de una "
        "estrella concreta."
    )

    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.markdown("#### Estrella")
        opciones = ["— Personalizada —"] + [
            ESTRELLAS_T_TAURI[k]["nombre_display"] for k in listar_estrellas()
        ]
        eleccion = st.selectbox("Catálogo de estrellas T Tauri", opciones)

        if eleccion == "— Personalizada —":
            preset = {
                "M_estrella_msol": 0.8, "R_estrella_rsol": 2.0,
                "B_estrella_gauss": 500, "P_rot_dias": 5.0,
                "Mdot0_msol_yr": 2e-8, "tau_disco_myr_ref": 5.0,
                "fuente": None,
            }
        else:
            clave = next(k for k in listar_estrellas()
                         if ESTRELLAS_T_TAURI[k]["nombre_display"] == eleccion)
            preset = obtener_estrella(clave)
            if preset.get("fuente"):
                st.caption(f"📖 Fuente: {preset['fuente']}")

        M_estrella = st.number_input("Masa estelar (M☉)", 0.1, 3.0,
                                      float(preset["M_estrella_msol"]), 0.05)
        R_estrella = st.number_input("Radio estelar (R☉)", 0.3, 5.0,
                                      float(preset["R_estrella_rsol"]), 0.1)
        B_estrella = st.number_input("Campo magnético superficial (G)", 10, 5000,
                                      int(preset["B_estrella_gauss"]), 50)
        P_rot = st.number_input("Período de rotación (días)", 0.5, 30.0,
                                 float(preset["P_rot_dias"]), 0.5)
        Mdot0 = st.number_input("Tasa de acreción inicial (M☉/año)",
                                 1e-10, 1e-6, float(preset["Mdot0_msol_yr"]),
                                 format="%.2e")
        tau_disco = st.number_input("Tiempo de disipación del disco (Myr)",
                                     0.5, 15.0, float(preset["tau_disco_myr_ref"]), 0.5)

    with col_der:
        st.markdown("#### Parámetros del acoplamiento (λ, ζ̃)")
        st.caption(
            f"Rangos sugeridos por el paper: λ ~ {LAMBDA_RANGO_SUGERIDO[0]}–"
            f"{LAMBDA_RANGO_SUGERIDO[1]} (alinea) · ζ̃ ~ "
            f"{ZETA_TILDE_RANGO_SUGERIDO[0]}–{ZETA_TILDE_RANGO_SUGERIDO[1]} "
            f"(desalinea)."
        )
        lam = st.slider("λ — torque de acreción (alineador)", 0.05, 2.0, 0.5, 0.05)
        zeta_tilde = st.slider("ζ̃ — torque de warping magnético (desalineador)",
                                0.1, 5.0, 1.0, 0.1)
        beta_inicial = st.slider("Desalineación inicial β₀ (°)", 0.0, 90.0, 1.0, 1.0)
        t_total_myr = st.slider("Tiempo total a simular (Myr)", 0.5, 20.0, 5.0, 0.5)

        razon = zeta_tilde / lam if lam > 0 else float("inf")
        if razon < 1.0:
            st.info(f"ζ̃/λ = {razon:.2f} < 1 → β=0 es el único equilibrio estable "
                    f"(el sistema tiende a alinearse).")
        else:
            st.info(f"ζ̃/λ = {razon:.2f} ≥ 1 → β=0 es INESTABLE, el sistema puede "
                    f"generar desalineación desde casi-cero.")

    if st.button("▶️ Evolucionar disco"):
        disco = DiscoProtoplanetario(
            M_estrella_msol=M_estrella, R_estrella_rsol=R_estrella,
            B_estrella_gauss=B_estrella, P_rot_dias=P_rot,
            Mdot0_msol_yr=Mdot0, tau_disco_myr=tau_disco,
            lam=lam, zeta_tilde=zeta_tilde, beta_inicial_deg=beta_inicial,
        )
        with st.spinner("Integrando d(cos β)/dt..."):
            beta_final, historial = disco.evolucionar(t_total_myr)
        equilibrio = disco.equilibrio_esperado()

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("β final", f"{beta_final:.1f}°", delta=f"{beta_final - beta_inicial:+.1f}°")
        if equilibrio["beta_plus_deg"] is not None:
            c2.metric("β de equilibrio analítico", f"{equilibrio['beta_plus_deg']:.1f}°")
        else:
            c2.metric("Equilibrio analítico", "β = 0° (estable)")
        c3.metric("r_in final", f"{historial['r_in_ua'][-1]:.4f} UA")

        fig_beta = go.Figure()
        fig_beta.add_trace(go.Scatter(
            x=historial["t_myr"], y=historial["beta_deg"],
            mode="lines", line=dict(color=COLOR_BETA, width=2.5),
            name="β (°)",
        ))
        fig_beta.update_layout(
            title="Evolución de la desalineación β",
            xaxis_title="Tiempo (Myr)", yaxis_title="β (°)",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1A2E"), height=380,
        )
        st.plotly_chart(fig_beta, use_container_width=True)

        with st.expander("Tasa de acreción y radio de truncamiento en el tiempo"):
            fig_mdot = go.Figure()
            fig_mdot.add_trace(go.Scatter(
                x=historial["t_myr"], y=historial["Mdot_msol_yr"],
                mode="lines", line=dict(color=COLOR_MDOT, width=2),
                name="Ṁ (M☉/año)",
            ))
            fig_mdot.update_layout(
                title="Tasa de acreción disco→estrella",
                xaxis_title="Tiempo (Myr)", yaxis_title="Ṁ (M☉/año)",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1A1A2E"), height=300,
            )
            st.plotly_chart(fig_mdot, use_container_width=True)

        st.caption(disco.advertencia_parametros_asumidos())
        st.caption(
            "🔎 Validación parcial disponible: el radio de truncamiento (r_in) "
            "calculado para DO Tau reproduce el valor publicado "
            "(Bessolaz et al. 2008) dentro de ~15%. Esto valida solo r_in, "
            "no la evolución de β completa — no existe una estrella real con "
            "β medido con precisión suficiente para eso."
        )
