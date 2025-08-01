#!/bin/bash

# URL prefix
base_url="https://aqs.epa.gov/aqsweb/airdata"

work_area="${PWD}"
mkdir -p data
cd data || { echo "Failed to enter data directory"; exit 1; }

# download the zip files for each year
for year in $(seq 2005 2024); do
  file="annual_aqi_by_county_${year}.zip"
  if [ ! -f "$file" ]; then
    echo "Downloading $file..."
    curl -O "${base_url}/${file}"
  else
    echo "$file already exists, skipping."
  fi
done

# return
cd ${work_area}
echo "Done!"
