import pandas as pd
import requests
import time
from datetime import datetime, timedelta, timezone

# USGS Earthquake API URL
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Get today's and past 10 days' date (timezone-aware)
end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
start_date = (datetime.now(timezone.utc) - timedelta(days=10)).strftime("%Y-%m-%d")

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
    earthquake_list.append([
        props["time"], coords[1], coords[0], props["mag"], props["place"], props["alert"]
    ])

df = pd.DataFrame(earthquake_list, columns=["datetime", "latitude", "longitude", "magnitude", "location", "risk_level"])

# Convert datetime
df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")

# Filter for India-specific locations
INDIA_LAT_RANGE = (6.5, 35.5)
INDIA_LON_RANGE = (68.0, 97.0)
df = df[(df["latitude"].between(*INDIA_LAT_RANGE)) & (df["longitude"].between(*INDIA_LON_RANGE))]

# Function to get the state name from latitude and longitude
def get_state_from_coordinates(lat, lon, max_retries=3):
    """Fetch the state name for given latitude and longitude in English using Nominatim API with retries."""
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers={"User-Agent": "DisasterAlert-Bot"}, timeout=10)
            data = response.json()
            return data.get("address", {}).get("state", "Unknown")
        
        except requests.exceptions.Timeout:
            print(f"Timeout fetching state for ({lat}, {lon}), retrying {attempt + 1}/{max_retries}...")
            time.sleep(2)  # Wait 2 seconds before retrying

        except Exception as e:
            print(f"Error fetching state for ({lat}, {lon}): {e}")
            break  # Stop retrying for other errors

    return "Unknown"

# Add state column
df["state"] = df.apply(lambda row: get_state_from_coordinates(row["latitude"], row["longitude"]), axis=1)

# Save the updated data with state information
df.to_csv(r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\real_time_india_earthquakes_with_states.csv", index=False)
print("Updated earthquake data saved with state information.")

# Load and filter processed earthquake data
processed_file = r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\processed_earthquake_data.csv"
try:
    df_processed = pd.read_csv(processed_file)
    df_processed = df_processed[df_processed["location"].str.contains("India", na=False)]
    df_processed.to_csv(processed_file, index=False)
except FileNotFoundError:
    print(f"Warning: {processed_file} does not exist. Skipping processing step.")

# Prepare data for ML model if processed data exists
try:
    df_ml = df_processed.copy()
    df_ml["magnitude_scaled"] = (df_ml["magnitude"] - df_ml["magnitude"].min()) / (df_ml["magnitude"].max() - df_ml["magnitude"].min())
    df_ml.to_csv(r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\ml_ready_india_earthquakes.csv", index=False)
    print("ML-ready dataset saved.")
except NameError:
    print("Skipping ML dataset creation as processed data is missing.")