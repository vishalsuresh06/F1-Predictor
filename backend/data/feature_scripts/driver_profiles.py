import fastf1
from collections import defaultdict

START_YEAR = 2015
END_YEAR = 2024

def get_driver_experience():
    experience = defaultdict(int)

    for year in range(START_YEAR, END_YEAR + 1):
        schedule = fastf1.get_event_schedule(year, include_testing=False)

        for _, event in schedule.iterrows():
            try:
                session = fastf1.get_session(year, event['RoundNumber'], 'R')
                session.load()
                drivers = session.results['Abbreviation']
                for driver in drivers:
                    experience[driver] += 1
            except Exception as e:
                print(f"Failed to load {event['EventName']} {year}: {e}")

    return dict(experience)

def get_track_experience():
    track_exp = defaultdict(lambda: defaultdict(int))  # driver -> track -> count

    for year in range(START_YEAR, END_YEAR + 1):
        schedule = fastf1.get_event_schedule(year, include_testing=False)

        for _, event in schedule.iterrows():
            try:
                session = fastf1.get_session(year, event['RoundNumber'], 'R')
                session.load()
                drivers = session.results['Abbreviation']
                track = event['EventName']
                for driver in drivers:
                    track_exp[driver][track] += 1
            except Exception as e:
                print(f"Failed to load {event['EventName']} {year}: {e}")

    return track_exp

def get_avg_finish():
    finishes = defaultdict(list)

    schedule = fastf1.get_event_schedule(END_YEAR, include_testing=False)

    for _, event in schedule.iterrows():
        try:
            session = fastf1.get_session(END_YEAR, event['RoundNumber'], 'R')
            session.load()
            for _, row in session.results.iterrows():
                driver = row['Abbreviation']
                pos = row['Position']
                finishes[driver].append(pos)
        except Exception as e:
            print(f"Failed to load {event['EventName']} {END_YEAR}: {e}")

    avg_finish = {driver: sum(pos_list)/len(pos_list) for driver, pos_list in finishes.items()}
    return avg_finish

    

def get_driver_profiles(races):
    experience = get_driver_experience()
    track_experience = get_track_experience()
    avg_finish = get_avg_finish()

    all_drivers = set(experience.keys()) | set(track_experience.keys()) | set(avg_finish.keys())

    profiles = {}

    for driver in all_drivers:
        profiles[driver] = {
            "total_races": experience.get(driver, 0),
            "track_experience": track_experience.get(driver, {}),
            "avg_finish_in_" + str(END_YEAR): avg_finish.get(driver, None)
        }

    return profiles
