"""
Data Transformation Module
Cleaning, joining, dan transformasi data
"""
import pandas as pd
import numpy as np
from datetime import datetime
import json
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATA_PATHS, RISK_THRESHOLDS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataTransformation:
    """Class untuk transformasi dan cleaning data"""
    
    def __init__(self):
        self.data_paths = DATA_PATHS
        self.risk_thresholds = RISK_THRESHOLDS
    
    def clean_api_data(self, pollution_data, weather_data):
        """
        Clean dan transform data dari API
        
        Args:
            pollution_data: list of pollution dictionaries
            weather_data: list of weather dictionaries
            
        Returns:
            tuple: (pollution_df, weather_df)
        """
        # Convert to dataframes
        pollution_df = pd.DataFrame(pollution_data)
        weather_df = pd.DataFrame(weather_data)
        
        # Clean pollution data
        if not pollution_df.empty:
            pollution_df['timestamp'] = pd.to_datetime(pollution_df['timestamp'])
            # Remove duplicates
            pollution_df = pollution_df.drop_duplicates(subset=['location', 'timestamp'])
            # Handle missing values (fill with 0 or mean)
            numeric_cols = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']
            for col in numeric_cols:
                if col in pollution_df.columns:
                    pollution_df[col] = pollution_df[col].fillna(pollution_df[col].mean())
        
        # Clean weather data
        if not weather_df.empty:
            weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
            # Remove duplicates
            weather_df = weather_df.drop_duplicates(subset=['location', 'timestamp'])
            # Handle missing values
            numeric_cols = ['temp_c', 'humidity', 'wind_kph', 'pressure_mb']
            for col in numeric_cols:
                if col in weather_df.columns:
                    weather_df[col] = weather_df[col].fillna(weather_df[col].mean())
        
        logger.info(f"Cleaned API data - Pollution: {len(pollution_df)} rows, Weather: {len(weather_df)} rows")
        return pollution_df, weather_df
    
    def add_risk_category(self, df):
        """
        Menambahkan kategori risiko berdasarkan AQI
        
        Args:
            df: dataframe with 'aqi' column
            
        Returns:
            dataframe with 'risk_category' column
        """
        if 'aqi' not in df.columns:
            logger.warning("No AQI column found, skipping risk category")
            return df
        
        def categorize_aqi(aqi):
            if pd.isna(aqi):
                return 'unknown'
            for category, (low, high) in self.risk_thresholds.items():
                if low <= aqi <= high:
                    return category
            return 'hazardous'
        
        df['risk_category'] = df['aqi'].apply(categorize_aqi)
        
        # Add risk score (0-5)
        risk_mapping = {
            'good': 0,
            'moderate': 1,
            'unhealthy_sensitive': 2,
            'unhealthy': 3,
            'very_unhealthy': 4,
            'hazardous': 5,
            'unknown': -1
        }
        df['risk_score'] = df['risk_category'].map(risk_mapping)
        
        logger.info("Added risk categories and scores")
        return df
    
    def join_pollution_weather(self, pollution_df, weather_df):
        """
        Join data polusi dengan data cuaca berdasarkan location dan timestamp
        
        Args:
            pollution_df: pollution dataframe
            weather_df: weather dataframe
            
        Returns:
            merged dataframe
        """
        if pollution_df.empty or weather_df.empty:
            logger.warning("One or both dataframes are empty, cannot join")
            return pd.DataFrame()
        
        # Round timestamps to nearest hour untuk matching
        pollution_df['timestamp_hour'] = pollution_df['timestamp'].dt.floor('H')
        weather_df['timestamp_hour'] = weather_df['timestamp'].dt.floor('H')
        
        # Merge on location and timestamp_hour
        merged_df = pd.merge(
            pollution_df,
            weather_df,
            on=['location', 'timestamp_hour'],
            how='inner',
            suffixes=('_pollution', '_weather')
        )
        
        # Keep the pollution timestamp as main timestamp
        if 'timestamp_pollution' in merged_df.columns:
            merged_df['timestamp'] = merged_df['timestamp_pollution']
            merged_df = merged_df.drop(['timestamp_pollution', 'timestamp_weather', 'timestamp_hour'], axis=1)
        
        logger.info(f"Joined pollution and weather data: {len(merged_df)} rows")
        return merged_df
    
    def clean_kualitas_udara_csv(self, df):
        """Clean dataset kualitas udara historis"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.dropna(how='all')  # Drop rows with all NaN
        
        # Convert numeric columns
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        
        logger.info(f"Cleaned kualitas udara CSV: {len(df_clean)} rows")
        return df_clean
    
    def clean_suhu_kelembaban_csv(self, df):
        """Clean dataset suhu dan kelembaban"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        df_clean = df.copy()
        
        # Remove rows with all NaN
        df_clean = df_clean.dropna(how='all')
        
        # Fill missing values with forward fill then backward fill
        df_clean = df_clean.ffill().bfill()
        
        logger.info(f"Cleaned suhu kelembaban CSV: {len(df_clean)} rows")
        return df_clean
    
    def clean_tekanan_angin_csv(self, df):
        """Clean dataset tekanan udara dan angin"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        df_clean = df.copy()
        
        # Remove rows with all NaN
        df_clean = df_clean.dropna(how='all')
        
        # Fill missing values
        df_clean = df_clean.ffill().bfill()
        
        logger.info(f"Cleaned tekanan angin CSV: {len(df_clean)} rows")
        return df_clean
    
    def clean_ispa_csv(self, df):
        """Clean dataset kasus ISPA"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        df_clean = df.copy()
        
        # Remove rows with all NaN
        df_clean = df_clean.dropna(how='all')
        
        # Fill missing numeric values with 0 (assuming no cases reported)
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df_clean[col] = df_clean[col].fillna(0)
        
        logger.info(f"Cleaned ISPA CSV: {len(df_clean)} rows")
        return df_clean
    
    def aggregate_daily_data(self, df):
        """
        Agregasi data per hari
        
        Args:
            df: dataframe with timestamp column
            
        Returns:
            aggregated dataframe
        """
        if df.empty or 'timestamp' not in df.columns:
            logger.warning("Cannot aggregate - empty dataframe or no timestamp")
            return df
        
        # Extract date
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Group by date and location
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        agg_dict = {}
        for col in numeric_cols:
            if col not in ['lat', 'lon']:
                agg_dict[col] = ['mean', 'max', 'min', 'std']
        
        if 'location' in df.columns:
            aggregated = df.groupby(['date', 'location']).agg(agg_dict).reset_index()
        else:
            aggregated = df.groupby('date').agg(agg_dict).reset_index()
        
        # Flatten column names
        aggregated.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                              for col in aggregated.columns.values]
        
        logger.info(f"Aggregated data to daily: {len(aggregated)} rows")
        return aggregated
    
    def create_features(self, df):
        """
        Create additional features untuk modeling
        
        Args:
            df: dataframe
            
        Returns:
            dataframe with new features
        """
        df_features = df.copy()
        
        # Time-based features
        if 'timestamp' in df_features.columns:
            df_features['timestamp'] = pd.to_datetime(df_features['timestamp'])
            df_features['hour'] = df_features['timestamp'].dt.hour
            df_features['day_of_week'] = df_features['timestamp'].dt.dayofweek
            df_features['month'] = df_features['timestamp'].dt.month
            df_features['is_weekend'] = df_features['day_of_week'].isin([5, 6]).astype(int)
        
        # Pollution features
        if 'pm2_5' in df_features.columns and 'pm10' in df_features.columns:
            df_features['pm_ratio'] = df_features['pm2_5'] / (df_features['pm10'] + 1)
        
        # Weather features
        if 'temp_c' in df_features.columns and 'humidity' in df_features.columns:
            # Heat index approximation
            df_features['heat_index'] = df_features['temp_c'] + (0.5 * df_features['humidity'] / 100)
        
        logger.info(f"Created additional features")
        return df_features
    
    def save_processed_data(self, df, filename):
        """
        Save processed data ke CSV
        
        Args:
            df: dataframe to save
            filename: output filename
        """
        output_path = self.data_paths['processed'] / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Saved processed data to {output_path}")
        return output_path
    
    def transform_all(self, api_data, csv_datasets):
        """
        Jalankan semua transformasi
        
        Args:
            api_data: dict with 'pollution' and 'weather' keys
            csv_datasets: dict of CSV dataframes
            
        Returns:
            dict of transformed dataframes
        """
        logger.info("Starting data transformation...")
        
        transformed = {}
        
        # Transform API data
        pollution_df, weather_df = self.clean_api_data(
            api_data.get('pollution', []),
            api_data.get('weather', [])
        )
        
        # Add risk categories
        pollution_df = self.add_risk_category(pollution_df)
        
        # Join pollution and weather
        merged_df = self.join_pollution_weather(pollution_df, weather_df)
        
        # Create features
        if not merged_df.empty:
            merged_df = self.create_features(merged_df)
            transformed['real_time_data'] = merged_df
            
            # Save
            self.save_processed_data(merged_df, 'real_time_merged.csv')
        
        # Clean CSV datasets
        if 'kualitas_udara' in csv_datasets:
            transformed['kualitas_udara'] = self.clean_kualitas_udara_csv(
                csv_datasets['kualitas_udara']
            )
            self.save_processed_data(
                transformed['kualitas_udara'], 
                'kualitas_udara_clean.csv'
            )
        
        if 'suhu_kelembaban' in csv_datasets:
            transformed['suhu_kelembaban'] = self.clean_suhu_kelembaban_csv(
                csv_datasets['suhu_kelembaban']
            )
            self.save_processed_data(
                transformed['suhu_kelembaban'], 
                'suhu_kelembaban_clean.csv'
            )
        
        if 'tekanan_angin' in csv_datasets:
            transformed['tekanan_angin'] = self.clean_tekanan_angin_csv(
                csv_datasets['tekanan_angin']
            )
            self.save_processed_data(
                transformed['tekanan_angin'], 
                'tekanan_angin_clean.csv'
            )
        
        if 'kasus_ispa' in csv_datasets:
            transformed['kasus_ispa'] = self.clean_ispa_csv(
                csv_datasets['kasus_ispa']
            )
            self.save_processed_data(
                transformed['kasus_ispa'], 
                'kasus_ispa_clean.csv'
            )
        
        logger.info("Data transformation completed!")
        return transformed


if __name__ == "__main__":
    # Test transformation module
    print("Testing transformation module...")
    print("Run this through the main pipeline for complete testing")
