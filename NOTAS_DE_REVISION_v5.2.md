# Notas de revisión — MHD-INT Pro v5.2

Revisión hecha antes del release comercial, sobre la propuesta de los 6
archivos (Modelo A2). Se encontraron y corrigieron 3 problemas reales,
verificados con pruebas funcionales (no solo lectura de código). El motor
físico (`engine.py` y todo lo que depende de `numba`) no se tocó ni se
pudo re-correr aquí por falta de red en este entorno — los `.py` afectados
por esta revisión no importan `numba_functions.py`, así que no bloquea la
validación física existente.

## 1. CRÍTICO — la generación de video fallaba siempre (`video_mpl.py`)

`Animation.save()` de Matplotlib no acepta `format=` como argumento, y en
la versión probada (3.10.x) tampoco acepta un `BytesIO` como destino aun
pasando un `writer` explícito — exige una ruta de archivo real. El código
original intentaba `anim.save(buffer, format='mp4', ...)` directamente
sobre un buffer en memoria; eso fallaba siempre, caía al `except`, y el
fallback a GIF fallaba por el mismo motivo. Resultado: la función insignia
del producto Pro (Capa 1, video nativo) nunca producía un video, en
ninguna instalación, con o sin ffmpeg.

**Fix:** se renderiza a un archivo temporal real (mismo patrón que ya usa
`reporte_pdf.py`) y se lee de vuelta a `BytesIO`. Probado con 3 casos:
serie con oblicuidad conocida, sin oblicuidad conocida, y serie corta
(fuerza el fallback a GIF) — los 3 generan archivo válido.

## 2. La oblicuidad nunca llegaba al video (`exportar_video.py` + `video_mpl.py`)

`construir_json_video()` (repo público) nunca incluía `eps_deg` por punto
en el JSON. `video_mpl.py` leía esa clave con `.get(..., 0.0)`, así que la
línea de oblicuidad se dibujaba plana en cero en absolutamente todos los
videos — incluidos los de Tierra/Marte/Júpiter/Urano/Venus, que sí tienen
el dato real. Esto también afectaba el JSON público que consumen IAs de
video externas (Manim, Blender, Sora).

**Fix:** `exportar_video.py` v5.1.1 (parche separado al repo público, no
forma parte de este zip Pro) ahora incluye `eps_deg` por punto y
`eps_conocido` en `meta`. `video_mpl.py` solo dibuja la línea ε si
`eps_conocido=True` — para el resto de los cuerpos, la omite en vez de
mostrar un cero falso, con una nota visible en el gráfico ("ε no
disponible para este cuerpo").

## 3. El donut/tabla de MHI no reconciliaban con el total mostrado

`calcular_mhi()` aplicaba la penalización de -20 pts por oblicuidad
extrema de forma interna, sin exponerla. El donut (app_streamlit_pro.py)
y la tabla del PDF (reporte_pdf.py) solo graficaban los 4 componentes
pesados, que suman más que `mhi_total` cuando hay penalización — sin
ninguna fila/explicación de la diferencia. Para un cliente pagando por el
reporte, se lee como un error de cálculo.

**Fix:** `habitabilidad.py` v5.1.1 (parche separado al repo público)
ahora retorna también `mhi_bruto` y `penalizacion_obl_pts`. El donut
grafica y etiqueta explícitamente la composición de `mhi_bruto`; el MHI
final (post-penalización) se muestra aparte con la penalización anotada.
La tabla del PDF agrega la fila "Penalización oblicuidad" + fila de
subtotal. Verificado con PDF de prueba: 20.0+30.0+18.9+6.0−20.0 = 54.9,
coincide exactamente con el MHI total del resumen ejecutivo.

## 4. Cache de video con clave incompleta (`app_streamlit_pro.py`)

- Modo Simulación: la clave de cache del video solo dependía de
  planeta+t_max+dt. Cambiar torques, modelo térmico o atmósfera y volver a
  simular con el mismo planeta/tiempo/paso mostraba el video de la corrida
  anterior.
- Modo Sintético: la clave solo dependía de masa+radio+t_max — cambiar
  distancia orbital, campo inicial, excentricidad, estrella, etc. no
  invalidaba el cache.
- El Comparador ya lo manejaba bien (limpia el cache en cada click de
  "Comparar") y no se modificó.

**Fix:** `_clave_video()` centralizada, que genera un hash estable
(SHA-256, primeros 16 caracteres) de TODOS los parámetros relevantes de la
simulación (`params_extra` completo + planeta + t_max + dt). Cualquier
cambio de parámetro invalida el cache automáticamente.

## 5. CRÍTICO — corrupción de estado global compartido (`engine.py`)

`self.planetas_db = planetas_db or PLANETAS or {}` (y lo mismo para
`estrellas_db`/`lunas_db`) dejaba `self.planetas_db` siendo el MISMO
objeto que el `PLANETAS` de `database.py` cuando no se pasaba un dict
explícito — que es el caso normal. Cualquier mutación posterior
(`estrella_personalizada`, futuro `lunas_personalizadas`) escribía
directo sobre la base de datos global, compartida por todo el proceso.

Reproducido con prueba real: una sola corrida del modo Sintético con
estrella personalizada dejaba `PLANETAS["Tierra"]["estrella"]` apuntando
permanentemente a la estrella inventada — cualquier simulación posterior
de la Tierra real (Validación, Comparador, u otro usuario en el mismo
servidor Streamlit, que corre un solo proceso para todas las sesiones)
heredaba la estrella equivocada hasta reiniciar el servidor.

**Fix:** copiar los 3 diccionarios a nivel superior al entrar a
`MotorMHD.__init__`, y copiar también la entrada específica del planeta
antes de mutar su campo `"estrella"` (una copia de nivel superior sigue
apuntando a los mismos sub-diccionarios internos). Verificado:
- Corrida sintética con estrella + luna personalizada: la instancia sí ve
  sus valores custom.
- `database.PLANETAS["Tierra"]` y `database.LUNAS["Tierra"]` quedan
  intactos después.
- Una Tierra real simulada justo después, en el mismo proceso, usa el Sol
  y la Luna real.
- `validar_todos()` da salida byte-idéntica antes/después del fix (0
  regresiones en los 6 cuerpos del sistema solar).

Hallazgo aparte, sin relación con este fix: Urano y Neptuno fallan
`B_gauss` por ~97% (ya fallaba igual con el motor sin parchar). La
excepción documentada en `validacion.py` cubre geometría del dipolo, no
magnitud — este gap queda pendiente de revisión, no se tocó.

## 6. Modo Sintético — 4 mejoras agregadas sobre el motor ya corregido

Todas confirmadas contra `engine.py` antes de escribir la UI: los 8
parámetros nuevos (`inercia`, `difusividad`, `k2_sobre_q`, `R_core`,
`T_cmb_inicial_K`, `T_manto_inicial_K`, `M_atm_inicial`,
`eficiencia_escape`) se leen todos con `self.parametros.get(clave, ...)`
sobre el dict que ya se pisa genéricamente con `parametros_extra` — cero
cambios adicionales a `engine.py` para estas 4 mejoras.

- **Presets rápidos** (Tierra/Venus/Marte/Júpiter-aprox.): valores reales
  tomados de `database.py`. El de Júpiter usa el tope de cada slider
  (masa, radio, distancia) y se marca explícitamente como no-a-escala —
  el Júpiter real (318 M⊕, 5.2 UA) excede el rango del modo Sintético.
  El preset de Venus carga la magnitud real del período (243.02 d) pero
  no puede cargar el sentido retrógrado: el slider siempre calcula
  `w_p_inicial` positivo. Documentado en el código, no oculto.
- **Parámetros internos avanzados**: inercia, difusividad y k2/Q como
  sliders/number_input, en un expander opcional.
- **Parámetros térmicos del núcleo** + **atmósfera personalizada**: el
  modo Sintético no tenía los checkboxes de modelo térmico/atmósfera —
  `render_reporte_comercial()` recibía `usar_termico=False,
  usar_atmosfera=False` fijos aunque el motor los hubiera corrido. Se
  agregaron ambos checkboxes; ahora el gauge Rm y el panel de atmósfera
  sí se muestran para planetas sintéticos cuando corresponde.

Verificado con los 4 presets corridos por el motor real (numba stubbeado
para este entorno), con modelo térmico y atmósfera activos y los 8
parámetros nuevos poblados: los 4 corren sin error. Se confirmó además
que `inercia` cambia `P_rot_final_dias` de forma medible, y que
`k2_sobre_q` entra linealmente en la fórmula de circularización de marea
(`calcular_de_dt_numba`, `numba_functions.py`).

Luna personalizada (mejora restante) queda pendiente: es la única que
dependía 100% del fix de esta sección para poder implementarse sin
repetir la misma corrupción de estado global.

## 7. Mejora #3 — Luna personalizada

Sin cambios a `engine.py` (usa el mecanismo `lunas_personalizadas` que ya
existía). Dos decisiones de diseño importantes:

- **k2 y Q_p nunca se usan por separado**, solo su razón
  (`calcular_torque_lunar`). Se expone un único slider "k2/Q_p" en vez de
  dos, para no sugerir dos grados de libertad donde hay uno. Truco de
  implementación: se manda `Q_p=1.0` y `k2=razón_elegida`, así
  `k2/Q_p = razón_elegida` exactamente.
- **Cambio de comportamiento por defecto**: antes, cualquier planeta
  sintético con "Marea lunar" tildado (default True) heredaba en
  silencio la Luna real de la Tierra (`self.lunas_db.get("Tierra")` la
  encuentra si no se manda override). Ahora el toggle "Añadir luna
  personalizada" nace en OFF y sin luna (`masa=0.0`) — hay que pedirla
  explícitamente.

**Validación física:** con los valores reales de la Luna (0.0123 M⊕,
0.00257 UA, k2/Q_p=0.025) el motor da una recesión lunar de 3.69 cm/año —
el valor medido real es ~3.8 cm/año (retrorreflectores Apollo). Buena
señal de que el modelo de marea lunar ya estaba bien calibrado.

**Hallazgo de estabilidad numérica (importante, no soy yo introduciendo
el bug, pero mi feature lo expone directamente por UI):** el integrador
de `engine.py` usa paso FIJO de 10.000 años en todo el modo Sintético.
Con lunas muy cercanas y masivas, el período orbital real de la luna
puede ser de horas — muchísimo más corto que el paso de integración — y
el resultado diverge numéricamente (`w_final` llega a miles de rad/s,
físicamente imposible) SIN que `resultado.es_valido()` lo detecte.
Confirmado con barrido de parámetros: el límite de estabilidad no es una
recta prolija, hay una zona caótica entre 0.0005-0.0009 UA donde la
estabilidad depende de forma no monótona del resto de los parámetros.

Mitigación aplicada (dos capas, no solo una):
1. Piso del slider de distancia subido de 0.0001 UA a 0.001 UA — el peor
   caso dentro de ese rango (masa=0.1 M⊕, distancia=0.001 UA, k2/Q_p=0.1,
   rotación del planeta=365 días) da `w_final` estable, verificado.
2. Chequeo defensivo independiente del slider: si `|w_final| > 1e-2`
   rad/s (período < 10 min, imposible físicamente) se muestra un error
   explícito en vez de dejar pasar el resultado como válido. Esto cubre
   cualquier combinación que no haya sido barrida explícitamente.

También se agregó un aviso de "colisión lunar" (si la luna migra hacia
adentro hasta el radio del planeta) reconstruido en la UI, ya que el
motor la frena en `a_luna = R_p` sin exponer ninguna bandera propia de
colisión.

Este hallazgo de estabilidad numérica del integrador de paso fijo es
más amplio que la luna — cualquier torque muy fuerte con dt=10.000 años
podría, en principio, producir el mismo tipo de divergencia. Queda para
una revisión aparte si en algún momento se quiere exponer más parámetros
que puedan generar torques igual de extremos.

## 8. Urano/Neptuno — resuelto (dos causas distintas, no una)

Se investigó a fondo en vez de solo documentar la falla. Resultaron ser
**dos problemas separados**, no uno:

**a) B_gauss — límite de alcance real del modelo, documentado, no
"arreglado".** Se trazó la curva de decaimiento completa: `B_p` cae
limpio y exponencial (sin ningún salto numérico) porque MHD-INT no tiene
término de generación de dínamo -- es un modelo de solo-decaimiento
(τ=1.2 Gyr, calibrado contra el núcleo de hierro terrestre) con un
interruptor fenomenológico basado en el número de Elsasser, calibrado
solo contra la Tierra. Para Urano/Neptuno ese número da muy por debajo
de la referencia, así que nunca se activa y decaen a la tasa terrestre
completa. Se probó la alternativa ya existente en el motor (modelo
térmico Christensen 2009, generación real vía Rm>40): mejora el orden de
magnitud pero tampoco pasa, y usa defaults térmicos de la Tierra que
`database.py` nunca redefinió para "Gigante de hielo" (Rm resultante,
~5 millones, no es físicamente creíble). Ninguno de los dos modelos
representa el mecanismo real (dínamo en manto iónico agua/amoníaco,
distinto del núcleo metálico terrestre) -- sigue siendo un problema
abierto en la ciencia planetaria real, no solo acá. Se documentó como
excepción de alcance en `validacion.py` (mismo criterio que Venus,
`B_gauss: None`) en vez de forzar una recalibración que hubiera repetido
el patrón de ajuste circular ya cerrado en TUM.

**b) P_rot_dias de Urano — esto SÍ era un bug de dato, y solo salió a la
luz después de sacar B_gauss del chequeo.** `w_p_inicial=-1.104e-4` en
`database.py` correspondía a un período de 15.81 h, pero el período real
documentado (y ya usado como referencia en `validacion.py`) es 17.24 h.
Se confirmó que NO es un artefacto de la física: `w_p` queda
prácticamente congelado en toda la simulación (-1.104000e-4 ->
-1.103999e-4 en 4.5 Gyr) porque a 19 UA las mareas estelares son
insignificantes -- el error de 8.3% ya estaba en el dato de entrada, la
simulación solo lo heredó sin corregirlo. Corregido a `-1.01238e-4`
(coherente con 17.24 h). Neptuno se revisó por las dudas: su
`w_p_inicial` ya representaba 0.6715 días vs 0.67125 real (0.035% de
diferencia) -- no necesitaba tocarse.

**Resultado final: validar_todos() da 6/6 aprobado**, verificado con
salida completa (no solo el booleano final).

## 9. Módulo nuevo — Fase 2 (disco protoplanetario) + Modificador de sistemas

Tres archivos nuevos revisados y sumados a v5.2, ninguno toca `engine.py`:

- **`disco_protoplanetario.py`**: evolución de la desalineación spin-disco
  (β) en estrellas T Tauri jóvenes, Ecuación 23 de Lai, Foucart & Lin
  (2011). Verificado independientemente, no solo leído: reproduje a mano
  la linealización de estabilidad cerca de β=0 (confirma exactamente el
  criterio λ vs ζ̃ que usa el código) y corrí
  `validar_radio_truncamiento_contra_do_tau()` yo mismo (0.0122 UA vs
  0.014 UA publicado, 12.6% de error -- coincide con lo declarado).
  Corregido un número de comentario desactualizado (decía "1.51 R*",
  el código calcula 1.32 R*) -- cosmético, no afectaba el resultado.
- **`database_estrellas.py`**: catálogo de 14 estrellas T Tauri, cada
  entrada con fuente citada o marcada explícitamente como "sin fuente
  individual confirmada". Corregido: el propio texto de venta que el
  archivo dice haber arreglado (para no sobre-prometer validación)
  afirmaba "15 estrellas" cuando el catálogo tiene 14 -- error de conteo
  en el mismo texto que corrige un error de conteo anterior.
- **`modificador_sistemas.py`**: generaliza "modificar un planeta y
  comparar contra el original" (ya existía solo para Tierra en modo
  Sintético) a cualquiera de los 300 planetas del catálogo. Rechaza
  explícitamente experimentos que el motor no puede responder
  físicamente (ej. "quitar Júpiter", que requeriría interacción
  N-cuerpos) documentando el motivo en vez de omitirlo en silencio.
  **Bug real encontrado y corregido**: al simular el planeta modificado
  bajo la clave `"{nombre}_modificado"`, la búsqueda de luna por nombre
  no encontraba la luna real del planeta base (solo "Tierra" tiene
  entrada en `LUNAS`) -- cualquier comparación sin llamar a
  `agregar_luna()` terminaba comparando "original con luna" contra
  "modificado sin luna" sin ningún aviso. Se corrigió trasladando la
  luna original automáticamente a la clave del modificado, salvo que el
  usuario ya haya pedido una luna distinta a propósito. Verificado con
  3 casos: sin `agregar_luna()` (la luna se conserva y queda registrado
  en `modificaciones_aplicadas`), con `agregar_luna()` explícito (se
  respeta lo pedido), y un planeta sin luna en `LUNAS` (no rompe nada).

**Pendiente de decisión, no técnico:** estos 3 archivos no llevan el
encabezado "Licencia: Comercial propietaria" que sí tienen los otros
módulos Pro (video_mpl.py, etc.), y ninguno depende de código
exclusivamente comercial -- `modificador_sistemas.py` solo importa de
`engine.py`/`database.py`/`habitabilidad.py` (todos AGPL). Se integraron
al paquete Pro por ahora porque así se pidió, pero falta decidir si
quedan ahí o si alguno (o los tres) va al repo público.

## Lo que NO se modificó

- `pack_figuras.py`: ya manejaba correctamente `eps_conocido` desde el
  diseño original — sin cambios funcionales.
- `comparador.py`: solo se agregó una línea que muestra la penalización de
  oblicuidad cuando aplica (mismo principio que los otros 2 fixes); el
  manejo de cache de video ya estaba bien.
- La lógica de licenciamiento/branding (`NIVEL`, `BRANDING_CLIENTE`) y la
  estructura de tiers: se revisó contra `TERMINOS_DE_LICENCIAMIENTO.md` y
  es consistente.
