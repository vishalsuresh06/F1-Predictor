import fastf1
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def get_driver_stats(year, race, event):
    session = fastf1.get_session(year, race, event)
    session.load(laps=True)
    laps = session.laps
    drivers = session.drivers
    results = session.results if hasattr(session, "results") else None

    driver_stats = []

    for driver in drivers:
        driver_laps = laps.pick_drivers(driver)

        if driver_laps.empty:
            continue
        
        accurate_laps = laps(
                session.laps.pick_drivers(f'{driver}')
                .pick_quicklaps()
                .query("IsAccurate and not Deleted")
            )
        
        # Basic metrics
        avg_lap_time = accurate_laps['LapTime'].mean()
        best_lap_time = accurate_laps['LapTime'].min()
        lap_time_std = accurate_laps['LapTime'].std()
        total_laps = len(accurate_laps)
        delta_to_best = accurate_laps['LapTime'] - best_lap_time

        # Sector times
        s1_avg = accurate_laps['Sector1Time'].mean()
        s2_avg = accurate_laps['Sector2Time'].mean()
        s3_avg = accurate_laps['Sector3Time'].mean()
        s1_min = accurate_laps['Sector1Time'].min()
        s2_min = accurate_laps['Sector2Time'].min()
        s3_min = accurate_laps['Sector3Time'].min()

        # Long runs (stints > 5 laps)
        long_stints = accurate_laps.groupby('Stint').filter(lambda x: len(x) > 5)
        long_run_avg_pace = long_stints['LapTime'].mean() if not long_stints.empty else pd.NaT

        # Long run degradation (linear regression: lap time vs lap number)
        degradation_rate = None
        if not long_stints.empty:
            X = long_stints['LapNumber'].values.reshape(-1, 1)
            y = long_stints['LapTime'].dt.total_seconds().values
            if len(X) > 1:
                model = LinearRegression().fit(X, y)
                degradation_rate = model.coef_[0]  # seconds per lap

        # Qualifying clean laps
        qualifying_clean_laps = driver_laps[~driver_laps['Deleted']] if 'Deleted' in driver_laps else pd.DataFrame()

        # Qualifying position (if results available)
        qualifying_position = None
        if results is not None and 'Abbreviation' in results.columns:
            try:
                qualifying_position = int(results.loc[results['Abbreviation'] == driver]['Position'].values[0])
            except IndexError:
                pass
        
                driver_stats.append({
            "driver": driver,
            "avg_lap_time": avg_lap_time,
            "best_lap_time": best_lap_time,
            "lap_time_std": lap_time_std,
            "total_laps": total_laps,
            "delta_to_session_best": delta_to_best.mean(),
            "sector1_avg": s1_avg,
            "sector2_avg": s2_avg,
            "sector3_avg": s3_avg,
            "sector1_min": s1_min,
            "sector2_min": s2_min,
            "sector3_min": s3_min,
            "long_run_avg_pace": long_run_avg_pace,
            "long_run_degradation_rate": degradation_rate,
            "qualifying_clean_laps": len(qualifying_clean_laps),
            "qualifying_position": qualifying_position
        })

    return pd.DataFrame(driver_stats)

    
            

    