# MHD-INT

Simulador de interacción planeta–estrella: evolución acoplada de órbita,
rotación, campo magnético, calor de marea, núcleo térmico, escape
atmosférico y oblicuidad, validado contra datos observacionales del
Sistema Solar y aplicado a exoplanetas conocidos.

**Autor:** Roney Rigg Mora
**Versión:** 5.1 — Julio 2026
**Licencia:** AGPL-3.0 (código de este repositorio) + licencia comercial
opcional — ver [`TERMINOS_DE_LICENCIAMIENTO.md`](./TERMINOS_DE_LICENCIAMIENTO.md)

---

## ¿Qué es MHD-INT?

MHD-INT modela cómo el campo magnético de un planeta evoluciona a lo
largo del tiempo en función de su órbita, su estructura interna y la
estrella que lo alberga — incluyendo generación de dínamo por
convección núcleo-manto, torque de marea estelar, escape atmosférico
impulsado por radiación XUV, y evolución estelar tipo Skumanich.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app_streamlit.py
```

La interfaz incluye 5 modos: Simulación, Modo Sintético (diseña tu
propio planeta), Mapa de Calor MHI, Análisis de Sensibilidad, y
Validación.

## Modelo de licenciamiento

Este repositorio contiene el **motor físico completo bajo AGPL-3.0**:
cualquiera puede ejecutarlo, estudiarlo, modificarlo y redistribuirlo,
incluso ofrecerlo como servicio de red, siempre que cumpla las
condiciones de la AGPL (código fuente disponible para los usuarios de
ese servicio).

Además del código abierto, existe un modelo comercial opcional —
ejecutables precompilados, base de datos extendida de exoplanetas,
soporte y formación — que **no restringe ni oculta nada del código
público**; es una vía alternativa para quienes prefieran no lidiar con
las obligaciones de AGPL. Ver
[`TERMINOS_DE_LICENCIAMIENTO.md`](./TERMINOS_DE_LICENCIAMIENTO.md)
para el detalle completo de cada nivel.

## Alcance y limitaciones de la validación

El simulador reproduce, dentro de tolerancias documentadas en
[`docs/MARCO_TEORICO.md`](./docs/MARCO_TEORICO.md), la rotación, campo
magnético y dinámica orbital de Tierra, Venus, Marte y Júpiter contra
datos observacionales reales (baseline: error <0.45%).

**Nota de transparencia:** esa validación depende de los módulos
`termica.py` y `atmosfera.py`, incluidos en este repositorio. La
rotación retrógrada de Venus está documentada como fuera del alcance
del modelo (requiere mareas térmicas atmosféricas) y excluida de forma
explícita de esa comparación, en vez de forzarse a coincidir. Ver
`docs/CAMBIOS.md` para el detalle de cada corrección de auditoría
aplicada históricamente al modelo.

## Documentación

- [`docs/MANUAL_USUARIO.md`](./docs/MANUAL_USUARIO.md) — guía de uso
  completa: instalación y explicación de cada modo de la interfaz.
- [`docs/MARCO_TEORICO.md`](./docs/MARCO_TEORICO.md) — ecuaciones,
  referencias científicas, validación y limitaciones conocidas.
- [`docs/CAMBIOS.md`](./docs/CAMBIOS.md) — historial de versiones y
  correcciones de auditoría.
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) — cómo contribuir (incluye
  requisito de CLA para contribuciones de código).
- [`TERMINOS_DE_LICENCIAMIENTO.md`](./TERMINOS_DE_LICENCIAMIENTO.md) —
  condiciones de la licencia pública y de los niveles comerciales.

## Base de datos

47 cuerpos (8 planetas del Sistema Solar + 39 exoplanetas confirmados)
en la versión actual. Cada entrada especifica su fuente; el modelo no
asigna valores por defecto no fundamentados para parámetros sin dato
observacional disponible (ver política en `CONTRIBUTING.md`).

## Contribuir

Los reportes de bugs y correcciones de documentación son bienvenidos
sin trámite adicional. Las contribuciones de código requieren firma de
CLA — ver [`CONTRIBUTING.md`](./CONTRIBUTING.md) para el porqué y el
procedimiento.
