# educacion_ui.py
# Pantalla de la sección "📚 Educación", compartida por las 3 versiones.
# Contenido en contenido_educativo.py (módulo Python, no .txt suelto --
# evita rutas rotas dentro de un .exe empaquetado con PyInstaller).

import streamlit as st

from contenido_educativo import (
    MARCO_TEORICO, GLOSARIO_ILUSTRADO,
    EJERCICIOS_SECUNDARIA, EJERCICIOS_UNIVERSIDAD, EJERCICIOS_CIENTIFICO,
    TROUBLESHOOTING,
)


def _render_ejercicio(idx: int, ej: dict, campos: list):
    simulable = ej.get("simulable", True)
    icono = "✅" if simulable else "🧭"
    with st.expander(f"{icono} Clase {idx}: {ej['titulo']}"):
        for etiqueta, clave in campos:
            if clave in ej and ej[clave] not in (None, "—"):
                st.markdown(f"**{etiqueta}:** {ej[clave]}")
        if not simulable:
            st.warning(
                "🧭 **Ejercicio conceptual — no simulable con MHD-INT hoy.**\n\n"
                + ej.get("nota_no_simulable", "")
            )


def render_educacion():
    st.markdown("### 📚 Educación")
    st.caption("De la secundaria a la investigación — marco teórico, glosario y ejercicios guiados con MHD-INT.")

    with st.expander("📄 Guía de estudio completa (PDF, 5 módulos)"):
        st.caption(
            "El mismo contenido de esta sección, organizado como PDF descargable "
            "-- se genera al momento a partir de lo que ves acá, no es un "
            "documento aparte que pueda quedar desactualizado."
        )
        if st.button("Generar guía de estudio (PDF)"):
            from guia_estudio import generar_guia_estudio_pdf
            ejercicios_por_nivel = {
                "Secundaria": EJERCICIOS_SECUNDARIA,
                "Universidad": EJERCICIOS_UNIVERSIDAD,
                "Científico": EJERCICIOS_CIENTIFICO,
            }
            st.session_state["guia_estudio_pdf_bytes"] = generar_guia_estudio_pdf(
                MARCO_TEORICO, ejercicios_por_nivel)
        if st.session_state.get("guia_estudio_pdf_bytes"):
            st.download_button(
                "⬇️ Descargar guía de estudio (.pdf)",
                data=st.session_state["guia_estudio_pdf_bytes"],
                file_name="MHD-INT_guia_de_estudio.pdf", mime="application/pdf",
            )

    tab_teoria, tab_glosario, tab_ejercicios, tab_trouble = st.tabs(
        ["🧠 Marco Teórico", "📖 Glosario ilustrado", "📝 Ejercicios", "🔧 Troubleshooting"]
    )

    # ---- Marco teórico ----
    with tab_teoria:
        st.markdown(MARCO_TEORICO["intro"])

        st.markdown("#### 🌌 Introducción a la astrofísica")
        st.caption("Lo mínimo para entender el resto de esta sección, si nunca estudiaste astrofísica antes.")
        for tema in MARCO_TEORICO["introduccion_astrofisica"]:
            with st.expander(tema["titulo"], expanded=False):
                st.markdown(tema["texto"])

        st.markdown("#### Los 4 pilares de la simulación")
        for pilar in MARCO_TEORICO["pilares"]:
            with st.expander(pilar["nombre"], expanded=False):
                st.markdown(f"**Nivel básico:** {pilar['basico']}")
                st.markdown(f"**Nivel avanzado:** {pilar['avanzado']}")

        st.markdown("#### La ecuación del MHI")
        st.markdown(MARCO_TEORICO["mhi_intro"])
        for peso, nombre, descripcion in MARCO_TEORICO["formula_mhi"]:
            st.markdown(f"- **{peso} — {nombre}:** {descripcion}")
        st.info(MARCO_TEORICO["nota_penalizacion_oblicuidad"])

        st.markdown("#### Temas de los módulos avanzados")
        st.caption("N-cuerpos, resonancias, alineaciones, torque atmosférico, efemérides y discos protoplanetarios.")
        for tema in MARCO_TEORICO["temas_avanzados"]:
            with st.expander(tema["nombre"], expanded=False):
                st.markdown(tema["explicacion"])
                if tema.get("ecuacion"):
                    st.code(tema["ecuacion"], language=None)
                st.markdown(f"**En MHD-INT:** {tema['relacion_mhd_int']}")

        st.markdown("#### 🧭 Interpretación gravitatoria y magnética")
        _igm = MARCO_TEORICO["interpretacion_gravedad_magnetismo"]
        st.markdown(_igm["intro"])
        st.info(f"**El ciclo:** {_igm['ciclo']}")
        col_grav, col_mag = st.columns(2)
        with col_grav:
            st.markdown("**Cómo interpretar la gravedad**")
            for linea in _igm["guia_gravedad"]:
                st.markdown(f"- {linea}")
        with col_mag:
            st.markdown("**Cómo interpretar el magnetismo**")
            for linea in _igm["guia_magnetismo"]:
                st.markdown(f"- {linea}")
        st.markdown("**Casos de ejemplo**")
        for caso in _igm["casos"]:
            with st.expander(caso["nombre"], expanded=False):
                st.markdown(caso["texto"])

        st.markdown("#### ⚙️ El bucle del motor — cómo funciona por dentro")
        _bucle = MARCO_TEORICO["bucle_motor"]
        st.markdown(_bucle["intro"])
        for paso in _bucle["pasos"]:
            st.markdown(paso)
        st.warning(_bucle["nota_torque_atmosferico"])
        with st.expander("Dónde está esto en el código"):
            for archivo, funcion, descripcion in _bucle["donde_esta_en_el_codigo"]:
                st.markdown(f"- `{archivo}` → `{funcion}` — {descripcion}")

    # ---- Glosario ilustrado ----
    with tab_glosario:
        st.caption(
            "Vocabulario general de astrofísica que aparece en el marco teórico "
            "y los ejercicios. Para el significado de cada variable propia de "
            "MHD-INT (a_ua, B_gauss, MHI...), ver la sección 📖 Glosario del menú principal."
        )
        for termino, definicion, analogia in GLOSARIO_ILUSTRADO:
            st.markdown(f"**{termino}** — {definicion}  \n*{analogia}*")
            st.markdown("---")

    # ---- Ejercicios ----
    with tab_ejercicios:
        st.caption("✅ = simulable con MHD-INT tal como está hoy · 🧭 = pregunta conceptual, fuera del alcance actual del motor.")
        nivel_tabs = st.tabs(["📘 Secundaria (14-18 años)", "📗 Universidad (18-22 años)", "📕 Científico (Tesis)"])

        with nivel_tabs[0]:
            campos = [("Objetivo", "objetivo"), ("Analogía", "analogia"),
                      ("Experimento", "experimento"), ("Predicción", "prediccion"),
                      ("Actividad", "actividad")]
            for i, ej in enumerate(EJERCICIOS_SECUNDARIA, 1):
                _render_ejercicio(i, ej, campos)

        with nivel_tabs[1]:
            campos = [("Concepto", "concepto"), ("Práctica", "practica"), ("Simulación", "simulacion")]
            for i, ej in enumerate(EJERCICIOS_UNIVERSIDAD, 1):
                _render_ejercicio(i, ej, campos)

        with nivel_tabs[2]:
            campos = [("Pregunta de investigación", "pregunta"), ("Método", "metodo"), ("Análisis", "analisis")]
            for i, ej in enumerate(EJERCICIOS_CIENTIFICO, 1):
                _render_ejercicio(i, ej, campos)

    # ---- Troubleshooting ----
    with tab_trouble:
        st.caption("10 problemas comunes, cómo diagnosticarlos y cómo resolverlos.")
        for i, ej in enumerate(TROUBLESHOOTING, 1):
            with st.expander(f"Ejercicio {i}: {ej['problema']}"):
                st.markdown(f"**Diagnóstico:** {ej['diagnostico']}")
                st.markdown(f"**Causa probable:** {ej['causa']}")
                st.markdown(f"**Solución:** {ej['solucion']}")
