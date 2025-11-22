"""
Dashboard Module
Streamlit dashboard untuk visualisasi data dan prediksi risiko ISPA
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATA_PATHS, RISK_THRESHOLDS, CITIES
from src.ingestion import DataIngestion
from src.transformation import DataTransformation
from src.model import ISPARiskPredictor
from src.batch_processing import BatchProcessor

# Page config
st.set_page_config(
    page_title="ISPA Risk Monitoring Dashboard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .risk-good { color: #2ecc71; }
    .risk-moderate { color: #f39c12; }
    .risk-unhealthy { color: #e74c3c; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load and cache data"""
    try:
        # Try to load processed data
        processed_path = DATA_PATHS['processed'] / 'real_time_merged.csv'
        if processed_path.exists():
            df = pd.read_csv(processed_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            st.warning("No processed data found. Please run the pipeline first.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


def get_risk_color(risk_category):
    """Get color based on risk category"""
    colors = {
        'good': '#2ecc71',
        'moderate': '#f39c12',
        'unhealthy_sensitive': '#e67e22',
        'unhealthy': '#e74c3c',
        'very_unhealthy': '#c0392b',
        'hazardous': '#8b0000'
    }
    return colors.get(risk_category, '#95a5a6')


def plot_aqi_timeseries(df, location=None):
    """Plot AQI time series"""
    if df.empty:
        st.warning("No data available for plotting")
        return
    
    df_plot = df.copy()
    if location and location != 'All':
        df_plot = df_plot[df_plot['location'] == location]
    
    fig = px.line(
        df_plot,
        x='timestamp',
        y='aqi',
        color='location' if location == 'All' else None,
        title=f'Air Quality Index Over Time - {location}',
        labels={'aqi': 'AQI', 'timestamp': 'Time'}
    )
    
    # Add risk threshold lines
    for category, (low, high) in RISK_THRESHOLDS.items():
        if high < 500:
            fig.add_hline(
                y=high, 
                line_dash="dash", 
                line_color=get_risk_color(category),
                annotation_text=category.replace('_', ' ').title()
            )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_pollutants_comparison(df, location):
    """Plot comparison of different pollutants"""
    if df.empty or location not in df['location'].values:
        st.warning("No data available for this location")
        return
    
    df_location = df[df['location'] == location].iloc[-1]
    
    pollutants = {
        'PM2.5': df_location.get('pm2_5', 0),
        'PM10': df_location.get('pm10', 0),
        'CO': df_location.get('co', 0) / 1000,  # Convert to mg/m3
        'NO2': df_location.get('no2', 0),
        'O3': df_location.get('o3', 0),
        'SO2': df_location.get('so2', 0)
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(pollutants.keys()),
            y=list(pollutants.values()),
            marker_color=['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#9b59b6', '#1abc9c']
        )
    ])
    
    fig.update_layout(
        title=f'Current Pollutant Levels - {location}',
        xaxis_title='Pollutant',
        yaxis_title='Concentration (μg/m³)',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_weather_correlation(df):
    """Plot correlation between weather and AQI"""
    if df.empty or 'aqi' not in df.columns:
        st.warning("Insufficient data for correlation plot")
        return
    
    weather_cols = ['temp_c', 'humidity', 'wind_kph', 'pressure_mb']
    available_cols = [col for col in weather_cols if col in df.columns]
    
    if not available_cols:
        st.warning("No weather data available")
        return
    
    df_corr = df[['aqi'] + available_cols].corr()
    
    fig = px.imshow(
        df_corr,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        title='Correlation: AQI vs Weather Parameters'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_risk_distribution(df):
    """Plot distribution of risk categories"""
    if df.empty or 'risk_category' not in df.columns:
        st.warning("No risk category data available")
        return
    
    risk_counts = df['risk_category'].value_counts()
    
    colors = [get_risk_color(cat) for cat in risk_counts.index]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=risk_counts.index,
            values=risk_counts.values,
            marker=dict(colors=colors),
            hole=0.3
        )
    ])
    
    fig.update_layout(title='Risk Category Distribution')
    
    st.plotly_chart(fig, use_container_width=True)


def plot_location_comparison(df):
    """Compare AQI across locations"""
    if df.empty or 'location' not in df.columns:
        st.warning("No location data available")
        return
    
    # Get latest data for each location
    latest_data = df.sort_values('timestamp').groupby('location').last().reset_index()
    
    fig = px.bar(
        latest_data,
        x='location',
        y='aqi',
        color='risk_category',
        color_discrete_map={cat: get_risk_color(cat) for cat in RISK_THRESHOLDS.keys()},
        title='Current AQI by Location'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_highest_pollution_cities(df):
    """Show cities with highest pollution levels"""
    if df.empty or 'location' not in df.columns or 'aqi' not in df.columns:
        st.warning("No pollution data available")
        return
    
    # Calculate average AQI per location
    avg_pollution = df.groupby('location').agg({
        'aqi': 'mean',
        'pm2_5': 'mean',
        'pm10': 'mean'
    }).round(2).sort_values('aqi', ascending=False).reset_index()
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=avg_pollution['location'],
        y=avg_pollution['aqi'],
        name='AQI',
        marker_color='#e74c3c',
        text=avg_pollution['aqi'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='🏭 Kota dengan Tingkat Polusi Tertinggi',
        xaxis_title='Kota',
        yaxis_title='Average AQI',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display as table
    st.dataframe(
        avg_pollution.style.background_gradient(subset=['aqi', 'pm2_5', 'pm10'], cmap='Reds'),
        use_container_width=True
    )


def plot_ispa_correlation(df, ispa_analysis):
    """Plot correlation between pollution and ISPA risk"""
    
    st.subheader("📊 Korelasi Polusi Udara dengan Risiko ISPA")
    
    if 'pollution_ispa_correlation' in ispa_analysis and ispa_analysis['pollution_ispa_correlation']:
        corr_data = ispa_analysis['pollution_ispa_correlation']
        
        # Create correlation chart
        pollutants = list(corr_data.keys())
        correlations = list(corr_data.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=pollutants,
                y=correlations,
                marker=dict(
                    color=correlations,
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title="Correlation")
                ),
                text=[f"{c:.3f}" for c in correlations],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='Korelasi Polutan dengan Risiko ISPA',
            xaxis_title='Polutan',
            yaxis_title='Correlation Coefficient',
            yaxis_range=[-1, 1]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Explanation
        st.info("""
        **📖 Interpretasi:**
        - Nilai mendekati **+1**: Korelasi positif kuat (polutan ↑ → risiko ISPA ↑)
        - Nilai mendekati **0**: Tidak ada korelasi signifikan
        - Nilai mendekati **-1**: Korelasi negatif kuat (jarang terjadi)
        """)
    
    # High risk locations
    if 'high_risk_locations' in ispa_analysis and ispa_analysis['high_risk_locations']:
        st.subheader("⚠️ Daerah Berisiko Tinggi")
        
        risk_df = pd.DataFrame(ispa_analysis['high_risk_locations'])
        risk_df = risk_df.sort_values('avg_aqi', ascending=False)
        
        # Color code by risk level
        def color_risk(val):
            if val == 'High':
                return 'background-color: #e74c3c; color: white'
            elif val == 'Moderate':
                return 'background-color: #f39c12; color: white'
            else:
                return 'background-color: #2ecc71; color: white'
        
        st.dataframe(
            risk_df.style.applymap(color_risk, subset=['risk_level']),
            use_container_width=True
        )
    
    # Recommendations
    if 'recommendations' in ispa_analysis and ispa_analysis['recommendations']:
        st.subheader("💡 Rekomendasi")
        for rec in ispa_analysis['recommendations']:
            st.warning(rec)


def plot_future_predictions(predictions_df):
    """Plot future ISPA risk predictions"""
    if predictions_df.empty:
        st.warning("No predictions available")
        return
    
    st.subheader("🔮 Prediksi Risiko ISPA 7 Hari Ke Depan")
    
    # Time series of predictions
    fig = px.line(
        predictions_df,
        x='date',
        y='predicted_ispa_risk',
        color='location',
        title='Prediksi Risiko ISPA per Lokasi',
        labels={
            'predicted_ispa_risk': 'ISPA Risk Score (0-100)',
            'date': 'Tanggal'
        },
        markers=True
    )
    
    # Add risk threshold lines
    fig.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Low Risk")
    fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Moderate Risk")
    fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="High Risk")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    st.subheader("📋 Detail Prediksi per Lokasi")
    
    for location in predictions_df['location'].unique():
        with st.expander(f"📍 {location}"):
            loc_data = predictions_df[predictions_df['location'] == location]
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_risk = loc_data['predicted_ispa_risk'].mean()
                st.metric("Rata-rata Risiko", f"{avg_risk:.1f}")
            with col2:
                max_risk = loc_data['predicted_ispa_risk'].max()
                max_date = loc_data.loc[loc_data['predicted_ispa_risk'].idxmax(), 'date']
                st.metric("Risiko Tertinggi", f"{max_risk:.1f}", f"pada {max_date}")
            with col3:
                high_risk_days = len(loc_data[loc_data['predicted_ispa_risk'] > 40])
                st.metric("Hari Berisiko Tinggi", high_risk_days)
            
            # Show table
            st.dataframe(
                loc_data[['date', 'predicted_ispa_risk', 'risk_category', 'predicted_aqi']],
                use_container_width=True
            )


def main():
    # Header
    st.markdown('<div class="main-header">🌫️ ISPA Risk Monitoring Dashboard</div>', unsafe_allow_html=True)
    st.markdown("### Monitoring Kualitas Udara dan Risiko ISPA - Jawa Tengah")
    
    # Sidebar
    st.sidebar.title("⚙️ Controls")
    
    # Refresh data button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data available. Please run the data pipeline first.")
        st.code("python src/main.py", language="bash")
        return
    
    # Location selector
    locations = ['All'] + sorted(df['location'].unique().tolist())
    selected_location = st.sidebar.selectbox("📍 Select Location", locations)
    
    # Date range
    if 'timestamp' in df.columns:
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
        
        date_range = st.sidebar.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            df = df[(df['timestamp'].dt.date >= date_range[0]) & 
                   (df['timestamp'].dt.date <= date_range[1])]
    
    # Load batch processing results for ISPA analysis
    try:
        batch_processor = BatchProcessor()
        ispa_analysis = batch_processor.analyze_ispa_correlation(df)
    except Exception as e:
        logger.error(f"Error loading ISPA analysis: {e}")
        ispa_analysis = {}
    
    # Generate predictions
    try:
        predictor = ISPARiskPredictor()
        future_predictions = predictor.predict_future_risk(df, days_ahead=7)
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        future_predictions = pd.DataFrame()
    
    # Main content
    st.markdown("---")
    
    # Key metrics
    st.subheader("📊 Current Status")
    
    # Get latest data
    if selected_location != 'All':
        df_filtered = df[df['location'] == selected_location]
    else:
        df_filtered = df
    
    if not df_filtered.empty:
        latest = df_filtered.sort_values('timestamp').iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            aqi_value = latest.get('aqi', 0)
            st.metric(
                label="Air Quality Index",
                value=f"{aqi_value:.0f}",
                delta=None
            )
        
        with col2:
            pm25_value = latest.get('pm2_5', 0)
            st.metric(
                label="PM2.5 (μg/m³)",
                value=f"{pm25_value:.1f}",
                delta=None
            )
        
        with col3:
            risk_cat = latest.get('risk_category', 'unknown')
            st.metric(
                label="Risk Category",
                value=risk_cat.replace('_', ' ').title(),
                delta=None
            )
        
        with col4:
            temp = latest.get('temp_c', 0)
            st.metric(
                label="Temperature (°C)",
                value=f"{temp:.1f}",
                delta=None
            )
    
    st.markdown("---")
    
    # Visualizations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Time Series", 
        "🔍 Pollutants", 
        "🌡️ Weather Impact", 
        "📍 Locations",
        "🏭 Kota Terpolusi",
        "🔮 Prediksi ISPA"
    ])
    
    with tab1:
        st.subheader("AQI Time Series")
        plot_aqi_timeseries(df, selected_location)
        
        st.subheader("Risk Distribution")
        plot_risk_distribution(df_filtered)
    
    with tab2:
        st.subheader("Pollutant Levels")
        if selected_location != 'All':
            plot_pollutants_comparison(df, selected_location)
        else:
            st.info("Please select a specific location to view pollutant comparison")
    
    with tab3:
        st.subheader("Weather Correlation Analysis")
        plot_weather_correlation(df_filtered)
    
    with tab4:
        st.subheader("Location Comparison")
        plot_location_comparison(df)
    
    with tab5:
        st.subheader("Kota dengan Tingkat Polusi Tertinggi")
        plot_highest_pollution_cities(df)
        
        if ispa_analysis:
            st.markdown("---")
            plot_ispa_correlation(df, ispa_analysis)
    
    with tab6:
        if not future_predictions.empty:
            plot_future_predictions(future_predictions)
        else:
            st.info("⚠️ Prediksi tidak tersedia. Pastikan ada cukup data historis.")
    
    # Data table
    st.markdown("---")
    st.subheader("📋 Raw Data")
    
    with st.expander("View Data Table"):
        display_cols = ['timestamp', 'location', 'aqi', 'pm2_5', 'pm10', 
                       'temp_c', 'humidity', 'risk_category']
        available_cols = [col for col in display_cols if col in df_filtered.columns]
        st.dataframe(df_filtered[available_cols].sort_values('timestamp', ascending=False))
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Data Pipeline & Infrastructure Project - Monitoring Kualitas Udara & Risiko ISPA</p>
        <p>Data sources: OpenWeatherMap API, WeatherAPI, BMKG, Kemenkes</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
