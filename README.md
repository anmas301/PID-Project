# 🌫️ ISPA Risk Monitoring System - Pipeline Data & Infrastruktur

> **Case 1 — Kualitas Udara dan Risiko Kesehatan (SDG 3: Good Health and Well-being)**

Project ini merupakan implementasi pipeline data untuk monitoring kualitas udara dan prediksi risiko kesehatan ISPA (Infeksi Saluran Pernapasan Akut) di Jawa Tengah. Pipeline ini mengintegrasikan data real-time dari API dengan dataset historis untuk menghasilkan insight dan prediksi risiko kesehatan.

## 📋 Problem Statement

Kota-kota besar di Indonesia mengalami peningkatan polusi udara yang berdampak langsung pada kasus ISPA. Diperlukan pipeline data untuk memantau kualitas udara dan mengidentifikasi area berisiko tinggi.

## 🎯 Tujuan

Mengintegrasikan data dari API real-time dan batch untuk menghasilkan insight risiko kesehatan berdasarkan polusi udara, dengan output berupa:
- Dashboard prediksi risiko ISPA berdasarkan kualitas udara
- Model machine learning untuk prediksi risiko
- Visualisasi data kualitas udara dan cuaca
- Sistem monitoring real-time

## 📊 Dataset & Data Sources

### Real-time API Data
1. **OpenWeatherMap Air Pollution API**
   - Parameter: AQI, PM2.5, PM10, CO, NO2, O3, SO2
   - Update: Real-time (hourly)
   - API Key: `a2a73644ed35384c9ac73bc606560ed5`

2. **WeatherAPI**
   - Parameter: Suhu, kelembaban, angin, tekanan udara
   - Update: Real-time (current)
   - API Key: `e67f32eab28541b892b40743251609`

### Historical CSV Datasets
1. `dlh-indeks-kualitas-udara-2018-2022.csv` - Data kualitas udara historis
2. `Rata-rata Suhu dan Kelembaban Udara Menurut Bulan di Provinsi Jawa Tengah, 2019 - 2021.csv`
3. `Rata-Rata Tekanan Udara, Kecepatan Angin dan Lama Penyinaran Matahari Menurut Bulan di Provinsi Jawa Tengah, 2019 - 2021.csv`
4. `tren-kasus-ispa-per-bulan-tahun-2020-2022.csv` - Data kasus ISPA

### Lokasi Monitoring
- Semarang (pusat)
- Solo
- Tegal
- Pekalongan
- Purwokerto

## 🔄 Pipeline Architecture

```
┌─────────────────┐
│   INGESTION     │ ← Fetch dari API + Load CSV
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TRANSFORMATION  │ ← Cleaning, Join, Feature Engineering
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    STORAGE      │ ← PostgreSQL / MongoDB (optional)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BATCH PROCESS   │ ← Agregasi harian/weekly/monthly
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ML MODELING    │ ← Train & Predict risiko ISPA
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  VISUALIZATION  │ ← Dashboard Streamlit
└─────────────────┘
```

## 🛠️ Tech Stack

- **Python 3.8+**
- **Data Processing**: pandas, numpy
- **APIs**: requests
- **Database**: PostgreSQL, MongoDB (optional)
- **ML**: scikit-learn, xgboost
- **Visualization**: Streamlit, Plotly, Matplotlib, Seaborn
- **Utilities**: python-dotenv, schedule, loguru

## 📁 Project Structure

```
PID-Project/
├── config/
│   └── config.py              # Configuration & API keys
├── src/
│   ├── ingestion.py           # Data ingestion dari API & CSV
│   ├── transformation.py      # Data cleaning & transformation
│   ├── storage.py             # Database operations
│   ├── batch_processing.py    # Batch processing & agregasi
│   ├── model.py               # ML model training & prediction
│   ├── dashboard.py           # Streamlit dashboard
│   └── main.py                # Main pipeline orchestration
├── data/
│   ├── raw/                   # Raw data dari API
│   └── processed/             # Processed data
├── models/                    # Trained ML models
├── output/                    # Output reports & visualizations
├── notebooks/                 # Jupyter notebooks untuk EDA
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

## 🚀 Installation & Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd PID-Project
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Setup (Optional)

Jika ingin menggunakan database:

```bash
cp .env.example .env
# Edit .env dengan credentials database Anda
```

### 5. Database Setup (Optional)

**PostgreSQL:**
```bash
# Install PostgreSQL
# Create database
createdb pid_project

# Or using psql
psql -U postgres
CREATE DATABASE pid_project;
```

**MongoDB:**
```bash
# Install MongoDB
# Start MongoDB service
mongod
```

## 💻 Usage

### Run Complete Pipeline

```bash
# Run full pipeline (tanpa database)
python src/main.py

# Run full pipeline dengan database storage
python src/main.py --use-database

# Run tanpa model training
python src/main.py --skip-model

# Run dengan regression model
python src/main.py --model-type regression
```

### Run Specific Steps

```bash
# Hanya ingestion
python src/main.py --step ingestion

# Hingga transformation
python src/main.py --step transformation

# Hingga batch processing
python src/main.py --step batch

# Hanya model training
python src/main.py --step model
```

### Launch Dashboard

```bash
streamlit run src/dashboard.py
```

Dashboard akan tersedia di `http://localhost:8501` atau `http://localhost:8502`

### View Predictions & Analysis

```bash
# Lihat prediksi ISPA 7 hari
cat output/future_ispa_predictions.csv

# Lihat alert risiko tinggi (jika ada)
cat output/risk_alerts.json 2>/dev/null || echo "No high-risk predictions"

# Lihat laporan lengkap dengan ISPA analysis
cat output/pipeline_report_*.json | python3 -m json.tool
```

## 📊 Dashboard Features

1. **Real-time Monitoring**
   - Current AQI dan pollutant levels
   - Risk category status
   - Weather conditions

2. **Time Series Analysis**
   - AQI trends over time
   - Historical data visualization
   - Risk category distribution

3. **Location Comparison**
   - Compare AQI across cities
   - Interactive maps
   - Location-specific insights

4. **Weather Correlation**
   - Correlation analysis between weather and AQI
   - Impact of temperature, humidity, wind

5. **Pollutant Breakdown**
   - Detailed pollutant levels (PM2.5, PM10, CO, NO2, O3, SO2)
   - Bar charts dan comparisons

6. **🆕 Kota dengan Polusi Tertinggi**
   - Ranking kota berdasarkan AQI tertinggi
   - Visualisasi perbandingan PM2.5 dan PM10
   - Korelasi polutan dengan risiko ISPA
   - Identifikasi daerah berisiko tinggi
   - Rekomendasi kesehatan otomatis

7. **🆕 Prediksi ISPA 7 Hari Ke Depan**
   - Prediksi risiko ISPA untuk setiap kota
   - Time series visualization dengan threshold
   - Detail prediksi harian per lokasi
   - Alert untuk prediksi risiko tinggi
   - Risk score dan kategori (Low/Moderate/High/Very High)

## 🤖 Machine Learning Models

### Classification Model
- **Task**: Predict risk category (good, moderate, unhealthy, etc.)
- **Algorithm**: Random Forest Classifier
- **Features**: AQI, pollutants, weather data, temporal features
- **Output**: Risk category + probability

### Regression Model
- **Task**: Predict ISPA risk score (0-100)
- **Algorithm**: Gradient Boosting Regressor
- **Features**: Same as classification
- **Output**: Continuous risk score

### Model Training

```python
from src.model import ISPARiskPredictor
import pandas as pd

# Initialize predictor
predictor = ISPARiskPredictor()

# Load data
df = pd.read_csv('data/processed/real_time_merged.csv')

# Train model
metrics = predictor.train_pipeline(df, target_type='classification')

# Make predictions
predictions = predictor.predict(df)
```

## 📈 Batch Processing

Batch processing melakukan:
- **Daily aggregation**: Average, max, min per hari
- **Weekly aggregation**: Trends per minggu
- **Monthly aggregation**: Patterns per bulan
- **Anomaly detection**: Deteksi nilai abnormal menggunakan z-score
- **Trend analysis**: Linear regression untuk trend identification
- **Statistical summary**: Comprehensive statistics per location

## 🔐 API Keys Configuration

API keys sudah tersimpan di `config/config.py`:

```python
OPENWEATHER_API_KEY = "a2a73644ed35384c9ac73bc606560ed5"
WEATHERAPI_KEY = "e67f32eab28541b892b40743251609"
```

Untuk production, disarankan menggunakan environment variables:

```bash
# .env file
OPENWEATHER_API_KEY=your_key_here
WEATHERAPI_KEY=your_key_here
```

## 📝 Logging

Pipeline menggunakan logging comprehensif:
- **INFO**: Progress updates
- **WARNING**: Non-critical issues
- **ERROR**: Errors dengan stacktrace

Logs ditampilkan di console dan bisa disimpan ke file.

## 🧪 Testing

Test individual modules:

```bash
# Test ingestion
python src/ingestion.py

# Test transformation
python src/transformation.py

# Test storage (requires database)
python src/storage.py

# Test batch processing
python src/batch_processing.py

# Test model
python src/model.py
```

## 📊 Expected Outputs

1. **Processed Data** (`data/processed/`)
   - `real_time_merged.csv`: Merged API data
   - `*_clean.csv`: Cleaned CSV datasets
   - `batch_*.csv`: Aggregated batch results

2. **Models** (`models/`)
   - `ispa_risk_model.joblib`: Trained ML model

3. **Reports & Predictions** (`output/`)
   - `pipeline_report_*.json`: Execution reports with ISPA analysis
   - `feature_importance.csv`: Feature importance scores
   - **🆕 `future_ispa_predictions.csv`**: Prediksi ISPA 7 hari ke depan
   - **🆕 `risk_alerts.json`**: Alert untuk prediksi risiko tinggi (jika ada)

4. **Dashboard**: Interactive web interface dengan 7 tabs (termasuk prediksi & korelasi)

## 🔧 Troubleshooting

### API Connection Issues
```bash
# Test API connectivity
curl "http://api.openweathermap.org/data/2.5/air_pollution?lat=-7.0051&lon=110.4381&appid=a2a73644ed35384c9ac73bc606560ed5"
```

### Database Connection Issues
- Pastikan PostgreSQL/MongoDB running
- Check credentials di `.env`
- Verify firewall settings

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Memory Issues
- Reduce data size dengan filtering
- Use `--skip-model` untuk skip ML training
- Increase system memory

## 🎓 Konsep Pembelajaran

Project ini mencakup konsep-konsep penting dalam **Pemrosesan Data & Infrastruktur Data**:

1. **Data Ingestion**: Fetching dari multiple sources (API + CSV)
2. **Data Transformation**: ETL pipeline, cleaning, joining
3. **Data Storage**: Relational (PostgreSQL) & NoSQL (MongoDB)
4. **Batch Processing**: Agregasi dan analisis temporal
5. **Machine Learning**: Classification & regression models
6. **Visualization**: Interactive dashboards
7. **Pipeline Orchestration**: End-to-end automation
8. **Error Handling**: Robust exception handling
9. **Logging**: Comprehensive activity tracking
10. **Configuration Management**: Centralized config

## 📚 References & Documentation

- [OpenWeatherMap API Docs](https://openweathermap.org/api/air-pollution)
- [WeatherAPI Docs](https://www.weatherapi.com/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Pandas Documentation](https://pandas.pydata.org/)

## 🤝 Contributing

Untuk kontribusi atau improvement:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

Project ini dibuat untuk keperluan pembelajaran mata kuliah **Pemrosesan Data dan Infrastruktur Data**.

## 👥 Authors

- **Your Name** - Project Developer
- **Mata Kuliah**: Pemrosesan Data dan Infrastruktur Data

## 🙏 Acknowledgments

- Data sources: OpenWeatherMap, WeatherAPI, BMKG, Kemenkes
- Inspiration: [ProjekPID by shandy225-beep](https://github.com/shandy225-beep/ProjekPID)
- SDG 3: Good Health and Well-being

---

**Note**: Pastikan untuk mereview dan customize configuration sesuai kebutuhan spesifik Anda, terutama API keys dan database credentials.

**Happy Coding! 🚀**