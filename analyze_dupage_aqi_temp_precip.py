import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Input data folder
DATA_DIR = 'data/temperature'  # contains both temp and precip

# ========== LOAD TEMPERATURE & PRECIPITATION ==========
all_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
weather_dfs = []

for file in all_files:
    df = pd.read_csv(os.path.join(DATA_DIR, file))
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['TEMP'] = pd.to_numeric(df['TEMP'], errors='coerce')
    df['PRCP'] = pd.to_numeric(df['PRCP'], errors='coerce')
    df = df[df['PRCP'] != 99.99]  # remove invalid precip
    weather_dfs.append(df)

weather_data = pd.concat(weather_dfs, ignore_index=True)

# ºF -> ºC
weather_data['TEMP'] = (weather_data['TEMP'] - 32) * 5 / 9
weather_data['YEAR'] = weather_data['DATE'].dt.year
weather_data['MONTH'] = weather_data['DATE'].dt.month

# Convert precipitation from inches to millimeters
weather_data['PRCP'] = weather_data['PRCP'] * 25.4  # 1 inch = 25.4 mm

# assign season
def assign_season(month):
    if month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Fall'
    else:
        return 'Winter'

weather_data['SEASON'] = weather_data['MONTH'].apply(assign_season)

# winter year adjustment
weather_data.loc[weather_data['MONTH'] == 12, 'YEAR'] += 1

# remove anomalies from 2007 and 2020
weather_data = weather_data[~weather_data['YEAR'].isin([2007, 2020])]

# ========== SEASONAL AVERAGES ==========
seasonal_avg = weather_data.groupby(['YEAR', 'SEASON'])[['TEMP', 'PRCP']].mean().reset_index()

# pivot: TEMP
seasonal_temp_pivot = seasonal_avg.pivot(index='YEAR', columns='SEASON', values='TEMP').reset_index()
# pivot: PRCP
seasonal_prcp_pivot = seasonal_avg.pivot(index='YEAR', columns='SEASON', values='PRCP').reset_index()

# ========== LOAD AQI ==========
AQI_DIR = 'data/air_quality'
aqi_files = [f for f in os.listdir(AQI_DIR) if f.endswith('.csv') and f.startswith('annual_aqi_by_county')]

aqi_data_list = []
for file in aqi_files:
    year = int(file[-8:-4])
    df = pd.read_csv(os.path.join(AQI_DIR, file))
    dupage = df[df['County'].str.lower() == 'dupage']
    if not dupage.empty:
        aqi_row = dupage[['Max AQI', '90th Percentile AQI', 'Median AQI']].copy()
        aqi_row['YEAR'] = year
        aqi_data_list.append(aqi_row)

aqi_df = pd.concat(aqi_data_list, ignore_index=True)

# ========== MERGE ==========
merged_temp_aqi = pd.merge(seasonal_temp_pivot, aqi_df, on='YEAR', how='inner').sort_values(by='YEAR')
merged_prcp_temp = pd.merge(seasonal_temp_pivot, seasonal_prcp_pivot, on='YEAR', suffixes=('_TEMP', '_PRCP')).sort_values(by='YEAR')
merged_prcp_aqi = pd.merge(seasonal_prcp_pivot, aqi_df, on='YEAR', how='inner').sort_values(by='YEAR')

# ========== PLOT 1: Seasonal TEMP vs AQI ==========
fig, ax1 = plt.subplots(figsize=(12, 7))
ax1.set_title('Seasonal Avg Temperature vs AQI in DuPage County (Excl. 2007, 2020)')
for season, color, marker in zip(['Spring', 'Summer', 'Fall', 'Winter'], ['green', 'orange', 'brown', 'blue'], ['o', '^', 's', 'd']):
    ax1.plot(merged_temp_aqi['YEAR'], merged_temp_aqi[season], label=f'{season} Temp', color=color, marker=marker)
ax1.set_ylabel('Temperature (°C)', color='black')
ax1.set_xlabel('Year')
ax1.set_xticks(merged_temp_aqi['YEAR'])
ax1.set_xticklabels(merged_temp_aqi['YEAR'].astype(int), rotation=45)
ax1.tick_params(axis='y', labelcolor='black')

ax2 = ax1.twinx()
for aqi_col, style, color in zip(['Max AQI', '90th Percentile AQI', 'Median AQI'], ['--', '--', '--'], ['red', 'purple', 'gray']):
    ax2.plot(merged_temp_aqi['YEAR'], merged_temp_aqi[aqi_col], linestyle=style, label=aqi_col, color=color, marker='x')
ax2.set_ylabel('Air Quality Index (AQI)', color='black')
ax2.tick_params(axis='y', labelcolor='black')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.grid(True)
plt.tight_layout()
os.makedirs('outputs', exist_ok=True)
plt.savefig('outputs/dupage_seasonal_temp_vs_aqi_dual_axis.png')
plt.close()

# ========== PLOT 2: Seasonal TEMP vs PRCP over time (dual axis) ==========
fig, ax1 = plt.subplots(figsize=(12, 7))
ax1.set_title('Seasonal Avg Temperature vs Precipitation (mm) Over Years in DuPage County')

# Left Y-axis: Temperature
for season, color, marker in zip(['Spring', 'Summer', 'Fall', 'Winter'], ['green', 'orange', 'brown', 'blue'], ['o', '^', 's', 'd']):
    ax1.plot(merged_prcp_temp['YEAR'], merged_prcp_temp[f'{season}_TEMP'],
             label=f'{season} Temp', color=color, linestyle='-', marker=marker)
ax1.set_ylabel('Temperature (°C)', color='black')
ax1.set_xlabel('Year')
ax1.set_xticks(merged_prcp_temp['YEAR'])
ax1.set_xticklabels(merged_prcp_temp['YEAR'].astype(int), rotation=45)
ax1.tick_params(axis='y', labelcolor='black')

# Right Y-axis: Precipitation
ax2 = ax1.twinx()
for season, color, marker in zip(['Spring', 'Summer', 'Fall', 'Winter'], ['green', 'orange', 'brown', 'blue'], ['x', 'x', 'x', 'x']):
    ax2.plot(merged_prcp_temp['YEAR'], merged_prcp_temp[f'{season}_PRCP'],
             label=f'{season} Precip', color=color, linestyle='--', marker=marker)
ax2.set_ylabel('Precipitation (mm)', color='black')
ax2.tick_params(axis='y', labelcolor='black')

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.grid(True)
plt.tight_layout()
plt.savefig('outputs/dupage_seasonal_temp_vs_precip_trends.png')
plt.close()

# ========== PLOT 3: Seasonal PRCP vs AQI ==========
fig, ax1 = plt.subplots(figsize=(12, 7))
ax1.set_title('Seasonal Avg Precipitation vs AQI in DuPage County')
for season, color in zip(['Spring', 'Summer', 'Fall', 'Winter'], ['green', 'orange', 'brown', 'blue']):
    ax1.plot(merged_prcp_aqi['YEAR'], merged_prcp_aqi[season], label=f'{season} Precip', color=color, marker='s')
ax1.set_ylabel('Precipitation (mm)', color='black')
ax1.set_xlabel('Year')
ax1.set_xticks(merged_prcp_aqi['YEAR'])
ax1.set_xticklabels(merged_prcp_aqi['YEAR'].astype(int), rotation=45)
ax1.tick_params(axis='y', labelcolor='black')

ax2 = ax1.twinx()
for aqi_col, color in zip(['Max AQI', '90th Percentile AQI', 'Median AQI'], ['red', 'purple', 'gray']):
    ax2.plot(merged_prcp_aqi['YEAR'], merged_prcp_aqi[aqi_col], linestyle='--', label=aqi_col, color=color, marker='x')
ax2.set_ylabel('Air Quality Index (AQI)', color='black')
ax2.tick_params(axis='y', labelcolor='black')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.savefig('outputs/dupage_seasonal_precip_vs_aqi_dual_axis.png')
plt.close()

