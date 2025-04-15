# 🏎️ F1 Race Predictor

A machine learning-based web application that predicts Formula 1 race results using free practice session data (FP1, FP2, FP3) powered by FastF1 and visualized through a sleek Next.js dashboard.

---

## 🚀 Project Overview

This project collects and analyzes data from the past five F1 seasons using the FastF1 API. By engineering performance features from free practice sessions, it trains a machine learning model to predict the likely outcomes of upcoming races. The predictions are served via a Python backend API and visualized on a frontend built with Next.js.

---

## 🧱 Architecture

```bash
f1-race-predictor/
├── backend/
│   ├── data/         # Data collection, caching, and preprocessing
│   ├── models/       # Model training and prediction logic
│   ├── scripts/      # Notebooks and scripts for building the dataset
│   ├── api/          # FastAPI or Flask backend serving predictions
│   └── utils/        # Configs, helpers, logging
│
├── frontend/         # Next.js frontend app
│   ├── pages/
│   ├── components/
│   ├── styles/
│   └── utils/
│
├── notebooks/        # Exploratory data analysis and prototyping
├── requirements.txt  # Python dependencies
├── package.json      # Frontend dependencies
├── .env              # Environment variables
└── README.md
```

## 📊 Features Used for Prediction

### **Driver Performance**
- Average and best lap times (FP1/2/3)
- Lap time consistency (std deviation)
- Long run performance & degradation

### **Car & Tyre**
- Compound usage stats
- Average stint pace by compound
- Top speed & braking data (if available)

### **Weather & Track**
- Track temperature, air temperature, humidity
- Wet vs dry session classification

### **Driver & Team Stats**
- Driver experience, past track performance
- Team season stats, average qualifying and race pace

### **Session Summary Features**
- Session rank, lap improvement rate, pace trends

# 🧠 Feature Suggestions for F1 Race Prediction

---

## 🔁 Driver Performance Features

| Feature                          | Description                                      |
|----------------------------------|--------------------------------------------------|
| `avg_lap_time_fp1/2/3/q`         | Average lap time in each session                |
| `best_lap_time_fp1/2/3/q`        | Fastest lap per session                         |
| `lap_time_std_fp1/2/3/q`         | Consistency indicator                           |
| `total_laps_fp1/2/3/q`           | Amount of running done                          |
| `delta_to_session_best_fp1/2/3/q`| Time behind fastest driver in session           |
| `sector_times_avg/fastest_fp1/2/3/q` | Per sector analysis (S1, S2, S3)          |
| `long_run_avg_pace`             | Avg lap time over stints > 5 laps (FP only)     |
| `long_run_degradation_rate`     | Pace drop-off in longer stints (FP only)        |
| `qualifying_clean_laps`         | Number of valid (non-deleted) laps in Quali     |
| `qualifying_position`         | Qualifying position                                |


---

## 🌦️ Weather & Track Features

| Feature               | Description                                  |
|-----------------------|----------------------------------------------|
| `track_temp_avg`      | Average temperature per session              |
| `air_temp_avg`        | Same as above                                |
| `humidity_avg`        | Could influence performance                  |
| `session_dry_or_wet`  | Binary indicator                             |
| `weather_variability` | Standard deviation of weather during FP/Q    |

---

## 👤 Driver Profile Features

| Feature                        | Description                                  |
|--------------------------------|----------------------------------------------|
| `driver_experience`           | Races or seasons completed                   |
| `track_experience`            | Previous appearances at this GP              |
| `driver_avg_finish_2024`      | Finishing position this season               |

---

## 🛠️ Team / Constructor Features

| Feature                      | Description                                  |
|------------------------------|----------------------------------------------|
| `team_avg_qualifying_pos`    | Team’s qualifying performance                |
| `team_avg_race_pos`          | Race pace benchmark                          |
| `constructor_points_season` | Championship standing snapshot               |

---

## 🧮 Session Summary / Derived Features

| Feature                          | Description                                         |
|----------------------------------|-----------------------------------------------------|
| `lap_time_improvement_rate`      | Did the driver improve across sessions?            |
| `pace_rank_fp1/2/3/q`            | Rank in each session by lap time                   |
| `fp_consistency_score`           | Composite of avg lap std dev across FP sessions    |
| `qualifying_consistency_score`   | Variability across qualifying segments (Q1-Q3)     |

---

## 🏁 Target Variable Examples

| Target Variable                    | Description                                   |
|-----------------------------------|-----------------------------------------------|
| `finishing_position`              | Final race position (regression or class)     |

---

## 🔁 Model Training Strategy

1. **Historical Data Collection**
   - Loop through 2019–2024 seasons
   - Download FP1–FP3 + race session data

2. **Feature Engineering**
   - Build one row per driver per race using session data

3. **Model Training**
   - Use models like Random Forest, XGBoost, or LightGBM
   - Evaluate with cross-validation

4. **Prediction**
   - Apply trained weights to live FP data of current races

---

## 🧠 Tech Stack

**Backend**
- Python, FastF1
- Pandas, scikit-learn, XGBoost
- FastAPI or Flask (for the API)

**Frontend**
- Next.js, React
- Chart.js or Recharts for visualizations
- SWR or Axios for API calls

---

## 🖥️ Frontend Features

- Select race and session
- View predicted results per driver
- View confidence or delta-to-leader
- Graphs: lap times, performance trends, feature impact

---

## ✅ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourname/f1-race-predictor.git
cd f1-race-predictor
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Enable FastF1 cache:

```bash
import fastf1
fastf1.Cache.enable_cache('path_to_cache_dir')
```

#### Run the API server:

```bash
uvicorn api.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 📂 Example Usage
1. Run the script to fetch past race data (scripts/generate_dataset.py)
2. Train the model using models/train_model.py
3. Use /predict endpoint to get predictions for a new race
4. Open the frontend to view predictions in real-time

## 🔮 Future Improvements
- Add qualifying session features
- Live telemetry-based updates
- Simulate race with strategy variations
- Include mechanical DNF prediction

