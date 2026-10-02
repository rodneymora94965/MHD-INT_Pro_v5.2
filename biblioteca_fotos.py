# biblioteca_fotos.py
# MHD-INT — Biblioteca de fotos astronómicas curada
# Licencia AGPL-3.0. Lógica pura, sin streamlit.
#
# Reemplaza la idea original de conectar la API APOD de la NASA en vivo:
# esa opción tenía un problema real para un producto vendido -- DEMO_KEY
# comparte límite de uso con todo el mundo, y depende de que la NASA
# esté arriba ese día. Esta biblioteca es estática: cada foto tiene una
# URL real y verificada de Wikimedia Commons (formato Special:FilePath,
# el mecanismo oficial y estable de Commons para enlazar archivos desde
# afuera -- no rutas armadas a mano), y el navegador la carga directo
# del servidor de Wikimedia, no del backend de MHD-INT.
#
# Cada entrada trae una conexión educativa real (a un tema de
# MARCO_TEORICO que YA existe) -- validado en el import, mismo patrón
# que rutas_aprendizaje.py: si la referencia no existe, tira ValueError
# en vez de mostrar un enlace roto en silencio.

_COMMONS_BASE = "https://commons.wikimedia.org/wiki/Special:FilePath/"


def _url(nombre_archivo_commons: str) -> str:
    return _COMMONS_BASE + nombre_archivo_commons.replace(" ", "_")


FOTOS = [
    dict(
        nombre="El Sol", categoria="Estrella",
        url=_url("The Sun by the Atmospheric Imaging Assembly of NASA's Solar Dynamics Observatory - 20100819.jpg"),
        fuente="NASA/SDO (Solar Dynamics Observatory), vía Wikimedia Commons -- imagen destacada",
        descripcion=(
            "Nuestra estrella, fotografiada en luz ultravioleta extrema por el "
            "Solar Dynamics Observatory. Lo que se ve no es la superficie visible "
            "sino la corona, la atmósfera exterior del Sol, calentada a millones "
            "de grados por procesos magnéticos que todavía no se entienden del "
            "todo. El viento solar (el que MHD-INT modela con datos reales de "
            "NOAA) sale precisamente de esta región."
        ),
        conexion=("introduccion_astrofisica", "Estrellas: qué son y cómo cambian con el tiempo"),
    ),
    dict(
        nombre="Mercurio", categoria="Planeta",
        url=_url("Mercury in color - Prockter07.jpg"),
        fuente="NASA/JHUAPL (misión MESSENGER), vía Wikimedia Commons",
        descripcion=(
            "El planeta más cercano al Sol y el más pequeño del Sistema Solar. "
            "Pese a su tamaño, tiene un campo magnético global débil pero real -- "
            "algo que sorprendió a los científicos, porque se esperaba que un "
            "núcleo tan chico se hubiera enfriado y solidificado hace mucho. "
            "Prácticamente no tiene atmósfera que proteger."
        ),
        conexion=("pilares", "Campo magnético (B)"),
    ),
    dict(
        nombre="Venus", categoria="Planeta",
        url=_url("Venus globe.jpg"),
        fuente="NASA/JPL (mosaico radar Magellan + Pioneer Venus + Venera 13/14), vía Wikimedia Commons -- imagen destacada",
        descripcion=(
            "Venus está permanentemente cubierto de nubes de ácido sulfúrico -- "
            "esta imagen es un mosaico de radar, no luz visible, porque así es "
            "la única forma de ver su superficie real. Gira al revés que casi "
            "todos los demás planetas, y muy lento: un día venusino dura más que "
            "su año."
        ),
        conexion=("temas_avanzados", "Torque atmosférico (rotación retrógrada de Venus)"),
    ),
    dict(
        nombre="La Tierra", categoria="Planeta",
        url=_url("The Blue Marble, AS17-148-22727.jpg"),
        fuente="NASA (tripulación del Apollo 17, 1972), vía Wikimedia Commons",
        descripcion=(
            "La icónica \"Canica Azul\", tomada por la tripulación del Apollo 17 "
            "camino a la Luna -- una de las fotos más reproducidas de la "
            "historia. El campo magnético que genera el núcleo de hierro líquido "
            "de la Tierra desvía el viento solar y protege la atmósfera que hace "
            "posible la vida en superficie."
        ),
        conexion=("interpretacion_gravedad_magnetismo", "Tierra — caso de éxito"),
    ),
    dict(
        nombre="La Luna", categoria="Luna",
        url=_url("FullMoon2010.jpg"),
        fuente="Wikimedia Commons -- imagen destacada",
        descripcion=(
            "El único satélite natural de la Tierra, probablemente formado hace "
            "unos 4.500 millones de años por el impacto de un cuerpo del tamaño "
            "de Marte contra la Tierra recién formada. La Luna estabiliza la "
            "inclinación del eje terrestre (la oblicuidad) a largo plazo -- sin "
            "ella, el clima de la Tierra sería mucho más caótico."
        ),
        conexion=("pilares", "Oblicuidad (ε)"),
    ),
    dict(
        nombre="Marte", categoria="Planeta",
        url=_url("Mars Hubble.jpg"),
        fuente="NASA/ESA, Telescopio Espacial Hubble, vía Wikimedia Commons",
        descripcion=(
            "El \"planeta rojo\", fotografiado por el Hubble en uno de sus "
            "acercamientos a la Tierra. Marte tuvo alguna vez un campo "
            "magnético global -- todavía se puede detectar magnetismo fósil en "
            "su corteza -- pero su dínamo se apagó hace miles de millones de "
            "años, y con él se fue buena parte de su atmósfera."
        ),
        conexion=("interpretacion_gravedad_magnetismo", "Marte — caso de pérdida"),
    ),
    dict(
        nombre="Júpiter", categoria="Planeta",
        url=_url("Jupiter.jpg"),
        fuente="NASA/JPL, vía Wikimedia Commons",
        descripcion=(
            "El planeta más grande del Sistema Solar, con el campo magnético "
            "más fuerte de todos los planetas -- generado por un núcleo de "
            "hidrógeno metálico, no hierro líquido como la Tierra. Su gravedad "
            "domina la dinámica de todo el sistema solar exterior, incluidas "
            "las órbitas de asteroides y cometas."
        ),
        conexion=("introduccion_astrofisica", "Campos magnéticos planetarios: el dínamo"),
    ),
    dict(
        nombre="Saturno", categoria="Planeta",
        url=_url("Saturn during Equinox (cropped).jpg"),
        fuente="NASA/JPL/Space Science Institute (misión Cassini), vía Wikimedia Commons",
        descripcion=(
            "Fotografiado por la sonda Cassini durante el equinoccio de Saturno, "
            "cuando la luz rasante hace visibles detalles sutiles en los "
            "anillos. Saturno es tan poco denso que, si existiera una bañera "
            "suficientemente grande, flotaría en agua."
        ),
        conexion=("temas_avanzados", "N-cuerpos"),
    ),
    dict(
        nombre="Urano", categoria="Planeta",
        url=_url("Uranus true colour.jpg"),
        fuente="NASA/JPL (misión Voyager 2), vía Wikimedia Commons",
        descripcion=(
            "Urano gira prácticamente \"de costado\": su eje de rotación está "
            "inclinado unos 98°, casi paralelo al plano de su órbita -- la "
            "oblicuidad más extrema de cualquier planeta del Sistema Solar, "
            "probablemente por una colisión antigua. Es el único planeta que "
            "MHD-INT marca con esa penalización por oblicuidad extrema."
        ),
        conexion=("pilares", "Oblicuidad (ε)"),
    ),
    dict(
        nombre="Neptuno", categoria="Planeta",
        url=_url("Neptune Voyager2 color calibrated.png"),
        fuente="NASA/JPL (misión Voyager 2), vía Wikimedia Commons",
        descripcion=(
            "El planeta más lejano del Sistema Solar, y el único descubierto "
            "por predicción matemática antes que por observación directa -- "
            "los astrónomos notaron que algo perturbaba la órbita de Urano, "
            "calcularon dónde debía estar ese algo, y ahí lo encontraron. Tiene "
            "los vientos más rápidos medidos en cualquier planeta."
        ),
        conexion=("introduccion_astrofisica", "Gravedad y órbitas: las leyes de Kepler y Newton"),
    ),
    dict(
        nombre="La Vía Láctea", categoria="Galaxia",
        url=_url("Milky Way Galaxy.jpg"),
        fuente="Wikimedia Commons -- imagen destacada",
        descripcion=(
            "Nuestra propia galaxia, vista desde dentro -- por eso la vemos como "
            "una franja de luz difusa cruzando el cielo nocturno, no como el "
            "disco espiral completo que sería visible desde afuera. El Sol y "
            "todo el Sistema Solar orbitan el centro galáctico, completando una "
            "vuelta cada ~225 millones de años."
        ),
        conexion=("introduccion_astrofisica", "Formación de sistemas planetarios"),
    ),
    dict(
        nombre="Galaxia de Andrómeda", categoria="Galaxia",
        url=_url("The Andromeda Galaxy M31.jpg"),
        fuente="Wikimedia Commons",
        descripcion=(
            "La galaxia espiral grande más cercana a la Vía Láctea, a unos 2,5 "
            "millones de años luz -- lo bastante cerca para verse a simple "
            "vista en una noche oscura. Andrómeda y la Vía Láctea se están "
            "acercando por gravedad mutua y se espera que colisionen (y se "
            "fusionen) dentro de varios miles de millones de años."
        ),
        conexion=("introduccion_astrofisica", "Estrellas: qué son y cómo cambian con el tiempo"),
    ),
]


def validar_biblioteca(marco_teorico: dict) -> None:
    """Confirma que cada 'conexion' de cada foto apunta a un tema real
    que existe en MARCO_TEORICO -- mismo criterio que
    rutas_aprendizaje.validar_rutas(). Rompe con ValueError si algo no
    calza, en vez de mostrar un enlace educativo roto en silencio."""
    for foto in FOTOS:
        seccion, titulo = foto["conexion"]
        if seccion not in marco_teorico:
            raise ValueError(f"'{foto['nombre']}': la sección '{seccion}' no existe en MARCO_TEORICO.")
        contenido = marco_teorico[seccion]
        if seccion == "interpretacion_gravedad_magnetismo":
            nombres = [c["nombre"] for c in contenido["casos"]]
        elif seccion == "introduccion_astrofisica":
            nombres = [t["titulo"] for t in contenido]
        elif seccion == "pilares":
            nombres = [p["nombre"] for p in contenido]
        elif seccion == "temas_avanzados":
            nombres = [t["nombre"] for t in contenido]
        else:
            raise ValueError(f"'{foto['nombre']}': sección '{seccion}' no soportada por el validador.")
        if titulo not in nombres:
            raise ValueError(f"'{foto['nombre']}': no se encontró '{titulo}' en MARCO_TEORICO['{seccion}'].")
