# MHD-INT — Términos de Licenciamiento (Modelo Dual)
**Versión 5.2.1 — Septiembre 2026** (precios y niveles actualizados)
**Contacto: Roney Rigg Mora**

> Nota: este documento es un borrador de trabajo, no un contrato. Antes de publicarlo o firmarlo con un cliente, revísalo con un abogado de propiedad intelectual — especialmente las secciones 3 y 4, que definen obligaciones legales reales.

---

## 1. Licencia pública (AGPL-3.0)

El código fuente completo de MHD-INT está disponible públicamente bajo los términos de la licencia **AGPL-3.0**.

Cualquier persona puede:
- Descargar, estudiar y ejecutar el código libremente.
- Modificarlo para uso propio.
- Redistribuirlo, siempre que mantenga la misma licencia AGPL-3.0.
- Ofrecerlo como servicio de red (SaaS), siempre que ponga a disposición de los usuarios de ese servicio el código fuente completo, incluidas sus propias modificaciones.

**Esta es la vía gratuita del proyecto.** No requiere pago ni contacto previo.

---

## 2. SaaS por créditos — no disponible

Se evaluó ofrecer MHD-INT como servicio alojado ($10 = 10 simulaciones). **Hoy no existe ese servicio** y no se vende. Si se lanza en el futuro, se publicarán sus condiciones.

---

## 3. Licencia Comercial del ejecutable — Standard y Pro

| Nivel | Licencia de 2 años (precio de lanzamiento, sep-2026) |
|---|---|
| Standard | $39 |
| Pro (incluye las 3 plantillas de Blender) | $79 |

Condiciones completas para el cliente: `docs/LICENCIA_DE_USO.md` (se entrega dentro del paquete).

Estos niveles **no se basan en restringir técnicamente el código AGPL**, sino en ofrecer una **licencia comercial alternativa** sobre el binario compilado, exenta de las obligaciones de AGPL, para quienes prefieran:

- Recibir un binario compilado con soporte, sin tener que compilar ni mantener el código.
- Usar el software sin las condiciones de AGPL (por ejemplo, en un flujo de trabajo cerrado).
- Recibir las actualizaciones 5.x durante el plazo de la licencia.

**Lo que compra el cliente:** el uso del binario por una persona durante el plazo (2 años) + soporte por email + actualizaciones 5.x durante ese plazo.

**Lo que NO compra:** el código fuente, exclusividad, ni el derecho a redistribuir el binario o la licencia.

*Nota técnica:* la licencia se verifica localmente con una firma ECDSA; no está atada al hardware. El valor de este nivel es el binario listo, el soporte y la comodidad, no un candado inquebrantable.

---

## 4. Licencia Comercial Completa (Código Fuente) — $33.000 USD

Este nivel otorga una **licencia comercial propietaria**, separada y exenta de las condiciones de AGPL-3.0, para el cliente específico que la adquiere.

Incluye el derecho a:
- Usar, modificar y redistribuir el código **sin** la obligación de publicar sus propias modificaciones (a diferencia de cualquier usuario bajo AGPL).
- Desarrollar productos cerrados (closed-source) derivados de MHD-INT.
- Operar su propio servicio SaaS basado en MHD-INT sin obligación de liberar su código, aun cuando lo ofrezca por red a terceros.
- Aplicar marca propia (branding) al producto derivado.

**Lo que NO otorga:** exclusividad frente a terceros. El repositorio AGPL público sigue existiendo en paralelo — cualquier otra persona puede seguir usando, estudiando y modificando la versión pública bajo sus propias condiciones AGPL. Esta licencia exime únicamente al comprador de esas condiciones, no elimina la versión pública.

Incluye además:
- Base de datos curada de 47 planetas, con derechos de uso comercial.
- Certificado de validación firmado.

---

## 5. Resumen de la lógica del modelo

| Nivel | Qué recibe el cliente | Base legal |
|---|---|---|
| Público (gratis) | Versión pública del código (ver §1) | AGPL-3.0 |
| Standard / Pro ($39 Standard / $79 Pro, 2 años) | Binario + soporte + actualizaciones 5.x durante el plazo, sin obligaciones AGPL para ese uso | Licencia comercial limitada al binario (`docs/LICENCIA_DE_USO.md`) |
| Código Fuente ($33.000) | Código fuente + derecho a cerrarlo/redistribuirlo | Licencia comercial propietaria (dual con AGPL) |

---

## Pendiente de definir

- Redacción legal formal del contrato de licencia comercial (niveles 3 y 4) — requiere revisión de abogado.
- Mecanismo de verificación de versión/soporte (no de bloqueo de uso) para los ejecutables.
- Texto exacto del aviso informativo que reemplaza el bloqueo de 30 días descartado.
- **Confirmar §1 (sep-2026):** esta sección dice "código fuente completo", pero `docs/MANUAL_USUARIO.md` §1.3 describe la versión pública como **reducida** (`app_streamlit.py`, 47 planetas, sin modos Pro). Ajustar §1 a lo que realmente esté publicado en el repositorio: si los módulos Pro están públicos bajo AGPL, cualquiera puede usarlos gratis.
