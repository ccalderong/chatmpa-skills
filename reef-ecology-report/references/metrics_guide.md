# Reef Ecology Metrics Guide

## Coral Coverage Metrics

### Percent Cover
The most fundamental reef health metric. Calculated from point intercept transects.

```python
def percent_cover(points_coral, total_points):
    """
    Calculate percent coral cover from point intercept data.

    Args:
        points_coral: Number of points falling on coral
        total_points: Total number of points sampled

    Returns:
        Percent cover as float (0-100)
    """
    return (points_coral / total_points) * 100
```

### Benthic Categories
Standard categories for point intercept surveys:
- Hard Coral (HC) - Scleractinian corals
- Soft Coral (SC) - Alcyonaceans
- Recently Killed Coral (RKC) - Dead <1 year
- Nutrient Indicator Algae (NIA) - Fleshy macroalgae
- Sponge (SP)
- Rock (RCK)
- Rubble (RB)
- Sand (SD)
- Other (OT)

## Diversity Indices

### Shannon-Wiener Index (H')
Measures species diversity considering both richness and evenness.

```python
import numpy as np

def shannon_wiener(abundances):
    """
    Calculate Shannon-Wiener diversity index.

    H' = -Σ(pi * ln(pi))

    Args:
        abundances: Array of species abundances

    Returns:
        H' value (typically 0-4 for reef communities)
    """
    total = np.sum(abundances)
    proportions = abundances / total
    proportions = proportions[proportions > 0]  # Remove zeros
    return -np.sum(proportions * np.log(proportions))
```

**Interpretation:**
- H' < 1.0: Low diversity
- H' = 1.0-2.0: Medium diversity
- H' = 2.0-3.0: High diversity
- H' > 3.0: Very high diversity

### Simpson's Index (D)
Probability that two randomly selected individuals belong to different species.

```python
def simpsons_index(abundances):
    """
    Calculate Simpson's diversity index.

    D = 1 - Σ(pi^2)

    Returns:
        D value (0-1, higher = more diverse)
    """
    total = np.sum(abundances)
    proportions = abundances / total
    return 1 - np.sum(proportions ** 2)
```

### Species Richness (S)
Simple count of species present.

```python
def species_richness(species_list):
    """Count unique species."""
    return len(set(species_list))
```

### Pielou's Evenness (J')
How evenly individuals are distributed among species.

```python
def pielous_evenness(abundances):
    """
    Calculate Pielou's evenness index.

    J' = H' / ln(S)

    Returns:
        J' value (0-1, 1 = perfectly even)
    """
    H = shannon_wiener(abundances)
    S = len(abundances[abundances > 0])
    if S <= 1:
        return 0
    return H / np.log(S)
```

## Bleaching Metrics

### Bleaching Prevalence
Percentage of colonies showing any bleaching.

```python
def bleaching_prevalence(colonies_bleached, total_colonies):
    """Percent of colonies with any bleaching."""
    return (colonies_bleached / total_colonies) * 100
```

### Bleaching Severity Index
Weighted average of bleaching intensity.

```python
def bleaching_severity_index(df):
    """
    Calculate bleaching severity on 0-4 scale.

    0 = Normal coloration
    1 = Pale
    2 = 1-50% bleached
    3 = 50-100% bleached
    4 = Recently dead
    """
    severity_weights = {
        'normal': 0,
        'pale': 1,
        'bleached_partial': 2,
        'bleached_severe': 3,
        'recently_dead': 4
    }
    df['severity_score'] = df['bleaching_category'].map(severity_weights)
    return df['severity_score'].mean()
```

## Reef Health Index

### Composite Reef Health Score
Combines multiple metrics into single 1-5 score.

```python
def reef_health_index(coral_cover, algae_cover, fish_biomass, recruitment):
    """
    Calculate composite reef health index.

    Based on Atlantic and Gulf Rapid Reef Assessment (AGRRA) methods.

    Returns:
        Score 1-5 (5 = excellent health)
    """
    scores = []

    # Coral cover score
    if coral_cover >= 40: scores.append(5)
    elif coral_cover >= 20: scores.append(4)
    elif coral_cover >= 10: scores.append(3)
    elif coral_cover >= 5: scores.append(2)
    else: scores.append(1)

    # Algae score (inverse - less is better)
    if algae_cover <= 10: scores.append(5)
    elif algae_cover <= 25: scores.append(4)
    elif algae_cover <= 50: scores.append(3)
    elif algae_cover <= 75: scores.append(2)
    else: scores.append(1)

    # Fish biomass score (g/m²)
    if fish_biomass >= 60: scores.append(5)
    elif fish_biomass >= 40: scores.append(4)
    elif fish_biomass >= 20: scores.append(3)
    elif fish_biomass >= 10: scores.append(2)
    else: scores.append(1)

    # Recruitment score (juveniles/m²)
    if recruitment >= 10: scores.append(5)
    elif recruitment >= 5: scores.append(4)
    elif recruitment >= 2: scores.append(3)
    elif recruitment >= 1: scores.append(2)
    else: scores.append(1)

    return np.mean(scores)
```

## Size Structure Metrics

### Colony Size Distribution
```python
def size_class_distribution(sizes, bins=[0, 5, 10, 20, 40, 100, np.inf]):
    """
    Categorize colonies into size classes.

    Default bins (cm diameter):
    - Recruits: 0-5
    - Small: 5-10
    - Medium: 10-20
    - Large: 20-40
    - Very Large: 40-100
    - Massive: >100
    """
    labels = ['Recruit', 'Small', 'Medium', 'Large', 'Very Large', 'Massive']
    return pd.cut(sizes, bins=bins, labels=labels[:-1])
```

### Recruitment Rate
```python
def recruitment_rate(juveniles_per_m2, years=1):
    """
    Calculate annual recruitment rate.

    Juveniles typically defined as <5cm diameter.
    """
    return juveniles_per_m2 / years
```

## Statistical Comparisons

### Power Analysis for Reef Surveys
```python
from scipy import stats

def required_sample_size(effect_size, alpha=0.05, power=0.8):
    """
    Calculate required transects for detecting change.

    Args:
        effect_size: Expected change as proportion of SD
        alpha: Significance level
        power: Desired statistical power

    Returns:
        Required number of transects per site
    """
    from scipy.stats import norm
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
    return int(np.ceil(n))
```
