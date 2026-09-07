# EcoMeter: Urban Carbon Footprint Tracker

EcoMeter is a capstone project developed for the Bangkit Academy program. It aims to help urban residents understand, monitor, and lower their carbon emissions through machine learning-driven vehicle emission calculations and personalized lifestyle recommendations.

---

## Features

- **Vehicle Carbon Calculator**: Estimates trip emissions based on vehicle specifications (engine capacity, cylinder count, fuel type) and travel distance using a trained TensorFlow Lite neural network model.
- **Lifestyle Footprint Audit**: Estimates annual personal carbon footprint across mobility, diet, home energy, and waste production.
- **Vehicle Catalog & Comparison**: Search and compare fuel consumption and carbon ratings across thousands of vehicle models.
- **Global Energy & Climate Insights**: Tracks national energy transition trajectories (renewable share, power generation sources, emissions) from 2000 to 2020.
- **Mobile Companion App**: Android application for logging daily trips, tracking weekly emission budgets, and receiving actionable sustainability tips.

---

## Project Structure

```
Bangkit-Product-Capstone/
├── MD - ecometer/       # Mobile application (Android, Kotlin, TFLite, Retrofit)
├── CC - backend/         # Cloud backend API (Node.js, Hapi.js, Google Cloud Firestore)
├── ML - model/           # Machine learning notebooks and trained TFLite models
├── streamlit_app/        # Interactive web dashboard (Streamlit, LiteRT)
└── Dataset/              # Transportation emissions, individual footprint, and energy datasets
```

---

## Tech Stack

- **Mobile Development (MD)**: Kotlin, Android Jetpack (ViewModel, Navigation Component), TensorFlow Lite Android Support, Retrofit.
- **Cloud Computing (CC)**: Node.js, Hapi.js, Google Cloud Firestore.
- **Machine Learning (ML)**: Python, TensorFlow / Keras, TensorFlow Lite, Pandas, Scikit-learn.
- **Web App**: Streamlit, LiteRT (`ai-edge-litert`), Plotly, Pandas.

---

## Getting Started

### 1. Web Application (Streamlit)

Requires Python 3.10+:

```bash
# Navigate to the project root and activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r streamlit_app/requirements.txt

# Run the app
streamlit run streamlit_app/app.py
```

### 2. Backend API (Node.js)

```bash
cd "CC - backend"
npm install
npm start
```

Runs by default on port `8080`. Requires a configured Google Cloud service account for Firestore access.

### 3. Mobile Application (Android)

1. Open `MD - ecometer` in Android Studio.
2. Ensure Android SDK 34 is installed.
3. Sync Gradle and run on an Android device or emulator (Android 7.0+ / API 24+).

---

## Datasets Used

- **Vehicle Emissions**: Natural Resources Canada vehicle fuel consumption and CO2 emissions ratings.
- **Individual Carbon Footprint**: Survey dataset mapping daily habits (commute, diet, waste) to yearly emissions.
- **Global Sustainable Energy (2000–2020)**: World Bank / UN indicators tracking renewable energy share, clean cooking access, and national emissions.
