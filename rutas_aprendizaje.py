# rutas_aprendizaje.py
# MHD-INT — Ruta de Aprendizaje: secuencia curada sobre contenido ya existente
# Licencia AGPL-3.0. Lógica pura, sin streamlit.
#
# NO agrega contenido nuevo -- cada etapa apunta a un tema real de
# MARCO_TEORICO y a un ejercicio real de EJERCICIOS_* (por título exacto,
# validado contra contenido_educativo.py). Si algún título cambia ahí,
# esto se rompe a propósito (ValueError en validar_rutas()) en vez de
# quedar mostrando una referencia rota en silencio.
#
# Cada etapa: leer (sección, título exacto en MARCO_TEORICO) + hacer
# (instrucción concreta en la app, texto libre) + ejercicio (título
# exacto en la lista de ejercicios del mismo nivel).

RUTAS = {
    "Secundaria": [
        dict(
            leer=("introduccion_astrofisica", "Gravedad y órbitas: las leyes de Kepler y Newton"),
            hacer="Abrí el modo Simulación, elegí la Tierra y corré la simulación con el tiempo al máximo (10 Gyr).",
            ejercicio="El Futuro de la Tierra",
        ),
        dict(
            leer=("pilares", "Campo magnético (B)"),
            hacer="En Simulación, corré la Tierra y después Marte con los mismos parámetros. Compará el campo magnético final de cada uno.",
            ejercicio="El Escudo Invisible (Campo Magnético)",
        ),
        dict(
            leer=("pilares", "Excentricidad (e)"),
            hacer="En modo Sintético, dejá todo por defecto y después subí bastante el slider de excentricidad inicial. Compará los 2 resultados.",
            ejercicio="La Pista de Baile (Excentricidad Orbital)",
        ),
        dict(
            leer=("introduccion_astrofisica", "Campos magnéticos planetarios: el dínamo"),
            hacer="En modo Sintético, diseñá un planeta propio desde cero (no uses ningún preset) y simulalo.",
            ejercicio="Diseñá tu Tierra (Modo Sintético)",
        ),
        dict(
            leer=("temas_avanzados", "Alineaciones planetarias"),
            hacer="En 🪐 Catálogo de Sistemas, elegí el Sol, activá condiciones iniciales reales (Horizons) y detectá la alineación aparente.",
            ejercicio="La Alineación de los Planetas",
        ),
    ],
    "Universidad": [
        dict(
            leer=("pilares", "Campo magnético (B)"),
            hacer="En Simulación, activá el 🔥 Modelo térmico para la Tierra y revisá el número de Elsasser en los resultados.",
            ejercicio="Física del Campo Magnético (Número de Elsasser)",
        ),
        dict(
            leer=("temas_avanzados", "N-cuerpos"),
            hacer="En 🪐 N-cuerpos (Beta), simulá TRAPPIST-1 completo (7 planetas) y mirá el error de energía y momento angular.",
            ejercicio="Resonancias en TRAPPIST-1",
        ),
        dict(
            leer=("temas_avanzados", "Discos protoplanetarios y oblicuidad estelar"),
            hacer="En 🌌 Disco Protoplanetario (Beta), probá distintos valores de ζ̃/λ y observá el régimen de alineación.",
            ejercicio="Formación Estelar y Discos Protoplanetarios",
        ),
        dict(
            leer=("temas_avanzados", "Condiciones iniciales reales y efemérides"),
            hacer="En 🪐 Catálogo de Sistemas, elegí el Sol con CI reales de Horizons y simulá el sistema con N-cuerpos.",
            ejercicio="N-cuerpos y la Alineación del Sistema Solar",
        ),
        dict(
            leer=("introduccion_astrofisica", "La zona habitable, y por qué no alcanza con eso"),
            hacer="Corré el modo Validación y revisá contra qué cuerpos reales se calibra el motor, y con qué tolerancia.",
            ejercicio="Validación del Modelo con Datos Reales",
        ),
    ],
    "Científico": [
        dict(
            leer=("temas_avanzados", "Torque atmosférico (rotación retrógrada de Venus)"),
            hacer="Simulá Venus con el flag de torque atmosférico desactivado y después activado (Fases 1/2/3), comparando el signo de w_final.",
            ejercicio="Torque Atmosférico vs. Gravitatorio en Venus",
        ),
        dict(
            leer=("temas_avanzados", "Resonancias orbitales"),
            hacer="En 🪐 Catálogo de Sistemas, corré el detector de resonancias sobre TRAPPIST-1, Kepler-90 y el Sistema Solar.",
            ejercicio="Validación de Resonancias en Sistemas Reales",
        ),
        dict(
            leer=("pilares", "Campo magnético (B)"),
            hacer="En Sensibilidad, variá la difusividad del núcleo y observá cómo cambia el campo magnético final.",
            ejercicio="Calibración del Modelo de Dínamo",
        ),
        dict(
            leer=("temas_avanzados", "Discos protoplanetarios y oblicuidad estelar"),
            hacer="En 🌌 Disco Protoplanetario (Beta), reproducí el caso de DO Tau y compará el radio de truncamiento contra el valor publicado.",
            ejercicio="Validación del Modelo de Disco con DO Tau",
        ),
        dict(
            leer=("temas_avanzados", "N-cuerpos"),
            hacer="En 🪐 N-cuerpos (Beta), simulá TRAPPIST-1 con un paso de tiempo fijo grande y después con dt_sugerido(). Compará el error de energía.",
            ejercicio="El Problema del Paso Fijo en el Integrador",
        ),
    ],
}


def _obtener_tema(marco_teorico: dict, seccion: str, titulo: str) -> dict:
    lista = marco_teorico[seccion]
    clave_titulo = "titulo" if seccion == "introduccion_astrofisica" else "nombre"
    for item in lista:
        if item[clave_titulo] == titulo:
            return item
    raise ValueError(f"No se encontró el tema '{titulo}' en MARCO_TEORICO['{seccion}'].")


def _obtener_ejercicio(lista_ejercicios: list, titulo: str) -> dict:
    for ej in lista_ejercicios:
        if ej["titulo"] == titulo:
            return ej
    raise ValueError(f"No se encontró el ejercicio '{titulo}'.")


def validar_rutas(marco_teorico: dict, ejercicios_por_nivel: dict) -> None:
    """
    Confirma que TODAS las referencias (leer/ejercicio) de RUTAS
    apuntan a contenido real que existe hoy en contenido_educativo.py.
    Se llama una vez al importar el módulo de UI -- si algo no calza
    (por ejemplo, alguien renombró un ejercicio), esto tira ValueError
    en vez de dejar una referencia rota mostrándose en silencio.
    """
    for nivel, etapas in RUTAS.items():
        ejercicios = ejercicios_por_nivel[nivel]
        for etapa in etapas:
            seccion, titulo_tema = etapa["leer"]
            _obtener_tema(marco_teorico, seccion, titulo_tema)
            _obtener_ejercicio(ejercicios, etapa["ejercicio"])


def obtener_etapas_resueltas(nivel: str, marco_teorico: dict, ejercicios_por_nivel: dict) -> list:
    """Devuelve RUTAS[nivel] con cada etapa enriquecida con el contenido
    real (texto del tema, dict completo del ejercicio) ya resuelto."""
    ejercicios = ejercicios_por_nivel[nivel]
    resultado = []
    for etapa in RUTAS[nivel]:
        seccion, titulo_tema = etapa["leer"]
        tema = _obtener_tema(marco_teorico, seccion, titulo_tema)
        ejercicio = _obtener_ejercicio(ejercicios, etapa["ejercicio"])
        resultado.append({**etapa, "tema_resuelto": tema, "ejercicio_resuelto": ejercicio})
    return resultado
