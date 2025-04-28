import pandas as pd
from pathlib import Path

def load_and_combine_data(base_path='backend/data/raw_data'):
    base = Path(base_path)

    # Load weather and results
    weather = pd.read_csv(base / 'weather_and_track_data' / 'weather_and_track_data.csv', index_col=[0, 1, 2, 3])
    results = pd.read_csv(base / 'weather_and_track_data' / 'results.csv', index_col=[0, 1, 2])

    # Load driver profiles
    profiles = pd.read_csv(base / 'driver_profiles' / 'driver_profiles.csv', index_col=0)

    # Load car data
    car = pd.read_csv(base / 'car_data' / 'car_data.csv')

    # Load session data (FP1, FP2, FP3, Quali)
    fp1 = pd.read_csv(base / 'driver_session_data' / 'fp1_data' / 'fp1_data.csv')
    fp2 = pd.read_csv(base / 'driver_session_data' / 'fp2_data' / 'fp2_data.csv')
    fp3 = pd.read_csv(base / 'driver_session_data' / 'fp3_data' / 'fp3_data.csv')
    quali = pd.read_csv(base / 'driver_session_data' / 'q_data' / 'q_data.csv')

    # Merge session data on (year, race_number, driver)
    session_data = fp1.merge(fp2, on=['year', 'race_number', 'driver'], suffixes=('_fp1', '_fp2'))
    session_data = session_data.merge(fp3, on=['year', 'race_number', 'driver'], suffixes=('', '_fp3'))
    session_data = session_data.merge(quali, on=['year', 'race_number', 'driver'], suffixes=('', '_q'))

    # Reset indexes to normal columns for merging
    weather_reset = weather.reset_index()
    results_reset = results.reset_index()

    # Merge session_data + weather + results
    combined = session_data.merge(weather_reset, how='left', on=['year', 'race_number', 'driver'])
    combined = combined.merge(results_reset, how='left', on=['year', 'race_number', 'driver'])

    # Car data: Filter to FP2 session as a standard
    car['Session'] = car['Session'].str.upper()
    car_fp2 = car[car['Session'] == 'FP2']
    combined = combined.merge(car_fp2, how='left', left_on=['year', 'race_number'], right_on=['Year', 'RoundNumber'])

    # Merge driver profiles
    combined = combined.merge(profiles, how='left', left_on='driver', right_index=True)

    # Drop unnecessary columns (duplicate keys)
    combined = combined.drop(columns=['Event', 'Session', 'Year', 'RoundNumber'], errors='ignore')

    return combined

# Usage
if __name__ == "__main__":
    df_final = load_and_combine_data()
    print(df_final.shape)
    print(df_final.head())

    # Optionally save it
    df_final.to_csv('backend/data/cleaned_data/clean_data.csv', index=False)
    print("✅ Combined data saved at 'backend/data/cleaned_data/clean_data.csv'")
