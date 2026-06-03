# =============================================================================
# 07_generate_policy_briefs.R
# Marine Prosperity Index: Policy Brief Generator
# =============================================================================
#
# Purpose: For each municipality in data/targeted_municipalities.csv, extract
#          grid cells within a 30 km buffer, compute MPI metrics, run policy
#          scenarios, and write a markdown policy brief.
#
# Inputs:
#   - data/targeted_municipalities.csv        (municipality, lon, lat)
#   - outputs/grid_sf_clean.rds               (spatial grid with geometry)
#   - outputs/normalized_scores.rds           (axis scores, nationally normalized)
#   - data/cost_template.csv
#   - outputs/tables/municipal_summary.csv    (optional; enables peer comparison)
#
# Outputs:
#   - policy_briefs/policy_brief_{slug}.md    (one file per municipality)
#
# Prerequisites: Run scripts 01 and 02 first.
# =============================================================================

library(tidyverse)
library(sf)
library(glue)

dir.create("policy_briefs", showWarnings = FALSE)

# -----------------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------------

cat("Loading data...\n")

grid_sf       <- readRDS("outputs/grid_sf_clean.rds")
normalized_df <- readRDS("outputs/normalized_scores.rds")
targets       <- read_csv("data/targeted_municipalities.csv", show_col_types = FALSE)
cost_data     <- read_csv("data/cost_template.csv", show_col_types = FALSE)

peer_path    <- "outputs/tables/municipal_summary.csv"
mun_summary  <- if (file.exists(peer_path)) {
  read_csv(peer_path, show_col_types = FALSE)
} else {
  message("Note: municipal_summary.csv not found — run script 03 to enable peer comparison.")
  NULL
}

# -----------------------------------------------------------------------------
# Constants and national averages
# -----------------------------------------------------------------------------

nat_avg <- tibble(
  nature     = mean(normalized_df$nature,     na.rm = TRUE),
  livelihood = mean(normalized_df$livelihood, na.rm = TRUE),
  wellbeing  = mean(normalized_df$wellbeing,  na.rm = TRUE),
  balance    = mean(normalized_df$balance,    na.rm = TRUE)
) %>%
  mutate(
    level      = (nature + livelihood + wellbeing) / 3,
    prosperity = balance * level
  )

costs <- list(
  nature     = cost_data$reference_unit_cost_increase_mxn[cost_data$axis == "nature"]     / 1e6,
  livelihood = cost_data$reference_unit_cost_increase_mxn[cost_data$axis == "livelihood"] / 1e6,
  wellbeing  = cost_data$reference_unit_cost_increase_mxn[cost_data$axis == "wellbeing"]  / 1e6
)

scenarios_def <- list(
  targeted     = list(name = "Targeted",     nat = 0,    liv = 0.15, well = 0,    focus = "100% economic"),
  sustainable  = list(name = "Sustainable",  nat = 0.05, liv = 0.10, well = 0,    focus = "67% economic, 33% environmental"),
  conservation = list(name = "Conservation", nat = 0.15, liv = 0,    well = 0,    focus = "100% environmental"),
  integrated   = list(name = "Integrated",   nat = 0.05, liv = 0.05, well = 0.05, focus = "33% each dimension")
)

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

# Evenness-based balance rescaled to [0, 1]
compute_balance_vec <- function(nat, liv, well) {
  mapply(function(n_, l_, w_) {
    x <- c(n_, l_, w_)
    if (any(is.na(x))) return(NA_real_)
    sum_x2 <- sum(x^2)
    if (sum_x2 == 0) return(NA_real_)
    raw <- (sum(x)^2) / (3 * sum_x2)
    (raw - 1/3) / (2/3)
  }, nat, liv, well, SIMPLIFY = TRUE)
}

classify_category <- function(balance, level) {
  case_when(
    balance >= 0.75 & level >= 0.40 ~ "Balanced Prosperity",
    balance >= 0.75 & level <  0.40 ~ "Balanced but Developing",
    balance <  0.75 & level >= 0.40 ~ "Imbalanced Growth",
    TRUE                            ~ "Lagging"
  )
}

status_vs_national <- function(val, nat_val) {
  diff <- val - nat_val
  if      (diff >  0.02) "Above average"
  else if (diff < -0.02) "Below average"
  else                   "At national average"
}

make_slug <- function(name) {
  name %>%
    str_to_lower() %>%
    str_replace_all("á", "a") %>%
    str_replace_all("é", "e") %>%
    str_replace_all("í", "i") %>%
    str_replace_all("ó", "o") %>%
    str_replace_all("ú", "u") %>%
    str_replace_all("ñ", "n") %>%
    str_replace_all("[^a-z0-9]+", "_") %>%
    str_replace_all("^_|_$", "")
}

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

build_strengths <- function(nat, liv, well, bal, lev, pp, nav) {
  items <- character(0)
  if (pp > nav$prosperity + 0.02)
    items <- c(items, glue("**Above-Average Prosperity ({round(pp, 2)}):** Combined Balance × Level exceeds the national coastal average ({round(nav$prosperity, 2)}), indicating both high coordination and strong overall performance."))
  if (bal >= 0.75)
    items <- c(items, glue("**High Balance ({round(bal, 2)}):** The region shows coordinated development — no single axis dominates or lags severely. This is uncommon along Mexico's coast."))
  if (nat  > nav$nature     + 0.02)
    items <- c(items, glue("**Above-Average Environmental Conditions ({round(nat, 2)}):** Ecological indicators exceed the national coastal average ({round(nav$nature, 2)}), reflecting stronger marine biodiversity, habitat extent, or reduced pressures."))
  if (liv  > nav$livelihood + 0.02)
    items <- c(items, glue("**Above-Average Livelihood ({round(liv, 2)}):** Economic indicators exceed the national average ({round(nav$livelihood, 2)}), reflecting diversified employment and income opportunities."))
  if (well > nav$wellbeing  + 0.02)
    items <- c(items, glue("**Above-Average Well-being ({round(well, 2)}):** Social indicators including education, health, and household services exceed the national average ({round(nav$wellbeing, 2)})."))
  if (lev  > nav$level      + 0.02)
    items <- c(items, glue("**Above-Average Overall Level ({round(lev, 2)}):** Prosperity level exceeds the national coastal average ({round(nav$level, 2)})."))
  if (length(items) == 0)
    items <- "Near-national-average performance — scores are broadly consistent with national coastal averages across dimensions."
  paste(paste0(seq_along(items), ". ", items), collapse = "\n\n")
}

build_constraints <- function(nat, liv, well, prim_axis, prim_score, lim_tab) {
  items <- character(0)
  second_score <- switch(prim_axis,
    Nature      = max(liv, well),
    Livelihood  = max(nat, well),
    `Well-being`= max(nat, liv)
  )
  gap <- second_score - prim_score
  items <- c(items, glue(
    "**{prim_axis} Gap:** The {prim_axis} axis ({round(prim_score, 2)}) trails the ",
    "stronger axes by {round(gap, 2)} points — targeted investment can close this gap ",
    "without disrupting existing strengths."
  ))
  lim_rows <- paste(
    sprintf("  - %d cells (%d%%) are %s-limited", lim_tab$n, lim_tab$pct, lim_tab$limiting_axis),
    collapse = "\n"
  )
  items <- c(items, glue(
    "**Spatial Heterogeneity:** The {sum(lim_tab$n)} grid cells show variation in limiting axes:\n{lim_rows}"
  ))
  paste(paste0(seq_along(items), ". ", items), collapse = "\n\n")
}

build_primary_rec <- function(prim_axis) {
  switch(prim_axis,
    "Nature" = paste(
      "- **Habitat restoration:** Invest in mangrove, reef, and coastal wetland rehabilitation",
      "- **Protected area management:** Strengthen existing MPAs or establish new ones",
      "- **Pollution control:** Address water quality and land-based pollution sources",
      "- **Sustainable fisheries:** Implement science-based management to rebuild depleted stocks",
      sep = "\n"
    ),
    "Livelihood" = paste(
      "- **Fisheries value chain:** Support cold storage, processing, and direct market access for small-scale fishers",
      "- **Sustainable aquaculture:** Explore mariculture opportunities appropriate to local conditions",
      "- **Ecotourism infrastructure:** Develop marine and coastal recreation services",
      "- **Employment and training:** Expand workforce development tied to coastal economy sectors",
      sep = "\n"
    ),
    "Well-being" = paste(
      "- **Health services:** Improve access to primary healthcare in coastal communities",
      "- **Education:** Expand school infrastructure and reduce education lag",
      "- **Basic services:** Extend water, sanitation, and electricity coverage",
      "- **Social transfers:** Target programs to the most marginalized coastal households",
      sep = "\n"
    )
  )
}

# -----------------------------------------------------------------------------
# Main brief generator
# -----------------------------------------------------------------------------

generate_brief <- function(mun_name, lon, lat) {

  # Spatial extraction: 30 km buffer in Mexico LCC, intersect with grid
  point_sf    <- st_sfc(st_point(c(lon, lat)), crs = 4326)
  buffer_proj <- st_buffer(st_transform(point_sf, 6372), dist = 30000)
  buffer_wgs  <- st_transform(buffer_proj, 4326)
  hits        <- grid_sf %>% st_filter(buffer_wgs, .predicate = st_intersects)
  cell_ids    <- hits$id
  n_cells     <- length(cell_ids)

  if (n_cells == 0) {
    message("  WARNING: No grid cells within 30 km of ", mun_name, " — skipping.")
    return(invisible(NULL))
  }
  cat(sprintf("  %d grid cells in buffer\n", n_cells))

  local_df <- normalized_df %>% filter(id %in% cell_ids)

  # Metrics
  local_nat  <- mean(local_df$nature,     na.rm = TRUE)
  local_liv  <- mean(local_df$livelihood, na.rm = TRUE)
  local_well <- mean(local_df$wellbeing,  na.rm = TRUE)
  local_bal  <- mean(local_df$balance,    na.rm = TRUE)
  local_lev  <- (local_nat + local_liv + local_well) / 3
  local_pp   <- local_bal * local_lev
  prosperity_cat <- classify_category(local_bal, local_lev)

  # Limiting axis breakdown
  lim_tab <- local_df %>%
    count(limiting_axis) %>%
    mutate(pct = round(100 * n / sum(n))) %>%
    arrange(desc(n))

  prim_axis  <- lim_tab$limiting_axis[1]
  prim_pct   <- lim_tab$pct[1]
  prim_score <- switch(prim_axis,
    Nature      = local_nat,
    Livelihood  = local_liv,
    `Well-being`= local_well
  )
  secondary_axis <- switch(prim_axis,
    Nature      = "Livelihood",
    Livelihood  = "Nature",
    `Well-being`= "Livelihood"
  )

  # Status labels
  nat_status  <- status_vs_national(local_nat,  nat_avg$nature)
  liv_status  <- status_vs_national(local_liv,  nat_avg$livelihood)
  well_status <- status_vs_national(local_well, nat_avg$wellbeing)
  bal_status  <- status_vs_national(local_bal,  nat_avg$balance)
  lev_status  <- status_vs_national(local_lev,  nat_avg$level)
  pp_status   <- status_vs_national(local_pp,   nat_avg$prosperity)

  # Run scenarios
  scen_results <- map(scenarios_def, function(s) {
    r <- run_scenario(local_df, s)
    prim_change <- switch(prim_axis,
      Nature      = s$nat,
      Livelihood  = s$liv,
      `Well-being`= s$well
    )
    list(
      name        = s$name,
      focus       = s$focus,
      prim_change = prim_change,
      bal_delta   = mean(r$bal_delta,  na.rm = TRUE),
      pp_delta    = mean(r$pp_new,     na.rm = TRUE) - local_pp
    )
  })

  bd  <- map_dbl(scen_results, "bal_delta")
  rk  <- rank(-bd, ties.method = "first")
  eff <- case_when(rk == 1 ~ "High", rk == 2 ~ "Medium", TRUE ~ "Low")
  names(eff) <- names(scen_results)

  # Scenario table
  scen_rows <- imap_chr(scen_results, function(s, k) {
    prim_col <- if (s$prim_change > 0) {
      sprintf("%.2f → %.2f", prim_score, prim_score + s$prim_change)
    } else {
      "No change"
    }
    sprintf("| %s | %s | %s | %+.1f%% | %+.1f%% | %s |",
            s$name, s$focus, prim_col,
            s$bal_delta * 100, s$pp_delta * 100, eff[[k]])
  })
  scen_table <- paste(
    sprintf("| Scenario | Investment Focus | %s Change | Balance Δ | Prosperity Δ | Efficiency |", prim_axis),
    "|----------|------------------|-----------|-----------|--------------|------------|",
    paste(scen_rows, collapse = "\n"),
    sep = "\n"
  )

  # Peer comparison
  if (!is.null(mun_summary)) {
    peers <- mun_summary %>%
      filter(municipality != mun_name) %>%
      mutate(
        level    = (nature + livelihood + wellbeing) / 3,
        category = classify_category(balance_score, level),
        dist     = abs(balance_score - local_bal) + abs(level - local_lev)
      ) %>%
      arrange(dist) %>%
      head(3)

    peer_rows <- sprintf("| %s | %.2f | %.2f | %s | %s |",
                         peers$municipality, peers$balance_score,
                         peers$level, peers$category, peers$limiting_axis)
    self_row  <- sprintf("| **%s** | %.2f | %.2f | %s | %s |",
                         mun_name, local_bal, local_lev, prosperity_cat, prim_axis)

    peer_section <- paste(
      "| Municipality | Balance | Level | Category | Limiting Axis |",
      "|--------------|---------|-------|----------|---------------|",
      self_row,
      paste(peer_rows, collapse = "\n"),
      sep = "\n"
    )
  } else {
    peer_section <- "_Peer comparison requires outputs/tables/municipal_summary.csv — run script 03 first._"
  }

  # Text sections
  strengths_text    <- build_strengths(local_nat, local_liv, local_well, local_bal, local_lev, local_pp, nat_avg)
  constraints_text  <- build_constraints(local_nat, local_liv, local_well, prim_axis, prim_score, lim_tab)
  primary_rec_text  <- build_primary_rec(prim_axis)
  date_str          <- format(Sys.Date(), "%B %Y")

  # Assemble markdown
  md <- glue('
# Marine Prosperity Index: {mun_name} Policy Brief

**Location:** {mun_name}

**Date:** {date_str}

**Prepared using:** Marine Prosperity Index (MPpI) Framework

---

## Executive Summary

The {mun_name} region is classified as **{prosperity_cat}** under the Marine Prosperity Index. Analysis of {n_cells} grid cells within a 30 km radius shows that {prim_axis} is the binding constraint in {prim_pct}% of cells (score: {round(prim_score, 2)}). The overall prosperity level is {round(local_lev, 2)} ({lev_status}, national average {round(nat_avg$level, 2)}), balance is {round(local_bal, 2)} ({bal_status}, national average {round(nat_avg$balance, 2)}), and the Prosperity index **Pp = Balance × Level = {round(local_pp, 2)}** is {pp_status} the national coastal average ({round(nat_avg$prosperity, 2)}).

---

## Key Metrics

| Dimension | Score | National Average | Status |
|-----------|-------|------------------|--------|
| **Nature** | {round(local_nat, 2)} | {round(nat_avg$nature, 2)} | {nat_status} |
| **Livelihood** | {round(local_liv, 2)} | {round(nat_avg$livelihood, 2)} | {liv_status} |
| **Well-being** | {round(local_well, 2)} | {round(nat_avg$wellbeing, 2)} | {well_status} |
| **Balance** | {round(local_bal, 2)} | {round(nat_avg$balance, 2)} | {bal_status} |
| **Level** | {round(local_lev, 2)} | {round(nat_avg$level, 2)} | {lev_status} |
| **Prosperity (Pp = B × L)** | {round(local_pp, 2)} | {round(nat_avg$prosperity, 2)} | {pp_status} |

**Prosperity Category:** {prosperity_cat}

**Limiting Axis:** {prim_axis} ({prim_pct}% of {n_cells} grid cells)

---

## Diagnostic Findings

### Strengths

{strengths_text}

### Constraints

{constraints_text}

---

## Policy Recommendations

### Category-Appropriate Strategy

As a **{prosperity_cat}** region, the investment priority is to address the **{prim_axis}** axis while protecting existing strengths in {secondary_axis} and other dimensions.

### Recommended Actions

**1. {prim_axis} Enhancement (Primary)**

{primary_rec_text}

**2. {secondary_axis} Safeguards (Secondary)**

- Maintain and monitor {secondary_axis} conditions
- Ensure primary investments do not degrade existing {secondary_axis} assets

**3. Cross-Dimensional Maintenance (Tertiary)**

- Ensure services and conditions keep pace with population and economic changes

---

## Projected Outcomes

{scen_table}

**Interpreting the results:** The Targeted scenario concentrates investment in the limiting axis ({prim_axis}), achieving the highest balance and prosperity improvement per unit invested. Conservation-only approaches may widen axis gaps if {prim_axis} is already the weakest dimension. Integrated investment distributes resources evenly but achieves less corrective impact. Prosperity Δ = change in Pp = Balance × Level relative to baseline.

---

## Comparison with Similar Regions

{peer_section}

---

## Equity Considerations

The MPpI identifies **what** to invest in but not **how** to ensure benefits reach marginalized groups. Before implementation, assess:

- **Small-scale fishers:** Ensure investments reach smaller operations, not just established cooperatives
- **Women and youth:** Target employment and training to underrepresented groups
- **Indigenous and migrant communities:** Consult with local communities regarding development affecting traditional territories

**Recommendation:** Apply Ocean Equity Index (OEI) assessment to specific interventions before implementation.

_[Additional regional equity considerations to be added by local experts]_

---

## Data Sources

- Environmental indicators: MODIS, Copernicus Marine Service, CONABIO
- Economic indicators: INEGI Economic Census, CONAPESCA fisheries statistics
- Social indicators: INEGI Population Census 2020, CONEVAL poverty measures
- Spatial resolution: 0.05° (~5 km) grid cells; {n_cells} cells within 30 km buffer of {mun_name}

---

## Contact

For methodology details, see: *The Marine Prosperity Index: A Decision Framework for Balanced Coastal Development* (Favoretto et al., in preparation)

For data access: [Zenodo repository link]

---

*This policy brief was generated automatically using the Marine Prosperity Index framework. The MPpI provides diagnostic guidance on investment priorities but does not prescribe specific intervention designs. Local stakeholder engagement and equity assessment should inform implementation.*
')

  out_path <- file.path("policy_briefs", paste0("policy_brief_", make_slug(mun_name), ".md"))
  writeLines(md, out_path)
  cat(sprintf("  Saved: %s\n", out_path))
  invisible(out_path)
}

# -----------------------------------------------------------------------------
# Run for all targeted municipalities
# -----------------------------------------------------------------------------

cat(sprintf("\nGenerating policy briefs for %d municipalities...\n", nrow(targets)))

for (i in seq_len(nrow(targets))) {
  cat(sprintf("\n[%d/%d] %s\n", i, nrow(targets), targets$municipality[i]))
  generate_brief(
    mun_name = targets$municipality[i],
    lon      = targets$lon[i],
    lat      = targets$lat[i]
  )
}

cat("\nDone. Policy briefs saved to policy_briefs/\n")
