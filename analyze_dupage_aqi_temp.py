import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Input data folders
TEMP_DIR = 'data/temperature'
AQI_DIR = 'data/air_quality'

# ========== TEMPERATURE DATA ==========
all_temp_files = [f for f in os.listdir(TEMP_DIR) if f.endswith('.csv')]

weather_dfs = []
for file in all_temp_files:
    df = pd.read_csv(os.path.join(TEMP_DIR, file))
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['TEMP'] = pd.to_numeric(df['TEMP'], errors='coerce')
    weather_dfs.append(df)

weather_data = pd.concat(weather_dfs, ignore_index=True)

# ºF -> ºC
weather_data['TEMP'] = (weather_data['TEMP'] - 32) * 5 / 9
weather_data['YEAR'] = weather_data['DATE'].dt.year
weather_data['MONTH'] = weather_data['DATE'].dt.month

# seasons
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

# winter case
weather_data.loc[(weather_data['MONTH'] == 12), 'YEAR'] += 1

# mean temp by years, seasons
seasonal_temp = weather_data.groupby(['YEAR', 'SEASON'])['TEMP'].mean().reset_index()

# Pivot wider table
seasonal_temp_pivot = seasonal_temp.pivot(index='YEAR', columns='SEASON', values='TEMP').reset_index()

# ========== AQI DATA ==========
all_aqi_files = [f for f in os.listdir(AQI_DIR) if f.endswith('.csv') and f.startswith('annual_aqi_by_county')]

aqi_data_list = []
for file in all_aqi_files:
    year = int(file[-8:-4])  # e.g. annual_aqi_by_county_2005.csv
    df = pd.read_csv(os.path.join(AQI_DIR, file))
    dupage = df[df['County'].str.lower() == 'dupage']
    if not dupage.empty:
        aqi_data = dupage[['Max AQI', '90th Percentile AQI', 'Median AQI']].copy()
        aqi_data['YEAR'] = year
        aqi_data_list.append(aqi_data)

aqi_df = pd.concat(aqi_data_list, ignore_index=True)

# combine data: temp & aqi
merged_df = pd.merge(seasonal_temp_pivot, aqi_df, on='YEAR', how='inner')
merged_df = merged_df.sort_values(by='YEAR')

# ========== PLOT ==========
fig, ax1 = plt.subplots(figsize=(12, 7))

# left y-axis: temp
ax1.plot(merged_df['YEAR'], merged_df['Spring'], label='Spring Temp', color='green', marker='o')
ax1.plot(merged_df['YEAR'], merged_df['Summer'], label='Summer Temp', color='orange', marker='^')
ax1.plot(merged_df['YEAR'], merged_df['Fall'], label='Fall Temp', color='brown', marker='s')
ax1.plot(merged_df['YEAR'], merged_df['Winter'], label='Winter Temp', color='blue', marker='d')
ax1.set_ylabel('Temperature (°C)', color='black')
ax1.set_xlabel('Year')
ax1.set_xticks(merged_df['YEAR'])
ax1.tick_params(axis='y', labelcolor='black')

# left y-axis range
temp_min = merged_df[['Spring', 'Summer', 'Fall', 'Winter']].min().min()
temp_max = merged_df[['Spring', 'Summer', 'Fall', 'Winter']].max().max()
ax1.set_ylim(temp_min - 2, temp_max + 2)

# right y-axis: AQI
ax2 = ax1.twinx()
ax2.plot(merged_df['YEAR'], merged_df['Max AQI'], label='Max AQI', color='red', linestyle='--', marker='x')
ax2.plot(merged_df['YEAR'], merged_df['90th Percentile AQI'], label='90th % AQI', color='purple', linestyle='--', marker='^')
ax2.plot(merged_df['YEAR'], merged_df['Median AQI'], label='Median AQI', color='gray', linestyle='--', marker='s')
ax2.set_ylabel('Air Quality Index (AQI)', color='black')
ax2.tick_params(axis='y', labelcolor='black')

# right y-axis range
aqi_min = merged_df[['Max AQI', '90th Percentile AQI', 'Median AQI']].min().min()
aqi_max = merged_df[['Max AQI', '90th Percentile AQI', 'Median AQI']].max().max()
ax2.set_ylim(aqi_min - 10, aqi_max + 10)

# combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.title('Seasonal Avg Temperature vs AQI in DuPage County (2006–2024)')
plt.grid(True)
plt.tight_layout()
os.makedirs('outputs', exist_ok=True)
plt.savefig('outputs/seasonal_temp_vs_aqi_dual_axis.png')
plt.close()

