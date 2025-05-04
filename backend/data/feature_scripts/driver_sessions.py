import fastf1
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.linear_model import LinearRegression



def safe_total_seconds(val):
    try:
        return val.total_seconds()
    except Exception:
        return float(val) if pd.notna(val) else None


def driver_session_data(START_YEAR, END_YEAR, SESSIONS):
    fastf1.Cache.enable_cache('backend/data/cache')

    # Column definitions
    fp_cols = ['year', 'race_number', 'driver', 'avg_lap_time', 'best_lap_time', 'lap_time_std',
               'total_laps', 'delta_to_best', 's1_avg', 's2_avg', 's3_avg',
               's1_fastest', 's2_fastest', 's3_fastest', 'run_avg_pace', 'run_deg_rate']

    quali_cols = ['year', 'race_number', 'driver', 'avg_lap_time', 'best_lap_time', 'lap_time_std',
                  'total_laps', 'delta_to_best', 's1_avg', 's2_avg', 's3_avg',
                  's1_fastest', 's2_fastest', 's3_fastest', 'quali_clean_laps']

    # Lists to accumulate row dicts
    fp1_rows, fp2_rows, fp3_rows, quali_rows = [], [], [], []

    for year in tqdm(range(START_YEAR, END_YEAR + 1), desc='Processing years'):
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        schedule = schedule[schedule['EventFormat'] == 'conventional']

        for race_number, (_, race) in enumerate(tqdm(schedule.iterrows(), total=schedule.shape[0], desc=f'{year} races', leave=False), start=1):
            event_name = race['EventName']

            for session in tqdm(SESSIONS, desc='Sessions', leave=False):
                try:
                    indiv_session = fastf1.get_session(year, event_name, session)
                    indiv_session.load(laps=True)
                    laps = indiv_session.laps.pick_accurate()
                    if laps.empty:
                        continue

                    drivers = indiv_session.results['Abbreviation'].tolist()

                    for driver in drivers:
                        driver_laps = laps.pick_drivers(driver).pick_accurate()
                        deg_laps = driver_laps
                        driver_laps = driver_laps.dropna(subset=['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time'])
                        if driver_laps.empty:
                            continue

                        avg_lap = driver_laps['LapTime'].mean()
                        best_lap = driver_laps['LapTime'].min()
                        lap_std = driver_laps['LapTime'].std() if driver_laps['LapTime'].count() > 1 else 0
                        total_laps = len(driver_laps)

                        delta_to_best = avg_lap - best_lap

                        s1_avg = driver_laps['Sector1Time'].mean()
                        s2_avg = driver_laps['Sector2Time'].mean()
                        s3_avg = driver_laps['Sector3Time'].mean()

                        s1_fastest = driver_laps['Sector1Time'].min()
                        s2_fastest = driver_laps['Sector2Time'].min()
                        s3_fastest = driver_laps['Sector3Time'].min()

                        # Session-specific values
                        run_avg_pace = safe_total_seconds(avg_lap) if session.startswith('FP') else None
                        quali_clean_laps = len(driver_laps)
                        
                        #Calculate the run degredation rate
                        deg_laps = laps = laps.reset_index(drop=True)
                        deg_laps['LapNumberInStint'] = range(1, len(laps) + 1)
                        deg_laps['LapTimeSeconds'] = deg_laps['LapTime'].dt.total_seconds()
                        x = deg_laps['LapNumberInStint'].values.reshape(-1, 1)
                        y = deg_laps['LapTimeSeconds'].values.reshape(-1, 1)
                        model = LinearRegression().fit(x, y)
                        run_deg_rate = model.coef_[0][0]

                        row = {
                            'year': year,
                            'race_number': race_number,
                            'driver': driver,
                            'avg_lap_time': safe_total_seconds(avg_lap),
                            'best_lap_time': safe_total_seconds(best_lap),
                            'lap_time_std': safe_total_seconds(lap_std),
                            'total_laps': total_laps,
                            'delta_to_best': safe_total_seconds(delta_to_best),
                            's1_avg': safe_total_seconds(s1_avg),
                            's2_avg': safe_total_seconds(s2_avg),
                            's3_avg': safe_total_seconds(s3_avg),
                            's1_fastest': safe_total_seconds(s1_fastest),
                            's2_fastest': safe_total_seconds(s2_fastest),
                            's3_fastest': safe_total_seconds(s3_fastest),
                        }

                        if session == 'FP1':
                            row.update({'run_avg_pace': run_avg_pace, 'run_deg_rate': run_deg_rate})
                            fp1_rows.append(row)
                        elif session == 'FP2':
                            row.update({'run_avg_pace': run_avg_pace, 'run_deg_rate': run_deg_rate})
                            fp2_rows.append(row)
                        elif session == 'FP3':
                            row.update({'run_avg_pace': run_avg_pace, 'run_deg_rate': run_deg_rate})
                            fp3_rows.append(row)
                        elif session == 'Q':
                            row.update({'quali_clean_laps': quali_clean_laps})
                            quali_rows.append(row)

                except Exception as e:
                    print(f"Failed to load {event_name} {session} ({year}): {e}")
                    continue

    # Create DataFrames once
    fp1_df = pd.DataFrame(fp1_rows, columns=fp_cols)
    fp2_df = pd.DataFrame(fp2_rows, columns=fp_cols)
    fp3_df = pd.DataFrame(fp3_rows, columns=fp_cols)
    quali_df = pd.DataFrame(quali_rows, columns=quali_cols)

    # Save
    output_dir = Path('backend/data/raw_data/driver_session_data')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_dir.joinpath('fp1_data').mkdir(parents=True, exist_ok=True)
    output_dir.joinpath('fp2_data').mkdir(parents=True, exist_ok=True)
    output_dir.joinpath('fp3_data').mkdir(parents=True, exist_ok=True)
    output_dir.joinpath('q_data').mkdir(parents=True, exist_ok=True)

    fp1_df.to_csv(output_dir / 'fp1_data' / 'fp1_data.csv', index=False)
    fp2_df.to_csv(output_dir / 'fp2_data' / 'fp2_data.csv', index=False)
    fp3_df.to_csv(output_dir / 'fp3_data' / 'fp3_data.csv', index=False)
    quali_df.to_csv(output_dir / 'q_data' / 'q_data.csv', index=False)
