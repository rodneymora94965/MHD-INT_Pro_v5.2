# contenido_i18n.py
# Etapa 2 del i18n: traducción del CONTENIDO (textos educativos, laboratorios,
# fotos, rutas). A diferencia de la interfaz (t("clave")), el contenido son
# estructuras de datos grandes. Se traduce por mapa: texto exacto en español ->
# texto en inglés (locales/contenido/en.json).
#
# - traducir(obj): devuelve una copia con los textos traducidos si el idioma es
#   inglés; en español devuelve el mismo objeto sin tocar nada.
# - Solo se reemplazan hojas de tipo str que estén en el mapa; lo que no esté
#   queda en español (fallback seguro, nunca falla).
# - NO se tocan estructuras, claves ni IDs internos: los .mhd siguen con IDs
#   en español.
import json
from pathlib import Path

try:
    from i18n import idioma_actual, t as _t
except ImportError:  # motor usado sin streamlit (headless): todo en español
    _t = None

    def idioma_actual():
        return "es"

_RUTA = Path(__file__).parent / "locales" / "contenido"
_CACHE = {}


def _mapa(idioma):
    if idioma not in _CACHE:
        try:
            with open(_RUTA / f"{idioma}.json", "r", encoding="utf-8") as f:
                _CACHE[idioma] = json.load(f)
        except (OSError, ValueError):
            _CACHE[idioma] = {}
    return _CACHE[idioma]


def _tr(obj, m, omitir):
    if isinstance(obj, str):
        return m.get(obj, obj)
    if isinstance(obj, dict):
        return {k: (v if k in omitir else _tr(v, m, omitir)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_tr(v, m, omitir) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_tr(v, m, omitir) for v in obj)
    return obj


def traducir(obj, omitir=()):
    """Traduce los textos de `obj` al idioma actual (español: sin cambios).

    `omitir`: nombres de clave de diccionario cuyo contenido NO se traduce
    (valores internos, p. ej. los nombres de planeta que usa el motor).
    """
    idioma = idioma_actual()
    if idioma == "es":
        return obj
    m = _mapa(idioma)
    return _tr(obj, m, frozenset(omitir)) if m else obj


# Nombres de cuerpos del Sistema Solar. El nombre en español es el ID que usa el
# motor (database.PLANETAS, Horizons); esto solo cambia la ETIQUETA visible.
_CUERPOS_EN = {
    "Sol": "Sun", "Mercurio": "Mercury", "Venus": "Venus", "Tierra": "Earth",
    "Marte": "Mars", "Jupiter": "Jupiter", "Júpiter": "Jupiter", "Saturno": "Saturn",
    "Urano": "Uranus", "Neptuno": "Neptune", "Luna": "Moon",
    "Próxima_Centauri": "Proxima_Centauri",
}


def nombre_cuerpo(nombre):
    """Etiqueta visible de un cuerpo (úsese como format_func). ES: sin cambios."""
    if idioma_actual() == "es":
        return nombre
    return _CUERPOS_EN.get(nombre, nombre)


_ES_MOTOR = {}


def tm(clave, **kwargs):
    """Mensaje del motor (locales/*/motor.json). Sin streamlit usa el español."""
    if _t is not None:
        return _t(clave, **kwargs)
    if not _ES_MOTOR:
        try:
            with open(Path(__file__).parent / "locales" / "es" / "motor.json", encoding="utf-8") as f:
                _ES_MOTOR.update(json.load(f))
        except (OSError, ValueError):
            pass
    texto = _ES_MOTOR.get(clave, clave)
    try:
        return texto.format(**kwargs) if kwargs else texto
    except (KeyError, IndexError, ValueError):
        return texto


_TIPOS_ID = {"Terrestre": "terrestre", "SuperTierra": "supertierra", "Gigante gaseoso": "gigante",
             "Hot Jupiter": "hot_jupiter", "SubNeptuno": "subneptuno", "Gigante de hielo": "hielo"}


def tipo_visible(tipo):
    """Etiqueta visible del tipo de planeta (claves motor.tipo.*)."""
    if idioma_actual() == "es" or tipo not in _TIPOS_ID:
        return tipo
    return tm(f"motor.tipo.{_TIPOS_ID[tipo]}")


def fuente_orbital_visible(valor):
    """Etiqueta visible de fuente_orbital (real / estimado)."""
    if idioma_actual() == "es":
        return valor
    return _clave_o_valor(f"motor.fuente.{valor}", valor)


def categoria_visible(score):
    """categoria_mhi() en el idioma actual (mismos cortes 80 / 50)."""
    q = "bueno" if score >= 80.0 else ("medio" if score >= 50.0 else "malo")
    return tm(f"motor.cat.{q}")


def _clave_o_valor(clave, valor):
    r = tm(clave)
    return valor if r == clave else r


def sev_visible(sev):
    """Severidad de un evento (critica, alta, ...) en el idioma actual."""
    return _clave_o_valor(f"sev.{sev}", sev)


def nivel_visible(nivel):
    """Nivel de una resonancia (fuerte, moderado, debil) en el idioma actual."""
    return _clave_o_valor(f"motor.f23.nivel.{nivel}", nivel)
