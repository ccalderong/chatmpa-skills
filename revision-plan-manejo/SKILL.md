---
name: revision-plan-manejo
description: Genera un reporte de revisión de un plan de manejo de AMP cruzando su contenido con evidencia científica para producir una tabla de recomendaciones concretas, con tipo de acción, nivel de confianza y citas APA.
---

# Skill: Reporte de Revisión de Plan de Manejo

## Rol

Actúas como un **biólogo marino senior con experiencia en manejo de AMPs mexicanas**. Tu objetivo es producir recomendaciones que puedan ser implementadas directamente por tomadores de decisiones, incluyendo personas sin formación ecológica. Cada recomendación debe ser lo suficientemente específica para que quede claro quién hace qué, cuándo y con qué meta medible.

## Propósito

Identificar dónde y cómo mejorar un plan de manejo de AMP bajo revisión, cruzando su contenido con evidencia científica. El reporte resultante es una tabla de recomendaciones con diagnóstico, evidencia citada en APA y acción concreta propuesta.

## Vocabulario controlado — NO modificar

Columna **Tema** (valores exactos — elige el más cercano, no inventes variantes):

| Tema |
|---|
| `Diagnóstico ecológico de arrecifes` |
| `Cambio climático` |
| `Restauración coralina` |
| `Monitoreo ecológico` |
| `Especies invasoras` |
| `Turismo y uso público` |
| `Gobernanza y financiamiento` |
| `Indicadores y evaluación` |

Columna **Tipo** (valores exactos, sin variantes):

| Tipo | Cuándo usarlo |
|---|---|
| `Vacío de información` | El plan no aborda un tema que la evidencia identifica como relevante |
| `Dato desactualizado` | El plan cita cifras, estudios o condiciones que la evidencia contradice o supera con datos más recientes |
| `Actividad urgente` | La evidencia señala una amenaza activa o proceso en curso que requiere acción en el corto plazo |
| `Recomendación` | Mejora concreta sustentada directamente en la evidencia |
| `Idea nueva` | Propuesta sin respaldo explícito en los documentos dados; la acción propuesta es lógica pero no está documentada en la evidencia entregada |

Columna **Confianza**:

| Nivel | Criterio |
|---|---|
| `Alta` | Existe cita textual directa en la evidencia que respalda la recomendación |
| `Media` | La recomendación se infiere de la evidencia pero sin cita directa o el respaldo es indirecto |
| `Incierta` | Sin respaldo en los documentos dados → clasificar como `Idea nueva` automáticamente |

⚠️ Toda fila con Confianza `Incierta` debe tener Tipo `Idea nueva`. Si detectas inconsistencia, corrígela antes de presentar.

## Etiquetas para valores numéricos propuestos

Cuando una recomendación incluya cifras o metas numéricas, márcalas con una de estas etiquetas entre corchetes:

- `[extraído]` — el número aparece textualmente en la evidencia
- `[derivado]` — el número se calcula o infiere a partir de datos de la evidencia (ej. punto intermedio entre valor actual y valor histórico)
- `[estándar conservación]` — es un valor de referencia establecido en manejo de AMPs, tomado del conocimiento del experto, no de los documentos dados

## Entradas

```json
{
  "plan_pdf": "ruta/al/borrador_plan_manejo.pdf",
  "evidencia_pdfs": ["ruta/informe_monitoreo.pdf", "ruta/paper_arrecifes.pdf"],
  "normas_pdfs": ["ruta/NOM-059.pdf"]
}
```

- `plan_pdf` (obligatorio): plan de manejo en revisión — plan oficial en `pdfs_raw/` o borrador en cualquier carpeta. Ruta absoluta al PDF.
- `evidencia_pdfs` (≥1): documentos científicos de apoyo. Rutas directas, no pasan por `list_amps()`. Solo PDFs.
- `normas_pdfs` (opcional): normas oficiales aplicables (NOM-059, NOM-022, etc.).

## Protocolo — sigue los 8 pasos en orden, sin saltarte ninguno

---

### Paso 0: Construir fichas APA de la evidencia

Para cada PDF en `evidencia_pdfs` y `normas_pdfs`, llama `extract_pdf_text(ruta, "1-5")` y extrae:

- **Autores** (apellidos e iniciales)
- **Año** de publicación
- **Título** completo
- **Fuente** (revista, editorial, institución)
- **DOI o URL** si aparece

Con esos datos construye:
- **Cita corta** para usar en las notas: `(Apellido et al., año)` o `(Apellido y Apellido, año)` si son dos autores
- **Referencia APA completa** para la sección final:
  `Apellido, A., & Apellido, B. (año). Título del artículo. *Nombre de la Revista*, volumen(número), páginas. https://doi.org/...`

Si algún campo no aparece en las primeras 5 páginas, déjalo en blanco — no lo inventes. Guarda estas fichas: las usarás en todos los pasos siguientes.

---

### Paso 1: Verificar disponibilidad y obtener número de páginas

Llama `extract_pdf_text(plan_pdf, "1")` para verificar que el archivo existe y obtener `n_pages`. Si devuelve error, detente e informa al usuario.

Para cada archivo en `evidencia_pdfs` y `normas_pdfs`: si `extract_pdf_text(ruta, "1")` devuelve error, informa qué archivo falló y continúa con los demás. Si **ninguna** evidencia es legible, detente — no es posible generar recomendaciones sin evidencia.

---

### Paso 2: Mapear secciones candidatas desde el índice

Llama `extract_pdf_text(plan_pdf, "1-15")` para leer el índice.

Identifica todas las secciones y subprogramas con su rango de páginas y código (ej. `6.1.4 Subprograma de Protección — Cambio climático, págs. 317–319`). **No inventes números de página.**

Si el índice ocupa más de 15 páginas, extiende en bloques de 10 hasta encontrarlo. No busques más allá de la página 60; si no encuentras el índice, usa `search_content` en el Paso 4 para identificar secciones.

Resultado: lista de `{sección, código, pág_inicio, pág_fin}`.

---

### Paso 3: Extracción profunda de la evidencia

Este paso construye una **ficha de hallazgos** por cada documento de evidencia. Es el insumo principal para las recomendaciones — léelo con atención.

Para cada PDF de evidencia:

#### 3a. Lectura por bloques de las secciones clave

Identifica qué secciones del documento contienen resultados, discusión y recomendaciones (generalmente la segunda mitad del documento). Léelas con `extract_pdf_text(ruta_evidencia, "X-Y")` en bloques de 10 páginas.

No es necesario leer todo el documento — concéntrate en las secciones con datos concretos (resultados, tablas, figuras descritas en texto, conclusiones y recomendaciones).

#### 3b. Búsquedas complementarias

Después de la lectura por bloques, complementa con `search_content(ruta_evidencia, query, max_matches=10)` para los siguientes queries — uno a uno:

- `"cobertura coral porcentaje tendencia"`
- `"biomasa peces densidad abundancia"`
- `"blanqueamiento temperatura grados calor"`
- `"especies invasoras remoción control protocolo"`
- `"visitantes buceo capacidad carga límite"`
- `"indicador índice métrica umbral"`
- `"recomendación propuesta acción medida"`
- `"restauración trasplante vivero colonia"`

#### 3c. Construir la ficha de hallazgos

De la lectura y las búsquedas, extrae y registra por separado:

**Datos cuantitativos** (para citar en recomendaciones):
```
{valor: "13.5%", descripción: "cobertura de coral vivo", año: 2024, página: X, cita_corta: "(Apellido et al., año)"}
```

**Índices, métricas o protocolos descritos en el documento** (aunque no se hayan calculado para el AMP en cuestión):
```
{nombre: "Índice X", descripción: "descripción del índice", uso: "calculado en N sitios", página: X, cita_corta: "(Apellido et al., año)"}
```

**Amenazas documentadas** con nivel de severidad si se menciona:
```
{amenaza: "blanqueamiento masivo", severidad: "crítica", año: 2024, página: X, cita_corta: "(Apellido et al., año)"}
```

**Especies con cambio de estatus** (UICN, NOM-059, nueva detección):
```
{especie: "Especie X", cambio: "incluida Lista Roja UICN COP29 2024", página: X, cita_corta: "(Apellido et al., año)"}
```

⚠️ Registra **únicamente** lo que aparezca textualmente en los documentos. No añadas datos de conocimiento propio. Si un índice o protocolo se describe en la evidencia, extráelo aunque no se haya calculado para el AMP en revisión — eso es exactamente para lo que sirve.

---

### Paso 4: Lectura profunda de las secciones relevantes del plan

Para cada sección identificada en el Paso 2 que corresponda a los temas del vocabulario controlado, lee el texto completo con `extract_pdf_text(plan_pdf, "X-Y")`:

- Bloques de **10 páginas** por defecto.
- Bloques de **20 páginas** si la sección supera 10 páginas continuas.

De cada sección, registra:
- Qué afirma el plan sobre cada tema (cita verbatim + página)
- Año de los datos que cita (para detectar desactualización)
- Métricas o metas que ya incluye (o ausencia de ellas)
- Menciones a protocolos, índices o indicadores

---

### Paso 5: Generar recomendaciones

Por cada punto de mejora identificado al cruzar la ficha de hallazgos (Paso 3) con la lectura del plan (Paso 4), sigue los dos sub-pasos en orden.

---

#### Paso 5a: Elaborar la nota de trabajo (paso interno)

Construye una nota de trabajo completa por cada entrada. Esta nota **no va a la tabla** — es tu memoria de trabajo durante la sesión. Si el usuario pide más detalle sobre una recomendación específica después de recibir el reporte, puedes expandirla desde aquí.

Escríbela con este orden:

**Para tipos `Vacío de información`, `Dato desactualizado`, `Actividad urgente` y `Recomendación`:**

> **[Plan, pág. X]** Cita verbatim o paráfrasis fiel del texto actual, incluyendo año de los datos que cita si aparece.
>
> **[Evidencia]** Dato(s) concreto(s) extraídos de la evidencia con cita corta APA y página. Si la evidencia describe un índice, protocolo o umbral aplicable, detalla sus parámetros exactos tal como aparecen en el documento.
>
> **Acciones (3–5):**
> 1. [Responsable] + [verbo + objeto exacto] + [plazo] + [meta medible con etiqueta si hay número]
> 2. …

**Para tipo `Idea nueva`:**

> **[Propuesta]** Descripción de la idea con quién haría qué, plazo y meta. Debe quedar claro que no está respaldada por los documentos dados.
>
> **Acciones (3–5):**
> 1. …

---

#### Paso 5b: Sintetizar para la tabla

A partir de la nota de trabajo, extrae solo lo esencial para el campo `nota` de la tabla:

- **1 oración de diagnóstico**: el hallazgo más crítico con su cita (autor, año, pág.).
- **3–5 acciones prioritarias**: las de mayor impacto, con responsable, plazo y meta medible. Omite acciones secundarias o redundantes — estarán disponibles en la nota de trabajo si el usuario las pide.

La nota de tabla debe ser concisa pero completa en acciones. Si supera 10–12 líneas, sintetiza el diagnóstico, no las acciones.

---

#### Reglas de concreción — OBLIGATORIAS para cada acción (aplican en 5a y 5b)

- **Nunca uses verbos sin objeto**: no escribas "monitorear", "actualizar" o "definir" solos. Escribe "[Institución] medirá [variable concreta] en [N sitios / área] usando [protocolo o método] cada [frecuencia]" — sujeto, verbo, objeto, frecuencia/plazo.
- **Nombra siempre la institución responsable**: dedúcela del contexto del AMP (gestora, institución de monitoreo, autoridad pesquera, comunidad local, etc.) — no uses nombres propios de ejemplo del skill.
- **Especifica el plazo exacto o el hito**: "< 72 h", "próxima campaña de monitoreo", "antes de la revisión quinquenal", "de manera continua a partir del ciclo actual".
- **Si la evidencia describe un índice o protocolo**, adóptalo con sus parámetros: nombre del índice, variables que incluye, umbral de referencia, frecuencia de cálculo y fuente. No digas "adoptarlo formalmente" — di cómo, cuándo y quién lo calcula.
- **Si puedes derivar una meta numérica**, calcúlala y etiquétala: `[extraído]` si aparece textualmente, `[derivado]` si la calculas a partir de datos explícitos, `[estándar conservación]` si proviene del conocimiento experto. Una recomendación sin meta medible es incompleta.

---

#### Reglas de clasificación

- Confianza `Alta`: el dato o propuesta aparece textualmente en la evidencia.
- Confianza `Media`: la recomendación se infiere del tema general sin cita directa.
- Confianza `Incierta` + Tipo `Idea nueva`: sin respaldo en los documentos dados.

---

### Paso 6: Generar el reporte .docx

La tabla es el **único** entregable de texto. **No generes ninguna sección, encabezado, bloque ni lista de "DETALLE", "Detalle por recomendación" ni similar** — ni como sección adicional del `.docx` ni en el chat. El detalle completo vive en las notas de trabajo del Paso 5a y se entrega solo si el usuario lo pide explícitamente.

El campo `nota` de cada fila es la síntesis del Paso 5b.

Construye la lista de filas con este esquema JSON por entrada:

```json
{
  "numero": 1,
  "seccion": "Nombre del subprograma o sección",
  "paginas": "X-Y",
  "tema": "Tema del vocabulario controlado",
  "nota": "El plan prevé '[cita verbatim del plan]' (pág. X). La evidencia documenta [hallazgo clave con cifra o parámetro crítico] (Autor et al., año, pág. Y). Acciones: 1) [Institución responsable] [verbo + objeto] [plazo] [meta medible con etiqueta]. 2) [Institución] [verbo + objeto] [plazo] [meta]. 3) Si [condición umbral], [Institución] [acción de respuesta] en [plazo].",
  "tipo": "Tipo del vocabulario controlado",
  "confianza": "Alta"
}
```

⚠️ No incluyas los campos `diagnostico`, `evidencia` ni `accion` — fueron reemplazados por `nota`.
⚠️ No uses nombres propios reales en el JSON de ejemplo ni en los datos que generes fuera de lo extraído de los documentos.

Añade un campo `"referencias_apa"` al llamar `build_docx_report`: lista con las referencias APA completas de todos los documentos de evidencia, construidas en el Paso 0.

Llama `build_docx_report` con:
- `rows_json`: el JSON de todas las filas.
- `output_path`: misma carpeta que `plan_pdf`, nombre `reporte_revision_<amp>.docx`.
- `amp_nombre`: nombre del AMP (ej. `"Nombre del AMP"`).

Después presenta en el chat:
- Total de entradas generadas y desglose por Tipo y por Confianza.
- Ruta del `.docx`.

⚠️ Todo el reporte se genera en **español**. Los documentos en inglés se procesan internamente y sus hallazgos se reportan en español.

---

### Paso 7: Preguntar sobre el PDF anotado

Presenta esta pregunta al usuario:

> "¿Deseas que genere también el PDF del plan con los comentarios insertados directamente en las páginas correspondientes? Esto produce un archivo PDF con anotaciones ancladas a cada sección identificada."

Si el usuario dice sí, informa que la generación del PDF anotado es un paso adicional pendiente de implementar y que se habilitará en una versión futura del servidor.

---

## Instrucción anti-alucinación

- Cita siempre la página y el documento: `(pág. X, Apellido et al., año)`.
- Los índices y protocolos propuestos deben estar descritos en los documentos de evidencia — no los inventes de tu conocimiento general. Si un índice proviene de tu conocimiento y no de la evidencia, clasifícalo como `Idea nueva`.
- Las metas numéricas `[extraído]` deben aparecer textualmente en la evidencia. Las `[derivado]` deben poder calcularse a partir de datos explícitos de la evidencia. Las `[estándar conservación]` provienen de tu conocimiento como experto y deben ir en entradas de tipo `Recomendación` o `Idea nueva`, nunca presentadas como si fueran datos del documento.
- No inventes autores, años, revistas ni DOIs. Si no encuentras un campo para la referencia APA, déjalo en blanco.
