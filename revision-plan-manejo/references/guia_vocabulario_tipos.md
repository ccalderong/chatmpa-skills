# Guía de Vocabulario: Tipos de Acción y Confianza

## Tipos de acción — criterios detallados y casos de borde

### `Vacío de información`
El plan **no menciona** el tema en absoluto, o lo menciona de manera tan superficial que no hay orientación para la acción. La evidencia demuestra que ese tema es relevante para el AMP.

**Casos típicos:**
- Un subprograma de protección que no menciona cambio climático mientras la evidencia documenta blanqueamiento masivo reciente.
- Un plan que no incluye protocolo de respuesta ante especies invasoras a pesar de registros de nuevas detecciones en el área.

**Distinción clave:** Si el plan *menciona* el tema pero con datos viejos, usar `Dato desactualizado`. Si *no lo menciona*, usar `Vacío de información`.

---

### `Dato desactualizado`
El plan cita cifras, estudios o diagnósticos que la evidencia supera con datos más recientes o contradictorios. El tema sí está cubierto, pero el contenido quedó obsoleto.

**Casos típicos:**
- El plan cita cobertura de coral del año 2000; la evidencia documenta valores actuales significativamente menores.
- El plan clasifica una especie como "sin riesgo"; la evidencia reporta su inclusión reciente en la Lista Roja UICN.
- El plan menciona una meta de visitantes basada en estudios de capacidad de carga anteriores al crecimiento turístico documentado.

**Distinción clave:** La evidencia no solo "complementa" — contradice o desactualiza específicamente lo que el plan afirma.

---

### `Actividad urgente`
La evidencia documenta una amenaza activa, un proceso en curso o un umbral crítico que requiere acción en el corto plazo — no en la próxima revisión quinquenal. El plan no la contempla o la trata como futura.

**Casos típicos:**
- Registro confirmado de una especie invasora en el AMP; el plan no tiene protocolo de respuesta rápida.
- Eventos de blanqueamiento masivo documentados en los últimos dos años; el plan no tiene protocolo de monitoreo de emergencia.
- Temperatura del mar cruzando umbrales críticos para el coral; el plan no prevé ninguna medida de respuesta.

**Distinción clave:** El criterio es la urgencia temporal, no la gravedad. Una amenaza grave pero de largo plazo es `Recomendación` o `Dato desactualizado`. Una amenaza que requiere acción este ciclo de monitoreo es `Actividad urgente`.

---

### `Recomendación`
Mejora concreta, sustentada directamente en la evidencia, que no implica urgencia inmediata. El plan podría funcionar sin ella, pero la evidencia demuestra que incorporarla lo fortalecería significativamente.

**Casos típicos:**
- Adoptar un índice de salud arrecifal que la evidencia describe y calcula para el área.
- Incorporar una meta numérica de cobertura que la evidencia sugiere como alcanzable.
- Ajustar la zonificación basándose en datos de distribución de especies actualizada.

---

### `Idea nueva`
Propuesta que el evaluador considera valiosa pero que **no está respaldada por ninguno de los documentos de evidencia proporcionados**. Puede ser lógica y bien fundamentada en el conocimiento experto, pero no puede citarse con una fuente específica de los documentos dados.

**Regla obligatoria:** Toda fila con Confianza `Incierta` debe ser `Idea nueva`. Si una recomendación no puede citarse con página y documento, es `Idea nueva`.

---

## Niveles de confianza — guía de aplicación

| Situación | Confianza |
|---|---|
| El dato, cifra o protocolo aparece textualmente en la evidencia con página identificable | `Alta` |
| El tema está cubierto en la evidencia pero la recomendación específica se infiere, no se cita directamente | `Media` |
| La recomendación proviene del conocimiento experto, no de los documentos dados | `Incierta` → forzar `Idea nueva` |

**Nota sobre confianza `Media`:** No es un nivel "de relleno". Úsalo cuando la evidencia documenta el problema pero no propone la solución específica. Ejemplo: la evidencia reporta blanqueamiento severo (dato verificable → `Alta` para el diagnóstico), pero la meta de recuperación propuesta se calcula por interpolación (→ `Media` o `[derivado]` para la meta numérica).
