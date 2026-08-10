# MHD-INT — Términos de Licenciamiento (Modelo Dual)
**Versión 5.0 — Julio 2026**
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

## 2. SaaS por créditos — $10 USD = 10 simulaciones

- Roney Rigg Mora opera el servicio de red bajo AGPL-3.0.
- El código fuente del servicio permanece público en el repositorio oficial, cumpliendo la obligación de red de AGPL.
- El pago cubre uso del servicio alojado (infraestructura, cómputo, mantenimiento), **no una licencia distinta** — el usuario no adquiere derechos adicionales sobre el código.
- Créditos adicionales al mismo precio ($10 = 10 corridas), sin vencimiento.

---

## 3. Licencia Comercial — Ejecutable Básico ($25) y Profesional ($100)

Estos niveles **no se basan en restringir técnicamente el código AGPL** (que es de acceso público), sino en ofrecer una **licencia comercial alternativa**, exenta de las obligaciones de AGPL, para quienes prefieran:

- Recibir un binario compilado con soporte oficial, sin tener que compilar ni mantener el código ellos mismos.
- Usar el software en un contexto donde no quieren (o no pueden) cumplir las condiciones de AGPL — por ejemplo, integrarlo en un flujo de trabajo cerrado sin obligación de publicar nada propio.
- Contar con actualizaciones, soporte prioritario y garantía de que el binario corresponde a una versión validada.

**Lo que compra el cliente:** el binario + soporte + la certeza de que su uso comercial no lo obliga a las cláusulas de AGPL, mientras use exclusivamente el ejecutable entregado (no el código fuente).

**Lo que NO compra:** exclusividad sobre el software, ni el derecho a redistribuir o hacer su propia versión cerrada — eso corresponde al nivel 4.

*Nota técnica:* los límites de "100 simulaciones" no pueden aplicarse con garantía técnica absoluta si el cliente decide acudir al repositorio AGPL público en paralelo. El valor real de este nivel es el soporte y la comodidad, no un candado inquebrantable — conviene comunicarlo así en vez de presentarlo como una restricción dura.

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
| Público (gratis) | Código fuente completo | AGPL-3.0 |
| SaaS ($10/10 sims) | Uso del servicio alojado | AGPL-3.0 (el servicio cumple la cláusula de red) |
| Básico/Profesional ($25/$100) | Binario + soporte, sin obligaciones AGPL para ese uso | Licencia comercial limitada al binario |
| Código Fuente ($33.000) | Código fuente + derecho a cerrarlo/redistribuirlo | Licencia comercial propietaria (dual con AGPL) |

---

## Pendiente de definir

- Redacción legal formal del contrato de licencia comercial (niveles 3 y 4) — requiere revisión de abogado.
- Mecanismo de verificación de versión/soporte (no de bloqueo de uso) para los ejecutables.
- Texto exacto del aviso informativo que reemplaza el bloqueo de 30 días descartado.
