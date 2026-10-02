# Historial de Cambios — MHD-INT

Formato: versión más reciente primero. Cada entrada indica qué cambió,
por qué, y qué auditoría o validación lo respaldó, siguiendo el estándar
del proyecto de no presentar precisión sin sustento verificable.

---

## v5.2.2 — Auditoría del motor (oct-2026)

Revisión completa del motor (`engine.py`, módulos opcionales, base de
datos) con barrido de los 300 planetas antes y después. Todas las
correcciones llevan el comentario `AUDITORIA oct-2026` en el código y un
test en `tests/test_auditoria_oct2026.py` (20 tests nuevos; la suite
completa pasa 90/90 y `validacion.py` da los mismos resultados que antes).

- **Migración orbital (grave):** dependía del paso dt y estrellaba a 91 de
  300 planetas. Reescrita como marea en la estrella con integración exacta
  (ver MARCO_TEORICO §6.1). Q'* = 1e7 por defecto.
- **Rotación cerca de la sincronía (grave):** la marea estelar hacía oscilar
  ω_p alrededor de n; el período final de TRAPPIST-1 e salía 14 d, 80 d o
  retrógrado según dt. Ahora se fija en la sincronía al cruzarla.
- **`se_estrello`:** umbral fijo de 0.01 UA reemplazado por el radio
  estelar o el límite de Roche (lo que sea mayor).
- **Atmósfera:** el flujo XUV se escalaba con a⁻⁴ en vez de a⁻², y el valor
  por defecto era 200 veces el documentado. El torque atmosférico volvía a
  la masa inicial tras perder la atmósfera.
- **MHI:** se quitó la penalización por oblicuidad < 5° (sin base física).
- **Datos corregidos** (Wikipedia / arXiv 1706.00509): GJ 1132 b, LHS 475 b,
  GJ 3293 b, HD 27894 b, c y d.
- **Interfaz:** el modelo térmico del núcleo se marca como EXPERIMENTAL
  (tiene errores de física conocidos, pendiente de rediseño).

Pendientes documentados (no cambian los resultados por defecto del Sistema
Solar): modelo térmico, calor por oblicuidad ∝ e², edad de la estrella no
usada, diagnósticos registrados un paso tarde, normalización del
decaimiento XUV, convenciones de oblicuidad de Saturno/Neptuno/Urano,
estrellas duplicadas, GJ 180 b.

---

## v5.2.1 — Correcciones previas a la venta (28-09-2026)

- **Detector de eclipses (N-cuerpos):** antes reportaba cada Luna nueva y
  llena como eclipse (49 en 2 años) porque solo miraba el plano x-y. Ahora,
  con posiciones 3D reales (laboratorio 14, JPL Horizons en el plano de la
  eclíptica) exige la latitud eclíptica de la Luna dentro de los límites
  eclípticos (±1,5° solar, ±1,1° lunar) y detecta la Luna nueva/llena por
  cambio de signo entre cuadros. Verificado con una órbita lunar analítica
  inclinada 5,145° y regresión nodal de 18,6 años: 2,3 solares y 1,9
  lunares por año (4,2 en total; la realidad es 4 a 7). En sistemas
  coplanares (armados desde la base de datos) ya no se inventan eclipses:
  se listan como "Luna nueva / Luna llena (alineación en el plano)".
- **Enlaces:** la app y el add-on apuntaban a solariscore.com (dominio que
  no es del proyecto); ahora a solariscore.com.co.
- **Paquete del cliente:** `build_exe.py` ahora incluye `documentacion/`
  (manual y licencia de uso) y un README con requisitos, activación y el
  aviso de SmartScreen.
- **Documentación:** requisitos del sistema, qué pasa al vencer la
  licencia, precios nuevos (Standard $39 y Pro $79, licencia de 2 años, precio de lanzamiento),
  y aclaración de qué mide `validacion.py` (consistencia, no predicción).
- **Nuevo:** `docs/LICENCIA_DE_USO.md` (términos para el cliente, borrador).

## v5.2 — Release comercial Pro (septiembre 2026)

Detalle completo, con verificación de cada punto, en
`NOTAS_DE_REVISION_v5.2.md`. Resumen:

- `video_mpl.py`: la generación de video fallaba siempre (crítico).
- `exportar_video.py` + `video_mpl.py`: la oblicuidad llega al video.
- Donut/tabla de MHI reconciliados con el total mostrado.
- Caché de video con clave completa.
- `engine.py`: corregida la corrupción de estado global compartido (crítico).
- Modo Sintético: 4 mejoras + luna personalizada.
- Urano/Neptuno resueltos (dos causas distintas).
- Módulos nuevos: disco protoplanetario (Fase 2) + Modificador de sistemas (BETA).
- Limpieza del paquete: se quitan cachés, pruebas sueltas de fases
  anteriores, `catalogo_exoplanetas_ui.py` (no conectado) y
  `RESUMEN_FASES.txt` (vacío).
- Versión pública (`app_streamlit.py`) alineada a 5.2.

---

## v5.1.1 — Parche de consistencia (hallado durante revisión de MHD-INT Pro)

- `exportar_video.py`: el esquema JSON para IAs de video (definido jul-2026,
  antes de que existiera oblicuidad como variable dinámica) nunca incluía
  `eps_deg` por punto. Cualquier consumidor externo del JSON (Manim,
  Blender, Sora, o la Capa 1 de video de MHD-INT Pro) recibía oblicuidad
  como 0.0 constante sin ninguna señal de que el dato faltaba. Se agrega
  `eps_deg` por punto y `eps_conocido` en `meta`.
- `habitabilidad.py`: `calcular_mhi()` aplicaba la penalización de
  oblicuidad (-20 pts) de forma interna antes de retornar `mhi_total`, sin
  exponerla como componente. Cualquier visualización que graficara los 4
  componentes pesados (escudo/campo/órbita/marea) sumaba más que el
  `mhi_total` mostrado, sin forma de reconciliar la diferencia. Se agregan
  `mhi_bruto` y `penalizacion_obl_pts` al dict de retorno.
- Ninguno de los dos cambios altera el cálculo físico ni el valor final de
  `mhi_total` — son estrictamente de exposición de datos que ya existían
  internamente. `validacion.py` sigue en verde.

## v5.1 — Dinámica de oblicuidad

- Se incorpora la evolución de la oblicuidad planetaria (ángulo axial)
  como variable dinámica del sistema, acoplada a la disipación de marea
  y al torque estelar.
- **Principio de datos establecido:** para exoplanetas sin oblicuidad
  medida u observacionalmente restringida, el modelo NO asigna un valor
  por defecto arbitrario. El campo se deja explícitamente marcado como
  "no disponible" en vez de rellenarse con una estimación no verificable
  — lección aplicada directamente del cierre del proyecto TUM, donde
  variables sin sustento observacional contaminaron la validación.
- Pendiente: definir el tratamiento de UI para exoplanetas sin este dato
  (Ferrari UI).

## v5.0 — Acoplamiento atmósfera/manto-núcleo

- `atmosfera.py`: modelo de escape atmosférico (fotoevaporación / escape
  hidrodinámico impulsado por flujo XUV estelar).
- `termica.py`: se fusiona el modelo térmico simple del núcleo (v4.2) con
  un factor de acoplamiento núcleo-manto tipo *stagnant-lid* (Korenaga,
  2008), diferenciando régimen tectónico móvil (Tierra) vs. estancado
  (Venus/Marte).
- **Limitación conocida y documentada:** el motor invoca `termica.py`
  con luminosidad estelar fija en 1.0 L☉ para todas las estrellas, ya
  que `database.py` aún no tiene un modelo de luminosidad por tipo
  espectral. Esto es razonable para estrellas G/K pero sobreestima la
  temperatura superficial (y por tanto Q_CMB) en enanas M. Queda anotado
  en el código como pendiente, no oculto.

## v4.2 — Núcleo térmico y generación de dínamo

- Se introduce `termica.py` (versión inicial): modelo 1D de evolución
  térmica del núcleo, número de Reynolds magnético (Rm), y campo
  magnético generado vía ley de escala de Christensen (2009).
- Umbral de Elsasser recalibrado empíricamente contra la Tierra tras
  detectar que era inalcanzable con los valores de dipolo superficial
  reales de la base de datos.

## v4.1 — Baseline validado (4 cuerpos)

- Auditoría 2026-07-22 detecta y corrige dos bugs de signo de exponente
  que afectaban la mayoría de la base de datos de planetas:
  - `w_estrella`: 23 de 47 planetas con el signo del exponente invertido
    (ej. `2.9e6` en vez de `2.9e-6`), lo que invertía el signo del
    torque magnético calculado en `numba_functions.py`.
  - `B_p_inicial`: 36 de 47 planetas con el mismo bug (ej. `3.1e5 T` en
    vez de `3.1e-5 T` para la Tierra).
- Tras la corrección, `validacion.py` confirma que el campo magnético
  inicial de Tierra y Júpiter coincide con los valores reales
  (0.31 G y 4.2 G respectivamente).
- `tau_dipolo` corregido de 1000 Gyr a 1.2 Gyr (error de varios órdenes
  de magnitud en la constante de decaimiento del dipolo).
- Se detecta y corrige que la evolución estelar (`stellar_evolution.py`)
  nunca era invocada durante la simulación principal.
- Se reconecta el Índice de Habitabilidad Magnética (MHI), que estaba
  desconectado de la app de Streamlit.
- Validación baseline: error <0.45% contra datos observacionales en
  4 cuerpos del Sistema Solar (Tierra, Venus, Marte, Júpiter).

## v3.3 – v3.6 — Mejoras físicas incorporadas

- Torque de marea estelar (Hut, 1981).
- Fórmula mejorada de resistencia óhmica (R_ohm).
- Paso de tiempo adaptativo tipo CFL.
- Rotación retrógrada de Venus documentada como fuera del alcance del
  modelo (requiere mareas térmicas atmosféricas, Correia & Laskar,
  2001) y excluida explícitamente de las validaciones correspondientes
  en vez de forzarse a coincidir artificialmente.

## v3.2 — Baseline inicial

- 48 cuerpos simulados, error <0.45% en validación del Sistema Solar.
- Primera versión estable tras el cierre del proyecto TUM.

---

## Nota sobre el índice ZHM/Imo de habitabilidad

Sigue siendo un ítem abierto documentado: ninguna fórmula probada logró
separar de forma confiable los colapsos de tipo "Júpiter caliente" de
los candidatos habitables en zona de enana M. Se mantiene como
heurística de respaldo el umbral B > 0.3 G, explícitamente señalado
como aproximación, no como resultado derivado.
