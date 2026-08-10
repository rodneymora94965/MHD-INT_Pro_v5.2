# Contribuir a MHD-INT

Gracias por tu interés en mejorar MHD-INT. Antes de abrir un Pull Request,
por favor lee esta guía completa — en particular la sección sobre el CLA,
que es obligatoria para cualquier contribución de código.

---

## 1. Antes de contribuir

- Abre un Issue describiendo el bug o la mejora antes de escribir código,
  salvo que sea una corrección trivial (typo, error de documentación).
- Si tu contribución toca física del modelo (`engine.py`, `termica.py`,
  `atmosfera.py`, `stellar_evolution.py`, `habitabilidad.py`), incluye
  referencia a la fuente científica (paper, libro de texto) que respalda
  el cambio. MHD-INT tiene un historial de auditoría estricta: no se
  aceptan constantes o correcciones "porque funcionan mejor" sin
  justificación física — ver `docs/MARCO_TEORICO.md` para el estándar
  esperado.
- Si tu cambio afecta la base de datos de planetas (`database.py`),
  toda fila nueva debe venir de una fuente verificable (NASA Exoplanet
  Archive, paper de descubrimiento, etc.). No se aceptan valores
  estimados o interpolados sin etiquetarlos explícitamente como tales.

## 2. Acuerdo de Licencia de Contribuyente (CLA)

**Toda contribución de código a este repositorio requiere la firma de
un CLA (Contributor License Agreement) antes de poder ser fusionada.**

### Por qué existe este requisito

MHD-INT se distribuye bajo AGPL-3.0 en este repositorio público, pero
el proyecto opera bajo un modelo de **licenciamiento dual**: el mismo
código también se ofrece bajo una licencia comercial separada (ver
`TERMINOS_DE_LICENCIAMIENTO.md`) para clientes que no pueden o no
quieren cumplir las obligaciones de AGPL.

Para que esa licencia comercial sea legalmente válida, el titular del
copyright de *todo* el código del repositorio debe poder otorgarla sin
necesitar el permiso individual de cada persona que haya contribuido.
Si aceptáramos código sin CLA, cada contribuyente conservaría sus
propios derechos de autor sobre su parte, y el dual-licensing dejaría
de ser posible sin el consentimiento de todos ellos.

El CLA no le quita a nadie el derecho a que su código siga siendo
público y libre bajo AGPL-3.0 — solo autoriza al proyecto a *también*
licenciarlo comercialmente en paralelo.

### Cómo funciona en la práctica

1. Al abrir tu primer Pull Request, un bot (o el mantenedor) te pedirá
   firmar el CLA electrónicamente.
2. El PR no se revisa ni se fusiona hasta que el CLA esté firmado.
3. Solo se firma una vez; aplica a todas tus futuras contribuciones.

*(Nota interna: el texto legal formal del CLA está pendiente de
redacción con asesoría de un abogado de propiedad intelectual — hasta
que exista, las contribuciones externas de código quedan en pausa.
Correcciones de documentación y reportes de bugs sí son bienvenidos
sin CLA.)*

## 3. Estilo y validación

- Todo cambio en los módulos de física debe pasar `validacion.py` sin
  regresiones antes de someterse a revisión.
- Sigue el estilo de nombres en español ya establecido en el código
  (`calcular_torque_magnetico`, `q_conv`, etc.) para consistencia.
- Incluye docstrings con la referencia física (paper, ecuación) cuando
  agregues o modifiques una fórmula.

## 4. Reportar bugs

Abre un Issue con:
- Versión de MHD-INT y sistema operativo.
- Pasos para reproducir.
- Salida esperada vs. salida obtenida.
- Si es posible, el planeta/parámetros usados en la simulación.

---

Gracias por ayudar a mantener MHD-INT riguroso y honesto científicamente.
