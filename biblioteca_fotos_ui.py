# biblioteca_fotos_ui.py
# MHD-INT — Pantalla de la Biblioteca de fotos astronómicas
# Licencia AGPL-3.0 (misma licencia que el resto de la app_streamlit base).
import streamlit as st

from contenido_educativo import MARCO_TEORICO
from biblioteca_fotos import FOTOS, validar_biblioteca

# Se valida una sola vez al importar -- si alguna conexión educativa
# quedó rota (p.ej. cambió el título de un tema real), esto rompe acá,
# al arrancar la app, no en silencio mientras alguien navega.
validar_biblioteca(MARCO_TEORICO)

_TITULO_CONEXION = {
    "introduccion_astrofisica": "Introducción a la Astrofísica",
    "pilares": "Marco Teórico — Pilares",
    "temas_avanzados": "Marco Teórico — Temas avanzados",
    "interpretacion_gravedad_magnetismo": "Interpretación gravitatoria y magnética",
}


def render_biblioteca_fotos():
    st.markdown("### 🌌 Biblioteca de Fotos Astronómicas")
    st.caption(
        "Galería curada, no la imagen del día vía API en vivo -- las fotos son "
        "reales (NASA/ESA/Wikimedia Commons, fuente indicada en cada una) y no "
        "dependen de una clave ni de que un servicio externo esté arriba hoy. "
        "Cada una conecta con un tema real de 📚 Educación."
    )

    categorias = ["Todas"] + sorted({f["categoria"] for f in FOTOS})
    filtro = st.selectbox("Filtrar por categoría", categorias)
    fotos_mostradas = FOTOS if filtro == "Todas" else [f for f in FOTOS if f["categoria"] == filtro]

    cols = st.columns(3)
    for i, foto in enumerate(fotos_mostradas):
        with cols[i % 3]:
            st.image(foto["url"], caption=foto["nombre"], use_container_width=True)
            with st.expander("Ver descripción"):
                st.markdown(foto["descripcion"])
                st.caption(f"Fuente: {foto['fuente']}")
                seccion, titulo_tema = foto["conexion"]
                st.info(f"📚 Conecta con: **{_TITULO_CONEXION.get(seccion, seccion)}** — \"{titulo_tema}\"")
