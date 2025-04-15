import os
import fastf1
import pandas as pd
from tqdm import tqdm
import sys

from feature_scripts.weather_and_track import get_weather_and_track_data
from feature_scripts.driver_session import get_driver_stats
from feature_scripts.driver_profiles import get_driver_profiles


# ------------------------------ #
#       CONFIGURATION SETUP     #
# ------------------------------ #
DATA_CACHE_PATH = 'backend/data/cache'
RAW_DATA_PATH = 'backend/data/raw_data'
YEARS = [2022, 2023, 2024]
SESSIONS = ['R', 'FP1', 'FP2', 'FP3', 'Q']

# Enable FastF1 cache and logging
fastf1.Cache.enable_cache(DATA_CACHE_PATH)
fastf1.logger.set_log_level('ERROR')


# ------------------------------ #
#           UTILITIES           #
# ------------------------------ #
def sanitize_filename(name: str) -> str:
    """Removes illegal characters from file paths."""
    return name.replace('/', '-').replace('\\', '-').replace(':', '-').replace('?', '').strip()

def save_dataframe(df: pd.DataFrame, filepath: str, label: str):
    """Saves a DataFrame to CSV if it's not empty."""
    if not df.empty:
        df.to_csv(filepath, index=False)
        tqdm.write(f"✅ Saved: {filepath}")
    else:
        tqdm.write(f"⚠️ Empty {label} data: {filepath}")

def create_output_dir(year: int, race_name: str, subfolder: str = '') -> str:
    """Creates and returns the path to the output directory for a specific event and optional subfolder."""
    base_path = os.path.join(RAW_DATA_PATH, str(year), race_name)
    path = os.path.join(base_path, subfolder) if subfolder else base_path
    os.makedirs(path, exist_ok=True)
    return path


# ------------------------------ #
#       MAIN PROCESS LOGIC      #
# ------------------------------ #
def save_driver_profiles():
    """Loads and saves static driver profiles."""
    profiles: pd.DataFrame = get_driver_profiles()
    profiles_file = os.path.join(RAW_DATA_PATH, 'driver_profiles.csv')
    profiles.to_csv(profiles_file, index=False)
    tqdm.write(f"✅ Saved: {profiles_file}")

def process_event_data(year: int, race: int, race_name: str, session: str):
    """Processes and saves data for a single event session."""
    try:
        weather_df = get_weather_and_track_data(year, race, session)
        stats_df = get_driver_stats(year, race, session)

        # Create separate directories for weather and driver stats
        weather_output_dir = create_output_dir(year, race_name, subfolder='weather_data')
        stats_output_dir = create_output_dir(year, race_name, subfolder='driver_stats')

        weather_file = os.path.join(weather_output_dir, f'{session}_weather_and_track.csv')
        stats_file = os.path.join(stats_output_dir, f'{session}_driver_stats.csv')

        save_dataframe(weather_df, weather_file, "weather and track")
        save_dataframe(stats_df, stats_file, "driver stats")

    except Exception as e:
        tqdm.write(f"❌ Error processing {year} Round {race} {session}: {e}")
        exit()


def run_data_collection():
    """Main function to iterate over seasons and collect event data."""
    save_driver_profiles()

    for year in tqdm(YEARS, desc="F1 Season"):
        schedule = fastf1.get_event_schedule(year)
        schedule = schedule[schedule['EventFormat'] == 'conventional']

        for i, row in tqdm(schedule.iterrows(), total=len(schedule), desc=f"{year} Races", leave=False):
            race = row['RoundNumber']
            race_name = sanitize_filename(row['EventName'])

            for session in tqdm(SESSIONS, desc=f"{year} {race_name} Sessions", leave=False):
                process_event_data(year, race, race_name, session)


# ------------------------------ #
#               RUN             #
# ------------------------------ #
if __name__ == "__main__":
    run_data_collection()
