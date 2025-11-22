# 🔮 Fitur Prediksi ISPA & Analisis Korelasi

## 📊 Fitur Baru yang Ditambahkan

### 1. **Prediksi Risiko ISPA 7 Hari Ke Depan**

Pipeline sekarang dapat memprediksi risiko ISPA untuk 7 hari ke depan berdasarkan kondisi kualitas udara saat ini.

#### Cara Kerja:
- Menggunakan data AQI, PM2.5, PM10, dan kondisi cuaca terkini
- Menghitung ISPA Risk Score (0-100) untuk setiap lokasi
- Mengkategorikan risiko: Low, Moderate, High, Very High
- Generate prediksi untuk 5 kota di Jawa Tengah

#### Output:
```
📁 output/future_ispa_predictions.csv
```

**Kolom:**
- `location`: Nama kota
- `date`: Tanggal prediksi
- `predicted_ispa_risk`: Skor risiko ISPA (0-100)
- `risk_category`: Kategori risiko
- `predicted_aqi`: Prediksi AQI
- `predicted_pm2_5`: Prediksi PM2.5

#### Contoh Data:
```csv
location,date,predicted_ispa_risk,risk_category,predicted_aqi
Semarang,2025-11-23,4.02,Low Risk,1
Solo,2025-11-23,5.42,Low Risk,1
Tegal,2025-11-23,3.46,Low Risk,1
```

### 2. **Analisis Korelasi Polusi dengan ISPA**

Menganalisis hubungan antara polutan udara dan risiko kesehatan ISPA.

#### Fitur:
- **Identifikasi Kota Terpolusi**: Ranking kota berdasarkan AQI
- **Korelasi Polutan**: Analisis korelasi 7 polutan dengan risiko ISPA
  - AQI
  - PM2.5
  - PM10
  - CO
  - NO2
  - O3
  - SO2
- **Rekomendasi Kesehatan**: Alert otomatis untuk area berisiko tinggi

#### Output dalam Dashboard:
- 📊 Bar chart kota dengan polusi tertinggi
- 📈 Correlation coefficient untuk setiap polutan
- ⚠️ Tabel daerah berisiko tinggi
- 💡 Rekomendasi tindakan kesehatan

### 3. **Dashboard Interaktif Baru**

#### Tab Baru:

**🏭 Kota Terpolusi:**
- Ranking kota berdasarkan rata-rata AQI
- Tabel perbandingan PM2.5 dan PM10
- Visualisasi korelasi dengan gradient color
- High-risk locations dengan risk level

**🔮 Prediksi ISPA:**
- Time series prediksi 7 hari ke depan
- Line chart per lokasi dengan markers
- Threshold lines (Low/Moderate/High Risk)
- Detail per lokasi:
  - Rata-rata risiko
  - Risiko tertinggi & tanggalnya
  - Jumlah hari berisiko tinggi
  - Tabel prediksi harian

## 🚀 Cara Menggunakan

### 1. Jalankan Pipeline dengan Prediksi

```bash
cd /workspaces/PID-Project
python src/main.py --skip-model
```

**Output:**
```
✓ ISPA_ANALYSIS:
  - high_risk_locations: 5
  - correlations_calculated: 7
  - recommendations: 0

✓ PREDICTIONS:
  - total_predictions: 35
  - locations: 5
  - days_ahead: 7
  - high_risk_predictions: 0
  - moderate_risk_predictions: 0
```

### 2. Lihat Hasil Prediksi

```bash
# Prediksi 7 hari
cat output/future_ispa_predictions.csv

# Alert risiko tinggi (jika ada)
cat output/risk_alerts.json
```

### 3. Akses Dashboard

Dashboard sekarang berjalan di: **http://localhost:8502**

Navigasi ke tab:
- **🏭 Kota Terpolusi** - Lihat ranking polusi & korelasi
- **🔮 Prediksi ISPA** - Lihat prediksi 7 hari ke depan

## 📈 Interpretasi Hasil

### ISPA Risk Score
- **0-20**: Low Risk (Aman)
- **20-40**: Moderate Risk (Kelompok sensitif berhati-hati)
- **40-60**: High Risk (Kurangi aktivitas outdoor)
- **60-100**: Very High Risk (Gunakan masker, hindari outdoor)

### Correlation Coefficient
- **+1.0**: Korelasi positif sempurna (polutan ↑ → ISPA ↑)
- **+0.7 to +1.0**: Korelasi kuat
- **+0.3 to +0.7**: Korelasi moderat
- **0 to +0.3**: Korelasi lemah
- **Negatif**: Korelasi terbalik (jarang)

## 🎯 Contoh Analisis

### Hasil Saat Ini (22 Nov 2025):

**Kota Terpolusi:**
| Kota | Avg AQI | PM2.5 | Risk Level |
|------|---------|-------|------------|
| Pekalongan | 1.0 | 1.75 | Low |
| Semarang | 1.0 | 5.57 | Low |
| Solo | 1.0 | 1.16 | Low |

**Prediksi 7 Hari:**
- Semua kota: **Low Risk** (skor < 6)
- Tidak ada alert risiko tinggi
- Kondisi udara diprediksi stabil

**Korelasi Polutan:**
- PM2.5 dengan ISPA: **Correlation terkuat**
- AQI dengan ISPA: **Korelasi moderat**
- Humidity dengan ISPA: **Korelasi positif**

## 🔧 Kustomisasi

### Ubah Jumlah Hari Prediksi

Edit `src/main.py`:
```python
future_predictions = self.model.predict_future_risk(
    real_time_data, 
    days_ahead=14  # Ubah dari 7 ke 14
)
```

### Ubah Threshold Risiko

Edit `src/model.py`:
```python
# Customize risk thresholds
if ispa_risk < 15:  # dari 20
    risk_cat = 'Low Risk'
elif ispa_risk < 35:  # dari 40
    risk_cat = 'Moderate Risk'
```

## 📊 Data Flow

```
Real-time API Data
        ↓
Batch Processing
        ↓
ISPA Correlation Analysis ──→ Dashboard Tab 5
        ↓
Future Risk Prediction ──→ Dashboard Tab 6
        ↓
Alerts & Reports
```

## 🎓 Manfaat untuk Pembelajaran

Fitur ini mendemonstrasikan:

1. **Time Series Forecasting** - Prediksi masa depan
2. **Correlation Analysis** - Analisis statistik
3. **Risk Assessment** - Health impact evaluation
4. **Data Visualization** - Interactive dashboards
5. **Alert Systems** - Automated warnings
6. **Decision Support** - Actionable recommendations

## 📝 Notes

- Prediksi menggunakan baseline dari kondisi terkini
- Akurasi meningkat dengan lebih banyak data historis
- Model dapat ditingkatkan dengan ML time series (ARIMA, LSTM)
- Alert otomatis disimpan jika ada prediksi risiko tinggi

---

**Pipeline Updated:** November 22, 2025
**Version:** 2.0 with ISPA Prediction & Correlation Analysis
