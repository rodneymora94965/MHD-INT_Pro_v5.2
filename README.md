# MHD-INT — versión pública

Simulador de interacción planeta–estrella: evolución acoplada de órbita,
rotación, campo magnético, mareas, escape atmosférico y oblicuidad, con el
Índice de Habitabilidad Magnética (MHI).

**Autor:** Roney Rigg Mora · Solaris Core
**Versión:** 5.2.2 (octubre 2026)
**Licencia:** AGPL-3.0 — ver [`LICENSE`](./LICENSE) y [`TERMINOS_DE_LICENCIAMIENTO.md`](./TERMINOS_DE_LICENCIAMIENTO.md)

## Qué incluye esta versión

- El motor físico completo (`engine.py`, `numba_functions.py`, `atmosfera.py`,
  `termica.py`, `stellar_evolution.py`, `habitabilidad.py`).
- La interfaz básica (`app_streamlit.py`): Simulación, Modo Sintético, Mapa MHI,
  Sensibilidad, Validación, Educación, Ruta de Aprendizaje y Biblioteca de Fotos.
- Una base de datos de **47 planetas**: los 8 del Sistema Solar y 39 exoplanetas
  con masa, radio y órbita tomados de sus publicaciones.
- Las pruebas automáticas (`tests/`).

Las versiones **STANDARD** y **PRO** (ejecutable para Windows, base de 300
planetas, comparador, N-cuerpos, efemerides JPL, reportes y exportaciones
avanzadas) se distribuyen por separado: <https://solariscore.com.co>.

## Instalación

```bash
pip install -r requirements.txt
streamlit run app_streamlit.py
```

## Pruebas

```bash
python -m pytest
```

Algunas pruebas se omiten (`skipped`) porque usan planetas que solo están en
la base completa; es lo esperado.

## Qué valida y qué no

`validacion.py` compara 6 cuerpos del Sistema Solar partiendo de sus valores
actuales: es una **prueba de consistencia**, no una predicción independiente.
Ningún exoplaneta tiene validación cuantitativa contra observaciones. El modelo
térmico del núcleo está marcado como **EXPERIMENTAL**. Los detalles y las
limitaciones conocidas están en [`docs/MARCO_TEORICO.md`](./docs/MARCO_TEORICO.md)
y el historial en [`docs/CAMBIOS.md`](./docs/CAMBIOS.md).

## Cómo citar

Mora, R. R. (2026). *MHD-INT: simulador de interacción planeta–estrella*,
versión 5.2.2. Solaris Core.
