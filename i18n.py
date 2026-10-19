"""i18n.py — Internacionalización (ES/EN) de MHD-INT.

Un solo código para los dos idiomas. Todo texto que ve el usuario pasa por t().

    from i18n import t, selector_idioma
    st.button(t("sim.btn.simular"))
    st.caption(t("sanity.densidad", valor=3.2))

Diseño
------
- El idioma activo vive en st.session_state["lang"] ("es" por defecto). Dura lo
  que dura la sesión, igual que el resto de la app (no hay login).
- Los textos están en locales/<idioma>/<modulo>.json, un archivo por módulo, no
  un JSON gigante. Así cada zip lleva solo los textos de las pantallas que
  incluye y no se filtran textos de módulos Pro al Open Source.
- Claves con formato modulo.seccion.elemento, en minúsculas:
      menu.catalogo            locales/*/menu.json
      fotos.filtro.todas       locales/*/biblioteca_fotos.json
- Fallback en cascada: si falta en el idioma activo, usa el español; si falta en
  los dos, devuelve la clave. NUNCA lanza una excepción por una traducción que
  falte: una app rota es peor que un texto sin traducir.

Regla de oro del proyecto: la física no cambia. Este módulo solo toca texto.
"""
import json
from pathlib import Path

import streamlit as st

IDIOMA_POR_DEFECTO = "es"
IDIOMAS = ("es", "en")
ETIQUETA_IDIOMA = {"es": "ES", "en": "EN"}

_DIR_LOCALES = Path(__file__).resolve().parent / "locales"

# Caché en memoria: {idioma: {clave: texto}}. Se llena la primera vez que se
# pide un idioma y se puede vaciar con recargar() (útil en desarrollo).
_cache = {}


# ---------------------------------------------------------------------------
# Carga de textos
# ---------------------------------------------------------------------------
def _textos(idioma):
    """Diccionario aplanado con todos los textos de un idioma."""
    if idioma not in _cache:
        datos = {}
        carpeta = _DIR_LOCALES / idioma
        if carpeta.is_dir():
            for f in sorted(carpeta.glob("*.json")):
                try:
                    with open(f, encoding="utf-8") as fh:
                        datos.update(json.load(fh))
                except (OSError, ValueError) as e:
                    # Un locale mal formado no puede tumbar la aplicación.
                    print(f"[i18n] aviso: no se pudo leer {f.name}: {e}")
        _cache[idioma] = datos
    return _cache[idioma]


def recargar():
    """Vacía la caché (desarrollo: útil tras editar un .json)."""
    _cache.clear()


# ---------------------------------------------------------------------------
# Idioma activo
# ---------------------------------------------------------------------------
def idioma_actual():
    """Idioma de la sesión. Siempre devuelve uno válido."""
    try:
        valor = st.session_state.get("lang", IDIOMA_POR_DEFECTO)
    except Exception:
        return IDIOMA_POR_DEFECTO
    return valor if valor in IDIOMAS else IDIOMA_POR_DEFECTO


def fijar_idioma(idioma):
    """Cambia el idioma de la sesión."""
    if idioma in IDIOMAS:
        st.session_state["lang"] = idioma


# ---------------------------------------------------------------------------
# Traducción
# ---------------------------------------------------------------------------
def t(clave, **kwargs):
    """Devuelve el texto de `clave` en el idioma activo.

    kwargs se sustituyen en los placeholders {...} del texto:
        t("sanity.densidad", valor=3.2)  ->  "Densidad: 3.2 g/cm³"

    Parámetro especial `defecto`: texto a usar cuando la clave no existe en
    ningún idioma. Sirve para valores que vienen de datos y no de locales:
        t("fotos.categoria.marte", defecto="Marte")

    Nunca lanza excepción: ante cualquier problema devuelve defecto o la clave.
    """
    defecto = kwargs.pop("defecto", None)

    texto = None
    for idioma in (idioma_actual(), IDIOMA_POR_DEFECTO):
        texto = _textos(idioma).get(clave)
        if texto is not None:
            break

    if texto is None:
        return defecto if defecto is not None else clave

    if not isinstance(texto, str):
        return defecto if defecto is not None else clave

    if kwargs:
        try:
            return texto.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            # Placeholders desalineados entre idiomas: mostrar el texto crudo
            # es mejor que romper la pantalla.
            return texto
    return texto


def tiene(clave):
    """True si la clave existe en el idioma activo."""
    return clave in _textos(idioma_actual())


# ---------------------------------------------------------------------------
# Selector 🌐 ES / EN
# ---------------------------------------------------------------------------
def selector_idioma(contenedor=None, key="selector_idioma"):
    """Dibuja el selector de idioma. Va arriba del sidebar.

    Usa el valor interno ("es"/"en") como opción del widget y traduce solo la
    etiqueta mostrada, con format_func. Así el valor guardado en session_state
    nunca es texto traducido (trampa #2 del proyecto).
    """
    cont = st.sidebar if contenedor is None else contenedor
    actual = idioma_actual()
    elegido = cont.radio(
        t("i18n.idioma", defecto="Idioma"),
        options=list(IDIOMAS),
        index=list(IDIOMAS).index(actual),
        format_func=lambda i: ETIQUETA_IDIOMA.get(i, i.upper()),
        key=key,
    )
    if elegido != actual:
        fijar_idioma(elegido)
        st.rerun()
    return elegido
