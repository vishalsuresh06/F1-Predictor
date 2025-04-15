import fastf1
import pandas as pd
import time

def safe_load_session(session, retries=3, delay=2):
    """Tries to load the session with retry logic."""
    for attempt in range(1, retries + 1):
        try:
            session.load(weather=True)
            if session.weather_data is not None and not session.weather_data.empty:
                return  # success
            else:
                raise ValueError("Weather data is missing or empty.")
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed to load session: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                raise RuntimeError(f"❌ Failed to load session after {retries} attempts.") from e

def get_weather_and_track_data(year, race, event):
    session = fastf1.get_session(year, race, event)
    safe_load_session(session)
    weather = session.weather_data
    
    featureRow = {
        "track_temp_avg": weather['TrackTemp'].mean(),
        "air_temp_avg": weather['AirTemp'].mean(),
        "humidity_avg": weather['Humidity'].mean(),
        "session_dry_or_wet": weather['Rainfall'].sum() > 0,
        "weather_variability": weather[['AirTemp', 'TrackTemp', 'Humidity']].std()
    }

    return pd.DataFrame([featureRow])