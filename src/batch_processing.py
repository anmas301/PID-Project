"""
Batch Processing Module
Agregasi harian dan batch processing untuk analisis data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATA_PATHS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """Class untuk batch processing dan agregasi"""
    
    def __init__(self):
        self.data_paths = DATA_PATHS
    
    def aggregate_daily(self, df):
        """
        Agregasi data menjadi daily averages
        
        Args:
            df: dataframe with timestamp column
            
        Returns:
            aggregated dataframe
        """
        if df.empty or 'timestamp' not in df.columns:
            logger.warning("Cannot aggregate - empty dataframe or no timestamp")
            return pd.DataFrame()
        
        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['timestamp']).dt.date
        
        # Define aggregation functions
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove lat/lon from aggregation if present
        agg_cols = [col for col in numeric_cols if col not in ['lat', 'lon']]
        
        agg_dict = {}
        for col in agg_cols:
            agg_dict[col] = ['mean', 'max', 'min', 'std']
        
        # Group by date and location if location exists
        if 'location' in df_copy.columns:
            grouped = df_copy.groupby(['date', 'location']).agg(agg_dict)
        else:
            grouped = df_copy.groupby('date').agg(agg_dict)
        
        # Flatten column names
        grouped.columns = ['_'.join(col).strip('_') for col in grouped.columns.values]
        grouped = grouped.reset_index()
        
        logger.info(f"Aggregated to daily: {len(grouped)} rows")
        return grouped
    
    def aggregate_weekly(self, df):
        """
        Agregasi data menjadi weekly averages
        
        Args:
            df: dataframe with timestamp column
            
        Returns:
            aggregated dataframe
        """
        if df.empty or 'timestamp' not in df.columns:
            logger.warning("Cannot aggregate - empty dataframe or no timestamp")
            return pd.DataFrame()
        
        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
        df_copy['week'] = df_copy['timestamp'].dt.isocalendar().week
        df_copy['year'] = df_copy['timestamp'].dt.year
        
        # Define aggregation
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns.tolist()
        agg_cols = [col for col in numeric_cols if col not in ['lat', 'lon', 'week', 'year']]
        
        agg_dict = {col: ['mean', 'max', 'min'] for col in agg_cols}
        
        if 'location' in df_copy.columns:
            grouped = df_copy.groupby(['year', 'week', 'location']).agg(agg_dict)
        else:
            grouped = df_copy.groupby(['year', 'week']).agg(agg_dict)
        
        grouped.columns = ['_'.join(col).strip('_') for col in grouped.columns.values]
        grouped = grouped.reset_index()
        
        logger.info(f"Aggregated to weekly: {len(grouped)} rows")
        return grouped
    
    def aggregate_monthly(self, df):
        """
        Agregasi data menjadi monthly averages
        
        Args:
            df: dataframe with timestamp column
            
        Returns:
            aggregated dataframe
        """
        if df.empty or 'timestamp' not in df.columns:
            logger.warning("Cannot aggregate - empty dataframe or no timestamp")
            return pd.DataFrame()
        
        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
        df_copy['month'] = df_copy['timestamp'].dt.month
        df_copy['year'] = df_copy['timestamp'].dt.year
        
        # Define aggregation
        numeric_cols = df_copy.select_dtypes(include=[np.number]).columns.tolist()
        agg_cols = [col for col in numeric_cols if col not in ['lat', 'lon', 'month', 'year']]
        
        agg_dict = {col: ['mean', 'max', 'min'] for col in agg_cols}
        
        if 'location' in df_copy.columns:
            grouped = df_copy.groupby(['year', 'month', 'location']).agg(agg_dict)
        else:
            grouped = df_copy.groupby(['year', 'month']).agg(agg_dict)
        
        grouped.columns = ['_'.join(col).strip('_') for col in grouped.columns.values]
        grouped = grouped.reset_index()
        
        logger.info(f"Aggregated to monthly: {len(grouped)} rows")
        return grouped
    
    def calculate_statistics(self, df, group_by='location'):
        """
        Calculate comprehensive statistics
        
        Args:
            df: dataframe
            group_by: column to group by
            
        Returns:
            statistics dataframe
        """
        if df.empty:
            return pd.DataFrame()
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        stats_list = []
        
        if group_by in df.columns:
            for group_value in df[group_by].unique():
                group_df = df[df[group_by] == group_value]
                
                stats = {'group': group_value}
                for col in numeric_cols:
                    if col in group_df.columns:
                        stats[f'{col}_mean'] = group_df[col].mean()
                        stats[f'{col}_median'] = group_df[col].median()
                        stats[f'{col}_std'] = group_df[col].std()
                        stats[f'{col}_min'] = group_df[col].min()
                        stats[f'{col}_max'] = group_df[col].max()
                
                stats_list.append(stats)
        else:
            # Overall statistics
            stats = {'group': 'all'}
            for col in numeric_cols:
                if col in df.columns:
                    stats[f'{col}_mean'] = df[col].mean()
                    stats[f'{col}_median'] = df[col].median()
                    stats[f'{col}_std'] = df[col].std()
                    stats[f'{col}_min'] = df[col].min()
                    stats[f'{col}_max'] = df[col].max()
            stats_list.append(stats)
        
        stats_df = pd.DataFrame(stats_list)
        logger.info(f"Calculated statistics for {len(stats_df)} groups")
        return stats_df
    
    def identify_trends(self, df, target_col='aqi'):
        """
        Identify trends in time series data
        
        Args:
            df: dataframe with timestamp
            target_col: column to analyze
            
        Returns:
            trend analysis dict
        """
        if df.empty or 'timestamp' not in df.columns or target_col not in df.columns:
            logger.warning("Cannot identify trends - missing required columns")
            return {}
        
        df_sorted = df.sort_values('timestamp').copy()
        df_sorted['timestamp'] = pd.to_datetime(df_sorted['timestamp'])
        
        # Calculate rolling averages
        df_sorted['rolling_7d'] = df_sorted[target_col].rolling(window=7, min_periods=1).mean()
        df_sorted['rolling_30d'] = df_sorted[target_col].rolling(window=30, min_periods=1).mean()
        
        # Calculate trend (linear regression coefficient)
        from sklearn.linear_model import LinearRegression
        
        X = np.arange(len(df_sorted)).reshape(-1, 1)
        y = df_sorted[target_col].values
        
        # Remove NaN values
        valid_idx = ~np.isnan(y)
        X_valid = X[valid_idx]
        y_valid = y[valid_idx]
        
        if len(X_valid) > 1:
            model = LinearRegression()
            model.fit(X_valid, y_valid)
            trend_coefficient = model.coef_[0]
            
            trend_direction = 'increasing' if trend_coefficient > 0 else 'decreasing'
            trend_strength = abs(trend_coefficient)
        else:
            trend_direction = 'unknown'
            trend_strength = 0
        
        result = {
            'target_column': target_col,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'current_value': df_sorted[target_col].iloc[-1] if len(df_sorted) > 0 else None,
            'mean_value': df_sorted[target_col].mean(),
            'median_value': df_sorted[target_col].median(),
            'data_points': len(df_sorted)
        }
        
        logger.info(f"Identified trend for {target_col}: {trend_direction}")
        return result
    
    def detect_anomalies(self, df, target_col='aqi', threshold=3):
        """
        Detect anomalies using z-score method
        
        Args:
            df: dataframe
            target_col: column to check for anomalies
            threshold: z-score threshold (default 3)
            
        Returns:
            dataframe with anomalies marked
        """
        if df.empty or target_col not in df.columns:
            logger.warning("Cannot detect anomalies - missing target column")
            return df
        
        df_copy = df.copy()
        
        # Calculate z-score
        mean = df_copy[target_col].mean()
        std = df_copy[target_col].std()
        
        if std > 0:
            df_copy['z_score'] = (df_copy[target_col] - mean) / std
            df_copy['is_anomaly'] = df_copy['z_score'].abs() > threshold
            
            anomaly_count = df_copy['is_anomaly'].sum()
            logger.info(f"Detected {anomaly_count} anomalies in {target_col}")
        else:
            df_copy['z_score'] = 0
            df_copy['is_anomaly'] = False
            logger.info("No anomalies detected (std=0)")
        
        return df_copy
    
    def analyze_ispa_correlation(self, df, ispa_data=None):
        """
        Analyze correlation between air quality and ISPA cases
        
        Args:
            df: air quality dataframe
            ispa_data: ISPA cases dataframe (optional)
            
        Returns:
            correlation analysis dict
        """
        if df.empty:
            return {}
        
        logger.info("Analyzing ISPA correlation with air quality...")
        
        analysis = {
            'high_risk_locations': [],
            'pollution_ispa_correlation': {},
            'recommendations': []
        }
        
        # Identify high pollution areas
        if 'location' in df.columns and 'aqi' in df.columns:
            location_avg_aqi = df.groupby('location')['aqi'].mean().sort_values(ascending=False)
            
            for location, aqi in location_avg_aqi.items():
                risk_level = 'Low'
                if aqi > 100:
                    risk_level = 'High'
                elif aqi > 50:
                    risk_level = 'Moderate'
                
                analysis['high_risk_locations'].append({
                    'location': location,
                    'avg_aqi': float(aqi),
                    'risk_level': risk_level
                })
        
        # Calculate correlations between pollutants and health metrics
        pollutant_cols = ['aqi', 'pm2_5', 'pm10', 'co', 'no2', 'o3', 'so2']
        weather_cols = ['temp_c', 'humidity', 'wind_kph']
        
        available_pollutants = [col for col in pollutant_cols if col in df.columns]
        available_weather = [col for col in weather_cols if col in df.columns]
        
        if available_pollutants and available_weather:
            # Calculate synthetic ISPA risk based on pollution
            df['synthetic_ispa_risk'] = 0
            if 'aqi' in df.columns:
                df['synthetic_ispa_risk'] += df['aqi'] * 0.3
            if 'pm2_5' in df.columns:
                df['synthetic_ispa_risk'] += df['pm2_5'] * 0.5
            if 'humidity' in df.columns:
                df['synthetic_ispa_risk'] += (df['humidity'] - 50) * 0.2
            
            # Calculate correlations
            for pollutant in available_pollutants:
                if 'synthetic_ispa_risk' in df.columns:
                    corr = df[pollutant].corr(df['synthetic_ispa_risk'])
                    analysis['pollution_ispa_correlation'][pollutant] = float(corr)
        
        # Generate recommendations
        if analysis['high_risk_locations']:
            top_risk = analysis['high_risk_locations'][0]
            if top_risk['avg_aqi'] > 100:
                analysis['recommendations'].append(
                    f"⚠️ {top_risk['location']} memiliki AQI tinggi ({top_risk['avg_aqi']:.1f}). "
                    "Disarankan untuk mengurangi aktivitas outdoor dan menggunakan masker."
                )
            elif top_risk['avg_aqi'] > 50:
                analysis['recommendations'].append(
                    f"⚡ {top_risk['location']} memiliki AQI moderat ({top_risk['avg_aqi']:.1f}). "
                    "Kelompok sensitif perlu berhati-hati."
                )
        
        logger.info(f"ISPA correlation analysis completed")
        return analysis
    
    def create_summary_report(self, df):
        """
        Create a summary report of the data
        
        Args:
            df: dataframe
            
        Returns:
            summary dict
        """
        if df.empty:
            return {}
        
        summary = {
            'total_records': len(df),
            'date_range': None,
            'locations': [],
            'numeric_summary': {}
        }
        
        # Date range
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            summary['date_range'] = {
                'start': str(df['timestamp'].min()),
                'end': str(df['timestamp'].max()),
                'days': (df['timestamp'].max() - df['timestamp'].min()).days
            }
        
        # Locations
        if 'location' in df.columns:
            summary['locations'] = df['location'].unique().tolist()
        
        # Numeric summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols:
            summary['numeric_summary'][col] = {
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'std': float(df[col].std())
            }
        
        logger.info("Created summary report")
        return summary
    
    def save_batch_results(self, data_dict, prefix='batch'):
        """
        Save batch processing results
        
        Args:
            data_dict: dict of dataframes
            prefix: prefix for filenames
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, df in data_dict.items():
            if not df.empty:
                filename = f"{prefix}_{name}_{timestamp}.csv"
                filepath = self.data_paths['processed'] / filename
                df.to_csv(filepath, index=False)
                logger.info(f"Saved {name} to {filepath}")
    
    def run_batch_processing(self, df):
        """
        Run complete batch processing
        
        Args:
            df: input dataframe
            
        Returns:
            dict of processed results
        """
        logger.info("Starting batch processing...")
        
        results = {}
        
        # Daily aggregation
        results['daily'] = self.aggregate_daily(df)
        
        # Weekly aggregation
        results['weekly'] = self.aggregate_weekly(df)
        
        # Monthly aggregation
        results['monthly'] = self.aggregate_monthly(df)
        
        # Statistics
        results['statistics'] = self.calculate_statistics(df)
        
        # Anomaly detection
        if 'aqi' in df.columns:
            results['anomalies'] = self.detect_anomalies(df, 'aqi')
            
            # Trend analysis
            trend = self.identify_trends(df, 'aqi')
            results['trend_analysis'] = pd.DataFrame([trend])
        
        # Summary report
        summary = self.create_summary_report(df)
        results['summary'] = summary
        
        # ISPA correlation analysis
        ispa_analysis = self.analyze_ispa_correlation(df)
        results['ispa_correlation'] = ispa_analysis
        
        # Save results
        self.save_batch_results({
            k: v for k, v in results.items() 
            if isinstance(v, pd.DataFrame)
        })
        
        logger.info("Batch processing completed!")
        return results


if __name__ == "__main__":
    # Test batch processor
    print("Testing batch processing module...")
    print("Run this through the main pipeline for complete testing")
