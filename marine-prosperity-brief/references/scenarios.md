# Four Policy Scenarios — Specification

Each brief simulates four scenarios. The simulation is intentionally simple: a constant additive perturbation per axis, clamped to [0, 1], with B / L / Pp recomputed and ranked by ΔBalance.

## Scenarios

| Scenario | ΔNature | ΔLivelihood | ΔWell-being | Investment mix |
|----------|---------|-------------|-------------|----------------|
| **Targeted** | 0.00 | +0.15 | 0.00 | 100% economic |
| **Sustainable** | +0.05 | +0.10 | 0.00 | 67% economic, 33% environmental |
| **Conservation** | +0.15 | 0.00 | 0.00 | 100% environmental |
| **Integrated** | +0.05 | +0.05 | +0.05 | 33% each dimension |

Total axis-points added is 0.15 in all scenarios so the scenarios are comparable per unit effort.

## Mechanics

```R
run_scenario <- function(df, s) {
  df %>%
    mutate(
      nat_new   = pmax(0, pmin(1, nature     + s$nat)),
      liv_new   = pmax(0, pmin(1, livelihood + s$liv)),
      well_new  = pmax(0, pmin(1, wellbeing  + s$well)),
      lev_new   = (nat_new + liv_new + well_new) / 3,
      bal_new   = compute_balance_vec(nat_new, liv_new, well_new),
      pp_new    = bal_new * lev_new,
      bal_delta = bal_new - balance
    )
}
```

Scenarios are evaluated **per cell**, then averaged across the buffer. This preserves the curvature of Balance (an evenness metric) — averaging axes first then computing B would understate ΔB for heterogeneous buffers.

## Efficiency ranking

```R
bd  <- map_dbl(scen_results, "bal_delta")
rk  <- rank(-bd, ties.method = "first")
eff <- case_when(rk == 1 ~ "High", rk == 2 ~ "Medium", TRUE ~ "Low")
```

High / Medium / Low refer **only to ΔBalance**, not absolute Pp. A Conservation scenario with high ΔB but small ΔL increase can still be ranked High because the framework prioritizes coordination.

## Interpretation rules

- **Limiting axis = Nature** → Conservation usually dominates ΔB. Targeted may produce negative ΔB (widens the gap).
- **Limiting axis = Livelihood** → Targeted dominates. Conservation widens the gap.
- **Limiting axis = Well-being** → No scenario directly addresses Well-being except Integrated. The brief should flag Well-being investment as a custom gap not captured by the four canonical scenarios, and recommend adding a +0.10 Well-being scenario.
- **Balanced + high Level community** → Integrated often produces the smallest ΔB because all axes start near each other; the gain comes from L, not from rebalancing.

## Extending the scenario set

To add scenarios (e.g. a Well-being-focused scenario), append to the `scenarios_def` list in `07_generate_policy_briefs.R`:

```R
scenarios_def <- list(
  targeted     = list(name = "Targeted",     nat = 0,    liv = 0.15, well = 0,    focus = "100% economic"),
  sustainable  = list(name = "Sustainable",  nat = 0.05, liv = 0.10, well = 0,    focus = "67% economic, 33% environmental"),
  conservation = list(name = "Conservation", nat = 0.15, liv = 0,    well = 0,    focus = "100% environmental"),
  integrated   = list(name = "Integrated",   nat = 0.05, liv = 0.05, well = 0.05, focus = "33% each dimension"),
  social       = list(name = "Social",       nat = 0,    liv = 0,    well = 0.15, focus = "100% well-being")    # custom
)
```

The brief's scenario table automatically adjusts to whatever scenarios are defined; downstream DOCX builder reads the rows by parsing markdown, no hardcoded scenario list.

## Limitations

- **Linear perturbation:** real interventions exhibit diminishing returns. The simulation overstates gains for cells already near 1.0 on a given axis (clamping mitigates this but does not eliminate optimism).
- **No cross-axis feedback:** the static scenarios ignore that boosting Livelihood (e.g. via fisheries expansion) can degrade Nature. The companion script `code/05_feedback_scenarios.R` models cross-axis dynamics using literature-derived coefficients in `data/feedback_parameters.csv`.
- **No spatial spillovers:** each cell is treated independently; spillovers from adjacent MPAs or industrial zones are not modeled.

For a more realistic outlook, layer the static scenarios with the feedback-augmented sensitivity from `feedback_analysis_results.rds` (script 05).
