# AI-Based Crowd Density Estimator for Public Safety

An AI-powered system that detects and counts people in real-time video 
to estimate crowd density and help prevent overcrowding incidents at 
public places like temples, stations, and events.

## Features
- Real-time person detection using YOLOv8
- Live people count with bounding box visualization
- History dashboard with logged crowd data
- Configurable risk thresholds (Low / Medium / High)
- SMS alert support for high-risk situations
- Streamlit web dashboard

## Tech Stack
- Python, OpenCV, YOLOv8 (Ultralytics)
- Streamlit for the web app
- SQLite for history logging

## How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure
- `detector.py` — Person detection & counting logic
- `app.py` — Streamlit web application
- `alerts.py` — Risk threshold and alert logic
- `config.py` — Configurable settings
- `database.py` — History logging
