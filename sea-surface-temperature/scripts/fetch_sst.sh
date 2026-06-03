#!/bin/bash
# Fetch SST data from ERDDAP
# Usage: ./fetch_sst.sh --lat MIN,MAX --lon MIN,MAX --start DATE --end DATE [--dataset ID]

set -e

# Default values
DATASET="jplMURSST41"
OUTPUT_DIR="./sst_data"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --lat)
            IFS=',' read -r LAT_MIN LAT_MAX <<< "$2"
            shift 2
            ;;
        --lon)
            IFS=',' read -r LON_MIN LON_MAX <<< "$2"
            shift 2
            ;;
        --start)
            START_DATE="$2"
            shift 2
            ;;
        --end)
            END_DATE="$2"
            shift 2
            ;;
        --dataset)
            DATASET="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$LAT_MIN" ] || [ -z "$LON_MIN" ] || [ -z "$START_DATE" ] || [ -z "$END_DATE" ]; then
    echo "Usage: $0 --lat MIN,MAX --lon MIN,MAX --start YYYY-MM-DD --end YYYY-MM-DD"
    echo ""
    echo "Options:"
    echo "  --lat      Latitude range (e.g., 20,30)"
    echo "  --lon      Longitude range (e.g., -90,-80)"
    echo "  --start    Start date (YYYY-MM-DD)"
    echo "  --end      End date (YYYY-MM-DD)"
    echo "  --dataset  ERDDAP dataset ID (default: jplMURSST41)"
    echo "  --output   Output directory (default: ./sst_data)"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build ERDDAP URL
BASE_URL="https://coastwatch.pfeg.noaa.gov/erddap/griddap"
CONSTRAINTS="[(${START_DATE}T00:00:00Z):(${END_DATE}T00:00:00Z)][(${LAT_MIN}):(${LAT_MAX})][(${LON_MIN}):(${LON_MAX})]"
URL="${BASE_URL}/${DATASET}.nc?analysed_sst${CONSTRAINTS}"

OUTPUT_FILE="${OUTPUT_DIR}/sst_${START_DATE}_${END_DATE}.nc"

echo "Downloading SST data..."
echo "Dataset: $DATASET"
echo "Region: lat=${LAT_MIN},${LAT_MAX} lon=${LON_MIN},${LON_MAX}"
echo "Period: ${START_DATE} to ${END_DATE}"
echo "URL: $URL"
echo ""

# Download
curl -o "$OUTPUT_FILE" "$URL"

if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "Download complete: $OUTPUT_FILE"
    echo "File size: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"

    # Show Python loading example
    echo ""
    echo "Load in Python:"
    echo "  import xarray as xr"
    echo "  ds = xr.open_dataset('$OUTPUT_FILE')"
    echo "  print(ds)"
else
    echo "Error: Download failed"
    exit 1
fi
