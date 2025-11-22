"""
Data Ingestion Module
Fetch data dari API real-time dan load data dari CSV
"""
import requests
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import (
    OPENWEATHER_API_KEY, WEATHERAPI_KEY,
    OPENWEATHER_POLLUTION_URL, WEATHERAPI_URL,
    CITIES, CSV_FILES, DATA_PATHS
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataIngestion:
    """Class untuk menghandle data ingestion dari berbagai sumber"""
    
    def __init__(self):
        self.data_paths = DATA_PATHS
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Memastikan semua direktori yang diperlukan ada"""
        for path in self.data_paths.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def fetch_air_pollution_data(self, lat, lon, location_name):
        """
        Fetch data polusi udara dari OpenWeatherMap API
        
        Args:
            lat: latitude
            lon: longitude
            location_name: nama lokasi
            
        Returns:
            dict: data polusi udara
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': OPENWEATHER_API_KEY
            }
            
            response = requests.get(OPENWEATHER_POLLUTION_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            if 'list' in data and len(data['list']) > 0:
                pollution_data = data['list'][0]
                
                result = {
                    'timestamp': datetime.now().isoformat(),
                    'location': location_name,
                    'lat': lat,
                    'lon': lon,
                    'aqi': pollution_data['main']['aqi'],
                    'co': pollution_data['components']['co'],
                    'no': pollution_data['components']['no'],
                    'no2': pollution_data['components']['no2'],
                    'o3': pollution_data['components']['o3'],
                    'so2': pollution_data['components']['so2'],
                    'pm2_5': pollution_data['components']['pm2_5'],
                    'pm10': pollution_data['components']['pm10'],
                    'nh3': pollution_data['components']['nh3']
                }
                
                logger.info(f"Successfully fetched air pollution data for {location_name}")
                return result
            else:
                logger.warning(f"No pollution data available for {location_name}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching air pollution data for {location_name}: {e}")
            return None
    
    def fetch_weather_data(self, location_name):
        """
        Fetch data cuaca dari WeatherAPI
        
        Args:
            location_name: nama lokasi
            
        Returns:
            dict: data cuaca
        """
        try:
            params = {
                'key': WEATHERAPI_KEY,
                'q': location_name,
                'aqi': 'no'
            }
            
            response = requests.get(WEATHERAPI_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'location': location_name,
                'temp_c': data['current']['temp_c'],
                'temp_f': data['current']['temp_f'],
                'humidity': data['current']['humidity'],
                'wind_kph': data['current']['wind_kph'],
                'wind_degree': data['current']['wind_degree'],
                'wind_dir': data['current']['wind_dir'],
                'pressure_mb': data['current']['pressure_mb'],
                'precip_mm': data['current']['precip_mm'],
                'cloud': data['current']['cloud'],
                'feelslike_c': data['current']['feelslike_c'],
                'visibility_km': data['current']['vis_km'],
                'uv': data['current']['uv'],
                'condition': data['current']['condition']['text']
            }
            
            logger.info(f"Successfully fetched weather data for {location_name}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data for {location_name}: {e}")
            return None
    
    def fetch_all_cities_data(self):
        """
        Fetch data untuk semua kota yang sudah didefinisikan
        
        Returns:
            tuple: (pollution_data_list, weather_data_list)
        """
        pollution_data = []
        weather_data = []
        
        for city in CITIES:
            logger.info(f"Fetching data for {city['name']}...")
            
            # Fetch pollution data
            pollution = self.fetch_air_pollution_data(
                city['lat'], 
                city['lon'], 
                city['name']
            )
            if pollution:
                pollution_data.append(pollution)
            
            # Fetch weather data
            weather = self.fetch_weather_data(city['name'])
            if weather:
                weather_data.append(weather)
        
        return pollution_data, weather_data
    
    def save_api_data_to_json(self, pollution_data, weather_data):
        """
        Save data dari API ke JSON files
        
        Args:
            pollution_data: list of pollution data dicts
            weather_data: list of weather data dicts
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save pollution data
        pollution_file = self.data_paths['raw'] / f'air_pollution_{timestamp}.json'
        with open(pollution_file, 'w') as f:
            json.dump(pollution_data, f, indent=2)
        logger.info(f"Saved pollution data to {pollution_file}")
        
        # Save weather data
        weather_file = self.data_paths['raw'] / f'weather_{timestamp}.json'
        with open(weather_file, 'w') as f:
            json.dump(weather_data, f, indent=2)
        logger.info(f"Saved weather data to {weather_file}")
        
        return pollution_file, weather_file
    
    def load_csv_datasets(self):
        """
        Load semua CSV datasets yang tersedia
        
        Returns:
            dict: dictionary of dataframes
        """
        datasets = {}
        
        for name, filepath in CSV_FILES.items():
            try:
                if filepath.exists():
                    df = pd.read_csv(filepath)
                    datasets[name] = df
                    logger.info(f"Loaded {name} dataset: {df.shape[0]} rows, {df.shape[1]} columns")
                else:
                    logger.warning(f"File not found: {filepath}")
            except Exception as e:
                logger.error(f"Error loading {name}: {e}")
        
        return datasets
    
    def run_ingestion(self):
        """
        Menjalankan seluruh proses ingestion
        
        Returns:
            dict: hasil ingestion
        """
        logger.info("Starting data ingestion process...")
        
        # Fetch API data
        pollution_data, weather_data = self.fetch_all_cities_data()
        
        # Save API data
        pollution_file, weather_file = self.save_api_data_to_json(
            pollution_data, 
            weather_data
        )
        
        # Load CSV datasets
        csv_datasets = self.load_csv_datasets()
        
        result = {
            'api_data': {
                'pollution': pollution_data,
                'weather': weather_data,
                'pollution_file': str(pollution_file),
                'weather_file': str(weather_file)
            },
            'csv_datasets': csv_datasets,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Data ingestion completed successfully!")
        return result


if __name__ == "__main__":
    # Test the ingestion module
    ingestion = DataIngestion()
    result = ingestion.run_ingestion()
    
    print("\n=== Ingestion Summary ===")
    print(f"Pollution data points: {len(result['api_data']['pollution'])}")
    print(f"Weather data points: {len(result['api_data']['weather'])}")
    print(f"\nCSV Datasets loaded:")
    for name, df in result['csv_datasets'].items():
        print(f"  - {name}: {df.shape}")
