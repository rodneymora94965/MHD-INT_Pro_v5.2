# modificador_ui.py
# MHD-INT PRO v5.9 — Capa 3: pantalla del Modificador de Sistemas
# Licencia: Comercial propietaria (dual con AGPL-3.0)
#
# ⚠️ ESTE MÓDULO NO PERTENECE AL REPOSITORIO PÚBLICO AGPL.
#
# Separado de modificador_sistemas.py a propósito, mismo criterio que
# disco_ui.py / disco_protoplanetario.py: ese archivo es lógica pura
# (sin streamlit), este es solo la pantalla que lo llama.

import streamlit as st
import plotly.graph_objects as go

from modificador_sistemas import ModificadorSistemas
from database import PLANETAS

COLOR_ORIGINAL = "#8A94A6"
COLOR_MODIFICADO = "#2E5C8A"


def render_modificador_sistemas():
    st.markdown("### 🧪 Modificador de Sistemas")
    st.caption(
        "Tomá un planeta real de la base de datos, modificá su órbita, masa, "
        "campo magnético o luna, y comparalo contra el original con el motor "
        "de simulación de MHD-INT."
    )

    no_implementados = ModificadorSistemas.experimentos_no_implementados()
    with st.expander("⚠️ Qué NO se puede simular acá (y por qué)", expanded=False):
        st.caption(
            "El motor de MHD-INT simula cada planeta de forma independiente "
            "(estrella-planeta-luna), sin gravedad planeta-planeta. Estos dos "
            "experimentos de la propuesta original quedaron fuera por eso, en "
            "vez de mostrarse con un resultado sin respaldo físico:"
        )
        for exp in no_implementados:
            st.markdown(f"- **{exp['experimento']}** — {exp['razon']}")

    planeta_base = st.selectbox("Planeta base", list(PLANETAS.keys()))

    st.markdown("#### Modificaciones a aplicar")
    col1, col2 = st.columns(2)

    with col1:
        mover = st.checkbox("Mover a otra órbita")
        a_ua = st.number_input("Nuevo semieje (UA)", 0.01, 50.0, 1.0, 0.01, disabled=not mover)

        cambiar_masa = st.checkbox("Cambiar masa")
        m_tierra = st.number_input("Nueva masa (M⊕)", 0.01, 500.0, 1.0, 0.1, disabled=not cambiar_masa)

    with col2:
        cambiar_b = st.checkbox("Cambiar campo magnético inicial")
        b_gauss = st.number_input("Nuevo B inicial (Gauss)", 0.0, 100.0, 0.5, 0.05, disabled=not cambiar_b)

        agregar_luna = st.checkbox("Agregar/reemplazar luna")
        c1, c2 = st.columns(2)
        masa_luna_kg = c1.number_input("Masa de la luna (kg)", 1e18, 1e24, 7.35e22,
                                        format="%.2e", disabled=not agregar_luna)
        a_luna_ua = c2.number_input("Distancia inicial luna (UA)", 0.0001, 0.05, 0.00257,
                                     format="%.5f", disabled=not agregar_luna)

    st.markdown("#### Duración de la simulación")
    t_max = st.slider("Tiempo máximo (Gyr)", 0.1, 10.0, 5.0, 0.1)
    dt = st.select_slider("Paso (años)", options=[1000, 5000, 10000, 50000, 100000], value=10000)

    if not (mover or cambiar_masa or cambiar_b or agregar_luna):
        st.info("Marcá al menos una modificación para poder comparar contra el original.")
        return

    if st.button("▶️ Simular y comparar"):
        m = ModificadorSistemas(planeta_base)
        if mover:
            m.mover_planeta(a_ua)
        if cambiar_masa:
            m.cambiar_masa(m_tierra)
        if cambiar_b:
            m.cambiar_campo_magnetico(b_gauss)
        if agregar_luna:
            m.agregar_luna(masa_luna_kg, a_luna_ua)

        with st.spinner("Simulando original y modificado..."):
            resultado = m.simular_y_comparar(t_max_gyr=t_max, dt_yr=dt)

        st.markdown("---")
        st.caption("Modificaciones aplicadas: " + " · ".join(resultado["modificaciones"]))

        if resultado["error"]:
            st.error(f"No se pudo completar la simulación: {resultado['error']}")
            return

        if resultado.get("advertencia_estabilidad"):
            st.warning(resultado["advertencia_estabilidad"])

        delta = resultado["delta"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ΔB final", f"{delta['delta_B_gauss']:+.4f} G")
        c2.metric("ΔMHI", f"{delta['delta_MHI']:+.1f}")
        c3.metric("ΔP_rot", f"{delta['delta_P_rot_dias']:+.2f} días")
        c4.metric("Δa final", f"{delta['delta_a_ua']:+.4f} UA")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**{planeta_base} (original)**")
            st.write(f"Campo protegido: {'✅' if delta['campo_protegido_original'] else '❌'}")
            st.write(f"MHI: {resultado['mhi_original']['mhi_total']:.1f}")
        with col_b:
            st.markdown(f"**{planeta_base} (modificado)**")
            st.write(f"Campo protegido: {'✅' if delta['campo_protegido_modificado'] else '❌'}")
            st.write(f"MHI: {resultado['mhi_modificado']['mhi_total']:.1f}")
            if delta["se_estrello_modificado"]:
                st.error("💥 El planeta modificado se estrelló contra la estrella.")

        r_orig, r_mod = resultado["original"], resultado["modificado"]
        if r_orig.tiene_serie() and r_mod.tiene_serie():
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=r_orig.serie.tiempos, y=r_orig.serie.B_p_gauss,
                                      mode="lines", name=f"{planeta_base} (original)",
                                      line=dict(color=COLOR_ORIGINAL, width=2)))
            fig.add_trace(go.Scatter(x=r_mod.serie.tiempos, y=r_mod.serie.B_p_gauss,
                                      mode="lines", name=f"{planeta_base} (modificado)",
                                      line=dict(color=COLOR_MODIFICADO, width=2)))
            fig.update_layout(
                title="Campo magnético — original vs. modificado",
                xaxis_title="Tiempo (Gyr)", yaxis_title="B (Gauss)",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1A1A2E"), height=380,
            )
            st.plotly_chart(fig, use_container_width=True)
