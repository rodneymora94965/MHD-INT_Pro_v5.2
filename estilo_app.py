# estilo_app.py
# MHD-INT — Constantes de estilo/branding compartidas entre módulos de UI.
#
# Extraído de app_core_pro.py (división del monolito, ago-2026). Antes
# vivían como variables locales dentro de main(), así que solo
# render_reporte_comercial() -- definida en el mismo scope -- podía verlas
# por closure. Al mover render_reporte_comercial a su propio archivo
# (reporte_comercial_ui.py), necesitan un hogar importable por ambos
# lados. Son constantes de presentación puras (no dependen de licencia ni
# de ningún estado de sesión), así que vivir a nivel de módulo es seguro.

# Paleta corporativa (usada por render_reporte_comercial para las gráficas)
COLOR_B = '#E50914'
COLOR_A = '#00C9FF'
COLOR_E = '#92FE9D'
COLOR_ATM = '#FFA500'
COLOR_BG = '#FFFFFF'  # CAMBIO (ago-2026): tema claro -- antes '#0A0A0F'

# Marca blanca (logo/nombre de cliente en el PDF ejecutivo): el esquema de
# precios anterior la ligaba al nivel "Código Fuente" ($33k), que ya no
# existe en el esquema nuevo (AGPL / Standard $49 / Pro $199). No hay
# decisión de negocio tomada sobre en qué nivel va -- queda DESACTIVADA
# por defecto para no regalar de más ni quitar de menos sin que Roney lo
# decida. Para activarla en PRO alcanza con descomentar el bloque de abajo
# (y volver a pasar NIVEL a donde se arma BRANDING_CLIENTE, si se decide
# que dependa del nivel).
BRANDING_CLIENTE = None
# BRANDING_CLIENTE = {
#     "logo_path": "assets/logo_cliente.png",
#     "nombre_cliente": "Nombre del Cliente",
# }

CSS_PREMIUM = """
<style>
/* CAMBIO (ago-2026): paleta profesional/atenuada -- ver misma nota en
   app_streamlit.py. Azul corporativo #2E5C8A en vez de rojo saturado,
   sin mayúsculas/glow en botones. */
.stApp {
    background: linear-gradient(180deg, #FFFFFF 0%, #F4F6FA 100%);
    color: #1A1A2E;
}
[data-testid="stSidebar"] {
    background: rgba(244, 246, 250, 0.92) !important;
    backdrop-filter: blur(12px) !important;
    border-right: 1px solid rgba(30, 60, 90, 0.12) !important;
}
.stButton > button {
    background: #2E5C8A !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 0.4rem 1rem !important;
    box-shadow: 0 1px 4px rgba(30, 60, 90, 0.2) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #24486E !important;
    box-shadow: 0 2px 8px rgba(30, 60, 90, 0.3) !important;
}
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(30, 60, 90, 0.12) !important;
    border-radius: 12px !important;
    padding: 14px !important;
    box-shadow: 0 2px 8px rgba(20, 20, 40, 0.05) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: #2E5C8A !important;
    box-shadow: 0 2px 10px rgba(46, 92, 138, 0.12) !important;
}
[data-testid="stMetric"] label, [data-testid="stMetricValue"] {
    color: #1A1A2E !important;
}
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #2E5C8A, #4F9C6D) !important;
    border-radius: 20px !important;
    height: 8px !important;
}
h1 {
    font-family: 'Courier New', monospace !important;
    letter-spacing: 1.5px !important;
    color: #1A1A2E !important;
    font-size: 1.9rem !important;
    border-bottom: 3px solid #2E5C8A;
    padding-bottom: 6px;
    display: inline-block;
}
h2, h3 {
    color: #1A1A2E !important;
    font-weight: 600 !important;
}
[data-testid="stExpanderHeader"] {
    color: #2E5C8A !important;
    font-weight: 600 !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
}
</style>
"""


def inyectar_css_premium(st):
    """st se recibe como parámetro (no se importa streamlit acá) para que
    este módulo no dependa de streamlit si algún día se reusa fuera de la
    app (ej. tests)."""
    st.markdown(CSS_PREMIUM, unsafe_allow_html=True)


# AUDITORIA oct-2026: st.metric dibuja una flecha VERDE hacia arriba en
# cualquier "delta" que no empiece con "-", así que "Estéril / atmósfera
# expuesta" o "Estéril" salían en verde con flecha de subida. Este helper
# colorea el texto según sea bueno (verde), malo (rojo) o intermedio (gris)
# y quita la flecha cuando la versión de Streamlit lo permite.
def metric_categoria(contenedor, etiqueta, valor, texto, calidad):
    """calidad: 'bueno' | 'malo' | 'medio'."""
    import inspect
    import streamlit as st
    kw = {"delta_color": {"bueno": "normal", "malo": "inverse"}.get(calidad, "off")}
    try:
        if "delta_arrow" in inspect.signature(st.metric).parameters:
            kw["delta_arrow"] = "off"
    except (TypeError, ValueError):
        pass
    return contenedor.metric(etiqueta, valor, delta=texto, **kw)


def calidad_mhi(mhi_total):
    return "bueno" if mhi_total >= 80 else ("medio" if mhi_total >= 50 else "malo")
