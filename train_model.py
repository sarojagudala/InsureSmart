import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

print("=" * 60)
print("InsureSmart - Insurance Risk Model Training")
print("=" * 60)

# ---------------------------------------------------
# Load Dataset
# ---------------------------------------------------
try:
    data = pd.read_csv("insurance_dataset.csv")
    print("Dataset Loaded Successfully")
except FileNotFoundError:
    print("ERROR: insurance_dataset.csv not found.")
    exit()

print("\nFirst 5 Records:")
print(data.head())

print("\nDataset Shape:", data.shape)

# ---------------------------------------------------
# Encode Categorical Columns
# ---------------------------------------------------
label_smoker = LabelEncoder()
label_diabetes = LabelEncoder()
label_bp = LabelEncoder()
label_risk = LabelEncoder()

data["Smoker"] = label_smoker.fit_transform(data["Smoker"])
data["Diabetes"] = label_diabetes.fit_transform(data["Diabetes"])
data["HighBP"] = label_bp.fit_transform(data["HighBP"])
data["RiskLevel"] = label_risk.fit_transform(data["RiskLevel"])

# ---------------------------------------------------
# Features & Target
# ---------------------------------------------------
X = data[[
    "Age",
    "Income",
    "BMI",
    "Smoker",
    "Diabetes",
    "HighBP"
]]

y = data["RiskLevel"]

# ---------------------------------------------------
# Train Test Split
# ---------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining Records :", len(X_train))
print("Testing Records  :", len(X_test))

# ---------------------------------------------------
# Train Model
# ---------------------------------------------------
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

print("\nModel Training Completed")

# ---------------------------------------------------
# Prediction
# ---------------------------------------------------
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nAccuracy : {:.2f}%".format(accuracy * 100))

print("\nClassification Report")
print(classification_report(
    y_test,
    predictions,
    target_names=label_risk.classes_
))

# ---------------------------------------------------
# Save Model
# ---------------------------------------------------
with open("insurance_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("\nModel Saved Successfully")
print("Filename : insurance_model.pkl")

# ---------------------------------------------------
# Sample Prediction
# ---------------------------------------------------
sample = pd.DataFrame([{
    "Age": 45,
    "Income": 600000,
    "BMI": 29,
    "Smoker": 1,
    "Diabetes": 0,
    "HighBP": 1
}])

prediction = model.predict(sample)[0]

risk = label_risk.inverse_transform([prediction])[0]

print("\nSample Prediction")
print("-------------------------")
print("Predicted Risk :", risk)

print("\nTraining Finished Successfully")
