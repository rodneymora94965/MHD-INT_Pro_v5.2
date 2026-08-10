# ===================================================================
# glosario_terminos.py
# Diccionario de términos de MHD-INT, compartido por las 3 versiones
# (Open Source, Standard, Pro). Un solo lugar para mantener las
# definiciones -- evita que las 3 UIs se desincronicen con el tiempo.
# ===================================================================

GLOSARIO_TERMINOS = {
    "Variables de la simulación": {
        "a_ua": (
            "Distancia orbital (a)",
            "Distancia promedio entre el planeta y su estrella, en Unidades "
            "Astronómicas (1 UA = distancia Tierra-Sol). Cambia con el tiempo "
            "por la migración de marea.",
        ),
        "B_gauss": (
            "Campo magnético (B)",
            "Intensidad del campo magnético planetario en Gauss. Es el que "
            "protege la atmósfera del viento estelar (magnetosfera).",
        ),
        "w_p": (
            "Velocidad de rotación (ω)",
            "Qué tan rápido gira el planeta sobre su propio eje, en radianes "
            "por segundo. Va cambiando por las mareas estelares y lunares.",
        ),
        "e": (
            "Excentricidad (e)",
            "Qué tan ovalada es la órbita. 0 = círculo perfecto; valores más "
            "altos = órbita más elíptica. Afecta el calentamiento por marea.",
        ),
        "T_cmb_K": (
            "Temperatura núcleo-manto (T_cmb)",
            "Temperatura en el límite entre el núcleo y el manto del planeta, "
            "en Kelvin. Es uno de los motores del dínamo térmico.",
        ),
        "B_gen_gauss": (
            "Campo generado por dínamo",
            "Parte del campo magnético que se genera activamente por "
            "convección en el núcleo (efecto dínamo), en vez de solo decaer.",
        ),
        "Rm": (
            "Número de Reynolds magnético (Rm)",
            "Mide si el núcleo del planeta puede sostener un dínamo activo. "
            "Rm > 40 se considera el umbral para generación de campo real.",
        ),
        "M_atm_kg": (
            "Masa atmosférica",
            "Cuánta atmósfera le queda al planeta, en kilogramos. Baja con el "
            "tiempo por erosión del viento estelar si el campo magnético es débil.",
        ),
        "eps_deg": (
            "Oblicuidad (ε)",
            "Inclinación del eje de rotación del planeta respecto a su órbita, "
            "en grados. La Tierra tiene ~23.4°.",
        ),
    },
    "Habitabilidad magnética (MHI)": {
        "MHI": (
            "Índice de Habitabilidad Magnética (MHI)",
            "Puntaje de 0 a 100 que combina protección magnética, órbita "
            "estable, campo activo y calentamiento por marea moderado, para "
            "estimar qué tan favorable es el escudo magnético de un planeta.",
        ),
        "mhi_bruto": (
            "MHI bruto",
            "Suma de los 4 componentes del MHI (escudo, campo, órbita, marea) "
            "antes de aplicar la penalización por oblicuidad extrema.",
        ),
        "penalizacion_obl_pts": (
            "Penalización por oblicuidad",
            "Puntos que se restan al MHI bruto cuando la inclinación del eje "
            "del planeta es extrema, porque desestabiliza el clima.",
        ),
        "categoria_mhi": (
            "Categoría de habitabilidad",
            "Lectura en palabras del puntaje MHI: 80+ Alta habitabilidad "
            "magnética · 50-79 Habitabilidad moderada / límite · <50 Estéril "
            "/ atmósfera expuesta.",
        ),
    },
    "Calidad de los datos": {
        "SIN_DATO": (
            "SIN_DATO",
            "Marca explícita en la base de datos: no existe una medición real "
            "publicada para ese campo. MHD-INT nunca inventa un valor "
            "\"razonable\" en su lugar -- lo deja marcado así.",
        ),
        "termico_estimado": (
            "Térmico estimado",
            "Bandera que indica que los parámetros térmicos internos del "
            "planeta (núcleo, manto) no vienen de una fuente real, sino que "
            "se estimaron por categoría de planeta.",
        ),
        "eps_conocido": (
            "Oblicuidad conocida",
            "Bandera que distingue una oblicuidad con respaldo observacional "
            "real de un valor interno del integrador sin ese respaldo. Cuando "
            "es falsa, MHD-INT lo aclara en vez de mostrar un dato como si "
            "fuera medido.",
        ),
        "fuente_orbital": (
            "Fuente orbital",
            "Indica si los datos orbitales de un planeta son \"real\" "
            "(medidos), \"estimado\" o \"revisar_pendiente\". Es la base del "
            "sistema de Tiers de confianza.",
        ),
        "Tier A/B/C": (
            "Tiers de confianza (A/B/C)",
            "Clasificación de cada planeta según qué tan respaldados están "
            "sus datos: Tier A = datos orbitales y térmicos reales; Tier B = "
            "datos orbitales reales pero térmica estimada; Tier C = datos a "
            "revisar.",
        ),
    },
}


def buscar_termino(clave: str):
    """Devuelve (título, definición) para una clave técnica (ej. 'B_gauss'),
    o None si no está en el glosario. Útil para mostrar un tooltip corto
    junto a una variable en vez de solo su etiqueta."""
    for _seccion, terminos in GLOSARIO_TERMINOS.items():
        if clave in terminos:
            return terminos[clave]
    return None
