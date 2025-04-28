import fastf1
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Load session data
session = fastf1.get_session(2024, 5, 'R')
session.load(laps=True, telemetry=True)

car_data = session.car_data
print(car_data['22'].to_csv('test.csv'))

