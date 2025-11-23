# PID---Pipeline-Kualitas-Udara-dan-Risiko-Kesehatan

Bagian *7. Metodologi* sudah aku ubah menjadi *format Markdown (.md)* supaya bisa langsung kamu tempel ke file .md di Codespace atau GitHub.

Silakan copy bagian ini:

---

# 7. Metodologi

## 7.1 Metode Pengambilan Data

Penjelasan mengenai teknik, sumber, protokol, dan alur pengambilan data kualitas udara serta parameter cuaca.

## 7.2 Metode Pembersihan & Transformasi Data

Proses preprocessing mencakup:

* Penghapusan nilai hilang atau outlier,
* Normalisasi dan standarisasi data,
* Penggabungan data cuaca dan polusi berdasarkan timestamp,
* Rekonsiliasi format antar-sumber.

## 7.3 Metode Analisis (Statistik/Korelasi)

### 7.3.1 Faktor Risiko Polusi Udara terhadap ISPA

Berbagai studi epidemiologis menunjukkan korelasi kuat antara peningkatan konsentrasi polutan udara dan risiko Infeksi Saluran Pernapasan Akut (ISPA). Rentang efek diambil dari ulasan sistematis dan studi primer, sementara nilai median dipakai pada model risiko multiplikatif.

*Tabel 1. Faktor Risiko Polusi Udara terhadap ISPA*

| Polutan | Rentang Efek (Δ Risiko) | Risk Ratio (RR Range) | Median Dipakai | Sumber Utama                         |
| ------- | ----------------------- | --------------------- | -------------- | ------------------------------------ |
| PM2.5   | 2% – 7% ↑               | 1.02 – 1.07           | 1.045          | Odo et al. (2022); Monoson et al.    |
| PM10    | 1% – 3% ↑               | 1.01 – 1.03           | 1.02           | Monoson et al.                       |
| NO₂     | 5% – 15% ↑              | 1.05 – 1.15           | 1.10           | Monoson et al.; studi kohort         |
| SO₂     | 2% – 6% ↑               | 1.02 – 1.06           | 1.04           | Monoson et al.                       |
| O₃      | 0% – 2% ↑               | 1.00 – 1.02           | 1.01           | Monoson et al.; analisis time-series |

Penjelasan: Studi Odo et al. menunjukkan OR ≈ 1.06 per kenaikan 10 μg/m³ PM2.5, terutama untuk anak di bawah lima tahun.

### 7.3.2 Faktor Risiko Cuaca terhadap ISPA

Parameter cuaca memengaruhi stabilitas virus, kondisi mukosa, dan dispersi polutan. Nilai kategori serta RR diambil dari penelitian eksperimental dan epidemiologis (Lowen et al. 2007; Shaman et al. 2009; Davis et al. 2016).

*Tabel 2. Faktor Risiko Cuaca terhadap ISPA*

| Parameter       | Kategori  | Penjelasan Singkat                | Risk Ratio | Sumber             |
| --------------- | --------- | --------------------------------- | ---------- | ------------------ |
| Suhu            | < 20°C    | Udara dingin → stabilitas virus ↑ | 1.05       | Lowen et al.       |
|                 | 20–25°C   | Kondisi normal                    | 1.00       | Davis et al.       |
|                 | > 30°C    | Stres panas → iritasi mukosa      | 1.03       | Davis et al.       |
| Kelembapan (RH) | < 40%     | RH rendah → aerosol bertahan lama | 1.05       | Lowen; Shaman      |
|                 | 40–60%    | Zona optimal                      | 1.00       | ASHRAE             |
|                 | > 70%     | Risiko mikroba ↑                  | 1.03       | Studi epidemiologi |
| Kecepatan Angin | < 1.5 m/s | Stagnasi → polutan menumpuk       | 1.03       | Studi dispersi     |
|                 | 1.5–3 m/s | Dispersi normal                   | 1.00       | Review dispersion  |
|                 | > 3 m/s   | Dispersi tinggi                   | 0.99       | Review dispersion  |

### 7.3.3 Model Risiko Multiplikatif

Model menghitung total risiko sebagai hasil perkalian seluruh risk ratio (RR) dari faktor polusi dan cuaca.

*Rumus:*


RR_total = RR_PM2.5 × RR_PM10 × RR_NO2 × RR_SO2 × RR_O3 × RR_suhu × RR_RH × RR_angin


Pendekatan ini mengasumsikan efek relatif setiap faktor bekerja independen pada skala RR.

## 7.4 Tools & Teknologi yang Digunakan

Daftar tools dan stack teknis yang digunakan dalam proses ingestion, transformasi, penyimpanan, analisis, hingga penyajian data.

---

Kalau kamu ingin, bisa aku buatkan versi *Markdown full seluruh proposal*, bukan hanya bagian 7.