# analyze_dupage_precip.py

import os
import pandas as pd
import matplotlib.pyplot as plt

# === Configuration ===
data_dir = 'data/temperature'
output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)

# === Load and preprocess data ===
all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
df_list = []

for file in all_files:
    path = os.path.join(data_dir, file)
    df = pd.read_csv(path)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df['PRCP'] = pd.to_numeric(df['PRCP'], errors='coerce')
    df = df[['DATE', 'PRCP']].dropna()
    df['PRCP_MM'] = df['PRCP'] * 25.4  # Convert inches to millimeters
    df_list.append(df)

full_df = pd.concat(df_list).sort_values('DATE').dropna(subset=['DATE', 'PRCP_MM'])

# Remove unrealistic extreme values (> 500 mm/day)
full_df = full_df[full_df['PRCP_MM'] < 500]

# === Add YEAR and MONTH columns ===
full_df['YEAR'] = full_df['DATE'].dt.year
full_df['MONTH'] = full_df['DATE'].dt.month

# === Define seasons and season year ===
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

full_df['SEASON'], full_df['SEASON_YEAR'] = zip(*full_df.apply(get_season_and_season_year, axis=1))

# === Annual statistics ===
annual_stats = full_df.groupby('YEAR').agg(
    DAYS=('DATE', 'count'),
    MEAN_PRCP_MM=('PRCP_MM', 'mean'),
    MAX_PRCP_MM=('PRCP_MM', 'max'),
    MIN_PRCP_MM=('PRCP_MM', 'min'),
    TOTAL_PRCP_MM=('PRCP_MM', 'sum'),
    RAINY_DAYS=('PRCP_MM', lambda x: (x > 0.1).sum())
).reset_index()

# === Seasonal statistics (by season year and season) ===
seasonal_stats = full_df.groupby(['SEASON_YEAR', 'SEASON']).agg(
    TOTAL_PRCP_MM=('PRCP_MM', 'sum'),
    RAINY_DAYS=('PRCP_MM', lambda x: (x > 0.1).sum())
).reset_index()

# Rename SEASON_YEAR for clarity in plots
seasonal_stats.rename(columns={'SEASON_YEAR': 'YEAR'}, inplace=True)

# === Extreme precipitation days (> 50mm) ===
extreme_days = full_df[full_df['PRCP_MM'] > 50].sort_values('PRCP_MM', ascending=False)
extreme_days.to_csv(os.path.join(output_dir, 'dupage_extreme_rain_days.csv'), index=False)

# === Plot helper function for annual plots ===
def plot_annual(df, x, y, title, ylabel, filename):
    plt.figure(figsize=(10, 5))
    plt.plot(df[x], df[y], marker='o')
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(ylabel)
    plt.xticks(df[x], rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()

# === Plot helper function for seasonal plots (multiple lines) ===
def plot_seasonal(df, y_col, title, ylabel, filename):
    plt.figure(figsize=(12, 6))
    seasons = ['Spring', 'Summer', 'Fall', 'Winter']
    for season in seasons:
        df_season = df[df['SEASON'] == season]
        plt.plot(df_season['YEAR'], df_season[y_col], marker='o', label=season)
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel(ylabel)
    plt.xticks(sorted(df['YEAR'].unique()), rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()

# === Generate all plots ===

# 1. Annual average daily precipitation
plot_annual(
    annual_stats, 'YEAR', 'MEAN_PRCP_MM',
    'Annual Average Daily Precipitation (mm)',
    'Average Precipitation (mm)',
    'dupage_annual_avg_precipitation.png'
)

# 2. Annual maximum daily precipitation
plot_annual(
    annual_stats, 'YEAR', 'MAX_PRCP_MM',
    'Annual Maximum Daily Precipitation (mm)',
    'Max Daily Precipitation (mm)',
    'dupage_annual_max_precipitation.png'
)

# 3. Annual number of rainy days
plot_annual(
    annual_stats, 'YEAR', 'RAINY_DAYS',
    'Annual Number of Rainy Days',
    'Rainy Days (>0.1 mm)',
    'dupage_annual_rainy_days.png'
)

# 4. Annual total precipitation
plot_annual(
    annual_stats, 'YEAR', 'TOTAL_PRCP_MM',
    'Annual Total Precipitation (mm)',
    'Total Precipitation (mm)',
    'dupage_annual_total_precipitation.png'
)

# 5. Seasonal total precipitation
plot_seasonal(
    seasonal_stats, 'TOTAL_PRCP_MM',
    'Seasonal Total Precipitation (mm)',
    'Total Precipitation (mm)',
    'dupage_seasonal_total_precipitation.png'
)

# 6. Seasonal number of rainy days
plot_seasonal(
    seasonal_stats, 'RAINY_DAYS',
    'Seasonal Number of Rainy Days',
    'Rainy Days (>0.1 mm)',
    'dupage_seasonal_rainy_days.png'
)
