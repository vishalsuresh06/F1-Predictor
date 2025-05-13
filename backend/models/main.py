import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, classification_report, confusion_matrix, accuracy_score
from xgboost import XGBRegressor

# Load dataset
dataset = pd.read_csv('raw_data.csv')

# Drop unused columns
dataset = dataset.drop(columns=['year', 'race_number'])

# Encode driver name
encoder = LabelEncoder()
dataset['driver'] = encoder.fit_transform(dataset['driver'])

# Separate features and target
X = dataset.drop(columns=['finish_position_y'])
y = dataset['finish_position_y']  # Keeping actual position (1 to 20)

# Standardize features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Train/val/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=42)

# Train XGBRegressor
model = XGBRegressor(random_state=42)
model.fit(X_train, y_train)

# Predict on validation set
y_pred = model.predict(X_val)

# Round predictions to nearest integer (position)
y_pred_rounded = np.round(y_pred).astype(int)
y_pred_rounded = np.clip(y_pred_rounded, 1, 20)  # Ensure in range [1, 20]

# Evaluate
# mae = mean_absolute_error(y_val, y_pred_rounded)
# print(f"\nMean Absolute Error (MAE): {mae:.4f}")

acc = accuracy_score(y_val, y_pred_rounded)
print(f"Exact Match Accuracy: {acc:.4f}")

# print("\nClassification Report:\n", classification_report(y_val, y_pred_rounded))
# print("\nConfusion Matrix:\n", confusion_matrix(y_val, y_pred_rounded))
