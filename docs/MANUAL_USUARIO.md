# MHD-INT v5.0 — Manual de Usuario

**Autor:** Roney Rigg Mora
**Versión del software:** 5.0 — Julio 2026

Este manual explica cómo instalar y usar MHD-INT desde la interfaz gráfica
(Streamlit). Para las ecuaciones y la validación científica del modelo, ver
`Marco_Teorico_v5_0.md`. Para condiciones de uso, ver
`TERMINOS_DE_LICENCIAMIENTO.md`.

---

## 1. Instalación

Requiere Python 3.9 o superior.

```
pip install -r requirements.txt
streamlit run app_streamlit.py
```

Esto abre la interfaz en el navegador (por defecto en `http://localhost:8501`).

---

## 2. Estructura de la interfaz

Al abrir la app, el panel izquierdo (barra lateral) tiene un selector
**"Modo"** con 5 opciones: **Simulación**, **Sintético**, **Mapa MHI**,
**Sensibilidad** y **Validación**. Debajo del selector de modo está el botón
**"📂 Ver historial de simulaciones"**, disponible en todos los modos (ver
§8).

---

## 3. Modo Simulación

El modo principal: corre la evolución completa de un planeta de la base de
datos (47 disponibles) a lo largo del tiempo.

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
- Marea lunar (solo tiene efecto para la Tierra, que es el único planeta
  con luna en la base de datos)

**Modelo de dínamo y atmósfera** (ambos desactivados por defecto):
- **Activar modelo térmico (Christensen 2009)** — reemplaza el interruptor
  empírico de generación de campo magnético por un balance térmico real del
  núcleo. Ver `Marco_Teorico_v5_0.md` §4.5 para el detalle y las
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
  una resolución de 25 corre 625 simulaciones. Resoluciones altas pueden
  tardar varios minutos.
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
Tierra, Venus, Marte y Júpiter, y muestra el resultado (aprobado/no
aprobado por cuerpo y por variable) en formato JSON. Es la forma más rápida
de confirmar que tu instalación reproduce los resultados documentados en
`Marco_Teorico_v5_0.md`.

---

## 8. Historial de simulaciones

El botón **"📂 Ver historial de simulaciones"** (disponible en cualquier
modo) muestra todas las simulaciones que guardaste con "📜 Guardar en
Historial" en el modo Simulación. Desde ahí podés revisar corridas
anteriores y borrarlas.

---

## 9. Preguntas frecuentes

**¿Por qué no veo la sección de oblicuidad en mi planeta?**
Porque solo 5 cuerpos (Tierra, Marte, Júpiter, Urano, Venus) tienen dato
real de oblicuidad inicial en la base de datos. Para el resto —incluidos
todos los exoplanetas— mostrar ese gráfico implicaría mostrar un supuesto
(0°) como si fuera un dato real, así que se omite. En el modo Sintético sí
aparece siempre, porque ahí la oblicuidad la elegís vos.

**¿Por qué el modelo térmico da resultados raros en un exoplaneta?**
Desde v5.2, los 47 planetas de la base de datos tienen parámetros
térmicos, pero solo Tierra/Venus/Marte/Júpiter son datos reales o
calibrados — el resto son estimados por categoría de planeta (terrestre,
superTierra, subNeptuno, gigante), documentados como tales
(`termico_estimado=True` en `database.py`). Útiles para exploración
cualitativa, no para afirmar un valor preciso. Ver limitaciones en
`Marco_Teorico_v5_0.md` §4.5 y §8.

**Mi simulación con atmósfera activada se ve inestable / con saltos.**
Bajá el paso de tiempo a 1.000 años o menos — la app lo advierte
automáticamente si detecta un paso mayor con este modelo activo.

**¿Puedo modificar la base de datos de planetas?**
Sí, está en `database.py`. Si adquiriste el nivel de Código Fuente
Completo, podés modificarla y redistribuir según los términos de esa
licencia — ver `TERMINOS_DE_LICENCIAMIENTO.md`.
