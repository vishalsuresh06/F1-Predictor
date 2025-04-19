import fastf1
from pathlib import Path
from tqdm import tqdm
import pandas as pd

def get_driver_profiles(START_YEAR, END_YEAR):
    fastf1.Cache.enable_cache('backend/data/cache/driver_profile_cache')
    appearances = {}
    avg_position_data = {}

    for year in tqdm(range(START_YEAR, END_YEAR + 1), desc='Processing years'):
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventFormat'] == 'conventional']

        for _, race in tqdm(schedule.iterrows(), total=schedule.shape[0], desc=f'{year} races', leave=False):
            event_name = race['EventName']
            try:
                race_session = fastf1.get_session(year, event_name, 'R')
                race_session.load(laps=False, telemetry=False, weather=False, messages=False)

                results = race_session.results[['Abbreviation', 'Position']]

                for _, row in results.iterrows():
                    driver = row['Abbreviation']
                    position = row['Position']

                    if driver not in appearances:
                        appearances[driver] = {}
                    if event_name not in appearances[driver]:
                        appearances[driver][event_name] = 1
                    else:
                        appearances[driver][event_name] += 1

                    if year == END_YEAR:
                        if driver not in avg_position_data:
                            avg_position_data[driver] = {'total_pos': 0, 'count': 0}
                        avg_position_data[driver]['total_pos'] += position
                        avg_position_data[driver]['count'] += 1

            except Exception as e:
                print(f"Skipping {event_name} {year} due to error: {e}")

    df = pd.DataFrame.from_dict(appearances, orient='index')
    df.fillna(0, inplace=True)
    df = df.astype(int)

    df['total_appearances'] = df.sum(axis=1)

    df['avg_finish'] = df.index.map(
        lambda driver: round(avg_position_data[driver]['total_pos'] / avg_position_data[driver]['count'], 2)
        if driver in avg_position_data else 20
    )

    cols = ['total_appearances', 'avg_finish'] + [col for col in df.columns if col not in ['total_appearances', 'avg_finish']]
    df = df[cols]
    df = df.sort_values(by='total_appearances', ascending=False)

    output_dir = Path('backend/data/raw_data/driver_profiles')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'driver_profiles.csv'
    df.to_csv(output_file)
