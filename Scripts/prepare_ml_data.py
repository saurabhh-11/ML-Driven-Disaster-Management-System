import pandas as pd
import requests
from datetime import datetime, timedelta, timezone

# USGS Earthquake API URL
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Get today's and yesterday's date with timezone-aware datetime
end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
start_date = (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d")

# Define API parameters
params = {
    "format": "geojson",
    "starttime": start_date,
    "endtime": end_date,
    "minmagnitude": 2.5,
    "maxlatitude": 35.5,
    "minlatitude": 6.5,
    "maxlongitude": 97.0,
    "minlongitude": 68.0,
    "limit": 1000,
}

# Fetch earthquake data
response = requests.get(USGS_URL, params=params)
data = response.json()

# Process data into DataFrame
features = data.get("features", [])
earthquake_list = []
for feature in features:
    props = feature["properties"]
    coords = feature["geometry"]["coordinates"]
    location = props["place"]
    
    # Ensure the location contains 'India' explicitly
    if "India" in location:
        earthquake_list.append([
            props["time"], coords[1], coords[0], props["mag"], location, props["alert"]
        ])

df = pd.DataFrame(earthquake_list, columns=["datetime", "latitude", "longitude", "magnitude", "location", "predicted risk"])

# Convert datetime
df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")

# Save the filtered data
df.to_csv("data/real_time_india_earthquakes.csv", index=False)

# Load and filter processed earthquake data
df_processed = pd.read_csv("data/processed_earthquake_data.csv")
df_processed = df_processed[df_processed["location"].str.contains("India", na=False)]
df_processed.to_csv("data/processed_earthquake_data.csv", index=False)

# Prepare data for ML model
df_ml = df_processed.copy()

# Feature engineering - Normalizing magnitude
df_ml["magnitude_scaled"] = (df_ml["magnitude"] - df_ml["magnitude"].min()) / (df_ml["magnitude"].max() - df_ml["magnitude"].min())

# Save ML-ready dataset
df_ml.to_csv("data/ml_ready_india_earthquakes.csv", index=False)
