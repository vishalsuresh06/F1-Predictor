import fastf1
import os

import fastf1.logger
from feature_scripts.driver_profile import get_driver_profiles
from feature_scripts.weather_data import get_weather_data
from feature_scripts.driver_sessions import driver_session_data

# Main Function
def main():
    fastf1.logger.set_log_level('ERROR')

    PROFILE_START_YEAR = 2018
    PROFILE_END_YEAR = 2024
    SESSIONS = ['FP1', 'FP2', 'FP3', 'Q', 'R']

    #get_driver_profiles(PROFILE_START_YEAR, PROFILE_END_YEAR)
    #get_weather_data(PROFILE_START_YEAR, PROFILE_END_YEAR, SESSIONS)
    driver_session_data(PROFILE_START_YEAR, PROFILE_END_YEAR, ['FP1', 'FP2', 'FP3', 'Q'])

if __name__ == '__main__':
    main()