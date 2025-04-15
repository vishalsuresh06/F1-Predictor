import fastf1
import pandas as pd

def get_weather_and_track_data(year, race, event):
    session = fastf1.get_session(year, race, event)
    session.load(weather=True)
    weather = session.weather_data
    
    featureRow = {
        "track_temp_avg": weather['TrackTemp'].mean(),
        "air_temp_avg": weather['AirTemp'].mean(),
        "humidity_avg": weather['Humidity'].mean(),
        "session_dry_or_wet": weather['Rainfall'].sum() > 0,
        "weather_variability": weather[['AirTemp', 'TrackTemp', 'Humidity']].std()
    }

    return pd.DataFrame([featureRow])