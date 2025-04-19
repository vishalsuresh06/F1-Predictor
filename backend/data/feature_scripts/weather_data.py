import fastf1
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
import time

def get_weather_data(START_YEAR, END_YEAR, SESSIONS):
    fastf1.Cache.enable_cache('backend/data/cache/weather_data_cache')

    weather_cols = [
        'avg_track_temp', 'avg_air_temp', 'avg_humidity',
        'dry_or_wet', 'weather_variability'
    ]
    
    result_cols = [
        'finish_position', 'qualifying_position'
    ]
    df = pd.DataFrame(columns=weather_cols)
    results_df = pd.DataFrame(columns=result_cols)

    for year in tqdm(range(START_YEAR, END_YEAR + 1), desc='Processing years'):
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventFormat'] == 'conventional']
        finish_pos = None
        qual_pos = None

        for race_number, (_, race) in enumerate(tqdm(schedule.iterrows(), total=schedule.shape[0], desc=f'{year} races', leave=False), start=1):
            event_name = race['EventName']
            driver_results = {}

            for session in tqdm(SESSIONS, desc='Sessions', leave=False):
                try:
                    session_obj = fastf1.get_session(year, event_name, session)

                    session_obj.load(weather=True, laps=False, telemetry=False, messages=False)

                    weather_data = session_obj.weather_data
                    if weather_data is None or weather_data.empty:
                        continue

                    avg_track_temp = weather_data['TrackTemp'].mean()
                    avg_air_temp = weather_data['AirTemp'].mean()
                    avg_humidity = weather_data['Humidity'].mean()
                    dry_or_wet = weather_data['Rainfall'].mean()  # 1 is dry, 0 is wet
                    variability = weather_data[['TrackTemp', 'AirTemp', 'Humidity']].std().mean()

                    results = session_obj.results
                    if results is None or results.empty:
                        continue

                    for _, row_data in results.iterrows():
                        driver = row_data['Abbreviation']

                        # Save session results
                        if driver not in driver_results:
                            driver_results[driver] = {'finish_position': 'DNF', 'qualifying_position': 'DNF'}
                        if session == 'R':
                            driver_results[driver]['finish_position'] = row_data['Position']
                        elif session == 'Q':
                            driver_results[driver]['qualifying_position'] = row_data['Position']

                        index = pd.MultiIndex.from_tuples(
                            [(year, race_number, session, driver)],
                            names=['year', 'race_number', 'session', 'driver']
                        )

                        row = pd.DataFrame([[
                            avg_track_temp, avg_air_temp, avg_humidity,
                            dry_or_wet, variability
                        ]], columns=weather_cols, index=index)

                        df = pd.concat([df, row])

                except Exception as e:
                    print(f"Failed to load {event_name} {session} ({year}): {e}")
                    continue

            # After all sessions, save result row for each driver
            for driver, res in driver_results.items():
                driver_index = pd.MultiIndex.from_tuples(
                    [(year, race_number, driver)],
                    names=['year', 'race_number', 'driver']
                )

                row = pd.DataFrame([[
                    res['finish_position'], res['qualifying_position']
                ]], columns=result_cols, index=driver_index)

                results_df = pd.concat([results_df, row])

    df = df.sort_index(level=['year', 'race_number'])
    output_dir = Path('backend/data/raw_data/weather_and_track_data')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_weather_data = output_dir / 'weather_and_track_data.csv'
    output_results = output_dir / 'results.csv'
    df.to_csv(output_weather_data)
    results_df.to_csv(output_results)
