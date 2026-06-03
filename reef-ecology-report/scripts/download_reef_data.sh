#!/bin/bash
# Download sample reef monitoring data for practice
# Usage: ./download_reef_data.sh [--region REGION]

REGION="${2:-global}"
OUTPUT_DIR="./reef_sample_data"

mkdir -p "$OUTPUT_DIR"

echo "Downloading sample reef data for region: $REGION"

# Create sample transect data
cat > "$OUTPUT_DIR/sample_transects.csv" << 'EOF'
site_id,transect_id,date,depth_m,hard_coral,soft_coral,algae,sponge,sand,rubble,total_points
SITE_A,T1,2024-01-15,5.0,35,8,22,5,15,15,100
SITE_A,T2,2024-01-15,5.0,32,10,25,4,14,15,100
SITE_A,T3,2024-01-15,10.0,28,12,30,6,12,12,100
SITE_B,T1,2024-01-16,5.0,42,6,18,8,14,12,100
SITE_B,T2,2024-01-16,5.0,38,8,20,7,15,12,100
SITE_B,T3,2024-01-16,10.0,35,10,22,8,13,12,100
SITE_C,T1,2024-01-17,5.0,25,5,35,4,16,15,100
SITE_C,T2,2024-01-17,5.0,22,6,38,5,15,14,100
SITE_C,T3,2024-01-17,10.0,18,8,42,6,14,12,100
EOF

# Create sample species data
cat > "$OUTPUT_DIR/sample_species.csv" << 'EOF'
site_id,transect_id,species,count,size_cm,bleaching_status
SITE_A,T1,Acropora palmata,12,25,normal
SITE_A,T1,Orbicella faveolata,8,45,pale
SITE_A,T1,Porites astreoides,15,12,normal
SITE_A,T2,Acropora palmata,10,22,normal
SITE_A,T2,Diploria strigosa,6,35,normal
SITE_B,T1,Acropora cervicornis,18,15,normal
SITE_B,T1,Montastraea cavernosa,12,55,normal
SITE_B,T1,Siderastrea siderea,9,20,pale
SITE_B,T2,Acropora palmata,8,28,normal
SITE_C,T1,Porites astreoides,20,10,normal
SITE_C,T1,Agaricia agaricites,14,8,pale
SITE_C,T2,Orbicella annularis,5,60,bleached_partial
EOF

# Create sample environmental data
cat > "$OUTPUT_DIR/sample_environment.csv" << 'EOF'
site_id,date,temperature_c,salinity_ppt,turbidity_ntu,ph
SITE_A,2024-01-15,27.5,35.2,2.1,8.15
SITE_B,2024-01-16,27.8,35.0,1.8,8.18
SITE_C,2024-01-17,28.2,34.8,3.5,8.12
EOF

echo "Sample data downloaded to: $OUTPUT_DIR/"
echo "Files created:"
ls -la "$OUTPUT_DIR/"

echo ""
echo "Load the data in Python:"
echo "  import pandas as pd"
echo "  transects = pd.read_csv('$OUTPUT_DIR/sample_transects.csv')"
echo "  species = pd.read_csv('$OUTPUT_DIR/sample_species.csv')"
echo "  environment = pd.read_csv('$OUTPUT_DIR/sample_environment.csv')"
