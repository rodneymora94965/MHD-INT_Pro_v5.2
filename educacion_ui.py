# educacion_ui.py
# Pantalla de la sección "📚 Educación", compartida por las 3 versiones.
# Contenido en contenido_educativo.py (módulo Python, no .txt suelto --
# evita rutas rotas dentro de un .exe empaquetado con PyInstaller).

import streamlit as st

from i18n import t
from contenido_i18n import traducir
from contenido_educativo import (
    MARCO_TEORICO as _MARCO_ES, GLOSARIO_ILUSTRADO as _GLOSARIO_ES,
    EJERCICIOS_SECUNDARIA as _EJ_SEC_ES, EJERCICIOS_UNIVERSIDAD as _EJ_UNI_ES,
    EJERCICIOS_CIENTIFICO as _EJ_CIE_ES, TROUBLESHOOTING as _TROUBLE_ES,
)


def _render_ejercicio(idx: int, ej: dict, campos: list):
    simulable = ej.get("simulable", True)
    icono = "✅" if simulable else "🧭"
    with st.expander(t("edu.ej.clase", icono=icono, n=idx, titulo=ej["titulo"])):
        for etiqueta, clave in campos:
            if clave in ej and ej[clave] not in (None, "—"):
                st.markdown(f"**{etiqueta}:** {ej[clave]}")
        if not simulable:
            st.warning(t("edu.ej.no_simulable") + ej.get("nota_no_simulable", ""))


def render_educacion():
    # Etapa 2: contenido traducido al idioma actual (en español, sin cambios).
    MARCO_TEORICO = traducir(_MARCO_ES)
    GLOSARIO_ILUSTRADO = traducir(_GLOSARIO_ES)
    EJERCICIOS_SECUNDARIA = traducir(_EJ_SEC_ES)
    EJERCICIOS_UNIVERSIDAD = traducir(_EJ_UNI_ES)
    EJERCICIOS_CIENTIFICO = traducir(_EJ_CIE_ES)
    TROUBLESHOOTING = traducir(_TROUBLE_ES)

    st.markdown(t("edu.titulo"))
    st.caption(t("edu.caption"))

    with st.expander(t("edu.guia.expander")):
        st.caption(t("edu.guia.caption"))
        if st.button(t("edu.guia.boton")):
            from guia_estudio import generar_guia_estudio_pdf
            # El PDF sigue en español hasta traducir guia_estudio.py (Etapa 2).
            ejercicios_por_nivel = {
                "Secundaria": _EJ_SEC_ES,
                "Universidad": _EJ_UNI_ES,
                "Científico": _EJ_CIE_ES,
            }
            st.session_state["guia_estudio_pdf_bytes"] = generar_guia_estudio_pdf(
                _MARCO_ES, ejercicios_por_nivel)
        if st.session_state.get("guia_estudio_pdf_bytes"):
            st.download_button(
                t("edu.guia.descargar"),
                data=st.session_state["guia_estudio_pdf_bytes"],
                file_name="MHD-INT_guia_de_estudio.pdf", mime="application/pdf",
            )

    tab_teoria, tab_glosario, tab_ejercicios, tab_trouble = st.tabs(
        [t("edu.tab.teoria"), t("edu.tab.glosario"), t("edu.tab.ejercicios"), t("edu.tab.trouble")]
    )

    # ---- Marco teórico ----
    with tab_teoria:
        st.markdown(MARCO_TEORICO["intro"])

        st.markdown(t("edu.intro.titulo"))
        st.caption(t("edu.intro.caption"))
        for tema in MARCO_TEORICO["introduccion_astrofisica"]:
            with st.expander(tema["titulo"], expanded=False):
                st.markdown(tema["texto"])

        st.markdown(t("edu.pilares.titulo"))
        for pilar in MARCO_TEORICO["pilares"]:
            with st.expander(pilar["nombre"], expanded=False):
                st.markdown(t("edu.nivel_basico", texto=pilar["basico"]))
                st.markdown(t("edu.nivel_avanzado", texto=pilar["avanzado"]))

        st.markdown(t("edu.mhi.titulo"))
        st.markdown(MARCO_TEORICO["mhi_intro"])
        for peso, nombre, descripcion in MARCO_TEORICO["formula_mhi"]:
            st.markdown(f"- **{peso} — {nombre}:** {descripcion}")
        st.info(MARCO_TEORICO["nota_penalizacion_oblicuidad"])

        st.markdown(t("edu.avanzados.titulo"))
        st.caption(t("edu.avanzados.caption"))
        for tema in MARCO_TEORICO["temas_avanzados"]:
            with st.expander(tema["nombre"], expanded=False):
                st.markdown(tema["explicacion"])
                if tema.get("ecuacion"):
                    st.code(tema["ecuacion"], language=None)
                st.markdown(t("edu.en_mhdint", texto=tema["relacion_mhd_int"]))

        st.markdown(t("edu.igm.titulo"))
        _igm = MARCO_TEORICO["interpretacion_gravedad_magnetismo"]
        st.markdown(_igm["intro"])
        st.info(t("edu.igm.ciclo", texto=_igm["ciclo"]))
        col_grav, col_mag = st.columns(2)
        with col_grav:
            st.markdown(t("edu.igm.gravedad"))
            for linea in _igm["guia_gravedad"]:
                st.markdown(f"- {linea}")
        with col_mag:
            st.markdown(t("edu.igm.magnetismo"))
            for linea in _igm["guia_magnetismo"]:
                st.markdown(f"- {linea}")
        st.markdown(t("edu.igm.casos"))
        for caso in _igm["casos"]:
            with st.expander(caso["nombre"], expanded=False):
                st.markdown(caso["texto"])

        st.markdown(t("edu.bucle.titulo"))
        _bucle = MARCO_TEORICO["bucle_motor"]
        st.markdown(_bucle["intro"])
        for paso in _bucle["pasos"]:
            st.markdown(paso)
        st.warning(_bucle["nota_torque_atmosferico"])
        with st.expander(t("edu.bucle.donde")):
            for archivo, funcion, descripcion in _bucle["donde_esta_en_el_codigo"]:
                st.markdown(f"- `{archivo}` → `{funcion}` — {descripcion}")

    # ---- Glosario ilustrado ----
    with tab_glosario:
        st.caption(t("edu.glosario.caption"))
        for termino, definicion, analogia in GLOSARIO_ILUSTRADO:
            st.markdown(f"**{termino}** — {definicion}  \n*{analogia}*")
            st.markdown("---")

    # ---- Ejercicios ----
    with tab_ejercicios:
        st.caption(t("edu.ej.leyenda"))
        nivel_tabs = st.tabs([t("edu.nivel.secundaria"), t("edu.nivel.universidad"), t("edu.nivel.cientifico")])

        with nivel_tabs[0]:
            campos = [(t("edu.campo.objetivo"), "objetivo"), (t("edu.campo.analogia"), "analogia"),
                      (t("edu.campo.experimento"), "experimento"), (t("edu.campo.prediccion"), "prediccion"),
                      (t("edu.campo.actividad"), "actividad")]
            for i, ej in enumerate(EJERCICIOS_SECUNDARIA, 1):
                _render_ejercicio(i, ej, campos)

        with nivel_tabs[1]:
            campos = [(t("edu.campo.concepto"), "concepto"), (t("edu.campo.practica"), "practica"), (t("edu.campo.simulacion"), "simulacion")]
            for i, ej in enumerate(EJERCICIOS_UNIVERSIDAD, 1):
                _render_ejercicio(i, ej, campos)

        with nivel_tabs[2]:
            campos = [(t("edu.campo.pregunta"), "pregunta"), (t("edu.campo.metodo"), "metodo"), (t("edu.campo.analisis"), "analisis")]
            for i, ej in enumerate(EJERCICIOS_CIENTIFICO, 1):
                _render_ejercicio(i, ej, campos)

    # ---- Troubleshooting ----
    with tab_trouble:
        st.caption(t("edu.trouble.caption"))
        for i, ej in enumerate(TROUBLESHOOTING, 1):
            with st.expander(t("edu.trouble.item", n=i, problema=ej["problema"])):
                st.markdown(t("edu.trouble.diagnostico", texto=ej["diagnostico"]))
                st.markdown(t("edu.trouble.causa", texto=ej["causa"]))
                st.markdown(t("edu.trouble.solucion", texto=ej["solucion"]))
