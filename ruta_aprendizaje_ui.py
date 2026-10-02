# ruta_aprendizaje_ui.py
# MHD-INT — Pantalla de Ruta de Aprendizaje
# Licencia AGPL-3.0 (misma licencia que el resto de la app_streamlit base).
import streamlit as st

from contenido_educativo import EJERCICIOS_SECUNDARIA, EJERCICIOS_UNIVERSIDAD, EJERCICIOS_CIENTIFICO, MARCO_TEORICO
from rutas_aprendizaje import RUTAS, validar_rutas, obtener_etapas_resueltas

_EJERCICIOS_POR_NIVEL = {
    "Secundaria": EJERCICIOS_SECUNDARIA,
    "Universidad": EJERCICIOS_UNIVERSIDAD,
    "Científico": EJERCICIOS_CIENTIFICO,
}

# Se valida una sola vez al importar el módulo (no en cada render) --
# si algún título de ejercicio o tema cambió y quedó una referencia
# rota, esto tira ValueError acá, al arrancar la app, no en silencio
# mientras alguien navega la pantalla.
validar_rutas(MARCO_TEORICO, _EJERCICIOS_POR_NIVEL)

_CAMPOS_EJERCICIO_POR_NIVEL = {
    "Secundaria": [("Objetivo", "objetivo"), ("Analogía", "analogia"), ("Experimento", "experimento"),
                   ("Predicción", "prediccion"), ("Actividad", "actividad")],
    "Universidad": [("Concepto", "concepto"), ("Práctica", "practica"), ("Simulación", "simulacion")],
    "Científico": [("Pregunta", "pregunta"), ("Método", "metodo"), ("Análisis", "analisis")],
}


def render_ruta_aprendizaje():
    st.markdown("### 🗺️ Ruta de Aprendizaje")
    st.caption(
        "No es contenido nuevo -- es una secuencia curada sobre lo que ya está en "
        "Educación (Introducción a la Astrofísica, Marco Teórico, ejercicios), "
        "ordenada con sentido pedagógico. El progreso se guarda solo durante esta "
        "sesión del navegador -- si cerrás y volvés mañana, arranca de nuevo."
    )

    nivel = st.radio("Elegí tu ruta", list(RUTAS.keys()), horizontal=True, key="ruta_nivel_sel")
    etapas = obtener_etapas_resueltas(nivel, MARCO_TEORICO, _EJERCICIOS_POR_NIVEL)
    campos_ejercicio = _CAMPOS_EJERCICIO_POR_NIVEL[nivel]

    clave_progreso = f"ruta_progreso_{nivel}"
    if clave_progreso not in st.session_state:
        st.session_state[clave_progreso] = [False] * len(etapas)
    progreso = st.session_state[clave_progreso]

    n_hechas = sum(progreso)
    st.progress(n_hechas / len(etapas) if etapas else 0.0,
               text=f"{n_hechas} de {len(etapas)} etapas completadas")

    for i, etapa in enumerate(etapas):
        hecha = progreso[i]
        titulo_etapa = f"{'✅' if hecha else '⬜'} Etapa {i + 1} — {etapa['tema_resuelto'].get('titulo') or etapa['tema_resuelto'].get('nombre')}"
        with st.expander(titulo_etapa, expanded=not hecha and (i == 0 or progreso[i - 1])):
            st.markdown("**📖 Leer**")
            _tema = etapa["tema_resuelto"]
            texto_tema = _tema.get("texto") or _tema.get("explicacion")
            if texto_tema is None and "basico" in _tema:
                # Las entradas de "pilares" usan basico/avanzado, no texto/explicacion
                texto_tema = f"{_tema['basico']}\n\n**Más en profundidad:** {_tema['avanzado']}"
            st.markdown(texto_tema or "")

            st.markdown("**🖱️ Hacer**")
            st.info(etapa["hacer"])

            st.markdown(f"**✏️ Ejercicio: {etapa['ejercicio_resuelto']['titulo']}**")
            for etiqueta, campo in campos_ejercicio:
                valor = etapa["ejercicio_resuelto"].get(campo)
                if valor and valor != "—":
                    st.markdown(f"- **{etiqueta}:** {valor}")

            nuevo_valor = st.checkbox("Marcar como hecho", value=hecha, key=f"ruta_check_{nivel}_{i}")
            if nuevo_valor != hecha:
                progreso[i] = nuevo_valor
                st.session_state[clave_progreso] = progreso
                st.rerun()

    if n_hechas == len(etapas) and etapas:
        st.success(f"🎉 Completaste la ruta de {nivel}. Podés repetirla, subir de nivel, o explorar el resto de la app libremente.")
