MARCO TEÓRICO — MHD-INT v5.0
=============================================================================
Simulador de Interacción Planeta–Estrella
AUTOR: Roney Rigg Mora
FECHA: Julio 2026
VERSIÓN: 5.0 (incorpora modelo térmico del núcleo, atmósfera y oblicuidad
        sobre la base de v4.1)
ESTADO: VALIDADO CONTRA CÓDIGO FUENTE — validar_todos() aprueba Tierra, Venus,
        Marte y Júpiter en su totalidad (incluyendo B_gauss), con los
        módulos nuevos (térmico/atmósfera/oblicuidad) desactivados por
        defecto y sin afectar la validación
NOTA: Esta versión reemplaza a v4.1. Añade tres capacidades nuevas,
opcionales y activables por separado: generación real de campo magnético
por dínamo térmico (§4.5), evolución y escape atmosférico (§4.6), y
evolución secular de la oblicuidad (§4.7). Ver §0 para el resumen de
cambios frente a v4.1.

-----------------------------------------------------------------------------
0. RESUMEN DE CAMBIOS v4.1 → v5.0
-----------------------------------------------------------------------------

- **Modelo térmico del núcleo (nuevo, §4.5):** reemplaza —de forma
  opcional, vía toggle `modelo_termico`— el interruptor puramente empírico
  de §4.4 por un balance térmico del núcleo (calentamiento radiogénico vs.
  conducción a través del manto) que genera un flujo convectivo real
  (q_conv) y, a partir de él, un campo magnético por ley de escala de
  Christensen. Con el toggle apagado (default), el comportamiento es
  idéntico a v4.1.
- **Modelo de atmósfera (nuevo, §4.6):** evolución de la masa atmosférica
  por escape hidrodinámico impulsado por radiación XUV estelar (Owen &
  Jackson 2012), activable vía toggle `modelo_atmosfera`.
- **Oblicuidad (nuevo, §4.7):** evolución secular del ángulo de
  inclinación axial (Laskar & Robutel 1993, versión simplificada) y su
  efecto sobre el calor de marea y el MHI, solo para los cuerpos con dato
  observacional real conocido.
- Ambos modelos nuevos (térmico y atmósfera) están desactivados por
  defecto — la validación de los 4 cuerpos del Sistema Solar contra datos
  reales no cambia respecto a v4.1.
- **v5.2:** el modelo térmico (§4.5) ahora tiene parámetros (aunque sean
  estimados, no reales) para los 47 planetas de la base de datos, no solo
  para los 4 del Sistema Solar — antes, activar el toggle térmico sobre un
  exoplaneta corría con valores genéricos idénticos para cualquier
  planeta, ignorando su masa/radio/tipo real.

=============================================================================
1. INTRODUCCIÓN
=============================================================================

MHD-INT v4.1 es un simulador numérico que modela la evolución acoplada de la
órbita, la rotación, el campo magnético y el calor de marea de un planeta
bajo la influencia de su estrella anfitriona. El modelo integra cinco
procesos físicos fundamentales (se agrega el quinto respecto a v4.0, antes
implícito):

  1. Evolución orbital — migración y circularización por interacciones de marea.
  2. Evolución rotacional — frenado/aceleración por torque magnético estelar
     y torque lunar (Darwin-Kaula).
  3. Evolución del campo magnético planetario — decaimiento secular
     modulado por un interruptor de "dínamo activo" (fenomenológico, ver §4.4).
  4. Calor de marea — disipación viscoelástica en el interior del planeta.
  5. Evolución estelar — decaimiento de la rotación estelar (Skumanich) y
     su efecto sobre el viento estelar, ahora conectada al bucle temporal.

El código está escrito en Python, acelerado con Numba, con interfaz gráfica
en Streamlit y Plotly. La base de datos incluye 47 planetas (8 del Sistema
Solar + 39 exoplanetas) con excentricidades reales calibradas.

**Historial de versiones:**
- v4.0 (2026-07-22): versión original, contenía varios desajustes entre
  documento y código, identificados y corregidos en la auditoría.
- v4.1 (julio 2026, esta versión): corrige 11 hallazgos de auditoría,
  fusiona la Adenda técnica, documenta explícitamente las limitaciones
  conocidas del modelo de dínamo.

=============================================================================
2. EVOLUCIÓN ORBITAL Y ROTACIONAL POR MAREA
=============================================================================
(Sin cambios respecto a v4.0 — verificado correcto contra el código en la
auditoría.)

## 2.1 Factor de Disipación de Marea Q

En la teoría de mareas de Goldreich & Soter (1966), el factor de calidad Q
mide la fracción de energía disipada por fricción de marea por radián
orbital: la fracción promedio de energía perdida por calor por radián de
órbita es Q⁻¹, y el abultamiento de marea se retrasa respecto a la dirección
instantánea de la compañera por un ángulo (2Q)⁻¹. Para planetas gigantes, la
literatura sugiere 10⁴ ≲ Q ≲ 10⁶.

MHD-INT utiliza el parámetro k₂/Q (donde k₂ es el número de Love de segundo
orden), que varía según el tipo de planeta:
  - k₂/Q = 0.015 para planetas rocosos (tipo Io, Peale & Cassen 1979)
  - k₂/Q = 1.0×10⁻⁵ para gigantes gaseosos (R_p > 3 R_Tierra)
  - k₂/Q = 0.0 para Mercurio (caso especial, ver §6.3)

## 2.2 Circularización Orbital (Hut 1981)

de/dt = -(21/2) · (k₂/Q) · (M_estrella / M_planeta) · (R_p / a)⁵ · n · e

donde n = sqrt(G · M_estrella / a³) es el movimiento medio orbital. Implementado
en `calcular_de_dt_numba()`.

## 2.3 Calor de Marea (Peale, Cassen & Reynolds 1979)

Q_tidal = (21/2) · (k₂/Q) · R_p⁵ · n⁵ · e² / G

Forma dimensionalmente correcta (Watts). NO usar G·M²/a⁶ (da Joules, error
corregido en v3.4). Implementado en `calcular_calor_marea_numba()`.

## 2.4 Torque Lunar Darwin-Kaula

tau_lunar = (3/2) · (k₂/Q_p) · G · M_luna² · R_p⁵ / a_luna⁶

Signo determinado por omega_p vs n_luna = sqrt(G · M_planeta / a_luna³).
Recesión lunar por conservación de momento angular:

da_luna/dt = - tau_lunar / (0.5 · M_luna · sqrt(G · M_planeta / a_luna))

Implementado en `calcular_torque_lunar()` y `calcular_recesion_lunar()`.

=============================================================================
3. INTERACCIÓN MAGNÉTICA ESTRELLA–PLANETA
=============================================================================
(Sin cambios en las fórmulas respecto a v4.0. CORRECCIÓN DE DATOS aplicada
en v4.1: ver §3.5.)

## 3.1 Viento Estelar y Presión de Ram

P_ram = rho_sw · v_sw²

Con factor de escala por distancia (a/UA)⁻² aplicado en
`calcular_presion_ram_numba()`. A partir de v4.1, rho_sw y v_sw ya NO son
constantes durante la simulación — evolucionan en el tiempo vía
`EstrellaEvolutiva.evolucionar()` (ver §5).

## 3.2 Radio de Alfvén

R_A = R_p · (B_p² / (2 · mu_0 · P_ram))^(1/6)

Clamp de estabilidad: R_A ≤ 0.9·a (ver §6.2).

## 3.3 Torque Magnético (Strugarek et al. 2017)

tau_mag = tau_0 · (B_alfven² / mu_0) · R_A³

donde B_alfven = B_p · (R_p / R_A)³ y tau_0 = 1.2×10⁻³. Signo determinado por
omega_p vs omega_estrella (ahora evolucionado en el tiempo, ver §5).
Clamp de estabilidad: |tau_mag| ≤ 1×10²² N·m.

## 3.4 Corrección Óhmica

R_ohm = 1 + alpha · tanh(E_p - 1),  alpha = 0.05

**CORRECCIÓN v4.1 (hallazgo #2 de auditoría):** en v4.0, R_ohm se calculaba
pero NO se aplicaba a la ecuación de rotación — solo afectaba al radio
magnetosférico reportado. En v4.1, se aplica correctamente:

  domega_p/dt = (tau_mag · R_ohm + tau_lunar) / I_p

tal como especifica §7 (Resumen del modelo acoplado). Verificado en
`engine.py`, función `_paso_temporal()`.

## 3.5 CORRECCIÓN DE DATOS: w_estrella (hallazgo #4 de auditoría)

En v4.0, 23 de 47 planetas tenían `w_estrella` con el exponente del signo
invertido en `database.py` (ej. 2.9e6 en vez de 2.9e-6), lo cual invertía el
signo del torque magnético calculado en §3.3. Afectaba a los 8 planetas del
Sistema Solar completos más 15 exoplanetas. **Corregido en v4.1** — verificado
que `validar_todos()` ahora reproduce correctamente el sentido de rotación
retrógrado de Venus.

=============================================================================
4. EVOLUCIÓN DEL CAMPO MAGNÉTICO PLANETARIO
=============================================================================
**Sección con cambios sustanciales respecto a v4.0.**

## 4.1 Número de Elsasser

E_p = B_p² / (mu_0 · rho_core · omega_p · eta)

Un valor E_p > 1 indica, en la literatura, condiciones favorables para el
dínamo. **LIMITACIÓN CONOCIDA (hallazgo #10 de auditoría):** en este modelo,
B_p representa el campo dipolar SUPERFICIAL, mientras que la fórmula de
Elsasser describe físicamente la condición del dínamo en el NÚCLEO, donde el
campo real es sustancialmente más intenso. Con B_p superficial, E_p resulta
sistemáticamente en el rango 10⁻⁴ a 10⁻² para todos los planetas del
dataset — el umbral E_p > 1 nunca se alcanza con esta definición. Ver §4.4
para cómo se resolvió esto en la práctica, y §8 para la discusión completa
de por qué no existe hoy un factor de conversión núcleo-superficie bien
establecido en la literatura (la incertidumbre observacional/teórica abarca
hasta 50x entre estimaciones).

## 4.2 Decaimiento Secular del Campo — CORREGIDO EN v4.1

**CORRECCIÓN (hallazgo #1 de auditoría):** en v4.0, la tasa de decaimiento
codificada (`TASA_DECAIMIENTO_B_BASE = 0.001` por Gyr) implicaba
tau_dipolo ≈ 1000 Gyr, contradiciendo el valor documentado de ~1.2 Gyr para
un núcleo terrestre. Con tau=1000 Gyr, el campo prácticamente no decaía en
ninguna simulación típica — la física de esta sección era, en la práctica,
un no-op.

En v4.1: `TASA_DECAIMIENTO_B_BASE = 1/1.2` → tau_dipolo = 1.2 Gyr, consistente
con el valor documentado.

## 4.3 Campo Magnético Protector

Un planeta posee "campo magnético protector" si:
  - B_p > 0.3 Gauss (umbral de protección atmosférica)
  - a > 0.01 UA (el planeta no ha colapsado contra la estrella)

Sin cambios respecto a v4.0 — verificado correcto en `_construir_resultado()`.

## 4.4 Interruptor de Dínamo Activo (NUEVO EN v4.1)

**Contexto:** al implementar tau_dipolo=1.2 Gyr (§4.2) SIN ningún mecanismo
de regeneración, cualquier planeta pierde ~97.65% de su campo inicial en
4.5 Gyr — incluida la Tierra, que sí sostiene su dínamo activo hoy. Esto
habría hecho fallar la validación contra datos reales de forma sistemática
para cualquier planeta con edad comparable a la del Sistema Solar.

**Solución implementada — recalibración empírica, NO un modelo de dínamo:**

  factor_dinamo = clip(E_p / E_P_REFERENCIA, 0, 1)
  tasa_efectiva = TASA_DECAIMIENTO_B_BASE · (1 - factor_dinamo · 0.99)
  E_P_REFERENCIA_DINAMO_ACTIVO = 8.739480×10⁻⁴  (E_p inicial de la Tierra)

La referencia se calibró contra el E_p inicial de la Tierra — el más débil
de los dos cuerpos del dataset con dínamo activo confirmado hoy (Tierra y
Júpiter). Se verificó una brecha natural de 4 a 8 órdenes de magnitud entre
estos dos cuerpos y los que no tienen campo global hoy (Venus: 2.15×10⁻⁸,
Marte: 1.15×10⁻¹⁰) — la separación activo/inactivo emerge de datos reales
conocidos, no de un ajuste al resultado numérico deseado.

**ADVERTENCIA EXPLÍCITA — leer antes de asumir que esto modela un dínamo:**
Este mecanismo NO es un modelo de generación de campo magnético. Sigue
siendo la misma ecuación de solo-decaimiento de §4.2, con un interruptor
(continuo, no binario) que decide qué tan rápido decae. No existe ningún
término que haga crecer B_p; no hay retroalimentación con convección del
núcleo, rotación real, ni número de Rayleigh. Es una aproximación
fenomenológica calibrada empíricamente, declarada como tal. Ver §8 para la
discusión de qué haría falta para un modelo de generación real.

**Resultado verificado:** con este interruptor, `validar_todos()` aprueba
Tierra y Júpiter en B_gauss con 3.68% de error (idéntico en ambos casos,
porque ambos saturan en factor_dinamo=1.0 durante toda la simulación —
consistente, no coincidencia espuria).

## 4.5 Modelo Térmico del Núcleo — Generación Real de Campo (NUEVO EN v5.0)

**Contexto:** §4.4 modula la *velocidad de decaimiento* de B_p pero no
genera campo — es un interruptor calibrado empíricamente, no un dínamo.
Este módulo (opcional, toggle `modelo_termico`, implementado en
`termica.py`) añade un balance térmico del núcleo que sí produce un flujo
convectivo real, del cual se deriva un campo magnético por ley de escala.

**Balance térmico del núcleo** (por paso temporal):

  Q_radio = H_radiogénico · M_núcleo
  Q_CMB = 4π·R_planeta² · k_manto · (T_cmb − T_superficie) / D_manto · factor_lid
  Q_conv = max(0, Q_radio − Q_CMB)
  q_conv = Q_conv / (4π·R_núcleo²)

donde `factor_lid` vale 1.0 en régimen de placas móviles (mobile lid, ej.
Tierra) y 0.35 en régimen de tapa estancada (stagnant lid, ej. Venus,
Marte) — Korenaga (2008). La temperatura superficial T_superficie se deriva
del balance radiativo con albedo real del planeta y flujo estelar a la
distancia orbital actual. T_cmb evoluciona según dT/dt = (Q_radio −
Q_CMB) / (M_núcleo · cp).

**Campo generado en el núcleo** (Christensen, Holzwarth & Reiners 2009):

  B_núcleo = C_calib · rho_núcleo^(1/3) · (q_conv · R_núcleo)^(2/3)

Atenuado a superficie por B_superficial = B_núcleo · (R_núcleo/R_planeta)³.
C_calib = 1.4215×10⁻⁸ está calibrado para que la Tierra reproduzca su
campo superficial real (~0.31 G) con este balance térmico completo.

**Número de Reynolds magnético:** Rm = v_conv·R_núcleo/η, con v_conv =
(q_conv·R_núcleo/rho_núcleo)^(1/3) — reportado como diagnóstico (umbral de
dínamo activo en la literatura: Rm ≳ 40-50, Christensen & Aubert 2006), no
usado como condición de activación en este modelo.

**Limitaciones declaradas:**
- **Actualización v5.3:** L_estrella ya no es fijo en 1.0 para todos los
  planetas — se calcula por la masa real de la estrella (dato exacto
  disponible para las 38 estrellas de la base), vía una relación
  masa-luminosidad estándar de secuencia principal (Eker et al. 2018;
  Salaris & Cassisi 2005 para la rama de baja masa): L/L☉=(M/M☉)^3.5 para
  M≥0.43 M☉, L/L☉=0.23·(M/M☉)^2.3 por debajo. Efecto observado: en
  planetas muy cercanos a estrellas M frías extremas (TRAPPIST-1e,
  GJ_1132b), el dínamo térmico pasa de activo a inactivo (Rm cae a 0) al
  corregir la luminosidad — la temperatura superficial calculada baja, el
  gradiente núcleo-manto se reduce, y la pérdida conductiva supera al
  calentamiento radiogénico. No es un error: es el modelo respondiendo a
  un dato de entrada más realista, pero cambia resultados previamente
  reportados para esos sistemas específicos (planetas alrededor de
  estrellas M4V o más frías). Validación de los 4 cuerpos del Sistema
  Solar no afectada (el Sol usa L=1.0 con o sin este cambio).
- Júpiter no está calibrado (núcleo de hidrógeno metálico, física distinta
  a un núcleo rocoso/ferroso) — el modelo da control cualitativo, no
  cuantitativo, para gigantes gaseosos.
- Con el toggle apagado (default), el motor usa el interruptor de §4.4 sin
  cambios — la validación de los 4 cuerpos del Sistema Solar es idéntica a
  v4.1.

**Cobertura de datos (actualizado v5.2):** solo Venus, Tierra, Marte y
Júpiter tienen R_core/T_cmb/T_manto/k_manto/regimen_tectonico/albedo
tomados de datos reales o calibrados directamente. Los 43 planetas
restantes de la base de datos usan una estimación por categoría de planeta
(`_estimar_parametros_termicos()` en `database.py`), NO datos observados,
marcada explícitamente con el flag `termico_estimado=True`:

- `R_core`, `k_manto` y `albedo` se derivan de la categoría del planeta
  (terrestre/superTierra/subNeptuno/gigante), con distinto grado de
  confianza: el ratio núcleo/radio de los 3 cuerpos rocosos reales es
  consistente (~0.54) y se reutiliza con más confianza que el de los
  gigantes (extrapolado del valor de calibración de Júpiter, que el propio
  §4.5 ya señala como no físico).
- `regimen_tectonico` (mobile-lid vs. stagnant-lid) **no es derivable** de
  ningún dato disponible — ni siquiera con observación directa se conoce el
  régimen tectónico de un exoplaneta. Es un supuesto de diseño, marcado con
  el flag `regimen_tectonico_conocido=False` (mismo patrón que
  `eps_conocido` en §4.7), no un dato reconstruido.
- `T_cmb_inicial`/`T_manto_inicial` son los campos menos sólidos: los 4
  casos reales no siguen una relación monótona simple con la masa (Venus,
  menos masivo que la Tierra, tiene T_cmb mayor), así que en vez de ajustar
  una curva a 4 puntos se usa un valor de referencia por categoría con una
  variación suave y declaradamente heurística.
- `Q_cmb_hoy_W` no se usa en ningún cálculo del motor — se mantiene solo
  por consistencia de esquema.

Probado (sin crashes, Rm > 40 en todos los casos, B generado en rango
físicamente razonable) sobre representantes de las 6 categorías: terrestre
(Proxima_b), superTierra (Kepler_452b), subNeptuno (K2_18b), hot Jupiter
(WASP_12b, HD_209458b), gigante de hielo (Urano, Neptuno). No validado
cuantitativamente contra datos reales — no existen datos reales de campo
magnético interno para ningún exoplaneta.

Implementado en `termica.py` (clase `NucleoTermico`), integrado en
`engine.py::_paso_temporal()`.

## 4.6 Atmósfera — Escape Hidrodinámico (NUEVO EN v5.0)

Modelo opcional (toggle `modelo_atmosfera`, `atmosfera.py`) de evolución de
la masa atmosférica por escape hidrodinámico impulsado por radiación XUV
estelar (Owen & Jackson 2012):

  dM_atm/dt = −η · (π · R_p³ · F_XUV) / (G · M_planeta)

donde η es la eficiencia de escape (por planeta, `database.py`) y F_XUV
decae en el tiempo según F_XUV(t) = F_XUV,0 · (t/t₀)^(−β), con β=1.5 para
estrellas de tipo solar y β=0.8 para enanas M (XUV saturado por más
tiempo, Loyd et al. 2020), y escala con la distancia orbital como
(a/UA)⁻².

F_XUV,0 = 0.005 W/m² a 1 UA (orden de magnitud del flujo XUV solar en
calma, Ribas et al. 2005). Con este valor la Tierra retiene ~72% de su
atmósfera a 4.5 Gyr y Venus la retiene casi entera; Marte la pierde por
completo (mayor eficiencia de escape y menor gravedad) — cualitativamente
consistente con la pérdida atmosférica real de Marte, aunque el *timing*
del modelo es más rápido que la escala geológica real (gap documentado,
no resuelto).

Un planeta se considera con "atmósfera perdida" cuando M_atm cae bajo el
10% de su masa atmosférica inicial (umbral relativo, no absoluto); esto
fuerza MHI=0, igual que el colapso orbital (`se_estrello`).

Implementado en `atmosfera.py` (clase `Atmosfera`), integrado en
`engine.py::_paso_temporal()`.

## 4.7 Oblicuidad — Evolución Secular (NUEVO EN v5.1, incluido en v5.0)

Evolución del ángulo de oblicuidad (inclinación axial) ε por fricción de
marea (Laskar & Robutel 1993, versión simplificada):

  dε/dt = −(3/2) · (k₂/Q) · (M_estrella/M_planeta) · (R_p/a)⁵ · n · sin(2ε) · (1 + e²/2)

El calor de marea total (§2.3) incorpora la contribución de la oblicuidad
además de la excentricidad.

**Dato conocido vs. no conocido:** solo Tierra (23.44°), Marte (25.19°),
Júpiter (3.13°), Urano (97.77°) y Venus (2.64°) tienen oblicuidad inicial
real en `database.py` (`eps_conocido=True`). El resto de los planetas
(incluidos todos los exoplanetas) parte de 0° con `eps_conocido=False`.

**Penalización en el MHI:** una oblicuidad final fuera del rango [5°,60°]
resta 20 puntos al MHI, mostrarido inestabilidad climática — pero
**solo si `eps_conocido=True`**. Esto evita penalizar planetas cuyo 0°
interno es un valor por defecto sin respaldo observacional, no un dato
real. Verificado: Tierra (dato real) sin penalización, Urano (dato real,
97.77°) penalizado, Saturno (sin dato) sin penalización pese a que
internamente el motor lo trata como 0°.

Implementado en `engine.py::_paso_temporal()` y `habitabilidad.py`.

=============================================================================
5. EVOLUCIÓN ESTELAR (VIENTO Y ROTACIÓN)
=============================================================================
**CORRECCIÓN v4.1 (hallazgo #3 de auditoría): sección ahora activa.**

En v4.0, la clase `EstrellaEvolutiva` existía y estaba correctamente
implementada, pero `MotorMHD._paso_temporal()` nunca llamaba a su método
`evolucionar()` — el motor usaba `rho_sw_base`, `v_sw_base` y `w_estrella`
fijos durante toda la simulación (hasta 10 Gyr). Esta sección completa era,
en la práctica, código muerto.

## 5.1 Ley de Skumanich

omega_estrella(t) ∝ t^(-1/2)   [estrellas G/K/F]
omega_estrella(t) ∝ t^(-0.3)   [enanas M — decaimiento más lento]

## 5.2 Viento Estelar

rho_sw ∝ omega_estrella²
v_sw ∝ omega_estrella^0.3

Heurísticas basadas en Wood et al. (2005) y Vidotto et al. (2014), no
calibradas específicamente para este modelo. Para enanas M, el campo
magnético estelar se asume saturado (constante).

## 5.3 Conexión al motor (v4.1)

En cada paso temporal, `_paso_temporal()` ahora llama:

  w_estrella_t, B_estrella_t, rho_sw_t, v_sw_t = self.estrella_evolutiva.evolucionar(t_gyr)

Estos valores evolucionados reemplazan a los fijos de v4.0 en el cálculo de
`P_ram` y `tau_mag`. **Nota de implementación:** no se pasa `a_ua` a
`evolucionar()`, porque la dependencia con la distancia (a/UA)⁻² ya la
aplica `calcular_presion_ram_numba()` por separado (§3.1) — pasarla también
aquí duplicaría el escalamiento por distancia.

## 5.4 Consolidación de B_estrella (hallazgo #11 de auditoría)

En v4.0 existían dos tablas independientes estimando el campo magnético
estelar por tipo espectral (`estimar_B_estrella()` en engine.py, escala
Tesla; y `EstrellaEvolutiva._estimar_B_actual()`, escala relativa
arbitraria). Se confirmó que ninguna alimentaba `P_ram` ni `tau_mag` — ambas
eran vestigiales. En v4.1, se consolidó a una sola fuente: `EstrellaEvolutiva`
recibe `B_inicial_tesla` como parámetro desde `estimar_B_estrella()`. El
valor `B_estrella_t` evolucionado queda disponible (ya no descartado) por si
se decide, en el futuro, correlacionar la presión de viento con el campo
magnético estelar real.

=============================================================================
6. DETALLES DE IMPLEMENTACIÓN (antes solo en la Adenda, fusionados aquí)
=============================================================================

## 6.1 Q_efectivo diferenciado por tipo de sistema

En `calcular_tiempo_migracion()`:

| Condición | Q_efectivo |
|---|---|
| tipo_planeta ∈ {Gigante gaseoso, Hot Jupiter, Sub-Neptuno} | 1×10⁵ |
| Estrella anfitriona es enana M | 1×10⁶ |
| Cualquier otro caso | 100 (valor por defecto) |

## 6.2 Límites numéricos de estabilidad (clamps)

No representan física adicional; evitan divergencias en la integración
explícita:

| Cantidad | Límite |
|---|---|
| Radio de Alfvén | R_A ≤ 0.9·a |
| Torque magnético | \|tau_mag\| ≤ 1×10²² N·m |
| Tiempo de migración | 10³ años ≤ tau_mig ≤ 10²⁰ años |
| Radio magnetosférico normalizado | R_m ≤ 100 |
| Campo magnético planetario | B_p ≥ 10⁻⁸ T |
| Excentricidad | e ≥ 10⁻⁸ (o se fija en 0) |

## 6.3 Caso especial: Mercurio

k2_sobre_q = 0.0 (mareas desactivadas). Justificación: la alta excentricidad
real de Mercurio (0.2056) es consecuencia de resonancias seculares con otros
planetas (efecto de N-cuerpos que MHD-INT no modela — ver §8, pendiente).
Sin este caso especial, el modelo de marea de dos cuerpos introduciría una
circularización artificial que no corresponde a la dinámica real.

## 6.4 estimar_B_estrella() por tipo espectral

| Tipo espectral | B_estrella (Tesla) |
|---|---|
| O, B | 5×10⁻² |
| A, F | 5×10⁻³ |
| G | 1×10⁻⁴ |
| K | 2×10⁻⁴ |
| M | 5×10⁻³ |
| Otro | 1×10⁻⁴ |

=============================================================================
7. ÍNDICE DE HABITABILIDAD MAGNÉTICA Y PLANETARIA (MHI)
=============================================================================
**Sin cambios en la fórmula respecto a v4.0. CORRECCIÓN v4.1: reconectado a
la aplicación (hallazgo #5 de auditoría) y aclaraciones metodológicas
añadidas.**

Basado en Driscoll & Barnes (2015) y Kopparapu et al. (2013). Media
ponderada de cuatro componentes:

| Componente | Peso | Descripción |
|---|---|---|
| Escudo magnético (S) | 40% | Fracción de tiempo con R_A > 5 R_p |
| Estabilidad orbital (O) | 20% | 100 × (1 - e/0.35), e_max = 0.35 |
| Campo activo (B) | 30% | Fracción de tiempo con B_p > 0.3 G |
| Calor de marea (T) | 10% | 60 si Q_tidal<1e12 W, 100 si 1e12-1e14, 20 si >1e14 |

MHI = 0.40·S + 0.20·O + 0.30·B + 0.10·T

Categorías: ≥80 alta habitabilidad, 50-80 moderada/límite, <50 estéril.
Si el planeta colapsa (se_estrello=True), MHI se fuerza a 0.

**ACLARACIONES AÑADIDAS EN v4.1 (antes ambiguas en v4.0):**
- El componente S usa `R_m_norm`, que YA incluye la corrección óhmica R_ohm
  (§3.4) — no es el radio de Alfvén crudo.
- Los componentes O y T usan PROMEDIO TEMPORAL de e y Q_tidal sobre toda la
  serie simulada (`e_promedio`, `q_promedio_w`), no valores finales
  puntuales. Verificado contra la implementación real en `habitabilidad.py`.

Implementado en `habitabilidad.py`: `calcular_mhi()`, `categoria_mhi()`.
Reconectado a `app_streamlit.py` en v4.1 (antes desconectado del modo
"Simulación").

=============================================================================
8. LIMITACIONES CONOCIDAS Y TRABAJO FUTURO
=============================================================================
(Nueva sección en v4.1 — consolidada desde MHD-INT_Estado_y_Trabajo_Futuro.md)

## 8.1 El "dínamo" no genera campo — es un modulador de decaimiento

**Actualización v5.0:** el modelo térmico opcional de §4.5 sí implementa
generación real de campo a partir de un flujo convectivo derivado de un
balance térmico del núcleo — no es solo un modulador de decaimiento como
§4.4. Sigue siendo una implementación parcial: no incluye retroalimentación
dinámica completa (rotación real del núcleo, número de Rayleigh, saturación
autoconsistente), y depende de una constante de calibración (C_calib) fijada
contra un único cuerpo (la Tierra). Queda como aproximación de primer orden,
más completa que §4.4 pero no un dínamo autoconsistente. Lo que sigue de
esta sección describe qué haría falta para llegar a eso:
  - Un término de generación, no solo modulación de decaimiento:
    dB_p/dt = -B_p/tau_dipolo + Generación(omega_p, rho_core, eta, q_c, ...)
  - Una escala de saturación B_sat hacia la cual el campo relaje.
  - Una escala de tiempo de regeneración tau_regen, no definida hoy.
  - Dependencia de la vigor convectiva del núcleo (flujo de calor q_c),
    variable que NO existe hoy en `database.py`.

**Experimento realizado (julio 2026):** se probó si la fórmula estándar de
número de Reynolds magnético (Rm = omega·R_p²/eta, Christensen & Aubert 2006)
podía reemplazar el interruptor empírico de §4.4 usando solo datos ya
disponibles. Resultado: el margen de separación entre planetas activos
(Tierra, Júpiter) e inactivos (Venus, Marte) fue de solo ~4x — mucho más
débil que el margen de ~10⁶-10⁷x que ya se tenía con el interruptor basado
en E_p. Conclusión: no hay atajo con los datos actuales; la vía real pasa
por modelar q_c mediante un balance térmico simplificado del núcleo
(calentamiento radiogénico + enfriamiento secular).

**Referencias para la implementación futura:**
  - Christensen, U.R. & Aubert, J. (2006). Scaling properties of
    convection-driven dynamos in rotating spherical shells. Geophys. J.
    Int., 166, 97-114. — Criterio Rm ≳ 50 para existencia del dínamo.
  - Christensen, U.R., Holzwarth, V. & Reiners, A. (2009). Energy flux
    determines magnetic field strength of planets and stars. Nature, 457,
    167-169. — Ley de escala: B²/(2mu_0) ∝ f_ohm·rho^(1/3)·(q_c·L/H_T)^(2/3).
  - Christensen, U.R. (2010). Dynamo scaling laws and applications to the
    planets. Space Sci. Rev., 152, 565-590.

## 8.2 Discrepancia núcleo/superficie de B_p

B_p se usa como un único número tanto para física de superficie (P_ram,
R_alfven, tau_mag, MHI) como para la condición de dínamo en el núcleo
(Elsasser, §4.1). La literatura no ofrece un factor de conversión bien
acotado: estimaciones del campo interior de la Tierra van de ~10⁻³ a
~5×10⁻² T, un rango de 50x. Parte de esta incertidumbre no es solo
atenuación geométrica (1/r³) del mismo campo con la distancia — el campo
toroidal en el núcleo no tiene componente radial y nunca "sale" hacia la
superficie, es una cantidad físicamente distinta al dipolo medido afuera.
No se resuelve en v4.1; documentado para futura decisión de modelado.

## 8.3 Pendientes no relacionados con el dínamo

  - N-body para 9 sistemas con resonancias seculares (incluye Mercurio).
  - ZHM (Zone Habitability Model): sin fórmula candidata exitosa, sigue con
    fallback B > 0.3 G.
  - MHI nunca corrido sobre los 47 planetas completos (solo verificado en
    fórmula).
  - `spec.txt`, `README.txt`, `run_app.py` no revisados.
  - `validacion.py` cubre solo 4 cuerpos del Sistema Solar; ningún
    exoplaneta tiene validación cuantitativa contra datos observacionales.

=============================================================================
9. RESUMEN DEL MODELO ACOPLADO (v4.1)
=============================================================================

Ecuaciones diferenciales ordinarias acopladas, integradas numéricamente con
paso temporal explícito. Orden de actualización por paso (ver
`MotorMHD._paso_temporal()`):

  1. Evolución estelar (NUEVO EN v4.1, antes ausente):
     w_estrella(t), B_estrella(t), rho_sw(t), v_sw(t) = EstrellaEvolutiva.evolucionar(t_gyr)

  2. Migración orbital: da/dt = -a / tau_migracion

  3. Circularización orbital (Hut 1981):
     de/dt = -(21/2)·(k₂/Q)·(M_estrella/M_planeta)·(R_p/a)⁵·n·e

  4. Rotación planetaria (CORREGIDO EN v4.1 — R_ohm ahora sí aplicado):
     domega_p/dt = (tau_mag · R_ohm + tau_lunar) / I_p

  5. Campo magnético planetario (CORREGIDO EN v4.1 — tau_dipolo=1.2 Gyr,
     modulado por interruptor de dínamo, §4.4):
     dB_p/dt = -B_p / tau_dipolo_efectivo(E_p)

  6. Recesión lunar:
     da_luna/dt = - tau_lunar / (0.5 · M_luna · sqrt(G · M_planeta / a_luna))

donde:
  tau_migracion = tiempo de migración orbital (Q_efectivo por tipo, §6.1)
  n = sqrt(G · M_estrella / a³)
  I_p = inercia · M_planeta · R_p²
  R_ohm = 1 + alpha · tanh(E_p - 1)
  tau_dipolo_efectivo = 1.2 Gyr / (1 - factor_dinamo·0.99), factor_dinamo
                        según §4.4

Implementado en `MotorMHD._paso_temporal()` y funciones Numba en
`numba_functions.py`.

=============================================================================
REFERENCIAS CLAVE
=============================================================================

Darwin, G.H. (1879). On the bodily tides of viscous and semi-elastic
spheroids. Phil. Trans. R. Soc. Lond.

Efroimsky, M. & Williams, J.G. (2009). Tidal torques. Celest. Mech. Dyn.
Astron., 104, 257-289.

Goldreich, P. & Soter, S. (1966). Q in the Solar System. Icarus, 5, 375-389.

Hut, P. (1981). Tidal evolution in close binary systems. A&A, 99, 126-140.

Kaula, W.M. (1964). Tidal dissipation by solid friction. Rev. Geophys., 2,
661-685.

Peale, S.J., Cassen, P. & Reynolds, R.T. (1979). Melting of Io by tidal
dissipation. Science, 203, 892-894.

Skumanich, A. (1972). Time scales for CA II emission decay. ApJ, 171, 565.

Strugarek, A. et al. (2017). Magnetic torques on planets in close-in
orbits. ApJ, 847, L16.

Driscoll, P.E. & Barnes, R. (2015). Tidal heating of Earth-like exoplanets
around M dwarfs. Astrobiology, 15, 739-760.

Kopparapu, R.K. et al. (2013). Habitable zones around main-sequence stars.
ApJ, 765, 131.

Vidotto, A.A. et al. (2014). Stellar wind interaction with exoplanets.
MNRAS, 441, 2361.

Murray, C.D. & Dermott, S.F. (1999). Solar System Dynamics. Cambridge
University Press.

Wood, B.E. et al. (2005). New mass-loss measurements from astrospheric
Lyman-alpha absorption. ApJ, 628, L143.

**Nuevas en v4.1 (dínamo, trabajo futuro §8.1):**

Christensen, U.R. & Aubert, J. (2006). Scaling properties of
convection-driven dynamos in rotating spherical shells. Geophys. J. Int.,
166, 97-114.

Christensen, U.R., Holzwarth, V. & Reiners, A. (2009). Energy flux
determines magnetic field strength of planets and stars. Nature, 457,
167-169.

Christensen, U.R. (2010). Dynamo scaling laws and applications to the
planets. Space Sci. Rev., 152, 565-590.

**Nuevas en v5.0 (térmico, atmósfera, oblicuidad):**

Korenaga, J. (2008). Plate tectonics, flood basalts, and the evolution of
Earth's oceans. Terra Nova, 20, 419-439. — Factor stagnant-lid vs mobile-lid.

Owen, J.E. & Jackson, A.P. (2012). Planetary evaporation by UV & X-ray
radiation: basic hydrodynamics. MNRAS, 425, 2931-2947.

Ribas, I. et al. (2005). Evolution of the solar activity over time and
effects on planetary atmospheres. ApJ, 622, 680-694.

Loyd, R.O.P. et al. (2020). MUSCLES XII: measuring the effects of high
XUV radiation on exoplanet atmospheres. ApJ, 890, 23.

Laskar, J. & Robutel, P. (1993). The chaotic obliquity of the planets.
Nature, 361, 608-612.

=============================================================================
FIN DEL DOCUMENTO TEÓRICO
Autor: Roney Rigg Mora
Fecha: Julio 2026
Versión: 5.0
Estado: VALIDADO — validar_todos() aprueba Tierra, Venus, Marte y Júpiter
        en su totalidad, con los módulos térmico/atmósfera/oblicuidad
        desactivados por defecto (comportamiento idéntico a v4.1).
        Limitaciones conocidas documentadas explícitamente en §8, no
        ocultas.
=============================================================================
