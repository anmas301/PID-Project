"""
ETL Pipeline Sederhana dengan Metodologi Multiplikatif
Extract → Transform → Load
"""

import pandas as pd
import requests
from datetime import datetime
import json
import sys
import os

# Tambahkan path config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import OPENWEATHER_API_KEY, WEATHERAPI_KEY
from config.rr_tables import (
    INDONESIAN_CITIES, 
    calculate_total_rr,
    RISK_CATEGORIES
)


class SimpleETL:
    """Pipeline ETL sederhana untuk kualitas udara dan risiko ISPA"""
    
    def __init__(self):
        self.openweather_key = OPENWEATHER_API_KEY
        self.weatherapi_key = WEATHERAPI_KEY
        self.data = []
    
    def extract(self):
        """
        STEP 1: EXTRACT
        Mengambil data real-time dari API untuk kota-kota besar Indonesia
        """
        print("\n" + "="*70)
        print("📥 STEP 1: EXTRACT DATA")
        print("="*70)
        
        for city in INDONESIAN_CITIES:
            try:
                print(f"\n🌆 Fetching data untuk {city['name']}, {city['province']}...")
                
                # 1. Ambil data polusi udara
                pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={city['lat']}&lon={city['lon']}&appid={self.openweather_key}"
                pollution_response = requests.get(pollution_url, timeout=10)
                
                if pollution_response.status_code == 200:
                    pollution_data = pollution_response.json()
                    
                    # 2. Ambil data cuaca
                    weather_url = f"http://api.weatherapi.com/v1/current.json?key={self.weatherapi_key}&q={city['lat']},{city['lon']}&aqi=yes"
                    weather_response = requests.get(weather_url, timeout=10)
                    
                    if weather_response.status_code == 200:
                        weather_data = weather_response.json()
                        
                        # Simpan data mentah
                        self.data.append({
                            'city': city['name'],
                            'province': city['province'],
                            'lat': city['lat'],
                            'lon': city['lon'],
                            'pollution': pollution_data,
                            'weather': weather_data,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        print(f"   ✅ Data berhasil diambil")
                    else:
                        print(f"   ❌ Error cuaca: {weather_response.status_code}")
                else:
                    print(f"   ❌ Error polusi: {pollution_response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print(f"\n✅ Extract selesai: {len(self.data)} kota berhasil")
        return self.data
    
    def transform(self):
        """
        STEP 2: TRANSFORM
        Membersihkan data dan menghitung Risk Ratio berdasarkan tabel metodologi
        """
        print("\n" + "="*70)
        print("🔄 STEP 2: TRANSFORM & CALCULATE RISK RATIO")
        print("="*70)
        
        transformed_data = []
        
        for record in self.data:
            try:
                city = record['city']
                print(f"\n🔧 Processing {city}...")
                
                # Extract komponen polusi
                components = record['pollution']['list'][0]['components']
                pollution = {
                    'PM2.5': components.get('pm2_5', 0),
                    'PM10': components.get('pm10', 0),
                    'NO2': components.get('no2', 0),
                    'SO2': components.get('so2', 0),
                    'O3': components.get('o3', 0),
                    'CO': components.get('co', 0)
                }
                
                # Extract parameter cuaca
                weather = {
                    'temp': record['weather']['current']['temp_c'],
                    'humidity': record['weather']['current']['humidity'],
                    'wind_speed': record['weather']['current']['wind_kph'] / 3.6,  # Convert to m/s
                    'pressure': record['weather']['current']['pressure_mb'],
                    'cloud': record['weather']['current']['cloud']
                }
                
                # Hitung Risk Ratio menggunakan model multiplikatif
                risk_result = calculate_total_rr(pollution, weather)
                
                # Buat record yang sudah ditransformasi
                transformed_record = {
                    'timestamp': record['timestamp'],
                    'city': city,
                    'province': record['province'],
                    'lat': record['lat'],
                    'lon': record['lon'],
                    
                    # Data Polusi (µg/m³)
                    'pm2_5': pollution['PM2.5'],
                    'pm10': pollution['PM10'],
                    'no2': pollution['NO2'],
                    'so2': pollution['SO2'],
                    'o3': pollution['O3'],
                    'co': pollution['CO'],
                    
                    # Data Cuaca
                    'temperature': weather['temp'],
                    'humidity': weather['humidity'],
                    'wind_speed': weather['wind_speed'],
                    'pressure': weather['pressure'],
                    'cloud_cover': weather['cloud'],
                    
                    # Risk Ratio
                    'rr_total': risk_result['rr_total'],
                    'risk_category': risk_result['category'],
                    
                    # Breakdown RR
                    'rr_pm2_5': risk_result['breakdown']['pollution']['PM2.5'],
                    'rr_pm10': risk_result['breakdown']['pollution']['PM10'],
                    'rr_no2': risk_result['breakdown']['pollution']['NO2'],
                    'rr_so2': risk_result['breakdown']['pollution']['SO2'],
                    'rr_o3': risk_result['breakdown']['pollution']['O3'],
                    'rr_temperature': risk_result['breakdown']['weather']['temperature']['rr'],
                    'rr_humidity': risk_result['breakdown']['weather']['humidity']['rr'],
                    'rr_wind': risk_result['breakdown']['weather']['wind_speed']['rr'],
                    
                    # Kategori Cuaca
                    'temp_category': risk_result['breakdown']['weather']['temperature']['category'],
                    'humidity_category': risk_result['breakdown']['weather']['humidity']['category'],
                    'wind_category': risk_result['breakdown']['weather']['wind_speed']['category']
                }
                
                transformed_data.append(transformed_record)
                
                print(f"   📊 PM2.5: {pollution['PM2.5']:.1f} µg/m³")
                print(f"   🌡️  Suhu: {weather['temp']:.1f}°C ({transformed_record['temp_category']})")
                print(f"   💧 Kelembapan: {weather['humidity']}% ({transformed_record['humidity_category']})")
                print(f"   🎯 RR Total: {risk_result['rr_total']:.4f} → {risk_result['category']}")
                
            except Exception as e:
                print(f"   ❌ Error processing {record['city']}: {str(e)}")
        
        print(f"\n✅ Transform selesai: {len(transformed_data)} records")
        return transformed_data
    
    def load(self, transformed_data, output_format='both'):
        """
        STEP 3: LOAD
        Menyimpan data hasil transformasi ke CSV dan JSON
        
        Args:
            transformed_data: List of dict hasil transform
            output_format: 'csv', 'json', atau 'both'
        """
        print("\n" + "="*70)
        print("💾 STEP 3: LOAD DATA")
        print("="*70)
        
        # Buat folder output jika belum ada
        os.makedirs('output', exist_ok=True)
        
        # Convert ke DataFrame
        df = pd.DataFrame(transformed_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save ke CSV
        if output_format in ['csv', 'both']:
            csv_path = f'output/risk_analysis_{timestamp}.csv'
            df.to_csv(csv_path, index=False)
            print(f"\n✅ CSV saved: {csv_path}")
            print(f"   📄 {len(df)} rows × {len(df.columns)} columns")
        
        # Save ke JSON
        if output_format in ['json', 'both']:
            json_path = f'output/risk_analysis_{timestamp}.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(transformed_data, f, indent=2, ensure_ascii=False)
            print(f"\n✅ JSON saved: {json_path}")
        
        # Summary statistik
        print("\n" + "="*70)
        print("📊 SUMMARY STATISTICS")
        print("="*70)
        
        print(f"\n🌆 Total Kota: {df['city'].nunique()}")
        print(f"📅 Timestamp: {df['timestamp'].iloc[0]}")
        
        print("\n🎯 Risk Category Distribution:")
        risk_dist = df['risk_category'].value_counts()
        for category, count in risk_dist.items():
            percentage = (count / len(df)) * 100
            print(f"   {category:15s}: {count:2d} kota ({percentage:5.1f}%)")
        
        print("\n📈 Risk Ratio Statistics:")
        print(f"   Mean RR   : {df['rr_total'].mean():.4f}")
        print(f"   Median RR : {df['rr_total'].median():.4f}")
        print(f"   Min RR    : {df['rr_total'].min():.4f} ({df.loc[df['rr_total'].idxmin(), 'city']})")
        print(f"   Max RR    : {df['rr_total'].max():.4f} ({df.loc[df['rr_total'].idxmax(), 'city']})")
        
        print("\n🏙️ Top 5 Kota dengan RR Tertinggi:")
        top5 = df.nlargest(5, 'rr_total')[['city', 'province', 'rr_total', 'risk_category']]
        for idx, row in top5.iterrows():
            print(f"   {row['city']:15s} ({row['province']:20s}): {row['rr_total']:.4f} - {row['risk_category']}")
        
        print("\n" + "="*70)
        
        return df
    
    def run(self, output_format='both'):
        """
        Menjalankan full ETL pipeline
        
        Args:
            output_format: 'csv', 'json', atau 'both'
        """
        print("\n" + "="*70)
        print("🚀 MEMULAI ETL PIPELINE")
        print("="*70)
        print(f"📍 Target: {len(INDONESIAN_CITIES)} kota besar di Indonesia")
        print(f"📊 Metodologi: Model Multiplikatif Risk Ratio")
        print("="*70)
        
        # Extract
        raw_data = self.extract()
        
        if not raw_data:
            print("\n❌ Tidak ada data yang berhasil di-extract!")
            return None
        
        # Transform
        transformed_data = self.transform()
        
        if not transformed_data:
            print("\n❌ Transform gagal!")
            return None
        
        # Load
        df = self.load(transformed_data, output_format)
        
        print("\n" + "="*70)
        print("✅ ETL PIPELINE SELESAI!")
        print("="*70)
        
        return df


if __name__ == "__main__":
    # Jalankan pipeline
    etl = SimpleETL()
    result = etl.run(output_format='both')
    
    if result is not None:
        print("\n🎉 Pipeline berhasil dijalankan!")
        print(f"📁 Hasil tersimpan di folder 'output/'")
