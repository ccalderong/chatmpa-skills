# ERDDAP Data Access Guide

## Introduction

ERDDAP (Environmental Research Division Data Access Program) is a data server that provides a simple, consistent way to download scientific data in various formats.

## Common ERDDAP Servers

```python
ERDDAP_SERVERS = {
    'coastwatch': 'https://coastwatch.pfeg.noaa.gov/erddap',
    'ioos': 'https://erddap.ioos.us/erddap',
    'copernicus': 'https://nrt.cmems-du.eu/erddap',
    'apdrc': 'http://apdrc.soest.hawaii.edu/erddap',
    'psl': 'https://psl.noaa.gov/erddap',
}
```

## Using erddapy

### Basic Setup

```python
from erddapy import ERDDAP

# Initialize connection
e = ERDDAP(
    server="https://coastwatch.pfeg.noaa.gov/erddap",
    protocol="griddap"  # or "tabledap" for tabular data
)

# Set dataset
e.dataset_id = "jplMURSST41"
```

### Discovering Datasets

```python
# Search for datasets
import pandas as pd

# Get full dataset list
url = f"{e.server}/search/index.csv?searchFor=sst"
datasets = pd.read_csv(url)
print(datasets[['Dataset ID', 'Title']].head(20))

# Get dataset metadata
info_url = e.get_info_url()
print(f"Dataset info: {info_url}")

# Get variable information
ds = e.to_xarray()
print(ds)
```

### Subsetting Data

```python
# Geographic subset
e.constraints = {
    "latitude>=": 20.0,
    "latitude<=": 30.0,
    "longitude>=": -90.0,
    "longitude<=": -80.0,
}

# Time subset
e.constraints["time>="] = "2024-01-01"
e.constraints["time<="] = "2024-12-31"

# Stride (skip every Nth point for large datasets)
e.constraints["latitude_step"] = 2
e.constraints["longitude_step"] = 2
```

### Downloading Data

```python
# As xarray Dataset (recommended)
ds = e.to_xarray()

# As pandas DataFrame
df = e.to_pandas()

# As NetCDF file
e.to_ncCF("output.nc")

# Get download URL (for manual download)
url = e.get_download_url()
print(url)
```

## Common SST Datasets

### MUR SST (jplMURSST41)
- **Resolution:** 1 km
- **Coverage:** Global, daily
- **Period:** 2002-present
- **Variables:** analysed_sst (Kelvin)

```python
e.dataset_id = "jplMURSST41"
e.variables = ["analysed_sst", "analysis_error"]
e.constraints = {
    "time>=": "2024-01-01T00:00:00Z",
    "time<=": "2024-01-31T00:00:00Z",
    "latitude>=": 15,
    "latitude<=": 35,
    "longitude>=": -100,
    "longitude<=": -75,
}
ds = e.to_xarray()
# Convert Kelvin to Celsius
ds['sst_celsius'] = ds['analysed_sst'] - 273.15
```

### MODIS SST (erdMH1sstd1day)
- **Resolution:** 4 km
- **Coverage:** Global, daily
- **Period:** 2003-present

```python
e.dataset_id = "erdMH1sstd1day"
e.variables = ["sst"]
```

### OISST (ncdcOisst21Agg)
- **Resolution:** 0.25° (~25 km)
- **Coverage:** Global, daily
- **Period:** 1981-present
- **Best for:** Long-term climate analysis

```python
e.dataset_id = "ncdcOisst21Agg"
e.variables = ["sst", "anom"]  # Includes anomaly
```

## Working with Large Datasets

### Chunked Downloads
```python
import xarray as xr

# Download in time chunks
years = range(2000, 2024)
datasets = []

for year in years:
    e.constraints["time>="] = f"{year}-01-01"
    e.constraints["time<="] = f"{year}-12-31"
    ds = e.to_xarray()
    datasets.append(ds)

# Combine
full_ds = xr.concat(datasets, dim='time')
```

### Using Dask for Parallel Processing
```python
import dask
from dask.diagnostics import ProgressBar

# Enable dask chunking
ds = e.to_xarray(chunks={'time': 30, 'latitude': 100, 'longitude': 100})

# Compute with progress bar
with ProgressBar():
    result = ds.mean(dim='time').compute()
```

## Handling Common Issues

### Authentication
Some servers require authentication:
```python
e = ERDDAP(
    server="https://protected-server.org/erddap",
    protocol="griddap"
)
e.auth = ("username", "password")
```

### Timeout Errors
```python
e.requests_kwargs = {"timeout": 300}  # 5 minutes
```

### SSL Issues
```python
e.requests_kwargs = {"verify": False}  # Not recommended for production
```

## Example: Multi-Dataset Analysis

```python
from erddapy import ERDDAP
import xarray as xr

def download_multi_source_sst(bbox, time_range):
    """
    Download SST from multiple sources for comparison.
    """
    datasets = {}

    # MUR SST
    e = ERDDAP(server="https://coastwatch.pfeg.noaa.gov/erddap", protocol="griddap")
    e.dataset_id = "jplMURSST41"
    e.variables = ["analysed_sst"]
    e.constraints = {
        "latitude>=": bbox[0], "latitude<=": bbox[1],
        "longitude>=": bbox[2], "longitude<=": bbox[3],
        "time>=": time_range[0], "time<=": time_range[1],
    }
    datasets['mur'] = e.to_xarray()

    # OISST
    e2 = ERDDAP(server="https://coastwatch.pfeg.noaa.gov/erddap", protocol="griddap")
    e2.dataset_id = "ncdcOisst21Agg"
    e2.variables = ["sst"]
    e2.constraints = e.constraints.copy()
    datasets['oisst'] = e2.to_xarray()

    return datasets

# Usage
bbox = [20, 30, -90, -80]  # lat_min, lat_max, lon_min, lon_max
time_range = ["2024-01-01", "2024-01-31"]
sst_data = download_multi_source_sst(bbox, time_range)
```
