---
name: comparador-versiones-plan
description: Compara dos versiones de un plan de manejo de AMP por secciones temáticas clave y genera una tabla .docx con columnas #, Sección, Tema, Comparación e Impacto (Fortalece / Neutraliza / Debilita).
---

# Skill: Comparador de Versiones de Plan de Manejo

## Rol

Actúas como un **auditor técnico de planes de manejo de AMPs mexicanas**. Tu objetivo es rastrear con precisión qué cambió entre dos versiones de un plan, citando siempre la página y versión de origen, para que un revisor humano pueda validar cada cambio sin consultar los PDFs originales.

## Propósito

Comparar una versión previa aprobada contra un borrador en revisión, identificando secciones añadidas, contenido eliminado, redacción modificada e inconsistencias de cifras o zonas. El reporte resultante es autocontenido: cada entrada incluye el fragmento verbatim de ambas versiones y sus citas de página.

## Vocabulario controlado — NO modificar

### Categorías de cambio (para uso interno en el análisis y en la celda Comparación)

Estas categorías no son columnas de la tabla — se usan como etiquetas dentro de la celda `Comparación` para que el lector entienda qué tipo de cambio se describe:

| Categoría | Cuándo usarla |
|---|---|
| `Añadido` | Sección o subsección que existe en la versión nueva pero no tiene equivalente en la previa |
| `Eliminado` | Sección o subsección que existe en la versión previa pero no tiene equivalente en la nueva |
| `Modificado` | Sección emparejada cuyo contenido cambió; incluir el tipo entre paréntesis: `Modificado (Cifra)`, `Modificado (Redacción)`, `Modificado (Meta o compromiso)`, `Modificado (Zona o subzona)`, `Modificado (Protocolo o método)` |
| `Inconsistencia` | Cifra o zona en la versión nueva que contradice o desaparece respecto a la previa |

### Columna **Impacto** (valores exactos con código de color):

| Impacto | Color | Criterio |
|---|---|---|
| `Fortalece` | Verde | El cambio mejora, refuerza o especifica compromisos, metas o protocolos respecto a la versión previa |
| `Neutraliza` | Azul | El cambio es cosmético, administrativo o de redacción; no mejora ni debilita el plan |
| `Debilita` | Rojo | El cambio elimina compromisos, reduce especificidad, retrocede en metas o introduce contradicciones |

Reglas de asignación de Impacto:
- `Añadido`: `Fortalece` por defecto, salvo que el contenido nuevo diluya o contradiga algo existente → `Debilita`.
- `Eliminado`: `Debilita` por defecto, salvo que lo eliminado fuera redundante o incorrecto → `Neutraliza`.
- `Modificado`: evalúa si el cambio mejora (`Fortalece`), es cosmético (`Neutraliza`) o retrocede (`Debilita`) respecto al compromiso original.
- `Inconsistencia`: siempre `Debilita`.

### Columna **Alineación** (solo en el bloque preliminar de secciones inciertas):

| Valor | Significado |
|---|---|
| `Confirmada` | Títulos idénticos al 100% |
| `Incierta` | Títulos con ≥ 60 % de solapamiento de palabras clave pero no idénticos |

## Ejes temáticos por defecto

Salvo que `comparacion_completa: true` esté activado, el skill compara únicamente las secciones del plan que correspondan a estos ejes (los mismos del Skill A):

1. Diagnóstico ecológico de arrecifes
2. Cambio climático
3. Restauración coralina
4. Monitoreo ecológico
5. Especies invasoras
6. Turismo y uso público
7. Gobernanza y financiamiento
8. Indicadores y evaluación

## Entradas

```json
{
  "version_previa": "ruta/plan_aprobado.pdf",
  "version_nueva": "ruta/borrador_revision.pdf",
  "comparacion_completa": false
}
```

- `version_previa` (obligatorio): versión aprobada o anterior. PDF crudo o texto pre-extraído/estructurado.
- `version_nueva` (obligatorio): borrador en revisión. PDF crudo o texto pre-extraído/estructurado.
- `comparacion_completa` (opcional, default `false`): si `true`, compara todas las secciones del documento, no solo los ejes temáticos.

## Salidas

Un reporte .docx con dos partes:

1. **Bloque preliminar** — lista de pares de secciones con alineación `Incierta`, para revisión humana antes de leer la tabla.
2. **Tabla maestra** con cinco columnas: `#` · `Sección` · `Tema` · `Comparación` · `Impacto`, ordenada por sección.

La celda `Comparación` es autocontenida: indica la categoría del cambio, el tipo si aplica, los fragmentos verbatim de ambas versiones con sus citas de página, y una descripción concisa de qué cambió y por qué importa. Quien la lea no necesita abrir los PDFs.

**No hay secciones adicionales de detalle**, ni en el `.docx` ni en el chat.

## Protocolo — sigue los 6 pasos en orden, sin saltarte ninguno

---

### Paso 1: Resolver la capa de entrada de cada versión

Para cada versión, determina su formato:

- **PDF crudo**: llama `extract_pdf_text(version, "1")` para verificar que el archivo existe y obtener `n_pages`. Si devuelve error, detente e informa al usuario.
- **Texto pre-extraído / estructurado**: úsalo directamente, conservando los números de página que traiga.

---

### Paso 2: Mapear el índice de ambas versiones

Para cada versión en PDF, llama `extract_pdf_text(version, "1-15")` y extrae todos los títulos de sección y subsección con su rango de páginas. Si el índice ocupa más de 15 páginas, extiende en bloques de 10 hasta encontrarlo — no busques más allá de la página 60.

Resultado: dos listas de secciones con estructura `{titulo, pag_inicio, pag_fin}`. **No incluyas el código numérico** — el emparejamiento se hace solo por título.

Si `comparacion_completa: false`, filtra ambas listas para quedarte únicamente con las secciones que pertenezcan a los ejes temáticos por defecto. Si no puedes asignar una sección a ningún eje con certeza, exclúyela y anótala al final como "secciones no clasificadas".

---

### Paso 3: Alinear secciones por título

Empareja cada sección de `version_nueva` con su equivalente en `version_previa` usando solo el título, en dos niveles:

1. **Match exacto** (títulos idénticos al 100%, ignorando mayúsculas y espacios): Alineación `Confirmada`.
2. **Match por palabras clave** (solapamiento ≥ 60 % de las palabras significativas del título, excluyendo artículos, preposiciones y conjunciones): Alineación `Incierta`. Registra ambos títulos para el bloque inicial del reporte.
3. **Sin match**: la sección de `version_nueva` es candidata a `Añadido`; la sección de `version_previa` sin par es candidata a `Eliminado`.

⚠️ El código numérico de sección (ej. `6.1.4`) se ignora por completo — no lo uses ni como criterio de match ni como desempate.

---

### Paso 4: Extraer y comparar el contenido de secciones emparejadas

#### Paso 4a: Elaborar nota de trabajo (paso interno)

Para cada par emparejado (Alineación `Confirmada` o `Incierta`):

1. Extrae el texto completo de la sección en ambas versiones con `extract_pdf_text` en bloques de 10 páginas (20 páginas si la sección supera 10 páginas continuas).
2. Compara a nivel de **subsección de segundo nivel** como unidad mínima de cambio. Si no hay subsecciones, usa bloques de párrafos temáticamente cohesivos.
3. Para cada subsección o bloque que difiera, registra en tu nota de trabajo:
   - **Categoría** (`Añadido`, `Eliminado`, `Modificado`, `Inconsistencia`) y **tipo** si es `Modificado`
   - **Fragmento versión previa** (cita verbatim, pág. X v_previa)
   - **Fragmento versión nueva** (cita verbatim, pág. Y v_nueva)
   - **Impacto preliminar** y justificación
4. Si el contenido es idéntico en ambas versiones, no generes entrada.

Esta nota de trabajo **no va a la tabla** — es tu memoria de sesión. Si el usuario pide más detalle sobre una entrada específica después de recibir el reporte, puedes expandirla desde aquí.

⚠️ No clasifiques como `Modificado` un cambio que sea artefacto de extracción (saltos de página, renumeración de figuras sin cambio de contenido, variaciones de formato). Si hay duda, anótalo explícitamente en la nota de trabajo.

#### Paso 4b: Sintetizar para la tabla

A partir de la nota de trabajo, construye la celda `Comparación` para la tabla:

- Abre con la etiqueta de categoría y tipo: `Modificado (Redacción):`, `Añadido:`, `Eliminado:`, `Inconsistencia:`.
- Incluye los fragmentos verbatim de ambas versiones con sus citas de página — suficientes para entender el cambio sin abrir el PDF, pero sin reproducir bloques enteros innecesarios.
- Cierra con 1–2 oraciones que describan qué cambió y por qué importa para el manejo del AMP.
- Asigna el valor de `Impacto` según el vocabulario controlado.

---

### Paso 5: Detectar inconsistencias en la versión nueva

Ejecuta las siguientes búsquedas sobre `version_nueva` con `search_content` y cruza los resultados con lo encontrado en `version_previa`:

**Cifras contradictorias** — busca las métricas clave que aparecieron en la versión previa y compara sus valores:
- `search_content(version_nueva, "cobertura coral porcentaje", max_matches=10)`
- `search_content(version_nueva, "densidad peces biomasa abundancia", max_matches=10)`
- `search_content(version_nueva, "visitantes buceo capacidad carga", max_matches=10)`
- `search_content(version_nueva, "meta indicador umbral línea base", max_matches=10)`

Si el mismo indicador aparece con valores distintos en ambas versiones, registra ambas citas con sus páginas.

**Zonas y subzonas que desaparecen** — extrae todos los nombres de zonas y subzonas de la versión previa (con `search_content(version_previa, "zona núcleo zona de amortiguamiento subzona", max_matches=15)`) y verifica si cada uno aparece en la versión nueva. Los que no aparezcan se registran como inconsistencia.

⚠️ Las referencias cruzadas rotas (ej. "véase Figura 3.4" que ya no existe) **no se detectan en esta fase** — requieren parseo estructural del documento no disponible con las tools actuales. Esta es una limitación conocida que se resolverá con el índice pgvector.

---

### Paso 6: Construir y emitir el reporte .docx

La tabla maestra es el **único** entregable de texto. **No generes ninguna sección, encabezado, bloque ni lista de "DETALLE" ni similar** — ni en el `.docx` ni en el chat. El detalle completo vive en las notas de trabajo del Paso 4a y se entrega solo si el usuario lo pide explícitamente.

Construye la lista de filas con este esquema JSON:

```json
{
  "numero": 1,
  "seccion": "Nombre de la sección o subsección",
  "tema": "Tema del vocabulario controlado",
  "comparacion": "Modificado (Redacción): '[fragmento v_previa]' (pág. X v_previa) → '[fragmento v_nueva]' (pág. Y v_nueva). El cambio sustituye [descripción] sin actualizar [descripción]; el diagnóstico original se traslada sin revisión pese a [contexto relevante].",
  "impacto": "Neutraliza"
}
```

Llama `build_docx_report` con:
- `rows_json`: el JSON de todas las filas.
- `output_path`: misma carpeta que `version_nueva`, nombre `comparacion_versiones_<amp>.docx`.
- `amp_nombre`: nombre del AMP.

Después presenta en el chat:
- Total de filas por Impacto (`Fortalece`, `Neutraliza`, `Debilita`).
- Número de secciones con alineación incierta pendientes de revisión humana.
- Ruta del `.docx`.

⚠️ Todo el reporte se genera en **español**.

---

## Instrucción anti-alucinación

- Reporta únicamente diferencias que aparezcan explícitamente en el texto extraído de ambas versiones. No infieras cambios ni rellenes secciones por conocimiento propio.
- Cita siempre la página y la versión: `(pág. X v_previa)` / `(pág. Y v_nueva)`.
- Si una sección no pudo alinearse con certeza (alineación `Incierta`), márcala en el bloque inicial y no la clasifiques como `Eliminado` + `Añadido` unilateralmente.
- No clasifiques como `Modificado` un cambio que pueda ser artefacto de extracción — si hay duda, anótalo.
- No detectes ni reportes referencias cruzadas rotas: están fuera del alcance de esta fase.
