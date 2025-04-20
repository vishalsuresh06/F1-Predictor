import fastf1
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Load session data
session = fastf1.get_session(2024, 5, 'R')
session.load(laps=True)
laps = session.laps.pick_drivers("PER").pick_accurate()
laps = laps.reset_index(drop=True)
laps['LapNumberInStint'] = range(1, len(laps) + 1)
laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()


x = laps['LapNumberInStint'].values.reshape(-1, 1)
y = laps['LapTimeSeconds'].values.reshape(-1, 1)
model = LinearRegression().fit(x, y)
degradation_rate = model.coef_[0][0]

plt.plot(laps['LapNumberInStint'], laps['LapTimeSeconds'], marker='o', label='Lap Times')
plt.plot(laps['LapNumberInStint'], model.predict(x), color='red', label='Trend (Deg Rate)')
plt.xlabel('Lap # in Stint')
plt.ylabel('Lap Time (s)')
plt.title('Tyre Degradation')
plt.legend()
plt.show()

