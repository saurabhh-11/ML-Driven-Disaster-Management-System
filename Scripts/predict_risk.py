import pandas as pd
import joblib

# Load trained model
model = joblib.load(r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\models\earthquake_risk_model.pkl")

# Load real-time earthquake data
df_real_time = pd.read_csv(r"DisasterAlert (8)/data/real_time_india_earthquakes_with_states.csv")

# Predict risk level
X_new = df_real_time[['latitude', 'longitude', 'magnitude']]
df_real_time['predicted_risk'] = model.predict(X_new)

# Map back to categorical labels
risk_mapping = {0: 'Low', 1: 'Medium', 2: 'High'}
df_real_time['predicted_risk'] = df_real_time['predicted_risk'].map(risk_mapping)

# Save results
df_real_time.to_csv(r"D:\WhatsApp\DisasterAlert (8)\DisasterAlert (8)\data\real_time_india_earthquakes_with_states.csv", index=False)

print(" Risk levels predicted and saved!")