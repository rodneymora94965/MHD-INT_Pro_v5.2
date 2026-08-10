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

    tab_teoria, tab_glosario, tab_ejercicios, tab_trouble = st.tabs(
        ["🧠 Marco Teórico", "📖 Glosario ilustrado", "📝 Ejercicios", "🔧 Troubleshooting"]
    )

    # ---- Marco teórico ----
    with tab_teoria:
        st.markdown(MARCO_TEORICO["intro"])
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
