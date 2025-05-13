import fastf1
from pathlib import Path
from tqdm import tqdm
import pandas as pd

def get_driver_profiles(START_YEAR, END_YEAR):
    fastf1.Cache.enable_cache('backend/data/cache')
    
    records = []

    for year in tqdm(range(START_YEAR, END_YEAR + 1), desc='Processing years'):
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventFormat'] == 'conventional']

        for race_number, (_, race) in enumerate(tqdm(schedule.iterrows(), total=schedule.shape[0], desc=f'{year} races', leave=False), start=1):
            event_name = race['EventName']
            event_key = event_name.lower().replace(" grand prix", "").replace(" ", "_").replace("-", "_")

            try:
                race_session = fastf1.get_session(year, event_name, 'R')
                race_session.load()

                if race_session.results is None or race_session.results.empty:
                    continue

                for _, row in race_session.results.iterrows():
                    driver = row['Abbreviation']
                    records.append({
                        'year': year,
                        'race_number': race_number,
                        'driver': driver,
                        'event_key': event_key,
                        'participated': 1
                    })

            except Exception as e:
                print(f"Skipping {event_name} {year} due to error: {e}")

    df = pd.DataFrame(records)

    # Get all unique rows
    all_keys = df[['year', 'race_number', 'driver']].drop_duplicates()

    # One-hot encode event participation
    participation_df = pd.get_dummies(df[['year', 'race_number', 'driver', 'event_key']], columns=['event_key'])
    participation_df['value'] = 1

    # Group by and sum to get a wide format
    wide_df = participation_df.pivot_table(
        index=['year', 'race_number', 'driver'],
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Merge with full keys to ensure all driver-race combinations are preserved
    final_df = pd.merge(all_keys, wide_df, on=['year', 'race_number', 'driver'], how='left').fillna(0)

    # Convert any float 1.0 to int 1
    for col in final_df.columns:
        if final_df[col].dtype == float:
            final_df[col] = final_df[col].astype(int)

    # Save
    output_dir = Path('backend/data/raw_data/driver_profiles')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'driver_profiles.csv'
    final_df.to_csv(output_file, index=False)

    print(f"✅ Fixed driver participation matrix saved to {output_file}")
