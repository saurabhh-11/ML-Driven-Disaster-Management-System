import pandas as pd
import os

# Corrected file path
file_path = r"D:\DisasterAlert\data\real_time_india_earthquakes_with_states.csv"

# Check if file exists before reading
if not os.path.exists(file_path):
    print(f" ERROR: File not found: {file_path}")
    print(" Run the preprocessing script first to generate this file.")
    exit()

# Read CSV
df = pd.read_csv(file_path)

# Perform risk assessment (Modify as needed)
df['risk_level'] = df['magnitude'].apply(lambda x: 'High' if x >= 6 else 'Medium' if x >= 4 else 'Low')

# Save updated dataset
df.to_csv(file_path, index=False)
print(f" Risk levels added and saved to: {file_path}")