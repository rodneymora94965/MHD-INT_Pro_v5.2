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
    # ------------------------------------------------------------------
    # Introducción general a la astrofísica -- pensada para alguien sin
    # formación previa, como puerta de entrada antes de los "pilares"
    # específicos de MHD-INT. Cubre lo mínimo indispensable para que el
    # resto del marco teórico tenga sentido: gravedad orbital, qué es
    # una estrella y cómo evoluciona, cómo se forman los sistemas
    # planetarios, y qué es un campo magnético planetario.
    # ------------------------------------------------------------------
    "introduccion_astrofisica": [
        {
            "titulo": "Gravedad y órbitas: las leyes de Kepler y Newton",
            "texto": (
                "Todo lo que orbita algo más masivo (un planeta a su estrella, "
                "una luna a su planeta) sigue, en buena aproximación, una "
                "elipse — no un círculo perfecto. Kepler lo descubrió "
                "observando datos reales de Marte (principios del siglo "
                "XVII); Newton explicó *por qué* un siglo después: la fuerza "
                "de gravedad entre dos cuerpos es proporcional al producto "
                "de sus masas e inversamente proporcional al cuadrado de la "
                "distancia entre ellos (F = G·M·m/r²). De ahí sale la "
                "Tercera Ley de Kepler que usa MHD-INT constantemente: el "
                "cuadrado del período orbital es proporcional al cubo del "
                "semieje mayor de la órbita (P² ∝ a³), y depende de la masa "
                "de la estrella. Es la misma ecuación que usan los módulos "
                "de Efemérides, N-cuerpos y Resonancias para calcular "
                "períodos orbitales."
            ),
        },
        {
            "titulo": "Estrellas: qué son y cómo cambian con el tiempo",
            "texto": (
                "Una estrella es una esfera de gas (sobre todo hidrógeno) lo "
                "bastante masiva para que la gravedad comprima su núcleo "
                "hasta encender fusión nuclear, liberando la energía que "
                "vemos como luz. Las estrellas no son estáticas: nacen "
                "rodeadas de un disco de gas y polvo (el disco "
                "protoplanetario, de donde se forman los planetas), giran "
                "rápido cuando son jóvenes y se van frenando con la edad a "
                "medida que el viento estelar se lleva momento angular "
                "(un proceso llamado frenado magnético). También emiten más "
                "radiación de alta energía (rayos X, ultravioleta) cuando "
                "son jóvenes, lo cual importa mucho para la atmósfera de "
                "los planetas que las orbitan de cerca. MHD-INT modela esta "
                "evolución estelar (rotación, viento, luminosidad) para "
                "saber cómo cambian las condiciones que recibe un planeta a "
                "lo largo de su vida, no solo hoy."
            ),
        },
        {
            "titulo": "Formación de sistemas planetarios",
            "texto": (
                "Los planetas se forman dentro del disco protoplanetario que "
                "rodea a una estrella joven: partículas de polvo chocan y se "
                "pegan, formando cuerpos cada vez más grandes (de polvo a "
                "guijarro, de guijarro a planetesimal, de planetesimal a "
                "planeta), en un proceso que toma unos pocos millones de "
                "años. La posición donde se forma un planeta no es "
                "necesariamente donde termina: los planetas pueden "
                "*migrar*, cambiando su distancia a la estrella por la "
                "interacción gravitacional con el gas del disco (eso es lo "
                "que modela el módulo de Migración de MHD-INT). Cuando "
                "varios planetas migran a velocidades relacionadas, pueden "
                "quedar atrapados en una resonancia orbital — sus períodos "
                "orbitales terminan en una razón de números enteros "
                "pequeños (ver más abajo). MHD-INT no simula la formación "
                "de planetas en sí (la acreción de polvo a planeta), pero sí "
                "su evolución posterior: migración, resonancias y física "
                "interna una vez que el planeta ya existe."
            ),
        },
        {
            "titulo": "Campos magnéticos planetarios: el dínamo",
            "texto": (
                "Un planeta con un núcleo de metal líquido en movimiento "
                "convectivo (como el núcleo externo de hierro fundido de la "
                "Tierra) puede generar su propio campo magnético por un "
                "mecanismo llamado dínamo: el movimiento de un fluido "
                "eléctricamente conductor, combinado con la rotación del "
                "planeta, retuerce las líneas de campo magnético y las "
                "amplifica, de forma parecida a como una dínamo de "
                "bicicleta convierte movimiento en electricidad. Este campo "
                "magnético desvía el viento estelar (partículas cargadas "
                "que la estrella emite constantemente) antes de que llegue "
                "a la atmósfera del planeta, formando una burbuja protegida "
                "llamada magnetosfera. Sin ese escudo, el viento estelar "
                "puede ir erosionando la atmósfera con el tiempo — se cree "
                "que esto es parte de lo que le pasó a Marte. Este es el "
                "corazón físico de MHD-INT: calcular si un planeta genera "
                "campo suficiente, y si ese campo alcanza para proteger su "
                "atmósfera, a lo largo de toda su historia."
            ),
        },
        {
            "titulo": "La zona habitable, y por qué no alcanza con eso",
            "texto": (
                "La \"zona habitable\" clásica es el rango de distancias a "
                "una estrella donde el agua líquida podría existir en la "
                "superficie de un planeta, según cuánta luz recibe. Es un "
                "concepto útil pero incompleto: un planeta puede estar en "
                "la zona habitable radiativa y aun así no ser habitable, si "
                "perdió su atmósfera por falta de escudo magnético (como "
                "posiblemente le pasó a Marte) o si su órbita es tan "
                "excéntrica que el clima varía demasiado. MHD-INT no "
                "reemplaza el cálculo de zona habitable radiativa (eso "
                "depende de la luminosidad de la estrella, que sí usa como "
                "dato), pero agrega una capa que casi ningún simulador de "
                "acceso público modela: si el planeta conserva su escudo "
                "magnético y su atmósfera a lo largo de miles de millones "
                "de años. Por eso el resultado central del proyecto se "
                "llama Índice de Habitabilidad *Magnética* (MHI), no "
                "simplemente \"habitabilidad\": mide una condición "
                "necesaria adicional, no toda la historia."
            ),
        },
    ],
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
    # ------------------------------------------------------------------
    # Temas de los módulos agregados después del marco teórico original
    # (N-cuerpos, Migración, Efemérides, Discos). Mismo formato que
    # 'introduccion_astrofisica': texto + relación explícita con el
    # módulo real de MHD-INT que lo implementa, para que el estudiante
    # pueda ir de la teoría a probarlo directo en la interfaz.
    # ------------------------------------------------------------------
    "temas_avanzados": [
        {
            "nombre": "N-cuerpos",
            "explicacion": (
                "Cuando hay más de dos cuerpos gravitando entre sí (una "
                "estrella y varios planetas, por ejemplo), no existe una "
                "fórmula cerrada como las elipses de Kepler — hay que "
                "calcular la fuerza gravitatoria de cada cuerpo sobre todos "
                "los demás e integrar el movimiento paso a paso en el "
                "tiempo. Esto es el \"problema de los N cuerpos\". MHD-INT "
                "usa un integrador simpléctico (velocity Verlet), elegido "
                "porque conserva la energía y el momento angular del "
                "sistema muy bien durante integraciones largas, algo que "
                "integradores más simples no garantizan."
            ),
            "ecuacion": "F_i = G · Σⱼ≠ᵢ (mᵢ·mⱼ / rᵢⱼ²), para cada cuerpo i",
            "relacion_mhd_int": (
                "Módulo 🪐 N-cuerpos (Beta) y motor n_cuerpos_ligero_optimizado.py. "
                "Verificado en esta misma base contra sistemas reales: con "
                "TRAPPIST-1 completo (8 cuerpos) el error de energía queda "
                "del orden de 10⁻⁷ y el de momento angular de 10⁻¹⁶ — "
                "conservación excelente."
            ),
        },
        {
            "nombre": "Resonancias orbitales",
            "explicacion": (
                "Dos planetas están en resonancia orbital cuando sus "
                "períodos guardan una razón de números enteros pequeños "
                "(2:1, 3:2, 5:2...). No es casualidad: suele ser el "
                "resultado de la migración planetaria — a medida que los "
                "planetas se acercan o alejan de su estrella, sus períodos "
                "cambian, y si en algún punto caen en una razón simple, la "
                "propia resonancia los \"atrapa\" y estabiliza esa relación."
            ),
            "ecuacion": "Pₑₓₜₑᵣᵢₒᵣ / Pᵢₙₜₑᵣᵢₒᵣ ≈ p/q (p, q enteros pequeños)",
            "relacion_mhd_int": (
                "Módulo 🌀 Migración y Resonancias (resonancias.py). Detecta "
                "candidatos resonantes cinemáticos (a partir de los "
                "períodos, no de una integración dinámica larga que confirme "
                "la captura). Validado con dos casos reales y bien "
                "documentados en la literatura: la resonancia 5:2 entre "
                "Júpiter y Saturno (la \"Gran Desigualdad\") y la cadena "
                "resonante de 7 planetas de TRAPPIST-1 (Agol et al. 2021)."
            ),
        },
        {
            "nombre": "Alineaciones planetarias",
            "explicacion": (
                "Una \"alineación planetaria\" en el sentido en que la "
                "reportan los medios es un fenómeno de perspectiva: varios "
                "planetas aparecen agrupados en una región chica del cielo "
                "visto desde la Tierra, aunque en el espacio real estén a "
                "distancias enormes entre sí y no formen ninguna fila "
                "física. Es geometría aparente, no un alineamiento físico. "
                "El efecto gravitatorio combinado de una alineación así "
                "sobre la Tierra es despreciable frente al de la Luna — la "
                "fuerza de marea cae con el cubo de la distancia, y los "
                "planetas están demasiado lejos para competir con un cuerpo "
                "tan cercano como la Luna, sin importar cuántos se alineen."
            ),
            "ecuacion": None,
            "relacion_mhd_int": (
                "Módulo 🪐 Catálogo de Sistemas (detector_alineacion.py): "
                "calcula la longitud eclíptica aparente de cada planeta "
                "visto desde la Tierra y encuentra el instante de menor "
                "dispersión angular entre ellos. Documentado explícitamente "
                "que mide geometría, no fuerza de marea — MHD-INT no modela "
                "gravedad planeta-planeta sobre la Tierra en ningún módulo, "
                "a propósito."
            ),
        },
        {
            "nombre": "Torque atmosférico (rotación retrógrada de Venus)",
            "explicacion": (
                "Venus rota al revés que casi todos los demás planetas del "
                "Sistema Solar, y muy lentamente (un día venusino dura más "
                "que su año). Una de las hipótesis para explicarlo es la "
                "marea térmica atmosférica: el calentamiento solar de la "
                "densísima atmósfera de Venus genera un patrón de mareas en "
                "el aire que ejerce un torque neto sobre el planeta sólido, "
                "capaz de frenarlo y hasta revertir su rotación a lo largo "
                "de miles de millones de años — a diferencia de la marea "
                "gravitatoria sólida, que por sí sola tendería a frenarlo "
                "pero no a invertirlo."
            ),
            "ecuacion": None,
            "relacion_mhd_int": (
                "Fase 1 del motor (engine.py, flag torque_atmosferico_on, "
                "desactivado por defecto). Con el flag activado, Venus "
                "efectivamente termina en rotación retrógrada en la "
                "simulación — con un ~26% de error frente al valor "
                "observado, documentado como pendiente de calibración fina, "
                "no como resultado definitivo."
            ),
        },
        {
            "nombre": "Condiciones iniciales reales y efemérides",
            "explicacion": (
                "Una efeméride es la posición y velocidad real y medida de "
                "un cuerpo del Sistema Solar en una fecha concreta — es un "
                "dato observacional, no el resultado de ninguna simulación. "
                "Se diferencia de \"simular desde el año 0\" en que parte de "
                "dónde está el cuerpo *de verdad hoy*, en vez de una "
                "posición inicial arbitraria o hipotética."
            ),
            "ecuacion": None,
            "relacion_mhd_int": (
                "Módulo 🛰️ Efemérides reales, que consulta JPL Horizons "
                "(NASA/JPL) directamente. También usado como condición "
                "inicial opcional en el Catálogo de Sistemas "
                "(n_cuerpos_real.py) para que una simulación de N-cuerpos "
                "arranque desde la configuración real del Sistema Solar en "
                "una fecha elegida, en vez de fases arbitrarias — solo "
                "disponible para el Sistema Solar, porque Horizons no cubre "
                "exoplanetas."
            ),
        },
        {
            "nombre": "Discos protoplanetarios y oblicuidad estelar",
            "explicacion": (
                "Cuando una estrella joven tiene un campo magnético fuerte, "
                "ese campo puede \"cortar\" el disco de gas que la rodea "
                "antes de que llegue hasta la superficie estelar, creando un "
                "hueco interno (el radio de truncamiento). La interacción "
                "magnética entre la estrella y el disco también puede ir "
                "desalineando el eje de rotación de la estrella respecto al "
                "plano del disco con el tiempo, dependiendo de qué tan "
                "fuerte sea el acoplamiento comparado con la inercia de la "
                "estrella."
            ),
            "ecuacion": "r_t ∝ B^(4/7) (relación de truncamiento magnetosférico)",
            "relacion_mhd_int": (
                "Módulo 🌌 Disco Protoplanetario (Beta), basado en Lai, "
                "Foucart & Lin (2011). Valida el régimen bi-estable de "
                "alineación/desalineación según el cociente ζ̃/λ, y el radio "
                "de truncamiento contra el caso real de la estrella T Tauri "
                "DO Tau (Bessolaz et al. 2008), con ~13-15% de error "
                "documentado."
            ),
        },
    ],
    # ------------------------------------------------------------------
    # Interpretación gravitatoria y magnética -- cómo se conectan las dos
    # fuerzas que MHD-INT modela, y qué significan los números que tira
    # el simulador. Los umbrales de esta sección se verificaron uno por
    # uno contra el código real antes de escribirse (ver notas inline):
    # dos de los que traía la propuesta original estaban mal (MHI y
    # excentricidad) y se corrigieron acá con los valores reales.
    # ------------------------------------------------------------------
    "interpretacion_gravedad_magnetismo": {
        "intro": (
            "MHD-INT combina dos fuerzas en cada simulación: la gravedad, que "
            "rige el movimiento orbital, y el magnetismo, que rige la "
            "protección del planeta. No son independientes: forman un ciclo."
        ),
        "ciclo": (
            "gravedad → determina la órbita (distancia a la estrella) → la "
            "distancia determina cuánto viento estelar recibe el planeta "
            "(factor 1/distancia², más cerca = más viento) → el viento "
            "comprime la magnetosfera → el campo magnético (si alcanza) "
            "protege la atmósfera → la atmósfera participa en el torque que "
            "frena o invierte la rotación (caso Venus) → la rotación alimenta "
            "el dínamo que genera el campo magnético, cerrando el ciclo."
        ),
        "guia_gravedad": [
            "Órbita estable = la energía del sistema se mantiene constante "
            "durante la simulación (chequealo en el modo Validación).",
            "Excentricidad alta = órbita más alargada, variación de "
            "distancia (y por lo tanto de luz recibida) más marcada a lo "
            "largo del año del planeta.",
            "Migración = la órbita cambia con el tiempo por interacción con "
            "el disco de gas (solo mientras el disco tiene masa).",
            "Colisión / eyección = resultado de una simulación N-cuerpos con "
            "varios planetas interactuando gravitacionalmente entre sí.",
        ],
        "guia_magnetismo": [
            "B_final (Gauss) es el campo magnético superficial al final de "
            "la simulación. El umbral real que usa el motor para contar "
            "\"tiempo con campo activo\" es 0.3 G (UMBRAL_B_CAMPO_ACTIVO_GAUSS "
            "en habitabilidad.py) -- no es un corte de \"protegido para "
            "siempre\", es el piso a partir del cual un instante cuenta como "
            "protegido en el promedio de toda la simulación.",
            "R_m > 5 R_p (radio de la magnetosfera, en radios planetarios) "
            "es el umbral real de \"protección significativa\" "
            "(UMBRAL_R_MP_PROTEGIDO) -- con el modelo térmico activado, es "
            "otra forma de ver si el escudo alcanza a cubrir al planeta.",
            "Rm > 40 (número de Reynolds magnético) es el corte real que usa "
            "el motor para decidir si el dínamo está activo (engine.py, "
            "modelo térmico de Christensen 2009) -- solo se calcula si "
            "activaste \"🔥 Modelo térmico\" en la simulación; sin eso, Rm "
            "queda en 0 y no significa que el dínamo esté apagado, significa "
            "que no se calculó.",
            "MHI (0-100) combina las 4 piezas (escudo 40%, campo activo 30%, "
            "órbita 20%, marea 10%). Las categorías reales que usa el "
            "software son: ≥80 \"Alta habitabilidad magnética\", ≥50 "
            "\"Habitabilidad moderada / límite\", <50 \"Estéril / atmósfera "
            "expuesta\" (categoria_mhi() en habitabilidad.py).",
        ],
        "casos": [
            {
                "nombre": "Tierra — caso de éxito",
                "texto": (
                    "Órbita casi circular (e=0.0167). Campo magnético fuerte "
                    "(B≈0.31 G) sostenido por un dínamo activo. Resultado: "
                    "MHI en la categoría alta, atmósfera retenida."
                ),
            },
            {
                "nombre": "Marte — caso de pérdida",
                "texto": (
                    "Órbita estable pero más excéntrica que la Tierra "
                    "(e=0.0934). Sin campo magnético hoy (B≈0) -- el dínamo "
                    "marciano se apagó hace miles de millones de años. "
                    "Resultado: MHI bajo, consistente con la pérdida de "
                    "atmósfera que muestra la evidencia geológica real."
                ),
            },
            {
                "nombre": "Venus — caso de inversión",
                "texto": (
                    "Órbita casi perfectamente circular (e=0.0068, la más "
                    "baja de las tres). Sin campo magnético (B≈0). Con la "
                    "Fase 1 del motor activada (torque atmosférico), termina "
                    "en rotación retrógrada -- distinto mecanismo que Marte, "
                    "mismo resultado de MHI bajo por falta de escudo, no por "
                    "la órbita."
                ),
            },
        ],
    },
    # ------------------------------------------------------------------
    # El bucle del motor -- qué pasa realmente en cada paso de tiempo.
    # Verificado línea por línea contra engine.py (_paso_temporal) antes
    # de escribirse: el orden real intercala cálculos, no son fases
    # limpias separadas, y el torque atmosférico tiene un matiz físico
    # (2 mecanismos distintos para Venus) que vale la pena explicar bien.
    # ------------------------------------------------------------------
    "bucle_motor": {
        "intro": (
            "Cada simulación avanza en pasos de tiempo (dt) fijos. En cada "
            "paso, el motor recalcula todo el estado del planeta -- esto es "
            "lo que hace realmente _paso_temporal() en engine.py, paso a paso."
        ),
        "pasos": [
            "1. Evolucionar la estrella en el tiempo (viento estelar y "
            "rotación estelar según la Ley de Skumanich) para obtener las "
            "condiciones de viento de ESTE instante, no fijas.",
            "2. Calcular la presión de viento (P_ram) que recibe el planeta, "
            "ya escalada por su distancia real a la estrella.",
            "3. Calcular el torque magnético, el número de Elsasser (qué tan "
            "vigoroso es el dínamo) y el radio de la magnetosfera, con una "
            "corrección óhmica que depende de ese mismo número de Elsasser.",
            "4. Calcular el calor de marea total (por excentricidad, más el "
            "aporte extra por oblicuidad si el planeta la tiene apreciable).",
            "5. Calcular cómo cambian la excentricidad y el semieje orbital "
            "(migración) en este paso.",
            "6. Calcular el torque de marea lunar y cómo se aleja la luna "
            "(si el planeta tiene una).",
            "7. Calcular el movimiento medio orbital y cómo evoluciona la "
            "oblicuidad del planeta.",
            "8. Calcular el torque de marea estelar sólida (Hut 1981) -- "
            "este mecanismo, por sí solo, predice que Venus debería girar "
            "PRÓGRADO, no retrógrado.",
            "9. Calcular el torque atmosférico (Fase 1, opcional): un "
            "mecanismo DISTINTO (marea térmica atmosférica, Correia & "
            "Laskar 2001) que sí puede revertir la rotación -- es la "
            "explicación real de por qué Venus gira al revés, no la marea "
            "sólida del paso anterior. Por esto Venus queda excluido del "
            "chequeo de sentido de rotación en el modo Validación.",
            "10. Sumar solo los torques cuyo interruptor está activo, y "
            "actualizar la velocidad de rotación.",
            "11. Actualizar la órbita (semieje y excentricidad) con los "
            "cambios calculados en el paso 5.",
            "12. Actualizar el campo magnético: si el modelo térmico está "
            "activo, un dínamo real (se regenera si el número de Reynolds "
            "magnético supera 40, si no decae); si no, un decaimiento "
            "simplificado que se frena según el número de Elsasser.",
            "13. Actualizar la atmósfera, si ese modelo está activo.",
            "14. Guardar el nuevo estado completo y pasar al siguiente paso "
            "de tiempo.",
        ],
        "nota_torque_atmosferico": (
            "El torque atmosférico real tiene 2 componentes, ambas escaladas "
            "por la densidad de la atmósfera y la distancia a la estrella -- "
            "pero con potencias DISTINTAS de esa distancia (la componente "
            "viscosa cae con 1/a², la térmica con 1/a³), algo fácil de "
            "simplificar de más si se describe de memoria."
        ),
        "donde_esta_en_el_codigo": [
            ("engine.py", "_paso_temporal()", "el bucle principal descrito arriba"),
            ("engine.py", "simular()", "orquesta el bucle paso a paso y arma el resultado"),
            ("engine.py", "calcular_torque_atmosferico_termico()", "el torque atmosférico (Fase 1)"),
            ("numba_functions.py", "calcular_*", "las funciones numéricas del bucle (torques, presión, migración)"),
            ("termica.py", "NucleoTermico.actualizar()", "el dínamo real, cuando el modelo térmico está activo"),
            ("atmosfera.py", "Atmosfera.actualizar()", "la evolución de la atmósfera, cuando ese modelo está activo"),
        ],
    },
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
    dict(titulo="La Alineación de los Planetas", objetivo="Distinguir una agrupación aparente en el cielo de un alineamiento físico real.",
         analogia="Tres personas paradas en fila desde tu punto de vista pueden estar en realidad a cuadras de distancia una de otra — la \"fila\" es solo cómo se ven desde donde estás parado.",
         experimento="En el Catálogo de Sistemas, elegí el Sol, activá condiciones iniciales reales (Horizons) con una fecha, y detectá la alineación aparente.",
         prediccion="¿Qué planetas quedan más agrupados en el cielo, y a qué distancia real están entre sí en la simulación?",
         actividad="Dibujá el sistema solar visto \"desde arriba\" (posiciones reales) y después dibujá cómo se ven esos mismos planetas agrupados en el cielo nocturno. Compará ambos dibujos.",
         simulable=True),
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
    dict(titulo="Fuerza de Marea en una Alineación", concepto="La fuerza de marea que un cuerpo ejerce sobre otro cae con el CUBO de la distancia (no el cuadrado, como la gravedad simple), lo que hace que cuerpos lejanos sean irrelevantes frente a uno cercano.",
         practica="Calcular a mano la fuerza de marea de Júpiter, Saturno y la Luna sobre la Tierra (usando sus masas y distancias reales) y compararlas.",
         simulacion="—",
         simulable=False, nota_no_simulable=(
             "MHD-INT no calcula fuerza de marea entre planetas -- a propósito, "
             "no modela gravedad planeta-planeta sobre la Tierra en ningún "
             "módulo (ver Marco Teórico, tema 'Alineaciones planetarias'). Este "
             "es un ejercicio de cálculo manual con la fórmula de marea "
             "(F_marea ∝ M/d³) y datos reales de masa/distancia, pensado para "
             "que el resultado numérico refuerce por qué una alineación "
             "aparente no es un evento físicamente relevante para la Tierra.")),
    dict(titulo="Resonancias en TRAPPIST-1", concepto="TRAPPIST-1 tiene 7 planetas en una cadena resonante casi perfecta, uno de los sistemas resonantes más extremos conocidos (Agol et al. 2021).",
         practica="Calcular a mano el período de cada planeta con la Tercera Ley de Kepler y buscar razones de números enteros pequeños entre vecinos.",
         simulacion="Usar el Catálogo de Sistemas con TRAPPIST-1 y comparar los candidatos resonantes detectados contra tu cálculo manual.", simulable=True),
    dict(titulo="N-cuerpos y la Alineación del Sistema Solar", concepto="Una simulación de N-cuerpos con condiciones iniciales reales permite ver la configuración exacta del Sistema Solar en cualquier fecha, no solo una posición hipotética.",
         practica="Elegir una fecha real y predecir cualitativamente qué planetas estarán más cerca en longitud eclíptica.",
         simulacion="Usar el Catálogo de Sistemas con CI reales (Horizons) para esa fecha y comparar contra tu predicción.", simulable=True),
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
    dict(titulo="Torque Atmosférico vs. Gravitatorio en Venus", pregunta="¿Cuánto cambia la evolución rotacional de Venus si se activa el torque atmosférico (Fase 1) frente al modelo solo-gravitatorio?",
         metodo="Simular Venus con torque_atmosferico_on=False (default) y =True, comparando w_final y el signo de la rotación.",
         analisis="Cuantificar el error frente al valor observado (~26% documentado) y discutir qué componente del torque falta calibrar (K_atm_vis, K_atm_term).", simulable=True),
    dict(titulo="Validación de Resonancias en Sistemas Reales", pregunta="¿El detector cinemático de resonancias reproduce las cadenas resonantes confirmadas en la literatura?",
         metodo="Correr el detector de resonancias sobre TRAPPIST-1, Kepler-90, HD 110067 y el Sistema Solar (Júpiter-Saturno).",
         analisis="Comparar contra los valores publicados (Agol et al. 2021; Luque et al. 2023) y reportar la tasa de coincidencia y los falsos positivos/negativos, si los hay.", simulable=True),
    dict(titulo="Alineaciones Aparentes y el MHI: ¿Están Acopladas?", pregunta="¿Una alineación planetaria aparente coincide con algún cambio detectable en el MHI de la Tierra en esa misma fecha?",
         metodo="—", analisis="—",
         simulable=False, nota_no_simulable=(
             "El detector de alineación (Catálogo de Sistemas) y el cálculo del "
             "MHI (motor principal, engine.py/habitabilidad.py) son dos "
             "sistemas de simulación completamente independientes que no "
             "comparten estado: uno integra posiciones orbitales de varios "
             "cuerpos (N-cuerpos), el otro evoluciona campo magnético/atmósfera "
             "de UN planeta aislado. No hay ningún mecanismo físico esperado "
             "que los conecte -- de hecho, esa es la conclusión pedagógica del "
             "ejercicio: una alineación aparente no tiene por qué afectar (ni "
             "afecta) el escudo magnético de un planeta. Buena pregunta para "
             "discutir por qué NO deberían estar acopladas, no un experimento "
             "que el software pueda correr.")),
    dict(titulo="Acoplamiento Magnético entre Planetas", pregunta="¿Puede el campo magnético de un planeta activo influir en el de un planeta vecino inactivo?",
         metodo="—", analisis="—",
         simulable=False, nota_no_simulable=(
             "MHD-INT no modela ningún tipo de interacción magnética entre "
             "planetas -- ni el motor principal (que simula cada planeta de "
             "forma aislada) ni el módulo de N-cuerpos (que solo integra "
             "gravedad, sin campos magnéticos). Físicamente, además, la "
             "distancia entre planetas hace que cualquier acoplamiento "
             "magnético directo sea despreciable frente a la interacción de "
             "cada planeta con el viento y el campo de su propia estrella. "
             "Pregunta de investigación legítima en otros contextos (ej. "
             "lunas de Júpiter muy cercanas entre sí), pero fuera del alcance "
             "actual de este software.")),
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
         solucion="Aumentar dt a 10.000 años o más, si la precisión requerida lo permite. Para N-cuerpos específicamente, usar el paso sugerido (dt_sugerido()) en vez de un paso fijo manual — lo calcula automáticamente a partir del período orbital más corto del sistema."),
    dict(problema="Activaste condiciones iniciales reales (Horizons) en el Catálogo de Sistemas, esperabas ver la alineación real del 11-12 de agosto, y la simulación no la muestra en esa fecha.",
         diagnostico="¿Realmente activaste el checkbox de CI reales, o la simulación sigue usando fases arbitrarias?",
         causa="Sin CI reales, cada corrida arranca desde una fase orbital arbitraria (semilla fija, pero no calendario real) — el detector de alineación sigue funcionando y puede encontrar SU propio instante de mínima dispersión, que es real dentro de esa simulación pero no corresponde a ninguna fecha del calendario.",
         solucion="Activar el checkbox '🛰️ Condiciones iniciales reales (JPL Horizons)' y elegir la fecha exacta. Si Horizons no responde, revisar conexión a internet — el detector no cae en un valor estimado, avisa con un error explícito."),
    dict(problema="El N-cuerpos de un sistema compacto (ej. TRAPPIST-1) no conserva bien la energía (error > 1e-3).",
         diagnostico="¿Se usó un paso de tiempo (dt) fijo manual en vez del sugerido?",
         causa="El paso de tiempo fijo es demasiado grande para resolver el período orbital más corto del sistema — en sistemas compactos ese período puede ser de días, no de años.",
         solucion="Usar dt_sugerido() (o dejar que la pantalla lo calcule automáticamente) en vez de un paso manual, y simular rangos de tiempo cortos (10-100 años) para sistemas compactos, no miles de años."),
]
