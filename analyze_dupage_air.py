
import pandas as pd
import glob
import matplotlib.pyplot as plt

# 1. Load all CSVs matching the pattern
files = sorted(glob.glob("data/air_quality/annual_aqi_by_county_*.csv"))

# 2. Extract only rows for Illinois / DuPage
df_list = []
for f in files:
    df = pd.read_csv(f)
    dupage_row = df[(df["State"] == "Illinois") & (df["County"] == "DuPage")]
    df_list.append(dupage_row)

# 3. Combine into one DataFrame
all_years = pd.concat(df_list).sort_values(by="Year")

# 4. Set year as index for plotting
all_years.set_index("Year", inplace=True)

# Optional: Save to CSV
all_years.to_csv("data/air_quality/dupage_aqi_summary.csv", index=True)

# 5. Plotting

## a. AQI Category Days
aqi_columns = ["Good Days", "Moderate Days",
               "Unhealthy for Sensitive Groups Days", "Unhealthy Days",
               "Very Unhealthy Days", "Hazardous Days"]

all_years[aqi_columns].plot(kind="bar", stacked=True, figsize=(14,6))
plt.title("DuPage County AQI Category Days (2005–2024)")
plt.ylabel("Number of Days")
plt.xlabel("Year")
plt.tight_layout()
plt.savefig("outputs/dupage_aqi_categories.png")
#plt.show()

## b. Max, 90th percentile, and Median AQI
all_years[["Max AQI", "90th Percentile AQI", "Median AQI"]].plot(marker='o', figsize=(12,5))
plt.title("DuPage County AQI Statistics Over Time")
plt.ylabel("AQI")
plt.grid(True)

# Force integer year ticks
years = all_years.index.tolist()
plt.xticks(ticks=years, labels=[str(y) for y in years], rotation=45)  # or rotation=0 if preferred

plt.tight_layout()
plt.savefig("outputs/dupage_aqi_stats.png")
#plt.show()

## c. Days by pollutant
pollutants = ["Days CO", "Days NO2", "Days Ozone", "Days PM2.5", "Days PM10"]
all_years[pollutants].plot(kind='bar', stacked=True, figsize=(14,6))
plt.title("Pollutant-Specific AQI Days in DuPage County")
plt.ylabel("Days")
plt.tight_layout()
plt.savefig("outputs/dupage_pollutant_days.png")
#plt.show()

