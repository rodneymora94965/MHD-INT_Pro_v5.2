# biblioteca_fotos_ui.py
# MHD-INT — Pantalla de la Biblioteca de fotos astronómicas
# Licencia AGPL-3.0 (misma licencia que el resto de la app_streamlit base).
#
# ETAPA 0 del i18n — pantalla piloto.
# Todo texto de la interfaz sale de t(). Los nombres y descripciones de las
# fotos viven en biblioteca_fotos.py (son datos de contenido): siguen en
# español y quedan para la Etapa 2. El mecanismo se valida igual.
import streamlit as st

from contenido_educativo import MARCO_TEORICO
from biblioteca_fotos import FOTOS, validar_biblioteca
from i18n import t
from contenido_i18n import traducir

# Se valida una sola vez al importar -- si alguna conexión educativa
# quedó rota (p.ej. cambió el título de un tema real), esto rompe acá,
# al arrancar la app, no en silencio mientras alguien navega.
validar_biblioteca(MARCO_TEORICO)

# Valor interno del filtro "todas". NO se traduce: es lo que queda guardado en
# session_state. La etiqueta visible la pone format_func (trampa #2 del spec:
# si se guarda el texto traducido, al cambiar de idioma el valor queda inválido).
_TODAS = "__todas__"

# Claves internas de sección -> clave de traducción. Las claves internas NO se
# traducen (las usa validar_biblioteca y MARCO_TEORICO); solo el título visible.
_SECCION_A_CLAVE = {
    "introduccion_astrofisica": "fotos.seccion.introduccion_astrofisica",
    "pilares": "fotos.seccion.pilares",
    "temas_avanzados": "fotos.seccion.temas_avanzados",
    "interpretacion_gravedad_magnetismo": "fotos.seccion.interpretacion_gravedad_magnetismo",
}


def _titulo_seccion(seccion):
    """Título traducido de una sección educativa.

    Si aparece una sección nueva sin traducir, muestra la clave interna en vez
    de romper (misma política que el fallback de i18n).
    """
    return t(_SECCION_A_CLAVE.get(seccion, ""), defecto=seccion)


def render_biblioteca_fotos():
    st.markdown(t("fotos.titulo"))
    st.caption(t("fotos.caption"))

    categorias = sorted({f["categoria"] for f in FOTOS})
    opciones = [_TODAS] + categorias
    filtro = st.selectbox(
        t("fotos.filtro"),
        opciones,
        format_func=lambda c: t("fotos.filtro.todas") if c == _TODAS else traducir(c),
    )
    fotos_mostradas = FOTOS if filtro == _TODAS else [f for f in FOTOS if f["categoria"] == filtro]
    fotos_mostradas = traducir(fotos_mostradas, omitir=("url",))

    cols = st.columns(3)
    for i, foto in enumerate(fotos_mostradas):
        with cols[i % 3]:
            st.image(foto["url"], caption=foto["nombre"], use_container_width=True)
            with st.expander(t("fotos.ver_descripcion")):
                st.markdown(foto["descripcion"])
                st.caption(t("fotos.fuente", fuente=foto["fuente"]))
                seccion, titulo_tema = foto["conexion"]
                st.info(t("fotos.conecta", titulo=_titulo_seccion(seccion), tema=titulo_tema))
