# OBIS Data Access Guide

## Introduction

OBIS (Ocean Biodiversity Information System) is the world's largest open-access repository for marine biodiversity data.

## Using pyobis

### Installation
```bash
pip install pyobis
```

### Basic Usage

```python
from pyobis import occurrences, taxa, checklist

# Search for species
result = taxa.search(q="Caretta caretta")
print(result)

# Get taxon details
taxon = taxa.search(scientificname="Caretta caretta")
taxon_id = taxon[0]['taxonID']  # AphiaID from WoRMS

# Download occurrences
occ = occurrences.search(taxonid=taxon_id)
```

### Filtering Occurrences

```python
# By geometry (WKT format)
geometry = "POLYGON((-80 25,-80 30,-75 30,-75 25,-80 25))"
occ = occurrences.search(taxonid=taxon_id, geometry=geometry)

# By date range
occ = occurrences.search(
    taxonid=taxon_id,
    startdate="2020-01-01",
    enddate="2023-12-31"
)

# By depth
occ = occurrences.search(
    taxonid=taxon_id,
    startdepth=0,
    enddepth=100
)

# By dataset
occ = occurrences.search(
    taxonid=taxon_id,
    datasetid="dataset_uuid"
)

# Combine filters
occ = occurrences.search(
    taxonid=taxon_id,
    geometry=geometry,
    startdate="2020-01-01",
    enddepth=200
)
```

### Pagination for Large Downloads

```python
def download_all_occurrences(taxon_id, **kwargs):
    """
    Download all occurrences handling pagination.
    """
    all_records = []
    offset = 0
    size = 10000  # Max per request

    while True:
        records = occurrences.search(
            taxonid=taxon_id,
            size=size,
            offset=offset,
            **kwargs
        )

        if not records:
            break

        all_records.extend(records)
        offset += size
        print(f"Downloaded {len(all_records)} records...")

        if len(records) < size:
            break

    return pd.DataFrame(all_records)

# Usage
df = download_all_occurrences(127405)  # Loggerhead turtle
```

## Data Quality Flags

OBIS includes quality control flags. Filter by quality:

```python
def filter_by_quality(df):
    """Filter occurrences by OBIS quality flags."""

    # Available quality flags:
    # - dropped: Record failed quality control
    # - absence: Absence record (not presence)
    # - marine: Record is marine
    # - terrestrial: Record is on land (error)

    # Keep only marine, non-dropped records
    clean = df[
        (df.get('dropped', False) == False) &
        (df.get('marine', True) == True) &
        (df.get('absence', False) == False)
    ]

    return clean
```

## Common Fields

| Field | Description |
|-------|-------------|
| decimalLongitude | Longitude in decimal degrees |
| decimalLatitude | Latitude in decimal degrees |
| eventDate | Date of observation |
| depth | Depth in meters |
| scientificName | Species name |
| taxonID | WoRMS AphiaID |
| datasetName | Source dataset |
| basisOfRecord | Type (observation, specimen, etc.) |
| coordinateUncertaintyInMeters | Spatial precision |
| institutionCode | Data provider |

## Taxonomic Queries

```python
from pyobis import taxa

# Search by common name
result = taxa.search(q="green turtle")

# Get children taxa
children = taxa.taxon(taxonid=137205, children=True)

# Get taxonomy hierarchy
hierarchy = taxa.taxon(taxonid=137205)
```

## Dataset Information

```python
from pyobis import dataset

# List datasets
datasets = dataset.search(q="coral")

# Get dataset details
info = dataset.get(id="dataset_uuid")
```

## Example: Complete Download Workflow

```python
import pandas as pd
from pyobis import occurrences, taxa

def download_species_data(species_name, region_wkt=None, start_year=2010):
    """
    Complete workflow to download and clean species occurrence data.

    Args:
        species_name: Scientific name
        region_wkt: Optional WKT geometry string
        start_year: Start year for records

    Returns:
        Cleaned pandas DataFrame
    """
    # Step 1: Get taxon ID
    print(f"Searching for {species_name}...")
    taxon_result = taxa.search(scientificname=species_name)

    if not taxon_result:
        raise ValueError(f"Species not found: {species_name}")

    taxon_id = taxon_result[0]['taxonID']
    print(f"Found taxon ID: {taxon_id}")

    # Step 2: Download occurrences
    print("Downloading occurrences...")
    kwargs = {
        'startdate': f"{start_year}-01-01",
    }
    if region_wkt:
        kwargs['geometry'] = region_wkt

    df = download_all_occurrences(taxon_id, **kwargs)
    print(f"Downloaded {len(df)} raw records")

    # Step 3: Clean data
    print("Cleaning data...")

    # Remove missing coordinates
    df = df.dropna(subset=['decimalLongitude', 'decimalLatitude'])

    # Remove duplicates
    df = df.drop_duplicates(subset=['decimalLongitude', 'decimalLatitude', 'eventDate'])

    # Filter by coordinate precision
    if 'coordinateUncertaintyInMeters' in df.columns:
        df = df[df['coordinateUncertaintyInMeters'].fillna(9999) < 10000]

    # Remove flagged records
    if 'dropped' in df.columns:
        df = df[df['dropped'] != True]

    print(f"Cleaned to {len(df)} records")

    # Step 4: Select useful columns
    columns = [
        'decimalLongitude', 'decimalLatitude', 'eventDate',
        'depth', 'scientificName', 'datasetName',
        'basisOfRecord', 'coordinateUncertaintyInMeters'
    ]
    df = df[[c for c in columns if c in df.columns]]

    return df

# Usage
caribbean = "POLYGON((-100 10,-100 35,-60 35,-60 10,-100 10))"
turtles = download_species_data(
    "Chelonia mydas",
    region_wkt=caribbean,
    start_year=2015
)
turtles.to_csv("green_turtle_occurrences.csv", index=False)
```

## Spatial Thinning

For SDM, reduce spatial autocorrelation by thinning points:

```python
from sklearn.neighbors import BallTree

def spatial_thin(df, min_distance_km=10):
    """
    Remove points that are too close together.

    Args:
        df: DataFrame with decimalLongitude, decimalLatitude
        min_distance_km: Minimum distance between points

    Returns:
        Thinned DataFrame
    """
    coords = np.radians(df[['decimalLatitude', 'decimalLongitude']].values)
    tree = BallTree(coords, metric='haversine')

    # Earth radius in km
    earth_radius = 6371
    min_rad = min_distance_km / earth_radius

    keep = []
    for i in range(len(df)):
        if i == 0:
            keep.append(True)
            continue

        # Check distance to all kept points
        kept_coords = coords[keep]
        distances = tree.query([coords[i]], k=1, return_distance=True)[0][0]

        if distances.min() >= min_rad:
            keep.append(True)
        else:
            keep.append(False)

    return df[keep].copy()

thinned = spatial_thin(turtles, min_distance_km=50)
print(f"Thinned: {len(turtles)} -> {len(thinned)} records")
```
