import os
import fastf1
import pandas as pd
from tqdm import tqdm
from feature_scripts.weather_and_track import get_weather_and_track_data
from feature_scripts.driver_session import get_driver_stats
from feature_scripts.driver_profiles import get_driver_profiles

# Enable FastF1 cache
fastf1.Cache.enable_cache('backend/data/cache')
fastf1.logger.set_log_level('ERROR')

# Define years and session types
years = [2022, 2023, 2024]
events = ['R', 'FP1', 'FP2', 'FP3', 'Q']
base_path = 'backend/data/raw_data'  # Output folder for raw data

def sanitize_filename(name):
    """Remove illegal characters from file paths."""
    return name.replace('/', '-').replace('\\', '-').replace(':', '-').replace('?', '').strip()

# Load static driver profile data once
profiles: pd.DataFrame = get_driver_profiles()
# Save driver profiles (once per event)
profiles_file = os.path.join(base_path, 'driver_profiles.csv')
profiles.to_csv(profiles_file, index=False)
tqdm.write(f"✅ Saved: {profiles_file}")

# Loop through years and races
for year in tqdm(years, desc="F1 Season"):
    schedule = fastf1.get_event_schedule(year)
    schedule = schedule[schedule['EventFormat'] == 'conventional']

    race_rounds = schedule['RoundNumber'].tolist()
    race_names = schedule['EventName'].tolist()

    for i, race in enumerate(tqdm(race_rounds, desc=f"{year} Races", leave=False)):
        race_name = sanitize_filename(race_names[i])

        for event in tqdm(events, desc=f"{year} {race_name} Events", leave=False):
            try:
                # Get dataframes
                weather_and_track_data: pd.DataFrame = get_weather_and_track_data(year, race, event)
                driver_stats: pd.DataFrame = get_driver_stats(year, race, event)

                # Create output directory
                output_dir = os.path.join(base_path, str(year), race_name)
                os.makedirs(output_dir, exist_ok=True)

                # Save each dataframe as CSV if available
                if not weather_and_track_data.empty:
                    weather_file = os.path.join(output_dir, f'{event}_weather_and_track.csv')
                    weather_and_track_data.to_csv(weather_file, index=False)
                    tqdm.write(f"✅ Saved: {weather_file}")

                if not driver_stats.empty:
                    stats_file = os.path.join(output_dir, f'{event}_driver_stats.csv')
                    driver_stats.to_csv(stats_file, index=False)
                    tqdm.write(f"✅ Saved: {stats_file}")

            except Exception as e:
                tqdm.write(f"❌ Error processing {year} Round {race} {event}: {e}")
