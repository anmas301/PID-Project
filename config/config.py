"""
Configuration file untuk API keys dan database settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# API Configuration
OPENWEATHER_API_KEY = "a2a73644ed35384c9ac73bc606560ed5"
WEATHERAPI_KEY = "e67f32eab28541b892b40743251609"

# Koordinat untuk Jawa Tengah (Semarang sebagai pusat)
JAWA_TENGAH_COORDS = {
    "lat": -7.0051,
    "lon": 110.4381,
    "location": "Semarang"
}

# Additional cities in Jawa Tengah
CITIES = [
    {"name": "Semarang", "lat": -7.0051, "lon": 110.4381},
    {"name": "Solo", "lat": -7.5755, "lon": 110.8243},
    {"name": "Tegal", "lat": -6.8694, "lon": 109.1402},
    {"name": "Pekalongan", "lat": -6.8886, "lon": 109.6753},
    {"name": "Purwokerto", "lat": -7.4246, "lon": 109.2379}
]

# API Endpoints
OPENWEATHER_POLLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
WEATHERAPI_URL = "http://api.weatherapi.com/v1/current.json"

# Database Configuration
DATABASE_CONFIG = {
    "postgresql": {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "pid_project"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres")
    },
    "mongodb": {
        "host": os.getenv("MONGO_HOST", "localhost"),
        "port": int(os.getenv("MONGO_PORT", "27017")),
        "database": os.getenv("MONGO_DB", "pid_project")
    }
}

# Data paths
DATA_PATHS = {
    "raw": BASE_DIR / "data" / "raw",
    "processed": BASE_DIR / "data" / "processed",
    "output": BASE_DIR / "output",
    "models": BASE_DIR / "models"
}

# CSV Dataset files
CSV_FILES = {
    "kualitas_udara": BASE_DIR / "dlh-indeks-kualitas-udara-2018-2022.csv",
    "suhu_kelembaban": BASE_DIR / "Rata-rata Suhu dan Kelembaban Udara Menurut Bulan di Provinsi Jawa Tengah, 2019 - 2021.csv",
    "tekanan_angin": BASE_DIR / "Rata-Rata Tekanan Udara, Kecepatan Angin dan Lama Penyinaran Matahari Menurut Bulan di Provinsi Jawa Tengah, 2019 - 2021.csv",
    "kasus_ispa": BASE_DIR / "tren-kasus-ispa-per-bulan-tahun-2020-2022.csv"
}

# Model Configuration
MODEL_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "cv_folds": 5
}

# Risk thresholds (AQI based)
RISK_THRESHOLDS = {
    "good": (0, 50),
    "moderate": (51, 100),
    "unhealthy_sensitive": (101, 150),
    "unhealthy": (151, 200),
    "very_unhealthy": (201, 300),
    "hazardous": (301, 500)
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}
