# ===================================================================
# contenido_educativo.py
# Contenido de la sección "📚 Educación", compartido por las 3
# versiones (Open Source, Standard, Pro). Igual que glosario_terminos.py,
# vive como módulo Python (no archivo .txt suelto) para no depender de
# rutas relativas que se rompen dentro de un .exe empaquetado.
#
# FUENTE: plan de estudios propuesto por Roney (09-ago-2026), revisado
# contra el código real antes de publicarlo. Dos correcciones respecto
# a la propuesta original:
#   1. La fórmula del MHI tenía los pesos mal asignados a los pilares
#      (ver MARCO_TEORICO['formula_mhi'] -- corregido contra
#      habitabilidad.py: PESO_ESCUDO=0.40, PESO_CAMPO=0.30,
#      PESO_ORBITA=0.20, PESO_MAREA=0.10).
#   2. Faltaba la salvedad de que la penalización por oblicuidad solo
#      se aplica a los 5 cuerpos con eps_conocido=True -- sin esa nota,
#      un estudiante que simule un exoplaneta sin dato de oblicuidad y
#      no vea la penalización actuar puede pensar que está roto.
# ===================================================================

MARCO_TEORICO = {
    "intro": (
        "MHD-INT es un simulador que modela la evolución temporal de "
        "planetas y estrellas jóvenes, calculando cómo cambian su campo "
        "magnético, su órbita, su rotación y su atmósfera a lo largo de "
        "millones o miles de millones de años. Permite responder "
        "preguntas como \"¿por qué la Tierra es habitable y Marte no?\" "
        "o \"qué pasaría si la Tierra tuviera una luna más grande?\"."
    ),
    "pilares": [
        {
            "nombre": "Campo magnético (B)",
            "basico": "Escudo invisible que protege al planeta de la radiación estelar.",
            "avanzado": "Generado por el movimiento de fluidos conductores en el núcleo (dínamo). Se mide en Gauss (G).",
        },
        {
            "nombre": "Excentricidad (e)",
            "basico": "Qué tan alargada es la órbita del planeta. 0 = círculo, valores más altos = más elíptica.",
            "avanzado": "Desviación de la órbita kepleriana respecto a un círculo perfecto. Afecta la variación de distancia a la estrella y el calor de marea.",
        },
        {
            "nombre": "Oblicuidad (ε)",
            "basico": "Inclinación del eje de rotación del planeta respecto a su órbita.",
            "avanzado": "Ángulo entre el eje de rotación y la perpendicular al plano orbital. Modula las estaciones y el clima a largo plazo.",
        },
        {
            "nombre": "Calor de marea (Q)",
            "basico": "Calor generado dentro del planeta por fricción gravitacional con su estrella o luna.",
            "avanzado": "Disipación de energía mecánica por deformación del cuerpo debido a fuerzas de marea. Crítico para actividad geológica.",
        },
    ],
    "mhi_intro": (
        "El MHI (Índice de Habitabilidad Magnética) es un número de 0 a 100 "
        "que combina 4 componentes para estimar qué tan favorable es el "
        "escudo magnético de un planeta."
    ),
    # CORREGIDO -- pesos verificados contra habitabilidad.py, no contra
    # la propuesta original (que los tenía cruzados).
    "formula_mhi": [
        ("40%", "Escudo", "Fracción del tiempo simulado en que el campo magnético es lo bastante grande frente al planeta (R_m ≥ 5 R_planeta) para desviar el viento estelar."),
        ("30%", "Campo activo", "Fracción del tiempo simulado en que el campo magnético supera un umbral mínimo (B ≥ 0.3 G) — hay campo, no solo escudo geométrico."),
        ("20%", "Estabilidad orbital", "Qué tan cerca de circular se mantiene la órbita (excentricidad baja = puntaje alto)."),
        ("10%", "Calor de marea adecuado", "Ni tan poco que no haya actividad geológica, ni tan alto que sea destructivo (banda tipo Ío)."),
    ],
    "nota_penalizacion_oblicuidad": (
        "⚠️ Hay una quinta pieza, la penalización por oblicuidad extrema "
        "(-20 puntos si ε > 60° o ε < 5°), pero **solo se aplica a 5 cuerpos "
        "con oblicuidad real medida**: Tierra, Marte, Júpiter, Urano y "
        "Venus. Para el resto de la base (casi todos los exoplanetas), la "
        "oblicuidad es un dato desconocido, no un dato bajo — penalizar "
        "por un valor no medido introduciría un sesgo sin base física. Si "
        "simulás un exoplaneta y no ves esta penalización actuar, es "
        "esperado, no un error."
    ),
}


# ---------------------------------------------------------------------
# Glosario ilustrado de astrofísica general (con analogías). Distinto
# de glosario_terminos.py -- ese cubre las VARIABLES propias de
# MHD-INT (a_ua, B_gauss, MHI...); este cubre vocabulario general de
# astrofísica que aparece en el marco teórico y los ejercicios.
# ---------------------------------------------------------------------
GLOSARIO_ILUSTRADO = [
    ("Acreción", "Proceso por el cual la gravedad atrae materia hacia un cuerpo celeste.", "Como una aspiradora que recoge polvo."),
    ("Corrotación", "Cuando la velocidad de rotación de un planeta iguala a la de su órbita.", "Un carrusel que gira a la misma velocidad que el caballito."),
    ("Dínamo", "Mecanismo que genera campo magnético por convección en el núcleo de un planeta.", "Una dínamo de bicicleta que genera electricidad al girar."),
    ("Fotoevaporación", "Pérdida de atmósfera por radiación estelar intensa.", "La estrella \"soplando\" la atmósfera del planeta."),
    ("Marea", "Fuerza deformante que un cuerpo ejerce sobre otro por gravedad diferencial.", "Cuando la Luna \"estira\" a la Tierra."),
    ("Precesión", "Movimiento lento del eje de rotación de un planeta, como un trompo que se tambalea.", "El bamboleo de un trompo antes de caer."),
    ("Radiación XUV", "Radiación de alta energía (rayos X y ultravioleta) emitida por estrellas jóvenes.", "La \"luz fuerte\" de una estrella recién nacida."),
    ("Radio de truncamiento (R_t)", "Distancia a la que el campo magnético de una estrella joven corta su disco protoplanetario.", "La frontera donde el \"escudo\" de la estrella detiene el disco."),
    ("Trazabilidad (Tier)", "Clasificación de la calidad y origen de los datos de un planeta: A = real, B = estimado, C = pendiente.", "Una etiqueta de calidad, como en los alimentos."),
    ("Viento estelar", "Flujo de partículas cargadas que una estrella emite continuamente al espacio.", "El \"aliento\" de la estrella."),
]


# ---------------------------------------------------------------------
# Ejercicios por nivel. Cada uno indica si es simulable con el motor
# actual de MHD-INT (simulable=True) o si es una pregunta conceptual
# que el software NO puede responder hoy porque requiere física que no
# está implementada (simulable=False, con nota explicando qué falta).
# Esto es a propósito: mejor marcar el límite real que prometer un
# resultado que el motor no puede dar (mismo criterio que ya se usó en
# modificador_sistemas.py).
# ---------------------------------------------------------------------
EJERCICIOS_SECUNDARIA = [
    dict(titulo="El Escudo Invisible (Campo Magnético)", objetivo="Entender que el campo magnético protege la atmósfera.",
         analogia="Un castillo con muralla (campo magnético) y foso (atmósfera). Sin muralla, los invasores (viento estelar) llegan al castillo.",
         experimento="Simular la Tierra con y sin campo magnético.", prediccion="¿Qué pasará con la atmósfera si el campo es 0?",
         actividad="Dibujá un castillo con y sin muralla. Explicá qué pasa cuando los invasores llegan.", simulable=True),
    dict(titulo="La Pista de Baile (Excentricidad Orbital)", objetivo="Relacionar la excentricidad con la estabilidad climática.",
         analogia="Órbita circular = bailarín que gira en un punto fijo. Órbita excéntrica = bailarín que se mueve en zigzag.",
         experimento="Simular la Tierra con excentricidad 0.01 y con 0.6.", prediccion="¿Cuál tendrá clima más estable?",
         actividad="Dibujá dos órbitas, una circular y una alargada. Explicá cómo afecta al clima de cada una.", simulable=True),
    dict(titulo="El Trompo (Oblicuidad)", objetivo="Comprender cómo la oblicuidad genera estaciones.",
         analogia="Un trompo que gira derecho (0°) no tiene estaciones. Uno inclinado (23.5°) sí.",
         experimento="Simular la Tierra con oblicuidad 0°, 23.5° y 90°.", prediccion="¿Cuál tendrá estaciones suaves y cuál extremas?",
         actividad="Explicá por qué la Tierra tiene estaciones y Urano tiene estaciones extremas.", simulable=True),
    dict(titulo="La Licuadora (Calor de Marea)", objetivo="Relacionar el calor de marea con la actividad geológica.",
         analogia="Al amasar plastilina, se calienta. Lo mismo pasa con planetas estrujados por gravedad.",
         experimento="Simular la Tierra con una luna masiva y sin luna.", prediccion="¿Cuál tendrá más actividad volcánica?",
         actividad="Explicá por qué Ío (luna de Júpiter) es tan volcánica.", simulable=True),
    dict(titulo="El Examen de Admisión (MHI)", objetivo="Entender qué es el MHI y cómo se calcula, de forma cualitativa.",
         analogia="El MHI es como un examen con 4 materias (escudo, campo, órbita, marea). Cada una suma puntos.",
         experimento="Simular la Tierra, Marte y Venus y comparar su MHI.", prediccion="¿Cuál tendrá el MHI más alto y por qué?",
         actividad="Ordená esos 3 planetas de mayor a menor MHI antes de simular, y compará con el resultado.", simulable=True),
    dict(titulo="Diseñá tu Tierra (Modo Sintético)", objetivo="Aplicar los conceptos para diseñar un planeta habitable.",
         analogia="Sos un arquitecto de planetas: elegís tamaño, órbita y campo magnético.",
         experimento="Diseñar un planeta con MHI > 80 en el Modo Sintético.", prediccion="¿Qué parámetros necesitás para que sea habitable?",
         actividad="Dibujá tu planeta y escribí sus características.", simulable=True),
    dict(titulo="Marte, el Planeta que Pudo Ser", objetivo="Entender por qué Marte perdió su atmósfera.",
         analogia="Marte es un castillo cuya muralla se derrumbó (perdió su campo magnético).",
         experimento="Simular Marte con y sin campo magnético.", prediccion="¿Qué pasó con la atmósfera de Marte?",
         actividad="Escribí un breve relato sobre la \"muerte\" de Marte.", simulable=True),
    dict(titulo="El Júpiter Caliente", objetivo="Ver cómo un planeta gigante muy cerca de su estrella afecta al sistema.",
         analogia="Un Júpiter caliente es como un elefante en una tienda de campaña.",
         experimento="Simular un Júpiter caliente a 0.05 UA con el Modo Sintético.", prediccion="¿Cómo cambia su propio campo/órbita a esa distancia?",
         actividad="Explicá por qué los Júpiter calientes son \"problemáticos\" para sistemas planetarios en general.",
         simulable=False, nota_no_simulable=(
             "MHD-INT simula cada planeta de forma INDEPENDIENTE, sin gravedad "
             "planeta-planeta. Podés simular el Júpiter caliente en sí mismo "
             "(su propio campo/órbita), pero el software no puede mostrar su "
             "efecto sobre otros planetas del sistema — esa es una pregunta "
             "conceptual para discutir en clase, no un experimento que el "
             "simulador pueda correr hoy.")),
    dict(titulo="La Luna, Estabilizadora del Clima", objetivo="Ver cómo la Luna estabiliza la oblicuidad de la Tierra.",
         analogia="La Luna es un ancla que evita que el barco (la Tierra) se tambalee demasiado.",
         experimento="Simular la Tierra con y sin Luna.", prediccion="¿Cómo cambia la oblicuidad sin Luna?",
         actividad="Explicá por qué la Luna es importante para la vida en la Tierra.", simulable=True),
    dict(titulo="El Futuro de la Tierra", objetivo="Ver cómo evolucionará la Tierra en los próximos 5.000 millones de años.",
         analogia="Un viaje en el tiempo para ver el \"fin\" de la Tierra.",
         experimento="Simular la Tierra durante 10 Gyr.", prediccion="¿Qué pasará con el campo magnético, la órbita y la atmósfera?",
         actividad="Escribí un breve ensayo sobre el destino final de la Tierra.", simulable=True),
]

EJERCICIOS_UNIVERSIDAD = [
    dict(titulo="Física del Campo Magnético (Número de Elsasser)", concepto="El campo magnético depende de la rotación y el núcleo conductor: E_p = B² / (μ₀ρΩη).",
         practica="Calcular E_p para la Tierra (B=0.31 G, Ω=7.29e-5 rad/s, ρ=10000 kg/m³, η=1.2 m²/s).",
         simulacion="Verificar que la Tierra tiene E_p ≈ 1 (umbral de dínamo activo).", simulable=True),
    dict(titulo="Mecánica Orbital (Excentricidad y Calor de Marea)", concepto="La excentricidad modula el calor de marea: Q ∝ e².",
         practica="Calcular cuánto aumenta Q si la excentricidad se duplica.",
         simulacion="Simular un planeta con e=0.01 y e=0.5, comparar Q_final.", simulable=True),
    dict(titulo="Oblicuidad y Clima", concepto="La oblicuidad evoluciona por mareas: dε/dt = -K sin(2ε). Equilibrio en ε=0° o ε=90°.",
         practica="Calcular el tiempo de amortiguamiento para la Tierra (K ≈ 1e-7 rad/año).",
         simulacion="Simular la Tierra y ver cómo evoluciona ε en 5 Gyr.", simulable=True),
    dict(titulo="Calor de Marea y Actividad Geológica", concepto="El calor de marea es la principal fuente de energía interna en lunas como Ío.",
         practica="Calcular el calor de marea de una luna de 0.5 M⊕ a 0.01 UA.",
         simulacion="Simular ese sistema en el Modo Sintético y comparar Q_tidal.", simulable=True),
    dict(titulo="El MHI como Herramienta de Clasificación", concepto="El MHI combina 4 componentes ponderados (ver Marco Teórico para los pesos correctos).",
         practica="Calcular manualmente el MHI de la Tierra con los pesos reales y comparar con el resultado del simulador.",
         simulacion="Simular la Tierra y verificar el MHI.", simulable=True),
    dict(titulo="Formación Estelar y Discos Protoplanetarios", concepto="Las estrellas jóvenes están rodeadas de discos que las frenan y pueden desalinear su eje.",
         practica="Calcular el radio de truncamiento (R_t) para una estrella T Tauri (DO Tau).",
         simulacion="Usar el módulo Disco Protoplanetario con DO Tau y comparar r_in.", simulable=True),
    dict(titulo="Efecto de la Luna en la Oblicuidad", concepto="La Luna estabiliza la oblicuidad de la Tierra frente a variación caótica.",
         practica="Discutir cualitativamente el mecanismo del torque lunar sobre la oblicuidad.",
         simulacion="Simular la Tierra sin Luna y comparar la evolución de ε.", simulable=True),
    dict(titulo="Migración Planetaria", concepto="Un planeta puede migrar por interacción de marea con su estrella (Q efectivo).",
         practica="Calcular el orden de magnitud del tiempo de migración para un planeta cercano.",
         simulacion="Simular un planeta con semieje pequeño y ver su migración orbital en el tiempo.", simulable=True),
    dict(titulo="Atmósferas y Fotoevaporación", concepto="La atmósfera puede perderse por radiación estelar (fotoevaporación / escape).",
         practica="Comparar cualitativamente la exposición de Tierra vs. Marte a esa pérdida.",
         simulacion="Simular la pérdida de atmósfera de Marte y comparar con la Tierra.", simulable=True),
    dict(titulo="Validación del Modelo con Datos Reales", concepto="El modelo debe reproducir datos observados del Sistema Solar dentro de una tolerancia.",
         practica="Revisar qué cuerpos están en validacion.py y con qué tolerancia.",
         simulacion="Ejecutar el modo Validación y analizar los errores reportados para cada cuerpo.", simulable=True),
]

EJERCICIOS_CIENTIFICO = [
    dict(titulo="Calibración del Modelo de Dínamo", pregunta="¿Cómo afecta la difusividad magnética (η) al campo generado por el dínamo?",
         metodo="Barrido paramétrico de η (0.5–3.0) vía Sensibilidad, midiendo B_final.",
         analisis="Encontrar la relación η–B y compararla con la ley de Christensen & Aubert.", simulable=True),
    dict(titulo="Influencia de la Oblicuidad en la Habitabilidad", pregunta="¿Cuál es la relación entre oblicuidad y MHI en planetas terrestres?",
         metodo="Simular planetas con ε de 0° a 90° (cada 10°, Modo Sintético) y medir MHI.",
         analisis="Encontrar el rango de ε que maximiza el MHI.", simulable=True),
    dict(titulo="Migración de Planetas en Discos Inclinados", pregunta="¿Cómo afecta la oblicuidad de la estrella a la migración de un planeta?",
         metodo="Simular un planeta migrando y, por separado, la oblicuidad estelar en Disco Protoplanetario.",
         analisis="Discutir la conexión conceptual entre ambos resultados.",
         simulable=False, nota_no_simulable=(
             "El módulo Disco Protoplanetario modela la alineación spin-disco de "
             "la ESTRELLA; no está acoplado al cálculo de migración orbital de un "
             "planeta. Hoy se pueden correr ambos por separado y comparar, pero "
             "no existe una simulación conjunta disco-inclinado→migración.")),
    dict(titulo="Formación de Planetas en Discos con Warp", pregunta="¿Pueden formarse planetas en discos deformados (warp)?",
         metodo="—", analisis="—",
         simulable=False, nota_no_simulable=(
             "MHD-INT no tiene un módulo de formación planetaria (acreción de "
             "núcleos, crecimiento de embriones). El módulo de disco modela "
             "solo la dinámica de alineación spin-disco de la estrella, no la "
             "formación de planetas dentro de él. Pregunta de investigación "
             "legítima, pero fuera del alcance actual del software.")),
    dict(titulo="Efecto de la Luna en la Oblicuidad a Largo Plazo", pregunta="¿Cuánto tarda una luna en estabilizar la oblicuidad de un planeta?",
         metodo="Simular la evolución de ε para distintas masas de luna (Modo Sintético / Modificador de Sistemas).",
         analisis="Encontrar la masa aproximada de luna que estabiliza ε en menos de 1 Gyr.", simulable=True),
    dict(titulo="La Zona Habitable Dinámica", pregunta="¿Cómo cambia la habitabilidad si la oblicuidad de la estrella varía?",
         metodo="—", analisis="—",
         simulable=False, nota_no_simulable=(
             "MHD-INT no calcula zona habitable radiativa (flujo estelar vs. "
             "distancia) como función de propiedades de la estrella distintas de "
             "luminosidad; no modela el acoplamiento oblicuidad-estelar → zona "
             "habitable. Pregunta abierta para investigación futura.")),
    dict(titulo="Atmósferas de Planetas con Alta Excentricidad", pregunta="¿Pueden los planetas con alta excentricidad retener atmósferas?",
         metodo="Simular planetas con e=0.5 y e=0.9 (Modo Sintético), medir pérdida atmosférica.",
         analisis="Relacionar e con el tiempo de retención atmosférica.", simulable=True),
    dict(titulo="El Problema del Paso Fijo en el Integrador", pregunta="¿Cómo afecta el paso de tiempo fijo (dt) a la precisión?",
         metodo="Simular el mismo sistema con dt=1000, 5000, 10000 años.",
         analisis="Medir la divergencia de resultados entre pasos.", simulable=True),
    dict(titulo="Validación del Modelo de Disco con DO Tau", pregunta="¿El modelo de disco reproduce el radio de truncamiento de DO Tau?",
         metodo="Simular DO Tau en el módulo Disco Protoplanetario y comparar r_in con la literatura (Bessolaz et al. 2008).",
         analisis="Calcular el error porcentual — el módulo ya documenta ~13-15% de error esperado.", simulable=True),
    dict(titulo="Priorización de Candidatos para Misiones", pregunta="¿Qué sistemas del catálogo son mejores candidatos para observación futura?",
         metodo="Simular un subconjunto grande del catálogo (300+ planetas) y clasificar por MHI y Tier de confianza.",
         analisis="Producir una lista priorizada, filtrando por Tier A/B para confiabilidad de datos.", simulable=True),
]

TROUBLESHOOTING = [
    dict(problema="Simulás un planeta con B=0.5 G y su atmósfera se escapa en 100 Myr, cuando esperabas 5 Gyr.",
         diagnostico="Mirá la excentricidad y la distancia a la estrella, no solo el campo.",
         causa="El planeta está muy cerca de la estrella o tiene excentricidad muy alta.",
         solucion="Alejar la órbita o reducir la excentricidad."),
    dict(problema="Simulás un planeta con MHI de 35 cuando esperabas más de 70.",
         diagnostico="¿Qué componente del MHI está fallando — escudo, campo, órbita o marea?",
         causa="El campo magnético es débil o la excentricidad es alta.",
         solucion="Aumentar el campo (masa/rotación) o reducir la excentricidad."),
    dict(problema="El planeta se estrella contra la estrella antes de terminar la simulación.",
         diagnostico="¿La migración orbital es demasiado rápida para ese sistema?",
         causa="Órbita muy cercana o estrella muy masiva.",
         solucion="Alejar la órbita inicial o reducir la masa de la estrella."),
    dict(problema="Simulaste un planeta con luna, pero al final a_luna_final_ua = 0.",
         diagnostico="¿La luna se estrelló contra el planeta o escapó?",
         causa="La luna partió demasiado cerca, o el planeta rota muy rápido.",
         solucion="Aumentar la distancia inicial de la luna o reducir la rotación del planeta."),
    dict(problema="Hacés clic en \"Generar video\" y no pasa nada o sale un error.",
         diagnostico="¿Falta ffmpeg en el sistema?",
         causa="ffmpeg no está instalado.",
         solucion="Instalar ffmpeg, o dejar que el programa use el fallback automático a GIF."),
    dict(problema="El donut del MHI muestra un total que no coincide con la suma de sus componentes.",
         diagnostico="¿Hay una penalización por oblicuidad que no se ve en el gráfico?",
         causa="La penalización por oblicuidad extrema (ver Marco Teórico) se resta del total pero no aparece como sector del donut.",
         solucion="Revisar el campo penalizacion_obl_pts en los resultados detallados."),
    dict(problema="No encontrás el planeta que querés simular en la lista.",
         diagnostico="¿Es un planeta nuevo que todavía no está en la base de datos?",
         causa="El planeta no está cargado en database.py.",
         solucion="Usar el Modo Sintético para crearlo manualmente con sus parámetros."),
    dict(problema="Activaste \"marea lunar\" en el Modo Sintético pero no aparece ninguna luna en los resultados.",
         diagnostico="¿Los parámetros de masa/distancia de la luna son válidos?",
         causa="El toggle de añadir luna está desactivado, o los valores son inválidos (cero o negativos).",
         solucion="Activar el toggle y dar valores positivos a masa y distancia."),
    dict(problema="El PDF del reporte no se descarga.",
         diagnostico="¿Falla la generación de la figura o falta reportlab?",
         causa="Dependencia faltante o error al generar el gráfico interno.",
         solucion="Verificar que reportlab esté instalado; revisar el mensaje de error si aparece."),
    dict(problema="Una simulación de 5 Gyr tarda varios minutos en completarse.",
         diagnostico="¿El paso de tiempo (dt) es muy chico para el rango simulado?",
         causa="dt muy pequeño (ej. 1000 años) para 5 Gyr de simulación total.",
         solucion="Aumentar dt a 10.000 años o más, si la precisión requerida lo permite."),
]
