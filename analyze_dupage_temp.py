# analyze_dupage_temp.py

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# ========== prepare data ==========

data_dir = 'data/temperature'
all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

df_list = []
for file in all_files:
    file_path = os.path.join(data_dir, file)
    df = pd.read_csv(file_path)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df_list.append(df)

weather_data = pd.concat(df_list, ignore_index=True)

# Data types
weather_data['TEMP'] = pd.to_numeric(weather_data['TEMP'], errors='coerce')
weather_data['MAX'] = pd.to_numeric(weather_data['MAX'], errors='coerce')
weather_data['MIN'] = pd.to_numeric(weather_data['MIN'], errors='coerce')
weather_data['MAX'] = weather_data['MAX'].replace(9999.9, np.nan)

# Missing data
weather_data.fillna({
    'TEMP': weather_data['TEMP'].mean(),
    'MAX': weather_data['MAX'].mean(),
    'MIN': weather_data['MIN'].mean()
}, inplace=True)

# Temperature unit (ºF->ºC)
weather_data['TEMP'] = (weather_data['TEMP'] - 32) * 5 / 9
weather_data['MAX'] = (weather_data['MAX'] - 32) * 5 / 9
weather_data['MIN'] = (weather_data['MIN'] - 32) * 5 / 9

# years & months
weather_data['YEAR'] = weather_data['DATE'].dt.year
weather_data['MONTH'] = weather_data['DATE'].dt.month

# ========== anaual summary (overall trends) ==========
annual_summary = weather_data.groupby('YEAR').agg({
    'TEMP': 'mean',
    'MAX': 'max',
    'MIN': 'min'
}).reset_index()

# ========== Seasons ==========
def get_season_and_season_year(row):
    month = row['MONTH']
    year = row['YEAR']
    if month in [3, 4, 5]:
        return 'Spring', year
    elif month in [6, 7, 8]:
        return 'Summer', year
    elif month in [9, 10, 11]:
        return 'Fall', year
    else:
        return 'Winter', year + 1 if month == 12 else year

weather_data['SEASON'], weather_data['SEASON_YEAR'] = zip(*weather_data.apply(get_season_and_season_year, axis=1))

# seasonal summary: mean, max, min
seasonal_summary = weather_data.groupby(['SEASON_YEAR', 'SEASON']).agg({
    'TEMP': 'mean',
    'MAX': 'max',
    'MIN': 'min'
}).reset_index()
seasonal_summary.rename(columns={'SEASON_YEAR': 'YEAR'}, inplace=True)

# ========== Plots ==========

os.makedirs("outputs", exist_ok=True)

# 1. Annual trends plot
plt.figure(figsize=(10, 6))
plt.plot(annual_summary['YEAR'], annual_summary['TEMP'], label='Average Temp', color='blue', marker='o')
plt.plot(annual_summary['YEAR'], annual_summary['MAX'], label='Max Temp', color='red', marker='x')
plt.plot(annual_summary['YEAR'], annual_summary['MIN'], label='Min Temp', color='green', marker='s')
plt.title('Annual Temperature Trends at DuPage Airport (2006-2025)', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Temperature (°C)', fontsize=12)
plt.xticks(annual_summary['YEAR'].astype(int))
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("outputs/dupage_temp.png")
plt.close()

# 2. Seasonal average temp
plt.figure(figsize=(10, 6))
for season in ['Spring', 'Summer', 'Fall', 'Winter']:
    df_season = seasonal_summary[seasonal_summary['SEASON'] == season]
    plt.plot(df_season['YEAR'], df_season['TEMP'], label=season, marker='o')
plt.title('Seasonal Average Temperature Trends')
plt.xlabel('Year')
plt.ylabel('Average Temperature (°C)')
plt.xticks(df_season['YEAR'].astype(int))
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("outputs/dupage_seasonal_avg_temp.png")
plt.close()

# 3. Seasonal max temp
plt.figure(figsize=(10, 6))
for season in ['Spring', 'Summer', 'Fall', 'Winter']:
    df_season = seasonal_summary[seasonal_summary['SEASON'] == season]
    plt.plot(df_season['YEAR'], df_season['MAX'], label=season, marker='x')
plt.title('Seasonal Max Temperature Trends')
plt.xlabel('Year')
plt.ylabel('Max Temperature (°C)')
plt.xticks(df_season['YEAR'].astype(int))
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("outputs/dupage_seasonal_max_temp.png")
plt.close()

# 4. Seasonal min temp
plt.figure(figsize=(10, 6))
for season in ['Spring', 'Summer', 'Fall', 'Winter']:
    df_season = seasonal_summary[seasonal_summary['SEASON'] == season]
    plt.plot(df_season['YEAR'], df_season['MIN'], label=season, marker='s')
plt.title('Seasonal Min Temperature Trends')
plt.xlabel('Year')
plt.ylabel('Min Temperature (°C)')
plt.xticks(df_season['YEAR'].astype(int))
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("outputs/dupage_seasonal_min_temp.png")
plt.close()
