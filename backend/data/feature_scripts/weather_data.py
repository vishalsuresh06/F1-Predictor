import fastf1
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm

def get_weather_data(START_YEAR, END_YEAR, SESSIONS):
    fastf1.Cache.enable_cache('backend/data/cache')

    base_cols = ['year', 'race_number', 'session', 'driver']
    weather_metrics = ['avg_track_temp', 'avg_air_temp', 'avg_humidity', 'dry_or_wet', 'weather_variability']
    weather_cols = base_cols + weather_metrics
    
    result_cols = [
        'year', 'race_number', 'driver',
        'finish_position', 'qualifying_position'
    ]

    weather_rows = []
    results_rows = []

    for year in tqdm(range(START_YEAR, END_YEAR + 1), desc='Processing years'):
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventFormat'] == 'conventional']

        for race_number, (_, race) in enumerate(tqdm(schedule.iterrows(), total=schedule.shape[0], desc=f'{year} races', leave=False), start=1):
            event_name = race['EventName']
            driver_results = {}

            for session in tqdm(SESSIONS, desc='Sessions', leave=False):
                try:
                    session_obj = fastf1.get_session(year, event_name, session)
                    session_obj.load(laps=True, telemetry=True, weather=True)

                    weather_data = session_obj.weather_data
                    if weather_data is None or weather_data.empty:
                        continue

                    avg_track_temp = weather_data['TrackTemp'].mean()
                    avg_air_temp = weather_data['AirTemp'].mean()
                    avg_humidity = weather_data['Humidity'].mean()
                    dry_or_wet = weather_data['Rainfall'].mean()
                    variability = weather_data[['TrackTemp', 'AirTemp', 'Humidity']].std().mean()

                    results = session_obj.results
                    if results is None or results.empty:
                        continue

                    for _, row_data in results.iterrows():
                        driver = row_data['Abbreviation']

                        if driver not in driver_results:
                            driver_results[driver] = {'finish_position': 'DNF', 'qualifying_position': 'DNF'}
                        if session == 'R':
                            driver_results[driver]['finish_position'] = row_data['Position']
                        elif session == 'Q':
                            driver_results[driver]['qualifying_position'] = row_data['Position']

                        # Append one row per (session, driver)
                        weather_rows.append([
                            year, race_number, session, driver,
                            avg_track_temp, avg_air_temp, avg_humidity,
                            dry_or_wet, variability
                        ])

                except Exception as e:
                    print(f"Failed to load {event_name} {session} ({year}): {e}")
                    continue

            # Save results once per race
            for driver, res in driver_results.items():
                results_rows.append([
                    year, race_number, driver,
                    res['finish_position'], res['qualifying_position']
                ])

    # Convert to DataFrames
    df_long = pd.DataFrame(weather_rows, columns=weather_cols)
    results_df = pd.DataFrame(results_rows, columns=result_cols)

    # Pivot weather data: session columns
    df_pivot = df_long.pivot_table(
        index=['year', 'race_number', 'driver'],
        columns='session',
        values=weather_metrics
    )

    # Flatten multi-level column index
    df_pivot.columns = [f"{sess}_{metric}" for metric, sess in df_pivot.columns]
    df_pivot = df_pivot.reset_index()

    # Merge with results
    final_df = pd.merge(df_pivot, results_df, on=['year', 'race_number', 'driver'], how='left')

    # Save to disk
    output_dir = Path('backend/data/raw_data/weather_and_track_data')
    output_dir.mkdir(parents=True, exist_ok=True)

    final_df.to_csv(output_dir / 'weather_and_track_data.csv', index=False)
    results_df.to_csv(output_dir / 'results.csv', index=False)

    print("✅ Pivoted weather and results data saved.")
