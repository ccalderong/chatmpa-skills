# Infographic Focus-Prompt Patterns for MPpI Briefs

NotebookLM's infographic generator works best when the `focus_prompt` names the metrics, units, and structure you want featured. Without an explicit prompt the tool defaults to a generic "Key insights" framing that buries the MPpI metrics under generic bullets. Use the patterns below.

## Pattern A — Single community brief

```
Frame this as a Marine Prosperity Index policy brief.
Headline: the prosperity category and Pp = Balance × Level value.

Show these elements:
- Three axes with scores: Nature, Livelihood, Well-being
- Balance (B) and Level (L) values vs national averages
- Limiting axis with cell-share percentage
- Four scenarios (Targeted, Sustainable, Conservation, Integrated)
  with their Balance deltas

Use icons for ocean / fisheries / community where appropriate.
Tone: technical-but-accessible, audience = coastal policymakers.
```

## Pattern B — Regional synthesis (multiple briefs)

```
Synthesize the regional pattern across the source briefs.

For each community show:
- Name
- Prosperity category
- Pp value
- Limiting axis

Aggregate panels:
- Distribution of communities across the four prosperity categories
- Regional mean Balance, Level, Prosperity vs national averages
- Limiting-axis distribution (Nature / Livelihood / Well-being)
- Top 3 communities by ΔPp under the Targeted scenario

Audience: regional planners and federal funders.
```

## Pattern C — Comparison across two regions

```
Compare two coastal regions side-by-side.

For each region show:
- Number of communities assessed
- Mean Balance, Level, Prosperity
- Dominant prosperity category
- Dominant limiting axis

Then a "key difference" callout that explains in 1–2 lines what
distinguishes the two regions' prosperity profiles.
```

## Pattern D — Scenario-focused brief

```
This brief covers <community>. Focus the infographic on the four
policy scenarios, not the baseline metrics.

Show:
- Baseline Pp value (single number, top)
- Each scenario with: investment focus, ΔBalance, ΔProsperity,
  efficiency rating (High/Medium/Low)
- A "recommended scenario" callout matched to the limiting axis

Defer the diagnostic / strengths / constraints sections to a sidebar.
```

## What not to include

NotebookLM tends to over-include. Tell it explicitly to **omit**:

- Data Sources section (visual clutter; cite in caption)
- Equity Considerations section (better left to a separate handout)
- Contact / methodology references
- Long bulleted "Recommendations" — keep to a single primary recommendation per axis

```
Omit the Data Sources, Equity Considerations, and Contact sections
from the infographic. Limit recommendations to the single primary
action per axis.
```

## Orientation choice

| Use case | Orientation |
|----------|-------------|
| Slide-deck inclusion, website banner | `landscape` |
| Printed handout, PDF page | `portrait` |
| Social-media card (Instagram, LinkedIn post) | `square` |

## Detail-level choice

| `detail_level` | When |
|----------------|------|
| `concise` | One-glance summary card; minimal text |
| `standard` (default) | Stakeholder briefing; balanced |
| `detailed` | Technical audience; includes scenario table and peer comparison |

## Language

Pass `language="es"` for Spanish-language briefs. The tool will translate metric names but **keep "Pp = Balance × Level" untranslated** — add to the focus prompt:

```
Keep "Prosperity (Pp = Balance × Level)" exactly as written; do not translate the formula.
```

Also keep the axis names in their canonical form (Nature / Livelihood / Well-being) for consistency across English and Spanish briefs.

## Iteration

If the first infographic misses key metrics, re-run with a more directive focus prompt rather than tweaking `detail_level`. Detail level affects density, not which metrics are surfaced. To force a specific layout:

```
Top section: prosperity category as a colored banner with Pp value.
Middle: three-axis bar chart (Nature / Livelihood / Well-being) with
        national-average reference line.
Bottom: scenario table with Balance and Prosperity deltas.
```
