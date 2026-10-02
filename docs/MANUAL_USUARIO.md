# MHD-INT — Manual de Usuario

**Autor:** Roney Rigg Mora / Solaris Core
**Versión del software:** 5.2.1 — Septiembre 2026

Este manual explica cómo instalar y usar MHD-INT desde la interfaz gráfica
(Streamlit). Para las ecuaciones y la validación científica del modelo, ver
`MARCO_TEORICO.md`. Para condiciones de uso, ver
`TERMINOS_DE_LICENCIAMIENTO.md`.

---

## 1. Instalación

MHD-INT se distribuye en dos niveles: **Standard** y **Pro**. La
diferencia entre ambos son los modos disponibles (ver §2) — el motor de
física es el mismo en los dos. También hay complementos que se compran
por separado.

| Producto | Precio |
|---|---|
| MHD-INT Standard — licencia de 2 años | $39 |
| MHD-INT Pro — licencia de 2 años | $79 |
| Add-on de Blender | Gratis |
| Plantilla Educativa | $9.99 |
| Plantilla Cinematográfica | $14.99 |
| Plantilla Científica | $14.99 |
| Las 3 plantillas juntas | $29.99 |

*(El add-on de Blender de §18 es gratuito y usa licencia
GPL-3.0-or-later. Con MHD-INT Pro, las 3 plantillas vienen incluidas.)*

**Qué pasa cuando vence la licencia:** la licencia (2 años en las compras de la tienda) tiene
fecha de vencimiento dentro del `license.json`. Al vencer, la app muestra
"🔒 Licencia no válida" y no abre hasta que la renuevas (recibes un
`license.json` nuevo). Tus archivos exportados (PDF, CSV, JSON, videos)
siguen siendo tuyos y no se borran.

### 1.0. Requisitos del sistema

- Windows 10 u 11 de 64 bits.
- 4 GB de RAM como mínimo; 8 GB recomendados (los modos Mapa MHI y
  N-cuerpos usan más memoria y procesador).
- Alrededor de 1 GB libre en disco (el ZIP descargado pesa ~160 MB).
- No necesitas instalar Python.
- Un navegador moderno (Chrome, Edge o Firefox): la interfaz se abre en
  el navegador, en `http://127.0.0.1:8501`, sin salir a internet.
- Internet solo para las funciones que consultan datos en vivo (ver la
  pregunta "¿Necesito internet?" en §21).

### 1.1. Si compraste el ejecutable (.exe) — la vía normal

1. Descomprimí la carpeta que te llegó. Adentro vas a encontrar
   `launcher.exe` y varios archivos de soporte — no muevas ni borres nada
   de ahí, todos son necesarios.
2. Copiá el archivo `license.json` que te mandamos por email a esa **misma
   carpeta**, al lado de `launcher.exe`.
3. Ejecutá `launcher.exe` (doble clic). Se abre una ventana de consola (no
   la cierres mientras usás la app) y el navegador con la interfaz.
   Si Windows muestra "Windows protegió su PC", hacé clic en "Más
   información" > "Ejecutar de todas formas": el ejecutable todavía no
   tiene firma digital, por eso Windows no reconoce al editor.
4. La primera vez que lo corrés, se crea automáticamente un acceso directo
   a MHD-INT en tu escritorio — no hace falta que lo repitas cada vez.

**Si ves el error "🔒 Licencia no válida":** confirmá que `license.json`
esté exactamente en la misma carpeta que `launcher.exe` (no en una
subcarpeta, no en el escritorio). Si compraste MHD-INT y no tenés ese
archivo, escribinos por Ko-fi (ko-fi.com/solariscoremhd).

### 1.2. Si trabajás desde el código fuente (nivel Código Fuente Completo)

Requiere Python 3.10 o superior.

```
pip install -r requirements-pro.txt    # o requirements.txt para Standard
streamlit run app_streamlit_pro.py
```

Necesitás igual un `license.json` válido en la raíz del proyecto — el
código fuente no exime de la licencia.

### 1.3. Versión pública (AGPL, sin licencia)

Existe una versión reducida y gratuita, sin licencia ni modos Pro:

```
pip install -r requirements.txt
streamlit run app_streamlit.py
```

Es la que describen las versiones anteriores de este manual. El resto de
este documento se refiere a las versiones Standard/Pro con licencia.

---

## 2. Estructura de la interfaz

Al abrir la app, el panel izquierdo (barra lateral) muestra tu nombre de
licenciado y el nivel de tu licencia, y debajo un selector **"Modo"**.

**Disponibles en Standard y Pro:**
Ruta de Aprendizaje, Laboratorios Guiados, Educación, Simulación,
Sintético, Mapa MHI, Sensibilidad, Validación, Biblioteca de Fotos,
Glosario.

**Exclusivos de Pro:** Comparador, Disco Protoplanetario (Beta),
Modificador de Sistemas, N-cuerpos (Beta), Migración y Resonancias (Beta),
Efemérides reales (JPL Horizons), Catálogo de Sistemas (Beta), Taller de
Contenido (Sistemas).

Si tenés licencia Standard, el selector directamente no muestra las
opciones de Pro — no es que aparezcan bloqueadas, no existen en tu menú.

---



## 3. Modo Simulación

El modo principal: corre la evolución completa de un planeta de la base de
datos (300 disponibles, incluidos sistemas reales como TRAPPIST-1) a lo
largo del tiempo.

**Parámetros (barra lateral):**
- **Planeta** — selecciona de la base de datos.
- **Tiempo máximo (Gyr)** — hasta cuánto tiempo evolucionar (0.1 a 10 Gyr).
- **Paso (años)** — resolución temporal de la integración (1.000 a 100.000
  años). Pasos más chicos = más precisión, más tiempo de cómputo.

**Control de torques (experimentos):** 3 casillas para aislar el efecto de
cada torque sobre la rotación — útil para depuración o fines didácticos.
Las 3 activas (valor por defecto) dan el comportamiento físico normal:
- Torque magnético
- Marea estelar
- Marea lunar (hoy tiene efecto real para la Tierra —con su Luna— y
  Júpiter —con sus 4 lunas galileanas: Ío, Europa, Ganímedes, Calisto—,
  los dos únicos planetas de la base de datos con lunas cargadas; el
  motor soporta múltiples lunas por planeta, pero la mayoría de los 300
  planetas no tienen ese dato completado)

**Modelo de dínamo y atmósfera** (ambos desactivados por defecto):
- **Activar modelo térmico (Christensen 2009)** — reemplaza el interruptor
  empírico de generación de campo magnético por un balance térmico real del
  núcleo. Ver `MARCO_TEORICO.md` §4.5 para el detalle y las
  limitaciones (validado con datos reales solo para Tierra/Venus/Marte/
  Júpiter; para el resto de la base de datos usa parámetros estimados por
  categoría, no datos observados).
- **Activar pérdida atmosférica (escape XUV)** — simula foto-evaporación
  atmosférica. Si la atmósfera se pierde durante la simulación, el MHI cae
  a 0 automáticamente. Con este modelo activo, se recomienda un paso ≤
  1.000 años (la app avisa si el paso elegido es mayor).

Clic en **"Simular"** para correr. Los resultados aparecen debajo:

- **JSON de resultado** — resumen numérico crudo de la simulación.
- **🛡️ MHI (Índice de Habitabilidad Magnética y Planetaria)** — puntaje de
  0 a 100, con % de tiempo con escudo magnético activo, % de tiempo con
  dínamo activo, excentricidad promedio y calor de marea medio.
- **🔥 Estado térmico del núcleo** (solo si activaste el modelo térmico) —
  temperatura del núcleo-manto, campo generado, y si el dínamo está activo
  (Rm > 40).
- **🌍 Estado de la Atmósfera** (solo si activaste el modelo de atmósfera)
  — masa atmosférica final en "Tierras" y si se perdió o se retuvo.
- **🌍 Evolución de la Oblicuidad** — solo aparece para los 5 cuerpos con
  dato real de oblicuidad (Tierra, Marte, Júpiter, Urano, Venus). Muestra
  el gráfico de oblicuidad en el tiempo con las franjas de riesgo climático
  (< 5° o > 60°).
- **Gráfico principal** — antes fijo (solo a y B), ahora configurable:
  - **Variables a graficar** — elegí cualquier combinación de a, B, ω, e,
    T_cmb, campo generado por dínamo, Rm, masa atmosférica u oblicuidad.
  - **Línea de umbral (opcional)** — marcá un valor de referencia sobre
    cualquiera de esas variables (ej. B=0.3 G) como línea punteada.
  - **Vista de panel** — en vez de un solo gráfico con varias curvas
    superpuestas, muestra un gráfico separado por variable seleccionada.

Debajo de los resultados:
- **📜 Guardar en Historial** — guarda esta corrida en tu historial personal
  (ver §8).
- **📹 Exportar para IA de Video** — descarga un JSON con la serie temporal
  completa (submuestreada a un máximo de 2.000 puntos), pensado para
  alimentar Manim, Blender, Sora u otras herramientas de generación de
  video.
- **🎬 Momentos capturables de esta corrida** — en vez de mirar los miles de
  millones de años completos, detecta automáticamente instantes puntuales
  donde pasó algo (pérdida de escudo magnético, pérdida de atmósfera,
  dínamo que se apaga o se enciende, pico de calor de marea, oblicuidad
  extrema, circularización orbital, colisión, luna perdida o escapada) y te
  deja elegir uno para hacer zoom a esa ventana de tiempo. Usa los mismos
  umbrales que ya definen el MHI — no son criterios nuevos. **Importante:**
  el zoom NO vuelve a simular con más resolución — reusa los puntos que ya
  calculó la corrida original (hasta 2.000). Si necesitás más detalle
  justo en ese momento, corré de nuevo la simulación acotando el tiempo
  máximo cerca de ese evento.

---

## 4. Modo Sintético — Diseña tu propio planeta

Permite crear un planeta hipotético desde cero, ajustando sus parámetros
con sliders, en vez de elegir uno ya cargado en la base de datos.

**Importante:** el planeta sintético parte de la Tierra como base — todo lo
que no ajustás explícitamente (perfil de viento estelar, difusividad del
núcleo, inercia) queda con el valor terrestre. Es una simplificación
declarada: no hay forma físicamente derivada de "inventar" esos valores
para un planeta que no existe.

**Parámetros ajustables:**
Masa, radio, distancia orbital, campo magnético inicial, tipo de planeta
(Terrestre / SuperTierra / Gigante gaseoso / Hot Jupiter / SubNeptuno),
período de rotación, excentricidad inicial, tipo espectral de la estrella
(G2V / G5V / K5V / F8V / M5V), edad de la estrella, tiempo de simulación, y
oblicuidad inicial.

Clic en **"🚀 Simular planeta sintético"**. Los resultados (JSON, MHI y
gráfico de a/B en el tiempo) aparecen igual que en el modo Simulación, pero
sin las secciones de térmico/atmósfera/historial/exportación de video (esas
son exclusivas del modo Simulación).

---

## 5. Modo Mapa MHI

Genera un mapa de calor del MHI variando dos parámetros a la vez: distancia
orbital (eje X) y campo magnético inicial (eje Y), mientras el resto de los
parámetros del planeta base queda fijo.

**Parámetros:**
- Planeta base
- Rango de distancia orbital (UA)
- Rango de campo inicial (Gauss)
- Resolución de la malla (N×N) — ⚠️ el total de simulaciones es N², así que
  una resolución de 25 corre 625 simulaciones. Desde la v5.2, el cálculo se
  reparte automáticamente entre los núcleos de tu procesador (si tenés más
  de una malla chica a la vez, como 2×2, corre en un solo proceso — no vale
  la pena repartir algo tan chico). En una máquina de varios núcleos, una
  malla de 625 simulaciones baja de 10+ minutos a 1-2 minutos.
- Tiempo de simulación por celda (Gyr)

Clic en **"🔥 Generar mapa"**. El resultado es un heatmap interactivo, con
MHI mínimo/máximo/promedio y cuántas combinaciones terminaron en colisión
orbital. Los datos crudos se pueden ver en una tabla expandible y descargar
como CSV.

---

## 6. Modo Sensibilidad

Analiza qué tan sensible es el resultado final (campo magnético) a la
incertidumbre en ciertos parámetros de entrada.

**Básica** — varía simultáneamente `k2_sobre_q` y `densidad_nucleo` de
forma aleatoria N veces (10 a 500 corridas) y muestra un histograma de los
valores finales de campo magnético.

**Extendida** — varía **un solo parámetro elegido** (distancia orbital,
campo inicial, masa, radio, velocidad de rotación, densidad del núcleo,
difusividad, o k2_sobre_q) en un rango definido por vos, y grafica cómo
responde el campo final a ese parámetro específico.

---

## 7. Modo Validación

Botón **"Validar todo"**: corre `validar_todos()`, que compara los
resultados del simulador contra los datos observacionales reales de
Tierra, Venus, Marte, Júpiter, Urano y Neptuno, y muestra el resultado
(aprobado/no aprobado por cuerpo y por variable) en formato JSON. Es la
forma más rápida de confirmar que tu instalación reproduce los resultados
documentados en `MARCO_TEORICO.md`.

**Qué significa "aprueba" (léelo antes de citarlo):** la simulación
arranca con los valores observados hoy (distancia, excentricidad, campo
y rotación de cada planeta) y avanza 4.500 millones de años. "Aprueba"
significa que el modelo es estable y no se aleja más de un 5 % de esos
valores. Es una prueba de consistencia del modelo, **no** una
predicción independiente de la historia del planeta: además, varios
parámetros (decaimiento del dipolo, umbral de dínamo) se calibraron con
la Tierra. Ver `MARCO_TEORICO.md` §8.

---

## 8. Historial de simulaciones

El botón **"📂 Ver historial de simulaciones"** (disponible en cualquier
modo) muestra todas las simulaciones que guardaste con "📜 Guardar en
Historial" en el modo Simulación. Desde ahí podés revisar corridas
anteriores y borrarlas.

---

## 9. Modo N-cuerpos (Beta) — exclusivo Pro

A diferencia de todos los modos anteriores —donde cada planeta se simula
**solo**, sin gravedad entre planetas—, este modo calcula la gravedad real
entre una estrella y hasta 7 planetas simultáneamente (8 cuerpos en
total), integrando sus órbitas con el método velocity Verlet.

**Importante, tal como lo aclara la propia app:** es un módulo
educativo/exploratorio. Para estudios serios de dinámica orbital, la
recomendación del propio software es usar herramientas especializadas
como REBOUND o Mercury-T.

**Cómo usarlo:**
1. Elegí un **sistema (estrella)** — solo aparecen listadas las estrellas
   con 2 o más planetas en la base de datos.
2. Elegí qué **planetas incluir** (hasta 7), ordenados por distancia
   orbital. Por defecto vienen los 3 más cercanos.
3. Definí el **tiempo total a simular** (en años, no Gyr como el resto de
   la app — acá las órbitas son de días o años, no miles de millones).
4. Si alguno de los planetas elegidos tiene lunas reales en la base de
   datos (hoy: Tierra o Júpiter), aparece la opción **"🌙 Incluir lunas
   reales"**. Apagada por defecto a propósito: agregar una luna obliga a
   un paso de integración mucho más chico (su período orbital es de días,
   no de años como los planetas), así que la simulación tarda
   sensiblemente más para el mismo tiempo total.

**Resultado:**
- Pasos completados, error relativo de energía y de momento angular — si
  el error de energía es mayor a 0.1%, la app avisa que el paso puede ser
  demasiado grande para ese sistema y las posiciones podrían no ser
  confiables.
- Colisiones o eyecciones detectadas durante la corrida, si las hubo.
- Si incluiste lunas: las Lunas nuevas y llenas (alineaciones en el
  plano). Este modo arma las órbitas en un mismo plano, sin la inclinación
  de ~5,1° de la órbita lunar, así que **no** puede decir cuáles fueron
  eclipses (en la realidad hay 4 a 7 por año, no uno por Luna nueva).
  El laboratorio "Calendario de eventos" (§10, Pro) usa posiciones reales
  3D de JPL Horizons y sí detecta eclipses posibles, con los límites
  eclípticos (corrección v5.2.1).
- Gráfico de trayectorias (vista desde arriba, en UA).
- Gráfico de energía total en el tiempo, como diagnóstico — si se mantiene
  prácticamente constante, confirma que el integrador está conservando la
  física correctamente.

**Límite técnico:** si el sistema pide más de 2.000.000 de pasos para el
tiempo total elegido, la app corta antes de arrancar y sugiere reducir el
tiempo — típico en sistemas con órbitas muy cerradas (períodos de días),
donde unos pocos años ya alcanzan para ver varias órbitas completas.

---

## 10. Laboratorios Guiados

Misiones educativas paso a paso: la app corre las simulaciones por vos y
evalúa automáticamente si cumpliste el objetivo, con preguntas de
reflexión e insignia al terminar. Es distinto de **🗺️ Ruta de
Aprendizaje** (esa es lectura + ejercicios sin simulación automática).

**Cómo se usa:** filtrás por nivel (Secundaria / Universidad / Científico
/ Todos), elegís un laboratorio, y avanzás paso a paso — cada paso te pide
simular algo puntual, observar un resultado, o comparar dos corridas. Al
terminar todos los pasos, la app evalúa tus resultados contra criterios
numéricos concretos (no es una autoevaluación) y te dice si aprobaste,
mostrando qué condición se cumplió y cuál no si fallaste alguna.

**Los 8 laboratorios disponibles hoy:**

| Laboratorio | Nivel | Dificultad | Duración | Insignia |
|---|---|---|---|---|
| El Escudo Invisible: Marte vs. Tierra | Secundaria | ⭐ | 10-15 min | Guardián del Campo Magnético |
| Venus: el planeta al revés | Secundaria | ⭐ | 15-20 min | Explorador de Venus |
| La zona habitable | Secundaria | ⭐⭐ | 20-25 min | Guardián de la Zona Habitable |
| El destino de Marte | Secundaria | ⭐⭐ | 20-25 min | Salvador de Marte |
| Exoplanetas en zona habitable: TRAPPIST-1e | Universidad | ⭐⭐ | 30-35 min | Cazador de Exoplanetas |
| La influencia de la Luna | Universidad | ⭐⭐ | 25-30 min | Maestro de Lunas |
| Calendario de eventos del Sistema Solar 🔒 | Universidad | ⭐⭐ | 45-60 min | Astrónomo del Tiempo |
| Validación con datos reales | Científico | ⭐⭐⭐ | 20-30 min | Validador Científico |

🔒 = requiere licencia Pro (usa simulación N-cuerpos con condiciones
reales de JPL Horizons — los otros 7 están en Standard y Pro).

**Sobre "El destino de Marte" en particular:** el propio laboratorio te
avisa de una limitación real del modelo — el escape atmosférico no está
acoplado al campo magnético en esta versión (ver §3), así que ahí
trabajás con la eficiencia de escape en vez del campo para ver el efecto.
No es un error de la consigna, es el laboratorio siendo honesto sobre
qué puede y no puede mostrar el simulador tal como está hoy.

---

---

## 11. Modo Comparador — exclusivo Pro

Simulá dos planetas lado a lado (A y B) y compará su evolución en la
misma pantalla — cada uno con su propio planeta, tiempo, modelo térmico y
atmósfera activables por separado.

**Resultado:** diferencias directas (ΔB, ΔMHI, Δa, Δe), un veredicto de
cuál es más habitable según el MHI, tarjetas individuales por planeta
(con su video si corriste con serie), y una tabla comparativa detallada
que incluye la penalización por oblicuidad de cada uno.

Las dos simulaciones corren en secuencia, no en paralelo (Streamlit no es
multi-hilo por sesión) — vas a ver una barra de progreso combinada
mientras corre primero A y después B.

---

## 12. Modo Disco Protoplanetario (Beta) — exclusivo Pro

Modela la desalineación (ángulo β) entre el eje de rotación de una
estrella joven y el eje de su disco protoplanetario, por acoplamiento
magnético y de acreción — implementa la Ecuación 23 de Lai, Foucart &
Lin (2011).

**⚠️ Advertencia que la propia app muestra siempre, no solo a veces:**
los parámetros λ (torque de acreción, alineador) y ζ̃ (torque de warping
magnético, desalineador) son valores elegidos dentro de un rango
plausible — el propio paper que se implementó los describe como "en gran
medida sin restringir". Este módulo explora un escenario plausible, **no
predice** el β real de una estrella concreta.

**Cómo usarlo:** elegís una estrella T Tauri de un catálogo (con su
fuente bibliográfica si la tiene) o cargás parámetros personalizados
(masa, radio, campo magnético, período de rotación, tasa de acreción,
tiempo de disipación del disco), ajustás λ, ζ̃, la desalineación inicial
y el tiempo a simular. La app te avisa antes de correr si, con esos
valores, β=0 es un equilibrio estable (el sistema tiende a alinearse) o
inestable (puede desarrollar desalineación).

**Resultado:** evolución de β en el tiempo, β de equilibrio analítico si
existe, radio de truncamiento del disco, y tasa de acreción en el tiempo.

**Validación real, pero parcial:** el radio de truncamiento calculado
para la estrella DO Tau reproduce el valor publicado (Bessolaz et al.
2008) dentro de ~15% — eso valida solo esa parte del modelo, no la
evolución completa de β (no existe una estrella real con β medido con
precisión suficiente para esa comparación).

---

## 13. Modo Modificador de Sistemas — exclusivo Pro

Tomá un planeta real de la base de datos, modificale la órbita, la masa,
el campo magnético inicial o agregale/reemplazale una luna, y comparalo
contra el original con el mismo motor de simulación.

**Modificaciones disponibles** (podés combinar más de una): mover a otra
órbita, cambiar masa, cambiar campo magnético inicial, agregar o
reemplazar una luna (masa y distancia inicial).

**Qué NO se puede simular acá, y por qué** (la propia app lo explica en
un desplegable, en vez de mostrar un resultado sin respaldo físico):
quitar un planeta del sistema para ver si eso desprotege a otro, o
agregar un "Júpiter caliente" para ver si expulsa a la Tierra. Los dos
necesitan gravedad planeta-planeta, y el motor de MHD-INT simula cada
planeta de forma independiente (estrella-planeta-luna) — sacar o meter
otro planeta de la lista no cambia en nada la física simulada del que te
interesa.

**Resultado:** ΔB, ΔMHI, ΔP_rot, Δa entre original y modificado, si el
campo quedó protegido en cada caso, si el planeta modificado se estrelló,
y un gráfico de la evolución del campo magnético de los dos superpuestos.

---

## 14. Modo Catálogo de Sistemas (Beta) — exclusivo Pro

Una galería de arquitecturas planetarias reales agrupadas por estrella
(incluye sistemas como TRAPPIST-1), con ficha técnica, candidatos a
resonancia orbital, y la opción de simularlos juntos con el motor de
N-cuerpos (hasta 7 planetas + estrella, igual límite que el modo
N-cuerpos de §9).

**Ficha del sistema:** cantidad de planetas, masa estelar, cuántos
planetas tienen distancia orbital real (vs. estimada), tabla completa
(semieje, masa, período, tipo, categoría, fuente del dato orbital).

**Candidatos resonantes:** detección cinemática entre vecinos (tolerancia
2%) — la app aclara que son *candidatos*, no confirmaciones: la
simulación conjunta usa fases iniciales arbitrarias (no efemérides reales)
y migración prescrita, salvo para el Sistema Solar, donde podés usar
condiciones iniciales reales de JPL Horizons.

**Puente al Taller de Contenido:** después de simular, podés exportar los
eventos detectados como JSON y generar un clip de las trayectorias o un
storyboard — desde ahí, el modo Taller de Contenido (§16) toma la posta
para armar guion y PDF.

---

## 15. Modo Migración y Resonancias (Beta) — exclusivo Pro

Modela la evolución del semieje orbital por migración prescrita en un
disco simple (masa del disco decayendo exponencialmente en el tiempo), y
detecta candidatos a resonancia orbital de la misma forma que el
Catálogo.

**Aviso explícito del propio módulo:** es un modelo exploratorio, **no
autoconsistente** — no reemplaza una simulación hidrodinámica real del
disco. Sirve para entender cualitativamente cómo la migración puede
empujar planetas hacia (o sacarlos de) una resonancia, no para predecir
la migración real de un sistema concreto.

---

## 16. Modo Taller de Contenido (Sistemas) — exclusivo Pro

Toma el JSON de eventos que exportás desde el Catálogo de Sistemas (§14)
y genera un guion narrativo y/o un PDF ejecutivo del sistema completo,
pensados para producir contenido audiovisual o de divulgación.

**Cómo usarlo:** subís el archivo `.json` que descargaste del Catálogo
("⬇️ Descargar eventos"). La app recalcula la tabla de planetas y los
candidatos de resonancia en el momento (esos datos no viajan en el JSON,
solo los eventos) — **si el sistema cambió en `database.py` desde que lo
simulaste**, el PDF puede no coincidir exactamente con esa corrida
original.

**Tres salidas posibles:**
- **Guion narrativo** (.txt) — texto listo para locución o guion de video.
- **PDF ejecutivo** — no incluye el gráfico de trayectorias (esa imagen
  no viaja en el JSON exportado, solo los eventos).
- **PDF para NotebookLM** — incluye el guion narrativo completo como
  texto, pensado específicamente como insumo para generar un podcast con
  NotebookLM.

---

## 17. Modo Efemérides reales (JPL Horizons) — exclusivo Pro

Consulta posiciones **reales, observacionales** de cuerpos del Sistema
Solar para un rango de fechas, directo de JPL Horizons (NASA/JPL) — esto
no es una simulación del motor de MHD-INT, es el dato real medido.

**Para qué sirve en la práctica:** comparar dónde está un planeta *de
verdad* en una fecha puntual (por ejemplo, una alineación real) contra lo
que predice la integración de MHD-INT desde condiciones iniciales — el
mismo tipo de comparación que usa el laboratorio "Calendario de eventos
del Sistema Solar" (§10) y el modo N-cuerpos con lunas reales (§9).

**Cómo usarlo:** elegís un cuerpo y un rango de fechas (inicio y fin).
Necesita conexión a internet — consulta un servicio externo (JPL
Horizons), no datos locales.

---

## 18. Exportar a Blender

Disponible en los resultados de **Simulación** y **Sintético**, siempre
que la corrida se haya hecho con serie temporal activada. El modo
N-cuerpos (§9) no tiene ninguna opción de exportación todavía; el
Catálogo de Sistemas (§14) tiene la suya propia, distinta (clip de
trayectorias y storyboard, no un archivo para Blender) — ver §16.

El botón **"🎬 Exportar a Blender (.json)"** descarga un archivo con la
trayectoria real calculada por el motor de física — no una animación
genérica: cada punto de la órbita en Blender es un valor que MHD-INT
realmente calculó, para el planeta, la estrella y las lunas que tenga
(incluye lunas múltiples, ej. Júpiter con sus 4 lunas galileanas).

**Para verlo en Blender**, necesitás instalar el add-on importador —
existen dos versiones:

- **`mhdint_importer` (Blender 4.2+, recomendado):** panel fijo en la
  barra lateral (`View3D > N > MHD-INT`), con botón de recargar datos,
  exportar la escena y trazar curvas de órbita visibles.
- **`blender_importer.py` (Blender 3.6 a 4.1):** un solo archivo, se usa
  desde `File > Import > MHD-INT Simulation (.json)`.

Instrucciones de instalación completas para las dos: `assets/README_blender.md`
(viene junto con la distribución de MHD-INT).

**Plantillas de escena (venta separada):** además del importador, hay 3
plantillas de Blender ya armadas con materiales, luces y cámara —
Educativa, Cinematográfica y Científica — pensadas para no tener que
armar la iluminación/cámara vos mismo cada vez. Se compran aparte del
add-on (ver tabla de precios, §1).

---

## 19. Exportar datos (CSV / Parquet)

En los resultados de Simulación y Sintético, además del PDF y Blender,
podés descargar la serie temporal completa como **CSV** o **Parquet**
(Parquet requiere `pyarrow`, se instala aparte si no lo tenés — el botón
de CSV siempre funciona sin dependencias extra).

**Qué incluye cada fila:** un punto de tiempo con todas las variables de
la simulación (semieje, velocidad angular, campo magnético, excentricidad,
calor de marea, y si corriste con modelo térmico/atmósfera, también esas
columnas). La columna **`a_lunas_ua`** trae la distancia de **todas** las
lunas del sistema en esa fila, no solo la primera — para un sistema como
Júpiter con 4 lunas, vas a ver una lista de 4 valores en formato JSON
dentro de esa celda (Excel y pandas la leen bien, solo hay que saber que
no es un número simple si el planeta tiene más de una luna).

---

## 20. Reportes en PDF

El botón **"📄 Generar Reporte PDF"** (en los resultados de Simulación y
Sintético) arma un reporte ejecutivo: resumen del MHI, desglose de sus
4 componentes, gráfico de evolución temporal, y gauge del número de
Reynolds magnético.

**Marca de agua de trazabilidad:** todo PDF que generás lleva tu nombre
de comprador (el mismo que figura en tu `license.json`) como marca de
agua diagonal, tenue, sobre el contenido — para que un PDF compartido sin
permiso se pueda rastrear a quién se le vendió la licencia. No se puede
desactivar desde la interfaz.

---

## 21. Preguntas frecuentes

**¿Por qué no veo la sección de oblicuidad en mi planeta?**
Porque solo 5 cuerpos (Tierra, Marte, Júpiter, Urano, Venus) tienen dato
real de oblicuidad inicial en la base de datos. Para el resto —incluidos
todos los exoplanetas— mostrar ese gráfico implicaría mostrar un supuesto
(0°) como si fuera un dato real, así que se omite. En el modo Sintético sí
aparece siempre, porque ahí la oblicuidad la elegís vos.

**¿Por qué el modelo térmico da resultados raros en un exoplaneta?**
Desde v5.2, los 300 planetas de la base de datos tienen parámetros
térmicos, pero solo Tierra/Venus/Marte/Júpiter son datos reales o
calibrados — el resto son estimados por categoría de planeta (terrestre,
superTierra, subNeptuno, gigante), documentados como tales
(`termico_estimado=True` en `database.py`). Útiles para exploración
cualitativa, no para afirmar un valor preciso. Ver limitaciones en
`MARCO_TEORICO.md` §4.5 y §8.

**Mi simulación con atmósfera activada se ve inestable / con saltos.**
Bajá el paso de tiempo a 1.000 años o menos — la app lo advierte
automáticamente si detecta un paso mayor con este modelo activo.

**¿Puedo modificar la base de datos de planetas?**
Sí, está en `database.py`. Si adquiriste el nivel de Código Fuente
Completo, podés modificarla y redistribuir según los términos de esa
licencia — ver `TERMINOS_DE_LICENCIAMIENTO.md`.

**¿Por qué activar/desactivar el campo magnético no cambia si Marte
pierde su atmósfera?**
Es una limitación real del modelo actual, no un bug: el escape
atmosférico (§3) depende del flujo XUV de la estrella y la gravedad del
planeta, pero todavía no está acoplado al campo magnético. El laboratorio
"El destino de Marte" (§10) usa la eficiencia de escape como palanca en
vez del campo, justamente por esto.

**Tengo licencia Standard y no veo Comparador / N-cuerpos / Catálogo /
etc. en el menú — ¿está roto?**
No — esos modos son exclusivos de Pro (ver la lista completa en §2). Con
Standard, el selector de modo directamente no los muestra como opción.

**¿Por qué mis PDF tienen mi nombre escrito en diagonal encima?**
Es la marca de agua de trazabilidad (§20) — identifica a qué licencia
pertenece ese PDF si se comparte sin permiso. Viene siempre, no se puede
apagar desde la interfaz.

**¿Necesito internet para usar MHD-INT?**
No, para el motor de simulación en sí — todo corre localmente. Las
excepciones son **Efemérides reales** (§17), que consulta JPL Horizons en
vivo, y la opción **"Viento solar real (NOAA)"** del modo Simulación, que
descarga las mediciones del día del satélite de NOAA en L1. El modo N-cuerpos con "lunas reales" (§9)
también consulta ese servicio la primera vez que pedís una fecha (después
queda en caché local).

**¿Cuál es la diferencia entre el add-on de Blender y las Plantillas de
Blender?**
Son dos productos distintos (§18). El **add-on** (`mhdint_importer` o
`blender_importer.py`) es el que lee el archivo que exportás desde
MHD-INT y arma los objetos/animación en Blender — sin él, no podés
importar nada. Las **Plantillas** son escenas de Blender ya armadas con
materiales, luces y cámara en un estilo particular (Educativa,
Cinematográfica, Científica) — un punto de partida visual, no reemplazan
al add-on.
