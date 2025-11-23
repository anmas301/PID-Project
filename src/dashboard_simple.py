"""
Dashboard Sederhana untuk Visualisasi Hasil ETL
Fokus: Extract → Transform → Load + Visualisasi Risk Ratio
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Setup page
st.set_page_config(
    page_title="Risk Ratio Dashboard - Kualitas Udara Indonesia",
    page_icon="🏥",
    layout="wide"
)

# Tambahkan path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.rr_tables import RISK_CATEGORIES, POLLUTION_RR, WEATHER_RR

# Title
st.title("🏥 Dashboard Analisis Risk Ratio ISPA")
st.markdown("**Metodologi Multiplikatif** untuk Risiko Infeksi Saluran Pernapasan Akut")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📊 Data Source")
    
    # Auto-load logic: prioritaskan file terbaru dari output folder
    auto_loaded_file = None
    if os.path.exists('output'):
        csv_files = [f for f in os.listdir('output') if f.endswith('.csv')]
        if csv_files:
            # Urutkan berdasarkan timestamp di nama file atau modification time
            sorted_files = sorted(csv_files, reverse=True)
            auto_loaded_file = f'output/{sorted_files[0]}'
    
    # Pilih file dari folder output
    uploaded_file = None
    if os.path.exists('output'):
        csv_files = [f for f in os.listdir('output') if f.endswith('.csv')]
        if csv_files:
            sorted_files = sorted(csv_files, reverse=True)
            selected_file = st.selectbox(
                "Pilih file hasil ETL:", 
                ['Auto (Terbaru)'] + sorted_files,
                help="Pilih 'Auto (Terbaru)' untuk load file terbaru otomatis"
            )
            
            if selected_file != 'Auto (Terbaru)':
                uploaded_file = f'output/{selected_file}'
            else:
                uploaded_file = auto_loaded_file
        else:
            st.warning("Folder output/ kosong. Jalankan ETL pipeline terlebih dahulu.")
    else:
        st.warning("Folder output/ tidak ditemukan.")
    
    # Jika tidak ada file yang dipilih, gunakan auto-loaded
    if not uploaded_file and auto_loaded_file:
        uploaded_file = auto_loaded_file
    
    # Tampilkan info file yang diload
    if uploaded_file:
        st.success(f"✅ Loaded: {os.path.basename(uploaded_file)}")
    
    st.markdown("---")
    st.markdown("### 📖 Metodologi")
    st.markdown("""
    **Model Multiplikatif:**
    
    RR_total = RR_PM2.5 × RR_PM10 × RR_NO2 × RR_SO2 × RR_O3 × RR_suhu × RR_RH × RR_angin
    
    **Sumber:**
    - Odo et al. (2022)
    - Monoson et al.
    - Lowen et al. (2007)
    - Davis et al. (2016)
    """)

# Load data with caching
@st.cache_data
def load_data(file_path):
    """Load dan cache data dari file CSV"""
    try:
        if isinstance(file_path, str):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_csv(file_path)
        
        # Validasi kolom yang diperlukan
        required_cols = ['city', 'province', 'rr_total', 'risk_category']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Kolom yang diperlukan tidak ditemukan: {missing_cols}")
        
        return df, None
    except Exception as e:
        return None, str(e)

df = None
error_msg = None

if uploaded_file:
    # Buat key unik untuk cache berdasarkan file path atau upload time
    cache_key = uploaded_file if isinstance(uploaded_file, str) else f"{uploaded_file.name}_{uploaded_file.size}"
    df, error_msg = load_data(cache_key if isinstance(uploaded_file, str) else uploaded_file)
    
    if df is not None:
        st.success(f"✅ Data berhasil dimuat: {len(df)} kota | {len(df.columns)} kolom")
    else:
        st.error(f"❌ Error loading data: {error_msg}")

if df is not None and len(df) > 0:
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍 Peta Risk Ratio", 
        "📊 Analisis Kota", 
        "🔬 Breakdown Faktor",
        "📈 Distribusi Risiko",
        "📋 Tabel Metodologi"
    ])
    
    # TAB 1: Peta Risk Ratio
    with tab1:
        st.header("🗺️ Peta Geografis Risk Ratio Indonesia")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Kota", len(df))
        with col2:
            st.metric("RR Rata-rata", f"{df['rr_total'].mean():.4f}")
        with col3:
            st.metric("RR Tertinggi", f"{df['rr_total'].max():.4f}")
        with col4:
            high_risk = len(df[df['risk_category'].isin(['Tinggi', 'Sangat Tinggi'])])
            st.metric("Kota Risiko Tinggi", high_risk)
        
        # Peta scatter
        # Pastikan kolom yang digunakan ada di dataframe
        map_hover_data = {'province': True, 'rr_total': ':.4f', 'risk_category': True, 'lat': False, 'lon': False}
        if 'pm2_5' in df.columns:
            map_hover_data['pm2_5'] = ':.1f'
        if 'temperature' in df.columns:
            map_hover_data['temperature'] = ':.1f'
        
        fig_map = px.scatter_geo(
            df,
            lat='lat',
            lon='lon',
            hover_name='city',
            hover_data=map_hover_data,
            color='risk_category',
            size='rr_total',
            color_discrete_map={
                'Rendah': 'green',
                'Sedang': 'yellow',
                'Tinggi': 'orange',
                'Sangat Tinggi': 'red'
            },
            projection='natural earth',
            title='Distribusi Risk Ratio ISPA di Indonesia'
        )
        
        fig_map.update_geos(
            center=dict(lat=-2, lon=118),
            lataxis_range=[-11, 6],
            lonaxis_range=[95, 141],
            showcountries=True,
            countrycolor="lightgray"
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    
    # TAB 2: Analisis Kota
    with tab2:
        st.header("🏙️ Analisis per Kota")
        
        # Sorting
        sort_by = st.radio(
            "Urutkan berdasarkan:",
            ['RR Total (Tertinggi)', 'RR Total (Terendah)', 'PM2.5 (Tertinggi)', 'Nama Kota'],
            horizontal=True
        )
        
        if sort_by == 'RR Total (Tertinggi)':
            df_sorted = df.sort_values('rr_total', ascending=False)
        elif sort_by == 'RR Total (Terendah)':
            df_sorted = df.sort_values('rr_total', ascending=True)
        elif sort_by == 'PM2.5 (Tertinggi)':
            df_sorted = df.sort_values('pm2_5', ascending=False)
        else:
            df_sorted = df.sort_values('city')
        
        # Bar chart RR Total
        bar_hover_data = {'province': True}
        if 'pm2_5' in df_sorted.columns:
            bar_hover_data['pm2_5'] = ':.1f'
        if 'temperature' in df_sorted.columns:
            bar_hover_data['temperature'] = ':.1f'
        
        fig_bar = px.bar(
            df_sorted,
            x='city',
            y='rr_total',
            color='risk_category',
            color_discrete_map={
                'Rendah': 'green',
                'Sedang': 'yellow',
                'Tinggi': 'orange',
                'Sangat Tinggi': 'red'
            },
            title='Risk Ratio Total per Kota',
            labels={'rr_total': 'RR Total', 'city': 'Kota'},
            hover_data=bar_hover_data
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Detail table
        st.subheader("📋 Detail Data Kota")
        
        # Pilih kolom yang ada
        base_cols = ['city', 'province', 'rr_total', 'risk_category']
        optional_cols = ['pm2_5', 'pm10', 'no2', 'temperature', 'humidity', 'wind_speed']
        display_cols = base_cols + [col for col in optional_cols if col in df_sorted.columns]
        
        # Format dictionary hanya untuk kolom yang ada
        format_dict = {'rr_total': '{:.4f}'}
        if 'pm2_5' in df_sorted.columns:
            format_dict['pm2_5'] = '{:.1f}'
        if 'pm10' in df_sorted.columns:
            format_dict['pm10'] = '{:.1f}'
        if 'no2' in df_sorted.columns:
            format_dict['no2'] = '{:.1f}'
        if 'temperature' in df_sorted.columns:
            format_dict['temperature'] = '{:.1f}°C'
        if 'humidity' in df_sorted.columns:
            format_dict['humidity'] = '{:.0f}%'
        if 'wind_speed' in df_sorted.columns:
            format_dict['wind_speed'] = '{:.2f} m/s'
        
        st.dataframe(
            df_sorted[display_cols].style.format(format_dict).background_gradient(subset=['rr_total'], cmap='RdYlGn_r'),
            use_container_width=True,
            height=400
        )
    
    # TAB 3: Breakdown Faktor
    with tab3:
        st.header("🔬 Breakdown Faktor Risk Ratio")
        
        # Pilih kota
        selected_city = st.selectbox("Pilih Kota:", df['city'].unique())
        city_data = df[df['city'] == selected_city].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💨 Faktor Polusi")
            
            pollution_rr = {
                'PM2.5': city_data['rr_pm2_5'],
                'PM10': city_data['rr_pm10'],
                'NO₂': city_data['rr_no2'],
                'SO₂': city_data['rr_so2'],
                'O₃': city_data['rr_o3']
            }
            
            fig_pollution = go.Figure(data=[
                go.Bar(
                    x=list(pollution_rr.values()),
                    y=list(pollution_rr.keys()),
                    orientation='h',
                    marker=dict(
                        color=list(pollution_rr.values()),
                        colorscale='Reds',
                        showscale=False
                    ),
                    text=[f"{v:.3f}" for v in pollution_rr.values()],
                    textposition='auto'
                )
            ])
            
            fig_pollution.update_layout(
                title=f"Risk Ratio Polusi - {selected_city}",
                xaxis_title="Risk Ratio",
                yaxis_title="Polutan"
            )
            
            st.plotly_chart(fig_pollution, use_container_width=True)
            
            # Konsentrasi aktual
            st.markdown("**Konsentrasi Aktual:**")
            st.metric("PM2.5", f"{city_data['pm2_5']:.1f} µg/m³")
            st.metric("PM10", f"{city_data['pm10']:.1f} µg/m³")
            st.metric("NO₂", f"{city_data['no2']:.1f} µg/m³")
        
        with col2:
            st.subheader("🌤️ Faktor Cuaca")
            
            weather_rr = {
                f"Suhu\n({city_data['temp_category']})": city_data['rr_temperature'],
                f"Kelembapan\n({city_data['humidity_category']})": city_data['rr_humidity'],
                f"Angin\n({city_data['wind_category']})": city_data['rr_wind']
            }
            
            fig_weather = go.Figure(data=[
                go.Bar(
                    x=list(weather_rr.values()),
                    y=list(weather_rr.keys()),
                    orientation='h',
                    marker=dict(
                        color=list(weather_rr.values()),
                        colorscale='Blues',
                        showscale=False
                    ),
                    text=[f"{v:.3f}" for v in weather_rr.values()],
                    textposition='auto'
                )
            ])
            
            fig_weather.update_layout(
                title=f"Risk Ratio Cuaca - {selected_city}",
                xaxis_title="Risk Ratio",
                yaxis_title="Parameter"
            )
            
            st.plotly_chart(fig_weather, use_container_width=True)
            
            # Nilai aktual
            st.markdown("**Kondisi Aktual:**")
            st.metric("Suhu", f"{city_data['temperature']:.1f}°C", delta=city_data['temp_category'])
            st.metric("Kelembapan", f"{city_data['humidity']:.0f}%", delta=city_data['humidity_category'])
            st.metric("Kec. Angin", f"{city_data['wind_speed']:.1f} m/s", delta=city_data['wind_category'])
        
        # Total RR
        st.markdown("---")
        st.subheader("🎯 Total Risk Ratio (Model Multiplikatif)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("RR Total", f"{city_data['rr_total']:.4f}")
        with col2:
            st.metric("Kategori Risiko", city_data['risk_category'])
        with col3:
            # Hitung kontribusi terbesar
            all_rr = {**pollution_rr, **weather_rr}
            max_contributor = max(all_rr, key=all_rr.get)
            st.metric("Faktor Dominan", max_contributor.split('\n')[0])
    
    # TAB 4: Distribusi Risiko
    with tab4:
        st.header("📈 Distribusi & Statistik Risiko")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart kategori
            risk_counts = df['risk_category'].value_counts()
            fig_pie = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title='Distribusi Kategori Risiko',
                color=risk_counts.index,
                color_discrete_map={
                    'Rendah': 'green',
                    'Sedang': 'yellow',
                    'Tinggi': 'orange',
                    'Sangat Tinggi': 'red'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Histogram RR
            fig_hist = px.histogram(
                df,
                x='rr_total',
                nbins=20,
                title='Distribusi Risk Ratio Total',
                labels={'rr_total': 'RR Total', 'count': 'Jumlah Kota'},
                color_discrete_sequence=['#636EFA']
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        # Box plot per provinsi (top 10)
        st.subheader("📦 Box Plot RR per Provinsi")
        top_provinces = df['province'].value_counts().head(10).index
        df_top = df[df['province'].isin(top_provinces)]
        
        fig_box = px.box(
            df_top,
            x='province',
            y='rr_total',
            color='risk_category',
            title='Distribusi RR per Provinsi (Top 10)',
            color_discrete_map={
                'Rendah': 'green',
                'Sedang': 'yellow',
                'Tinggi': 'orange',
                'Sangat Tinggi': 'red'
            }
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
        # Statistik deskriptif
        st.subheader("📊 Statistik Deskriptif")
        stats = df['rr_total'].describe()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean", f"{stats['mean']:.4f}")
            st.metric("Std Dev", f"{stats['std']:.4f}")
        with col2:
            st.metric("Median", f"{stats['50%']:.4f}")
            st.metric("Q1", f"{stats['25%']:.4f}")
        with col3:
            st.metric("Q3", f"{stats['75%']:.4f}")
            st.metric("IQR", f"{stats['75%'] - stats['25%']:.4f}")
        with col4:
            st.metric("Min", f"{stats['min']:.4f}")
            st.metric("Max", f"{stats['max']:.4f}")
    
    # TAB 5: Tabel Metodologi
    with tab5:
        st.header("📋 Tabel Metodologi Risk Ratio")
        
        st.subheader("Tabel 1: Faktor Risiko Polusi Udara terhadap ISPA")
        
        pollution_table = []
        for pollutant, data in POLLUTION_RR.items():
            pollution_table.append({
                'Polutan': pollutant,
                'Rentang Efek': f"{(data['range'][0]-1)*100:.0f}% – {(data['range'][1]-1)*100:.0f}% ↑",
                'RR Range': f"{data['range'][0]:.2f} – {data['range'][1]:.2f}",
                'Median (Dipakai)': data['median'],
                'Sumber': data['source']
            })
        
        st.dataframe(pd.DataFrame(pollution_table), use_container_width=True)
        
        st.markdown("---")
        st.subheader("Tabel 2: Faktor Risiko Cuaca terhadap ISPA")
        
        # Temperature
        st.markdown("**Suhu (Temperature)**")
        temp_table = [
            {'Kategori': '< 20°C', 'Penjelasan': 'Udara dingin → stabilitas virus ↑', 'RR': 1.05, 'Sumber': 'Lowen et al.'},
            {'Kategori': '20–25°C', 'Penjelasan': 'Kondisi normal', 'RR': 1.00, 'Sumber': 'Davis et al.'},
            {'Kategori': '25–30°C', 'Penjelasan': 'Kondisi hangat', 'RR': 1.01, 'Sumber': 'Interpolasi'},
            {'Kategori': '> 30°C', 'Penjelasan': 'Stres panas → iritasi mukosa', 'RR': 1.03, 'Sumber': 'Davis et al.'}
        ]
        st.dataframe(pd.DataFrame(temp_table), use_container_width=True)
        
        # Humidity
        st.markdown("**Kelembapan (Relative Humidity)**")
        humid_table = [
            {'Kategori': '< 40%', 'Penjelasan': 'RH rendah → aerosol bertahan lama', 'RR': 1.05, 'Sumber': 'Lowen; Shaman'},
            {'Kategori': '40–60%', 'Penjelasan': 'Zona optimal', 'RR': 1.00, 'Sumber': 'ASHRAE'},
            {'Kategori': '60–70%', 'Penjelasan': 'Kelembapan sedang', 'RR': 1.01, 'Sumber': 'Interpolasi'},
            {'Kategori': '> 70%', 'Penjelasan': 'Risiko mikroba ↑', 'RR': 1.03, 'Sumber': 'Studi epidemiologi'}
        ]
        st.dataframe(pd.DataFrame(humid_table), use_container_width=True)
        
        # Wind Speed
        st.markdown("**Kecepatan Angin (Wind Speed)**")
        wind_table = [
            {'Kategori': '< 1.5 m/s', 'Penjelasan': 'Stagnasi → polutan menumpuk', 'RR': 1.03, 'Sumber': 'Studi dispersi'},
            {'Kategori': '1.5–3 m/s', 'Penjelasan': 'Dispersi normal', 'RR': 1.00, 'Sumber': 'Review dispersion'},
            {'Kategori': '> 3 m/s', 'Penjelasan': 'Dispersi tinggi', 'RR': 0.99, 'Sumber': 'Review dispersion'}
        ]
        st.dataframe(pd.DataFrame(wind_table), use_container_width=True)
        
        st.markdown("---")
        st.subheader("🧮 Model Multiplikatif")
        st.latex(r"RR_{total} = RR_{PM2.5} \times RR_{PM10} \times RR_{NO_2} \times RR_{SO_2} \times RR_{O_3} \times RR_{suhu} \times RR_{RH} \times RR_{angin}")
        
        st.markdown("**Asumsi:** Efek relatif setiap faktor bekerja independen pada skala RR")
        
        st.markdown("---")
        st.subheader("📊 Kategori Risiko ISPA")
        category_table = []
        for cat in RISK_CATEGORIES:
            max_val = cat['max'] if cat['max'] != float('inf') else '∞'
            category_table.append({
                'RR Range': f"{cat['min']:.2f} – {max_val}",
                'Kategori': cat['category'],
                'Deskripsi': cat['description']
            })
        st.dataframe(pd.DataFrame(category_table), use_container_width=True)

else:
    st.info("👈 Upload file CSV hasil ETL atau pilih dari hasil sebelumnya di sidebar")
    
    st.markdown("""
    ### 📖 Cara Menggunakan Dashboard:
    
    1. **Jalankan ETL Pipeline** terlebih dahulu:
       ```bash
       python src/etl_pipeline.py
       ```
    
    2. **Upload hasil CSV** dari folder `output/` atau pilih dari dropdown di sidebar
    
    3. **Eksplorasi hasil** melalui 5 tab yang tersedia:
       - 📍 Peta geografis distribusi risiko
       - 📊 Analisis detail per kota
       - 🔬 Breakdown faktor polusi & cuaca
       - 📈 Distribusi statistik risiko
       - 📋 Tabel metodologi lengkap
    
    ### 🎯 Fitur Dashboard:
    
    - ✅ Visualisasi peta Indonesia dengan risk ratio
    - ✅ Ranking kota berdasarkan risiko ISPA
    - ✅ Breakdown kontribusi masing-masing faktor
    - ✅ Analisis statistik deskriptif
    - ✅ Referensi tabel metodologi multiplikatif
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Risk Ratio Dashboard</strong> | Metodologi Multiplikatif | Data Real-time dari OpenWeather & WeatherAPI</p>
    <p>Sumber: Odo et al. (2022), Monoson et al., Lowen et al. (2007), Davis et al. (2016)</p>
</div>
""", unsafe_allow_html=True)
