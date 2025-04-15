import fastf1
from tqdm import tqdm
from feature_scripts.weather_and_track import get_weather_and_track_data
from feature_scripts.driver_session import get_driver_stats
from feature_scripts.driver_profiles import get_driver_profiles

fastf1.Cache.enable_cache('backend/data/cache')

years = [2022, 2023, 2024]  # Get last 3 years for F1
events = ['R', 'FP1', 'FP2', 'FP3', 'Q']

fastf1.logger.set_log_level('ERROR')

for year in tqdm(years, desc="F1 Season"):
    schedule = fastf1.get_event_schedule(year)
    schedule = schedule[schedule['EventFormat'] == 'conventional']

    race_rounds = schedule['RoundNumber'].tolist()
    race_names = schedule['EventName'].tolist()

    for i, race in enumerate(tqdm(race_rounds, desc=f"{year} Races", leave=False)):
        race_name = race_names[i]

        for event in tqdm(events, desc=f"{year} {race_name} Events", leave=False):
            try:
                weather_and_track_data = get_weather_and_track_data(year, race, event)
                driver_stats = get_driver_stats(year, race, event)
                profiles = get_driver_profiles()
            except Exception as e:
                tqdm.write(f"Error processing {year} Round {race} {event}: {e}")
