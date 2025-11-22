"""
Utility functions untuk project
"""
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def convert_timestamp(timestamp_str):
    """Convert string timestamp to datetime"""
    try:
        return pd.to_datetime(timestamp_str)
    except Exception as e:
        logger.error(f"Error converting timestamp: {e}")
        return None


def calculate_aqi_category(aqi):
    """Calculate AQI category from AQI value"""
    if aqi <= 50:
        return "good"
    elif aqi <= 100:
        return "moderate"
    elif aqi <= 150:
        return "unhealthy_sensitive"
    elif aqi <= 200:
        return "unhealthy"
    elif aqi <= 300:
        return "very_unhealthy"
    else:
        return "hazardous"


def format_number(number, decimal_places=2):
    """Format number with specified decimal places"""
    try:
        return round(float(number), decimal_places)
    except:
        return 0.0


def create_timestamp():
    """Create current timestamp string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
