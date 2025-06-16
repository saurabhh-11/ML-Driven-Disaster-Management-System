import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load training data
X_train = pd.read_csv(r"D:\DisasterAlert\data\X_train.csv")
y_train = pd.read_csv(r"D:\DisasterAlert\data\y_train.csv").values.ravel()

# Train Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save trained model
joblib.dump(model, r"D:\DisasterAlert\models\earthquake_risk_model.pkl")

print(" Model trained and saved!")