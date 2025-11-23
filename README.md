# 🌫️ ISPA Risk Analysis - ETL Pipeline dengan Metodologi Risk Ratio

> **Case 1 — Kualitas Udara dan Risiko Kesehatan (SDG 3: Good Health and Well-being)**

Project ini merupakan implementasi **ETL (Extract-Transform-Load) Pipeline** untuk analisis risiko ISPA (Infeksi Saluran Pernapasan Akut) di Indonesia menggunakan **metodologi Risk Ratio multiplikatif**. Pipeline mengambil data real-time dari API, menghitung risk ratio berdasarkan penelitian ilmiah, dan menghasilkan visualisasi interaktif.

## 📋 Problem Statement

Kota-kota di Indonesia mengalami variasi polusi udara dan kondisi cuaca yang berdampak pada risiko ISPA. Diperlukan sistem ETL sederhana untuk mengambil data real-time, menganalisis risiko menggunakan metodologi ilmiah, dan menyajikan hasil dalam dashboard interaktif.

## 🎯 Tujuan

Membangun pipeline ETL sederhana untuk analisis risiko ISPA dengan:
- **Extract**: Mengambil data real-time dari API (OpenWeatherMap & WeatherAPI)
- **Transform**: Menghitung Risk Ratio menggunakan metodologi multiplikatif
- **Load**: Menyimpan hasil analisis dalam format CSV dan JSON
- **Visualisasi**: Dashboard interaktif dengan 5 tab analisis komprehensif

## 📊 Data Sources

### Real-time API Data
1. **OpenWeatherMap Air Pollution API**
   - Parameter: PM2.5, PM10, NO2, SO2, O3
   - Update: Real-time
   - Endpoint: Air Pollution API

2. **WeatherAPI**
   - Parameter: Suhu, kelembaban, kecepatan angin
   - Update: Real-time (current weather)
   - Data untuk analisis kondisi cuaca

## 🗺️ Coverage Area

**34 Kota** mewakili **semua provinsi di Indonesia** (1 kota per provinsi):

- **Sumatera** (10): Banda Aceh, Medan, Padang, Pekanbaru, Jambi, Palembang, Bengkulu, Bandar Lampung, Pangkal Pinang, Batam
- **Jawa** (6): Jakarta, Bandung, Semarang, Yogyakarta, Surabaya, Serang
- **Kalimantan** (5): Pontianak, Palangkaraya, Banjarmasin, Balikpapan, Tarakan
- **Sulawesi** (6): Manado, Palu, Makassar, Kendari, Gorontalo, Mamuju
- **Bali & Nusa Tenggara** (3): Denpasar, Mataram, Kupang
- **Maluku & Papua** (4): Ambon, Ternate, Jayapura, Manokwari

## 🔄 Pipeline Architecture (ETL)

```
┌─────────────────────────────────────────────────────┐
│                   EXTRACT                            │
│  • Fetch air pollution data (OpenWeatherMap API)    │
│  • Fetch weather data (WeatherAPI)                  │
│  • 34 kota × 8 parameters = Real-time data          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                  TRANSFORM                           │
│  • Lookup Risk Ratio dari tabel metodologi          │
│  • Hitung RR Total (Model Multiplikatif):           │
│    RR = RR_PM2.5 × RR_PM10 × RR_NO2 × RR_SO2 ×     │
│         RR_O3 × RR_temp × RR_humidity × RR_wind    │
│  • Assign kategori risiko (Rendah-Sangat Tinggi)    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                    LOAD                              │
│  • Save to CSV: output/risk_analysis_*.csv          │
│  • Save to JSON: output/risk_analysis_*.json        │
│  • Summary statistics & console report              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│               VISUALIZATION                          │
│  • Dashboard Streamlit (5 tabs)                     │
│  • Peta geografis, ranking, breakdown, statistik    │
│  • Auto-load data terbaru                           │
└─────────────────────────────────────────────────────┘
```

## 📐 Metodologi Risk Ratio

Pipeline menggunakan **Model Multiplikatif** berdasarkan penelitian ilmiah:

### Formula
```
RR_total = RR_PM2.5 × RR_PM10 × RR_NO2 × RR_SO2 × RR_O3 × 
           RR_suhu × RR_kelembapan × RR_angin
```

### Sumber Penelitian
- **Odo et al. (2022)**: PM2.5 → ISPA (+4.5%)
- **Monoson et al.**: PM10 → ISPA (+2%)
- **Davis et al. (2016)**: Suhu & kelembapan → transmisi virus
- **Lowen et al. (2007)**: Kondisi udara dingin & kering → aerosol stability

Lihat detail lengkap di [`TabelMetodologi.md`](TabelMetodologi.md)

## 🛠️ Tech Stack

- **Python 3.12+**
- **Data Processing**: pandas, numpy
- **APIs**: requests (OpenWeatherMap, WeatherAPI)
- **Visualization**: Streamlit, Plotly
- **No Database Required**: Direct CSV/JSON output
- **No Machine Learning**: Risk Ratio methodology dari penelitian

## 📁 Project Structure (Simplified)

```
PID-Project/
├── config/
│   ├── config.py              # API keys & configuration
│   └── rr_tables.py           # Risk Ratio methodology tables
│
├── src/
│   ├── etl_pipeline.py        # ETL Pipeline (Extract-Transform-Load)
│   └── dashboard_simple.py    # Streamlit Dashboard (5 tabs)
│
├── output/
│   ├── risk_analysis_*.csv    # Hasil analisis (34 kota)
│   └── risk_analysis_*.json   # Format API-ready
│
├── README.md                  # Documentation (this file)
├── README_ETL.md              # ETL Pipeline detailed guide
├── TabelMetodologi.md         # Risk Ratio methodology reference
├── requirements.txt           # Python dependencies
└── .streamlit/
    └── config.toml            # Streamlit configuration
```

**Total**: Hanya **2 file Python utama** - ultra-simple!

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/anmas301/PID-Project.git
cd PID-Project
pip install -r requirements.txt
```

**That's it!** No database, no ML training, no API key setup needed.

## 💻 Usage

### Step 1: Run ETL Pipeline

```bash
python src/etl_pipeline.py
```

**Output:**
- `output/risk_analysis_YYYYMMDD_HHMMSS.csv` - Data 34 kota dengan RR analysis
- `output/risk_analysis_YYYYMMDD_HHMMSS.json` - Format API-ready
- Console report dengan statistik dan ranking

**Execution time:** ~30 detik untuk 34 kota

### Step 2: Launch Dashboard

```bash
streamlit run src/dashboard_simple.py
```

Dashboard tersedia di: **http://localhost:8501**

**Features:**
- 📍 **Tab 1**: Peta geografis Risk Ratio Indonesia
- 📊 **Tab 2**: Ranking dan analisis per kota
- 🔬 **Tab 3**: Breakdown faktor polusi vs cuaca
- 📈 **Tab 4**: Distribusi statistik risiko
- 📋 **Tab 5**: Tabel metodologi lengkap

### View Results

```bash
# Lihat hasil ETL terbaru
ls -lht output/risk_analysis_*.csv | head -1

# Baca dengan pandas
python -c "import pandas as pd; df = pd.read_csv('output/risk_analysis_20251123_080852.csv'); print(df[['city', 'rr_total', 'risk_category']].head(10))"

# Lihat summary JSON
cat output/risk_analysis_*.json | python -m json.tool | head -50
```

**Example Output:**
```
Total Cities Analyzed: 34

Risk Distribution:
  Tinggi        : 22 cities (64.7%)
  Sangat Tinggi : 12 cities (35.3%)

Top 5 Highest Risk:
  1. Denpasar   (Bali)                - RR: 1.3458
  2. Jayapura   (Papua)               - RR: 1.3458
  3. Palembang  (Sumatera Selatan)    - RR: 1.3197
  4. Balikpapan (Kalimantan Timur)    - RR: 1.3197
  5. Jambi      (Jambi)               - RR: 1.3066

Statistics:
  Mean   : 1.2870
  Median : 1.2812
  Min    : 1.2438 (Bandar Lampung)
  Max    : 1.3458 (Denpasar)
```

## 📊 Dashboard Features (5 Tabs)

### Tab 1: 📍 Peta Risk Ratio
- Visualisasi geografis seluruh Indonesia
- Scatter map dengan color coding berdasarkan Risk Ratio
- Hover information: kota, provinsi, RR, kategori risiko
- Identifikasi wilayah berisiko tinggi secara visual

### Tab 2: 📊 Analisis per Kota
- Ranking kota dari RR tertinggi ke terendah
- Bar chart Risk Ratio dengan threshold kategori
- Tabel detail dengan semua parameter (polusi + cuaca)
- Styling berdasarkan kategori risiko

### Tab 3: 🔬 Breakdown Analisis
- Breakdown faktor polusi vs cuaca per kota
- Bar chart contribution analysis
- Identifikasi faktor dominan (polusi atau cuaca)
- Perbandingan antar kota

### Tab 4: 📈 Distribusi Risiko
- Pie chart distribusi kategori risiko
- Histogram distribusi Risk Ratio
- Box plot untuk statistical analysis
- Summary statistics (mean, median, std, min, max)

### Tab 5: 📋 Metodologi
- Tabel Risk Ratio lengkap (polusi & cuaca)
- Formula multiplikatif dengan LaTeX
- Referensi penelitian ilmiah
- Penjelasan kategori risiko



## 🔐 Configuration

API keys sudah dikonfigurasi di `config/config.py` - langsung bisa digunakan!

**No environment variables needed** - semua sudah built-in untuk kemudahan penggunaan.

## 📊 Output Structure

```
output/
├── risk_analysis_20251123_080852.csv    # Latest: 34 kota × 29 kolom
├── risk_analysis_20251123_080852.json   # API-ready format
└── (older runs...)
```

**CSV Columns (29 total)**:
- Identitas: city, province, latitude, longitude
- Polusi: pm2_5, pm10, no2, so2, o3, aqi
- Cuaca: temp_c, humidity, wind_kph
- Risk Ratios: rr_pm2_5, rr_pm10, rr_no2, rr_so2, rr_o3, rr_temp, rr_humidity, rr_wind
- Hasil: rr_total, risk_category
- Metadata: timestamp

**Auto-load**: Dashboard otomatis pilih file terbaru

### Example Results

```bash
# Lihat hasil ETL terbaru
ls -lht output/risk_analysis_*.csv | head -1

# Baca dengan pandas
python -c "import pandas as pd; df = pd.read_csv('output/risk_analysis_20251123_080852.csv'); print(df[['city', 'rr_total', 'risk_category']].head(10))"

# Lihat summary JSON
cat output/risk_analysis_*.json | python -m json.tool | head -50
```

**Example Pipeline Output:**
```
✅ ETL Pipeline Completed Successfully!

Total Cities Analyzed: 34

Risk Distribution:
  Tinggi        : 22 cities (64.7%)
  Sangat Tinggi : 12 cities (35.3%)

Top 5 Highest Risk Cities:
  1. Denpasar   (Bali)                - RR: 1.3458 ⚠️
  2. Jayapura   (Papua)               - RR: 1.3458 ⚠️
  3. Palembang  (Sumatera Selatan)    - RR: 1.3197 ⚠️
  4. Balikpapan (Kalimantan Timur)    - RR: 1.3197 ⚠️
  5. Jambi      (Jambi)               - RR: 1.3066 ⚠️

Statistics:
  Mean   : 1.2870
  Median : 1.2812
  Min    : 1.2438 (Bandar Lampung - Lowest Risk)
  Max    : 1.3458 (Denpasar - Highest Risk)
```

## 🔧 Troubleshooting

### API Timeout
- Check internet connection
- APIs gratis memiliki rate limit
- Tunggu beberapa detik dan coba lagi

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Dashboard Not Loading Data
- Pastikan ETL pipeline sudah dijalankan minimal 1x
- Check folder `output/` memiliki file CSV
- Refresh browser (F5)

## 🎓 Technical Concepts

Project ini mencakup konsep-konsep penting dalam **Data Engineering & Pipeline Development**:

1. **ETL Pipeline**: Extract → Transform → Load architecture
2. **Data Ingestion**: RESTful API consumption (OpenWeatherMap, WeatherAPI)
3. **Data Transformation**: Lookup tables, categorical mapping, risk calculation
4. **Data Loading**: Multiple formats (CSV, JSON)
5. **Visualization**: Interactive dashboard dengan Streamlit & Plotly
6. **Pipeline Automation**: Single-command execution
7. **Error Handling**: Timeout protection, API fallback
8. **Configuration Management**: Centralized config
9. **Documentation**: Comprehensive README & methodology docs
10. **Version Control**: Git workflow dengan meaningful commits

## 📚 References & Documentation

### API Documentation
- [OpenWeatherMap Air Pollution API](https://openweathermap.org/api/air-pollution)
- [WeatherAPI Documentation](https://www.weatherapi.com/docs/)

### Research Papers (Risk Ratio Methodology)
- **Odo et al. (2022)**: PM2.5 impact on respiratory diseases
- **Monoson et al.**: PM10 and air quality health effects
- **Davis et al. (2016)**: Temperature and humidity effects on respiratory transmission
- **Lowen et al. (2007)**: Aerosol stability and environmental factors

### Technical Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/)

### Additional Resources
- [`README_ETL.md`](README_ETL.md) - Detailed ETL pipeline guide
- [`TabelMetodologi.md`](TabelMetodologi.md) - Complete RR methodology

## 🎯 Project Highlights

✅ **Ultra-simple**: 2 main Python files (ETL + Dashboard)  
✅ **No ML complexity**: Evidence-based Risk Ratio methodology  
✅ **No database required**: Direct CSV/JSON output  
✅ **Real-time data**: Live API integration  
✅ **Comprehensive coverage**: All 34 provinces of Indonesia  
✅ **Interactive dashboard**: 5 tabs with rich visualizations  
✅ **Well-documented**: Detailed README, ETL guide, methodology tables  

## 📄 License & Usage

Project ini dibuat untuk keperluan pembelajaran dan portfolio.

**Free to use** untuk tujuan pembelajaran dan non-komersial.

## 👥 Author

**Focus**: Data Engineering & ETL Pipeline Development

**Skills Demonstrated**:
- ✅ ETL Pipeline Design & Implementation
- ✅ RESTful API Integration & Data Ingestion
- ✅ Data Transformation with Evidence-based Methodology
- ✅ Interactive Dashboard Development (Streamlit)
- ✅ Data Visualization (Plotly, Geographic Maps)
- ✅ Clean Code Architecture & Documentation
- ✅ Git Workflow & Version Control

## 🙏 Acknowledgments

- **Data Sources**: OpenWeatherMap, WeatherAPI
- **Research**: Odo et al., Monoson et al., Davis et al., Lowen et al.
- **SDG Framework**: United Nations SDG 3 (Good Health and Well-being)
- **Inspiration**: Open-source data engineering projects

---

**Repository**: [github.com/anmas301/PID-Project](https://github.com/anmas301/PID-Project)
