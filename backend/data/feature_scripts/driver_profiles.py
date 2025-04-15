import fastf1
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
import re

START_YEAR = 2018
END_YEAR = 2024

def get_driver_experience():
    experience = defaultdict(int)

    for year in tqdm(range(START_YEAR, END_YEAR + 1), desc="Driver Experience - Years"):
        schedule = fastf1.get_event_schedule(year, include_testing=False)

        for _, event in tqdm(schedule.iterrows(), total=len(schedule), desc=f"{year} Races", leave=False):
            try:
                session = fastf1.get_session(year, event['RoundNumber'], 'R')
                session.load(weather=False, messages=False, laps=False, telemetry=False)
                drivers = session.results['Abbreviation']
                for driver in drivers:
                    experience[driver] += 1
            except Exception as e:
                tqdm.write(f"❌ Failed to load {event['EventName']} {year}: {e}")

    return dict(experience)

def get_track_experience():
    track_exp = defaultdict(lambda: defaultdict(int))  # driver -> track -> count

    for year in tqdm(range(START_YEAR, END_YEAR + 1), desc="Track Experience - Years"):
        schedule = fastf1.get_event_schedule(year, include_testing=False)

        for _, event in tqdm(schedule.iterrows(), total=len(schedule), desc=f"{year} Tracks", leave=False):
            try:
                session = fastf1.get_session(year, event['RoundNumber'], 'R')
                session.load(weather=False, messages=False, laps=False, telemetry=False)
                drivers = session.results['Abbreviation']
                track = event['EventName']
                for driver in drivers:
                    track_exp[driver][track] += 1
            except Exception as e:
                tqdm.write(f"❌ Failed to load {event['EventName']} {year}: {e}")

    return track_exp

def get_avg_finish():
    finishes = defaultdict(list)

    schedule = fastf1.get_event_schedule(END_YEAR, include_testing=False)

    for _, event in tqdm(schedule.iterrows(), total=len(schedule), desc=f"{END_YEAR} Avg Finishes"):
        try:
            session = fastf1.get_session(END_YEAR, event['RoundNumber'], 'R')
            session.load(weather=False, messages=False, laps=False, telemetry=False)
            for _, row in session.results.iterrows():
                driver = row['Abbreviation']
                pos = row['Position']
                finishes[driver].append(pos)
        except Exception as e:
            tqdm.write(f"❌ Failed to load {event['EventName']} {END_YEAR}: {e}")

    avg_finish = {driver: sum(pos_list)/len(pos_list) for driver, pos_list in finishes.items()}
    return avg_finish

import re

def clean_column_name(col):
    # Lowercase, remove "Track: ", replace non-alphanumeric with underscore
    col = col.lower()
    col = col.replace("track: ", "track_")
    col = re.sub(r'[^a-z0-9]+', '_', col)
    col = re.sub(r'_+', '_', col).strip('_')  # remove duplicate underscores and trim
    return col

def get_driver_profiles(output_path='driver_profiles.csv'):
    fastf1.Cache.enable_cache('backend/data/cache/driver_cache')
    
    experience = get_driver_experience()
    track_experience = get_track_experience()
    avg_finish = get_avg_finish()

    all_drivers = set(experience.keys()) | set(track_experience.keys()) | set(avg_finish.keys())

    data = []

    for driver in tqdm(all_drivers, desc="Compiling Driver Profiles"):
        row = {
            "driver": driver,
            "total_races": experience.get(driver, 0),
            f"avg_finish_{END_YEAR}": avg_finish.get(driver, None),
        }

        # Flatten track experience into key-value columns
        track_data = track_experience.get(driver, {})
        for track, count in track_data.items():
            key = f"track_{track}"
            row[key] = count

        data.append(row)

    df = pd.DataFrame(data)
    df.fillna(0, inplace=True)
    df.sort_values(by="total_races", ascending=False, inplace=True)

    # Clean all column headers
    df.columns = [clean_column_name(col) for col in df.columns]

    return df
