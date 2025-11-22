"""
Database Storage Module
Koneksi dan operasi database untuk PostgreSQL dan MongoDB
"""
import psycopg2
from psycopg2.extras import execute_values
import pymongo
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
import logging
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PostgreSQLStorage:
    """Class untuk handle PostgreSQL operations"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG['postgresql']
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            self.cursor = self.conn.cursor()
            logger.info("Connected to PostgreSQL successfully")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables"""
        try:
            # Table untuk real-time air pollution data
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS air_pollution (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    lat FLOAT,
                    lon FLOAT,
                    aqi INTEGER,
                    co FLOAT,
                    no FLOAT,
                    no2 FLOAT,
                    o3 FLOAT,
                    so2 FLOAT,
                    pm2_5 FLOAT,
                    pm10 FLOAT,
                    nh3 FLOAT,
                    risk_category VARCHAR(50),
                    risk_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table untuk weather data
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    temp_c FLOAT,
                    humidity INTEGER,
                    wind_kph FLOAT,
                    wind_degree INTEGER,
                    wind_dir VARCHAR(10),
                    pressure_mb FLOAT,
                    precip_mm FLOAT,
                    cloud INTEGER,
                    visibility_km FLOAT,
                    uv FLOAT,
                    condition VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table untuk merged data (untuk analisis)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS merged_data (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    aqi INTEGER,
                    pm2_5 FLOAT,
                    pm10 FLOAT,
                    temp_c FLOAT,
                    humidity INTEGER,
                    wind_kph FLOAT,
                    pressure_mb FLOAT,
                    risk_category VARCHAR(50),
                    risk_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table untuk daily aggregates
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_aggregates (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    avg_aqi FLOAT,
                    max_aqi FLOAT,
                    avg_pm2_5 FLOAT,
                    max_pm2_5 FLOAT,
                    avg_temp FLOAT,
                    avg_humidity FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, location)
                )
            """)
            
            self.conn.commit()
            logger.info("Tables created successfully")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error creating tables: {e}")
            self.conn.rollback()
            return False
    
    def insert_pollution_data(self, df):
        """Insert pollution data from dataframe"""
        try:
            data = df[['timestamp', 'location', 'lat', 'lon', 'aqi', 'co', 'no', 
                      'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3', 
                      'risk_category', 'risk_score']].values.tolist()
            
            query = """
                INSERT INTO air_pollution 
                (timestamp, location, lat, lon, aqi, co, no, no2, o3, so2, 
                 pm2_5, pm10, nh3, risk_category, risk_score)
                VALUES %s
                ON CONFLICT DO NOTHING
            """
            
            execute_values(self.cursor, query, data)
            self.conn.commit()
            logger.info(f"Inserted {len(data)} pollution records")
            return True
        except Exception as e:
            logger.error(f"Error inserting pollution data: {e}")
            self.conn.rollback()
            return False
    
    def insert_weather_data(self, df):
        """Insert weather data from dataframe"""
        try:
            data = df[['timestamp', 'location', 'temp_c', 'humidity', 'wind_kph',
                      'wind_degree', 'wind_dir', 'pressure_mb', 'precip_mm',
                      'cloud', 'visibility_km', 'uv', 'condition']].values.tolist()
            
            query = """
                INSERT INTO weather_data 
                (timestamp, location, temp_c, humidity, wind_kph, wind_degree,
                 wind_dir, pressure_mb, precip_mm, cloud, visibility_km, uv, condition)
                VALUES %s
                ON CONFLICT DO NOTHING
            """
            
            execute_values(self.cursor, query, data)
            self.conn.commit()
            logger.info(f"Inserted {len(data)} weather records")
            return True
        except Exception as e:
            logger.error(f"Error inserting weather data: {e}")
            self.conn.rollback()
            return False
    
    def insert_merged_data(self, df):
        """Insert merged data from dataframe"""
        try:
            required_cols = ['timestamp', 'location', 'aqi', 'pm2_5', 'pm10',
                           'temp_c', 'humidity', 'wind_kph', 'pressure_mb',
                           'risk_category', 'risk_score']
            
            data = df[required_cols].values.tolist()
            
            query = """
                INSERT INTO merged_data 
                (timestamp, location, aqi, pm2_5, pm10, temp_c, humidity,
                 wind_kph, pressure_mb, risk_category, risk_score)
                VALUES %s
                ON CONFLICT DO NOTHING
            """
            
            execute_values(self.cursor, query, data)
            self.conn.commit()
            logger.info(f"Inserted {len(data)} merged records")
            return True
        except Exception as e:
            logger.error(f"Error inserting merged data: {e}")
            self.conn.rollback()
            return False
    
    def get_latest_data(self, table_name, limit=100):
        """Get latest data from a table"""
        try:
            query = f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT {limit}"
            df = pd.read_sql(query, self.conn)
            logger.info(f"Retrieved {len(df)} records from {table_name}")
            return df
        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("PostgreSQL connection closed")


class MongoDBStorage:
    """Class untuk handle MongoDB operations"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG['mongodb']
        self.client = None
        self.db = None
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                host=self.config['host'],
                port=self.config['port']
            )
            self.db = self.client[self.config['database']]
            # Test connection
            self.client.server_info()
            logger.info("Connected to MongoDB successfully")
            return True
        except pymongo.errors.ConnectionError as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            return False
    
    def insert_pollution_data(self, data_list):
        """Insert pollution data (list of dicts)"""
        try:
            collection = self.db['air_pollution']
            if isinstance(data_list, list) and len(data_list) > 0:
                result = collection.insert_many(data_list)
                logger.info(f"Inserted {len(result.inserted_ids)} pollution records to MongoDB")
                return True
            return False
        except Exception as e:
            logger.error(f"Error inserting pollution data to MongoDB: {e}")
            return False
    
    def insert_weather_data(self, data_list):
        """Insert weather data (list of dicts)"""
        try:
            collection = self.db['weather_data']
            if isinstance(data_list, list) and len(data_list) > 0:
                result = collection.insert_many(data_list)
                logger.info(f"Inserted {len(result.inserted_ids)} weather records to MongoDB")
                return True
            return False
        except Exception as e:
            logger.error(f"Error inserting weather data to MongoDB: {e}")
            return False
    
    def insert_dataframe(self, df, collection_name):
        """Insert dataframe to MongoDB collection"""
        try:
            collection = self.db[collection_name]
            records = json.loads(df.to_json(orient='records', date_format='iso'))
            if len(records) > 0:
                result = collection.insert_many(records)
                logger.info(f"Inserted {len(result.inserted_ids)} records to {collection_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error inserting dataframe to MongoDB: {e}")
            return False
    
    def get_latest_data(self, collection_name, limit=100):
        """Get latest data from collection"""
        try:
            collection = self.db[collection_name]
            cursor = collection.find().sort('timestamp', -1).limit(limit)
            data = list(cursor)
            df = pd.DataFrame(data)
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            logger.info(f"Retrieved {len(df)} records from {collection_name}")
            return df
        except Exception as e:
            logger.error(f"Error retrieving data from MongoDB: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
        logger.info("MongoDB connection closed")


class DataStorage:
    """Unified storage interface"""
    
    def __init__(self, use_postgres=True, use_mongodb=True):
        self.use_postgres = use_postgres
        self.use_mongodb = use_mongodb
        self.postgres = None
        self.mongodb = None
        
        if use_postgres:
            self.postgres = PostgreSQLStorage()
        if use_mongodb:
            self.mongodb = MongoDBStorage()
    
    def connect_all(self):
        """Connect to all databases"""
        success = True
        
        if self.use_postgres:
            if self.postgres.connect():
                self.postgres.create_tables()
            else:
                success = False
                logger.warning("PostgreSQL connection failed")
        
        if self.use_mongodb:
            if not self.mongodb.connect():
                success = False
                logger.warning("MongoDB connection failed")
        
        return success
    
    def store_all_data(self, transformed_data):
        """Store all transformed data"""
        logger.info("Storing data to databases...")
        
        real_time_data = transformed_data.get('real_time_data')
        
        if real_time_data is not None and not real_time_data.empty:
            if self.use_postgres and self.postgres:
                self.postgres.insert_merged_data(real_time_data)
            
            if self.use_mongodb and self.mongodb:
                self.mongodb.insert_dataframe(real_time_data, 'real_time_merged')
        
        logger.info("Data storage completed!")
    
    def close_all(self):
        """Close all database connections"""
        if self.postgres:
            self.postgres.close()
        if self.mongodb:
            self.mongodb.close()


if __name__ == "__main__":
    # Test storage module
    print("Testing storage module...")
    print("Note: Make sure PostgreSQL and/or MongoDB are running")
    
    storage = DataStorage(use_postgres=True, use_mongodb=True)
    if storage.connect_all():
        print("Successfully connected to databases!")
        storage.close_all()
    else:
        print("Failed to connect to one or more databases")
