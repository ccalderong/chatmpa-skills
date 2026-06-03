#!/bin/bash
# Download species occurrence data from OBIS
# Usage: ./download_obis.sh --species "Chelonia mydas" [--region caribbean] [--output FILE]

set -e

# Default values
OUTPUT_FILE="occurrences.csv"
REGION=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --species)
            SPECIES="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate species
if [ -z "$SPECIES" ]; then
    echo "Usage: $0 --species \"Scientific name\" [--region REGION] [--output FILE]"
    echo ""
    echo "Options:"
    echo "  --species    Scientific name (required)"
    echo "  --region     Region name: caribbean, pacific, atlantic, global"
    echo "  --output     Output CSV file (default: occurrences.csv)"
    exit 1
fi

# Define region WKT polygons
case $REGION in
    caribbean)
        GEOMETRY="POLYGON((-100 10,-100 35,-60 35,-60 10,-100 10))"
        ;;
    gulf)
        GEOMETRY="POLYGON((-98 18,-98 31,-80 31,-80 18,-98 18))"
        ;;
    pacific)
        GEOMETRY="POLYGON((120 -60,120 60,-120 60,-120 -60,120 -60))"
        ;;
    atlantic)
        GEOMETRY="POLYGON((-80 -60,-80 60,0 60,0 -60,-80 -60))"
        ;;
    *)
        GEOMETRY=""
        ;;
esac

echo "Downloading OBIS data for: $SPECIES"
[ -n "$REGION" ] && echo "Region: $REGION"

# Create Python script
SCRIPT=$(cat << 'PYTHON'
import sys
import pandas as pd
from pyobis import occurrences, taxa

species_name = sys.argv[1]
output_file = sys.argv[2]
geometry = sys.argv[3] if len(sys.argv) > 3 else None

print(f"Searching for {species_name}...")
taxon = taxa.search(scientificname=species_name)
if not taxon:
    print(f"Species not found: {species_name}")
    sys.exit(1)

taxon_id = taxon[0]['taxonID']
print(f"Taxon ID: {taxon_id}")

print("Downloading occurrences...")
kwargs = {}
if geometry:
    kwargs['geometry'] = geometry

records = occurrences.search(taxonid=taxon_id, size=10000, **kwargs)
df = pd.DataFrame(records)

print(f"Downloaded {len(df)} records")

# Basic cleaning
df = df.dropna(subset=['decimalLongitude', 'decimalLatitude'])
df = df.drop_duplicates(subset=['decimalLongitude', 'decimalLatitude'])

# Select columns
cols = ['decimalLongitude', 'decimalLatitude', 'eventDate', 'depth',
        'scientificName', 'datasetName', 'basisOfRecord']
df = df[[c for c in cols if c in df.columns]]

df.to_csv(output_file, index=False)
print(f"Saved to {output_file}")
PYTHON
)

# Run Python script
python3 -c "$SCRIPT" "$SPECIES" "$OUTPUT_FILE" "$GEOMETRY"

echo ""
echo "Data saved to: $OUTPUT_FILE"
echo ""
echo "Load in Python:"
echo "  import pandas as pd"
echo "  occ = pd.read_csv('$OUTPUT_FILE')"
