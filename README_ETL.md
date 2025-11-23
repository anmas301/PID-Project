# 🏥 Pipeline ETL - Analisis Risk Ratio ISPA

Pipeline **Extract-Transform-Load (ETL)** untuk menganalisis risiko Infeksi Saluran Pernapasan Akut (ISPA) berdasarkan kualitas udara dan parameter cuaca menggunakan **metodologi multiplikatif**.

## �� Ringkasan

Pipeline ini mengimplementasikan **3 tahap utama**:

1. **Extract** 📥: Mengambil data real-time kualitas udara dan cuaca dari 17 kota besar Indonesia
2. **Transform** 🔄: Membersihkan data dan menghitung Risk Ratio (RR) berdasarkan tabel metodologi
3. **Load** 💾: Menyimpan hasil analisis ke format CSV dan JSON

## 🎯 Metodologi: Model Multiplikatif

**Rumus:**

\`\`\`
RR_total = RR_PM2.5 × RR_PM10 × RR_NO₂ × RR_SO₂ × RR_O₃ × RR_suhu × RR_RH × RR_angin
\`\`\`

## 🚀 Quick Start

### 1. Jalankan ETL Pipeline

\`\`\`bash
python src/etl_pipeline.py
\`\`\`

**Output:**
- \`output/risk_analysis_YYYYMMDD_HHMMSS.csv\` - Data dalam format CSV
- \`output/risk_analysis_YYYYMMDD_HHMMSS.json\` - Data dalam format JSON

### 2. Visualisasi dengan Dashboard

\`\`\`bash
streamlit run src/dashboard_simple.py
\`\`\`

Buka browser: \`http://localhost:8501\`

## 📊 Hasil Pipeline

\`\`\`
🎯 Risk Category Distribution:
   Tinggi         : 10 kota (58.8%)
   Sangat Tinggi  :  7 kota (41.2%)

�� Risk Ratio Statistics:
   Mean RR   : 1.2926
   Min RR    : 1.2558 (Yogyakarta)
   Max RR    : 1.3458 (Surabaya)

🏙️ Top 5 Kota dengan RR Tertinggi:
   1. Surabaya   - 1.3458 (Sangat Tinggi)
   2. Denpasar   - 1.3458 (Sangat Tinggi)
   3. Palembang  - 1.3197 (Sangat Tinggi)
\`\`\`

## 📁 Struktur Project

\`\`\`
PID-Project/
├── config/
│   ├── config.py          # API keys & konfigurasi
│   └── rr_tables.py       # Tabel Risk Ratio metodologi
├── src/
│   ├── etl_pipeline.py    # Main ETL pipeline
│   └── dashboard_simple.py # Dashboard visualisasi
├── output/                # Hasil ETL (CSV & JSON)
└── README_ETL.md         # Dokumentasi ini
\`\`\`

## 📚 Referensi Metodologi

- **Odo, D. B., et al.** (2022) - PM2.5 and respiratory infection
- **Monoson, A., et al.** - Air pollutants review
- **Lowen, A. C., et al.** (2007) - Temperature & humidity effects
- **Davis, R. E., et al.** (2016) - Weather impact on mortality
