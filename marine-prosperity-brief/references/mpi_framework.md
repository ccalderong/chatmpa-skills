# Marine Prosperity Index — Framework Reference

The Marine Prosperity Index (MPpI) is a diagnostic framework for coastal regions that classifies grid cells by **both** the evenness of development across three axes and the absolute level of performance. Unlike single-axis indicators, the MPpI explicitly identifies which dimension constrains a system, then sequences investment accordingly.

## Three axes

| Axis | Indicators | Domain |
|------|-----------|--------|
| **Nature** | 13 | Biodiversity, mangrove extent, MPA coverage, water quality, marine productivity, carbon storage, climate stress |
| **Livelihood** | 12 | GDP per capita, fisheries production, employment rate, investment, tourism revenue, cooperative coverage |
| **Well-being** | 23 | Education attainment, health insurance coverage, household services (water/sanitation/electricity), CONEVAL poverty measures, governance |

All 48 indicators are min-max normalized to [0, 1] with 1% / 99% winsorization. Negatively-signed indicators (poverty rate, sediment-load anomaly, etc.) are direction-reversed before aggregation so that higher = better for every input. Within each axis, indicators are averaged with equal weight.

## Core metrics

### Balance (B)

Evenness-based coordination metric rescaled to [0, 1]:

```
E = (Σxᵢ)² / (n · Σxᵢ²)
B = (E − 1/n) / (1 − 1/n)
```

For n = 3 axes, this simplifies to:

```
B = (E − 1/3) / (2/3)
```

- B = 1 → all three axes equal (perfect coordination)
- B → 0 → one axis dominates / others collapse
- Threshold: B ≥ 0.75 is "balanced"

### Level (L)

Simple arithmetic mean of the three axes:

```
L = (Nature + Livelihood + Well-being) / 3
```

- L ∈ [0, 1]
- Threshold: L ≥ 0.40 is "high level"

### Prosperity (Pp)

Composite indicator:

```
Pp = Balance × Level
```

- Pp ∈ [0, 1]
- National coastal mean Pp ≈ 0.30 (Mexico, 2025 reference data)

## Limiting axis

For each grid cell, the **limiting axis** is the axis with the lowest score. Nationally (Mexico coast):

| Limiting axis | Share of cells |
|---------------|---------------|
| Livelihood | 88% |
| Nature | 9% (industrialized ports, high-tourism zones) |
| Well-being | 3% (remote indigenous communities) |

The skill must always report the **local** limiting axis distribution — investments aimed at the national-pattern axis can fail when the local cells are limited elsewhere.

## Viability threshold

Any axis score below **0.20** triggers a priority-rescue recommendation regardless of overall Balance or Level. A cell with `nature = 0.18, livelihood = 0.55, wellbeing = 0.50` is classified by category as Imbalanced Growth but still requires Nature rescue first.

## Four prosperity categories

| Category | Balance | Level | Description | Policy approach |
|----------|---------|-------|-------------|-----------------|
| **Balanced Prosperity** | ≥ 0.75 | ≥ 0.40 | Coordinated, high performance | Maintain trajectory; strengthen limiting axis |
| **Balanced but Developing** | ≥ 0.75 | < 0.40 | Coordinated but low overall | Broad uplift across all axes |
| **Imbalanced Growth** | < 0.75 | ≥ 0.40 | Strong overall but one axis lags | Target the binding constraint |
| **Lagging** | < 0.75 | < 0.40 | Severe deficits with one worst | Urgent priority on weakest axis |

## Four policy scenarios

Each brief simulates four scenarios as linear perturbations to local axis scores (clamped to [0, 1]):

| Scenario | ΔNature | ΔLivelihood | ΔWell-being | Investment mix |
|----------|---------|-------------|-------------|----------------|
| **Targeted** | 0 | +0.15 | 0 | 100% economic |
| **Sustainable** | +0.05 | +0.10 | 0 | 67% economic, 33% environmental |
| **Conservation** | +0.15 | 0 | 0 | 100% environmental |
| **Integrated** | +0.05 | +0.05 | +0.05 | 33% each |

Scenarios are evaluated by their ΔBalance and ΔProsperity. The scenario that closes the gap on the **local** limiting axis usually ranks first by ΔB; the brief labels it "High" efficiency, second "Medium", remainder "Low".

When the local limiting axis is Nature, the Conservation scenario typically dominates. When it's Livelihood, Targeted dominates. The Integrated scenario rarely dominates but is the safest hedge under uncertainty.

## Spatial extraction

Briefs aggregate over a **30 km buffer** around the municipality centroid:

1. Cast the (lon, lat) point to EPSG:4326.
2. Reproject to **EPSG:6372** (Mexico Lambert Conformal Conic) for accurate metric distances.
3. Buffer 30,000 m.
4. Reproject back to EPSG:4326.
5. Intersect with the grid (`sf::st_filter(.predicate = st_intersects)`).

Typical Mexican coastal municipality returns 15–30 grid cells. If fewer than 5, the brief flags a warning — buffer may be over land or in an unmapped sliver.

## Cost-effectiveness (optional)

When `data/cost_template.csv` provides reference unit-cost-per-axis-increase (`reference_unit_cost_increase_mxn` per axis), the skill can convert ΔPp into MXN-per-Pp-point and rank scenarios by cost-effectiveness as well as ΔB. The default brief surfaces only ΔB and ΔPp; cost-per-Pp can be added by extending `run_scenario()` in `07_generate_policy_briefs.R`.

## Equity

The MPpI tells you *what* to invest in but not *how* to ensure benefits reach marginalized populations. Briefs include a standing recommendation to follow the **Ocean Equity Index (OEI)** assessment before implementation, with reminders to consider small-scale fishers, women and youth, and indigenous/migrant communities. Equity considerations should be added by local experts — the auto-generated brief leaves space for that.

## References

- Favoretto F. et al. (in prep). *The Marine Prosperity Index: A Decision Framework for Balanced Coastal Development.*
- INEGI Population Census 2020; CONEVAL poverty measures
- CONAPESCA fisheries statistics
- MODIS, Copernicus Marine Service, CONABIO
