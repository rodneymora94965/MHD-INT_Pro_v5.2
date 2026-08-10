# sesion.py
# MHD-INT -- identificador de sesión por visitante.
# Licencia AGPL-3.0
#
# En una demo pública (un solo deploy en Streamlit Cloud atendiendo a
# muchos visitantes), cada visitante tiene su propio st.session_state
# (Streamlit lo aísla por navegador/pestaña), pero el historial se
# guarda en un archivo compartido en el disco del servidor. Este id
# se usa para filtrar ese archivo por visitante -- ver historial.py.

import uuid
import streamlit as st


def obtener_sesion_id() -> str:
    """Devuelve un id estable para esta sesión de navegador, generándolo
    la primera vez que se llama en cada sesión."""
    if "sesion_id" not in st.session_state:
        st.session_state["sesion_id"] = str(uuid.uuid4())
    return st.session_state["sesion_id"]
