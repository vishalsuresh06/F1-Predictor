import os
import pandas as pd
from functools import reduce

# === Paths Setup ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")
SESSION_DATA_DIR = os.path.join(RAW_DATA_DIR, "driver_session_data")
WEATHER_DIR = os.path.join(RAW_DATA_DIR, "weather_and_track_data")

# === Session File Loading ===
session_names = ["fp1", "fp2", "fp3", "q"]
session_dfs = {}

# Load weather and results data
weather_df = pd.read_csv(os.path.join(WEATHER_DIR, "weather_and_track_data.csv"))
results_df = pd.read_csv(os.path.join(WEATHER_DIR, "results.csv"))

# Load and rename session data
for name in session_names:
    path = os.path.join(SESSION_DATA_DIR, f"{name}_data", f"{name}_data.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing session file: {path}")
    
    df = pd.read_csv(path)

    base_cols = df.columns[:3].tolist()
    renamed_cols = [f"{name}_{col}" for col in df.columns[3:]]
    df.columns = base_cols + renamed_cols
    
    session_dfs[name] = df

# Merge all session DataFrames
combined_df = reduce(
    lambda left, right: pd.merge(left, right, on=["year", "race_number", "driver"], how="outer"),
    session_dfs.values()
)

# Merge with weather data (on year and race_number)
combined_df = pd.merge(combined_df, weather_df, on=["year", "race_number", "driver"], how="left")

# Merge with results data (on year, race_number, driver)
combined_df = pd.merge(combined_df, results_df, on=["year", "race_number", "driver"], how="left")

combined_df = combined_df.dropna()
combined_df.drop(combined_df.columns[-3], axis=1, inplace=True)
combined_df.drop(combined_df.columns[-3], axis=1, inplace=True)

# Save to CSV
output_path = os.path.join(BASE_DIR, "combined_sessions_only.csv")
combined_df.to_csv(output_path, index=False)
print(f"✅ Combined session + weather + results dataset saved to: {output_path}")
