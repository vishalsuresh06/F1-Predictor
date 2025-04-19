import fastf1

# Load session data
session = fastf1.get_session(2019, 'Japanese Grand Prix', 'FP3')
session.load()

# Print the columns of the weather data
print(session)
