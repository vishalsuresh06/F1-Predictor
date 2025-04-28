import fastf1
from pathlib import Path
import pandas as pd
from tqdm import tqdm

# Enable FastF1 cache
fastf1.Cache.enable_cache('backend/data/cache')

def get_car_data(START_YEAR, END_YEAR, SESSIONS):
    save_path = Path('backend/data/raw_data/car_data')
    save_path.mkdir(parents=True, exist_ok=True)

    all_metrics = []

    for year in range(START_YEAR, END_YEAR + 1):
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventFormat'] == 'conventional']

        for _, race in tqdm(schedule.iterrows(), total=schedule.shape[0], desc=f'{year} races', leave=False):
            event_name = race['EventName'].replace(" ", "_")
            round_number = race['RoundNumber']

            for session in tqdm(SESSIONS, desc='Sessions', leave=False):
                try:
                    indiv_session = fastf1.get_session(year, round_number, session)
                    indiv_session.load(telemetry=True)

                    max_speeds = []
                    max_accels = []
                    max_decels = []

                    for driver in indiv_session.drivers:
                        try:
                            drv = indiv_session.get_driver(driver)
                            car_data = drv.car_data.add_driver_ahead().dropna().to_pandas()

                            # Calculate acceleration
                            car_data['TimeDiff'] = car_data['Time'].diff().dt.total_seconds()
                            car_data['SpeedDiff'] = car_data['Speed'].diff()
                            car_data['Acceleration'] = car_data['SpeedDiff'] / car_data['TimeDiff']
                            car_data = car_data.dropna()

                            max_speeds.append(car_data['Speed'].max())
                            max_accels.append(car_data['Acceleration'].max())
                            max_decels.append(car_data['Acceleration'].min())
                        except Exception:
                            continue

                    if max_speeds:
                        metrics = {
                            'Year': year,
                            'Event': event_name,
                            'Session': session,
                            'TopSpeed': max(max_speeds),
                            'MaxAcceleration': max(max_accels),
                            'MaxDeceleration': min(max_decels),
                        }
                        all_metrics.append(metrics)

                except Exception as e:
                    print(f"Failed to load {event_name} {session} ({year}): {e}")
                    continue

    df_metrics = pd.DataFrame(all_metrics)
    df_metrics.to_csv(save_path / 'car_data.csv', index=False)

