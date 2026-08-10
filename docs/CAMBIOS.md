# Historial de Cambios — MHD-INT

Formato: versión más reciente primero. Cada entrada indica qué cambió,
por qué, y qué auditoría o validación lo respaldó, siguiendo el estándar
del proyecto de no presentar precisión sin sustento verificable.

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
