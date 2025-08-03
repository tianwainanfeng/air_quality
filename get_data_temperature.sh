#!/bin/bash

# Directory to store data
OUTPUT_DIR="data/temperature"
mkdir -p ${OUTPUT_DIR}

# Station ID for DuPage Airport
station_id=72530594892

# Loop over years
for year in {2006..2025}; do
    echo "Downloading $year..."
    curl -f -o "${OUTPUT_DIR}/${station_id}_${year}.csv" \
        "https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/${year}/${station_id}.csv"
done

echo "✅ Download complete."

