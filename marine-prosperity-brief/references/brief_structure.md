# Policy Brief Structure (11 sections)

Every MPpI policy brief follows this fixed structure. The R generator (`07_generate_policy_briefs.R`) fills each section from the computed metrics — do not reorder.

## 1. Header

```
# Marine Prosperity Index: <Community> Policy Brief

**Location:** <Community>
**Date:** <Month Year>
**Prepared using:** Marine Prosperity Index (MPpI) Framework
```

## 2. Executive Summary

One paragraph. Must include:
- Prosperity category (Balanced Prosperity / Balanced but Developing / Imbalanced Growth / Lagging)
- Number of grid cells in the 30 km buffer
- Limiting axis name and percentage of cells limited by it
- Level value with status vs national average
- Balance value with status vs national average
- Pp = B × L with status vs national average

## 3. Key Metrics table

```
| Dimension | Score | National Average | Status |
|-----------|-------|------------------|--------|
| Nature | … | … | Above/At/Below average |
| Livelihood | … | … | … |
| Well-being | … | … | … |
| Balance | … | … | … |
| Level | … | … | … |
| Prosperity (Pp = B × L) | … | … | … |
```

Plus two lines:
- **Prosperity Category:** <category>
- **Limiting Axis:** <axis> (X% of N grid cells)

## 4. Diagnostic Findings — Strengths

Numbered list. Each item triggers only if a threshold is crossed (see `build_strengths()` in the R generator). Possible items:
- Above-average Prosperity (Pp > national + 0.02)
- High Balance (B ≥ 0.75)
- Above-average Nature / Livelihood / Well-being (axis > national + 0.02)
- Above-average overall Level (L > national + 0.02)

If no strengths fire, emit a single line stating "Near-national-average performance".

## 5. Diagnostic Findings — Constraints

Two numbered items:
1. **<limiting-axis> Gap** — quantifies the gap between the limiting axis and the next-strongest.
2. **Spatial Heterogeneity** — cells by limiting axis (e.g. "23 cells: 100% Nature-limited").

## 6. Policy Recommendations

Three-tier:

1. **<Limiting-axis> Enhancement (Primary)** — four bullets specific to that axis:
   - Nature: habitat restoration, MPA management, pollution control, sustainable fisheries
   - Livelihood: fisheries value chain, sustainable aquaculture, ecotourism, employment & training
   - Well-being: health services, education, basic services, social transfers
2. **<Secondary-axis> Safeguards (Secondary)** — maintain and monitor the second-strongest axis so primary investments don't degrade it.
3. **Cross-Dimensional Maintenance (Tertiary)** — ensure services keep pace with population/economic change.

## 7. Projected Outcomes — Scenario table

```
| Scenario | Investment Focus | <Limiting-axis> Change | Balance Δ | Prosperity Δ | Efficiency |
|----------|------------------|------------------------|-----------|--------------|------------|
| Targeted | 100% economic | 0.46 → 0.61 | +X.X% | +Y.Y% | High/Medium/Low |
| Sustainable | 67% economic, 33% environmental | … | … | … | … |
| Conservation | 100% environmental | … | … | … | … |
| Integrated | 33% each dimension | … | … | … | … |
```

Followed by a one-paragraph interpretation. The Efficiency column ranks scenarios by ΔBalance: rank 1 = High, rank 2 = Medium, rest = Low.

## 8. Comparison with Similar Regions

Table of the **3 nearest peer municipalities** in (Balance, Level) Euclidean space, plus the target community as the first row in bold:

```
| Municipality | Balance | Level | Category | Limiting Axis |
|--------------|---------|-------|----------|---------------|
| **<Target>** | … | … | … | … |
| peer1 | … | … | … | … |
| peer2 | … | … | … | … |
| peer3 | … | … | … | … |
```

Requires `outputs/tables/municipal_summary.csv` (from `code/03_baseline_analysis.R`). If missing, emit a placeholder note.

## 9. Equity Considerations

Standing text reminding implementers to:
- Reach small-scale fishers, not just established cooperatives
- Target employment and training to women and youth
- Consult with indigenous and migrant communities
- Apply Ocean Equity Index (OEI) before implementation

End with `[Additional regional equity considerations to be added by local experts]`.

## 10. Data Sources

Standard list:
- Environmental: MODIS, Copernicus Marine Service, CONABIO
- Economic: INEGI Economic Census, CONAPESCA fisheries statistics
- Social: INEGI Population Census 2020, CONEVAL poverty measures
- Spatial resolution: 0.05° (~5 km) grid; N cells within 30 km of <Community>

## 11. Contact

```
For methodology details, see: *The Marine Prosperity Index: A Decision Framework
for Balanced Coastal Development* (Favoretto et al., in preparation)

For data access: [Zenodo repository link]
```

Closing italic disclaimer that the brief is auto-generated diagnostic guidance and requires local stakeholder engagement.

## Slug rules

The brief filename is `policy_brief_<slug>.md` where the slug is:

1. Lowercased
2. Accents folded (á→a, é→e, í→i, ó→o, ú→u, ñ→n)
3. Non-alphanumerics replaced with `_`
4. Leading/trailing `_` trimmed

`Bahía de Kino` → `bahia_de_kino`. The Python map generator and DOCX builder both use this same slug as the dictionary key.
