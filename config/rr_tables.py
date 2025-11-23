"""
Tabel Risk Ratio (RR) untuk Model Multiplikatif
Berdasarkan Metodologi Kelompok
"""

# Tabel 1: Faktor Risiko Polusi Udara terhadap ISPA
POLLUTION_RR = {
    'PM2.5': {
        'range': (1.02, 1.07),
        'median': 1.045,
        'source': 'Odo et al. (2022); Monoson et al.'
    },
    'PM10': {
        'range': (1.01, 1.03),
        'median': 1.02,
        'source': 'Monoson et al.'
    },
    'NO2': {
        'range': (1.05, 1.15),
        'median': 1.10,
        'source': 'Monoson et al.; studi kohort'
    },
    'SO2': {
        'range': (1.02, 1.06),
        'median': 1.04,
        'source': 'Monoson et al.'
    },
    'O3': {
        'range': (1.00, 1.02),
        'median': 1.01,
        'source': 'Monoson et al.; analisis time-series'
    }
}

# Tabel 2: Faktor Risiko Cuaca terhadap ISPA
WEATHER_RR = {
    'temperature': [
        {'condition': lambda t: t < 20, 'rr': 1.05, 'category': 'Dingin', 'source': 'Lowen et al.'},
        {'condition': lambda t: 20 <= t <= 25, 'rr': 1.00, 'category': 'Normal', 'source': 'Davis et al.'},
        {'condition': lambda t: t > 30, 'rr': 1.03, 'category': 'Panas', 'source': 'Davis et al.'},
        {'condition': lambda t: 25 < t <= 30, 'rr': 1.01, 'category': 'Hangat', 'source': 'Interpolasi'}
    ],
    'humidity': [
        {'condition': lambda h: h < 40, 'rr': 1.05, 'category': 'Rendah', 'source': 'Lowen; Shaman'},
        {'condition': lambda h: 40 <= h <= 60, 'rr': 1.00, 'category': 'Optimal', 'source': 'ASHRAE'},
        {'condition': lambda h: h > 70, 'rr': 1.03, 'category': 'Tinggi', 'source': 'Studi epidemiologi'},
        {'condition': lambda h: 60 < h <= 70, 'rr': 1.01, 'category': 'Sedang', 'source': 'Interpolasi'}
    ],
    'wind_speed': [
        {'condition': lambda w: w < 1.5, 'rr': 1.03, 'category': 'Lemah', 'source': 'Studi dispersi'},
        {'condition': lambda w: 1.5 <= w <= 3, 'rr': 1.00, 'category': 'Normal', 'source': 'Review dispersion'},
        {'condition': lambda w: w > 3, 'rr': 0.99, 'category': 'Kuat', 'source': 'Review dispersion'}
    ]
}

# Kota-kota besar di Indonesia
INDONESIAN_CITIES = [
    # Jawa
    {'name': 'Jakarta', 'lat': -6.2088, 'lon': 106.8456, 'province': 'DKI Jakarta'},
    {'name': 'Surabaya', 'lat': -7.2575, 'lon': 112.7521, 'province': 'Jawa Timur'},
    {'name': 'Bandung', 'lat': -6.9175, 'lon': 107.6191, 'province': 'Jawa Barat'},
    {'name': 'Semarang', 'lat': -6.9667, 'lon': 110.4167, 'province': 'Jawa Tengah'},
    {'name': 'Yogyakarta', 'lat': -7.7956, 'lon': 110.3695, 'province': 'DI Yogyakarta'},
    {'name': 'Malang', 'lat': -7.9797, 'lon': 112.6304, 'province': 'Jawa Timur'},
    
    # Sumatera
    {'name': 'Medan', 'lat': 3.5952, 'lon': 98.6722, 'province': 'Sumatera Utara'},
    {'name': 'Palembang', 'lat': -2.9761, 'lon': 104.7754, 'province': 'Sumatera Selatan'},
    {'name': 'Pekanbaru', 'lat': 0.5071, 'lon': 101.4478, 'province': 'Riau'},
    {'name': 'Padang', 'lat': -0.9471, 'lon': 100.4172, 'province': 'Sumatera Barat'},
    
    # Kalimantan
    {'name': 'Balikpapan', 'lat': -1.2379, 'lon': 116.8529, 'province': 'Kalimantan Timur'},
    {'name': 'Banjarmasin', 'lat': -3.3194, 'lon': 114.5900, 'province': 'Kalimantan Selatan'},
    {'name': 'Pontianak', 'lat': -0.0263, 'lon': 109.3425, 'province': 'Kalimantan Barat'},
    
    # Sulawesi
    {'name': 'Makassar', 'lat': -5.1477, 'lon': 119.4327, 'province': 'Sulawesi Selatan'},
    {'name': 'Manado', 'lat': 1.4748, 'lon': 124.8421, 'province': 'Sulawesi Utara'},
    
    # Bali & Nusa Tenggara
    {'name': 'Denpasar', 'lat': -8.6705, 'lon': 115.2126, 'province': 'Bali'},
    {'name': 'Mataram', 'lat': -8.5830, 'lon': 116.1162, 'province': 'Nusa Tenggara Barat'},
]

# Kategori Risiko berdasarkan RR Total
RISK_CATEGORIES = [
    {'min': 0, 'max': 1.05, 'category': 'Rendah', 'color': 'green', 'description': 'Risiko ISPA minimal'},
    {'min': 1.05, 'max': 1.15, 'category': 'Sedang', 'color': 'yellow', 'description': 'Risiko ISPA moderat'},
    {'min': 1.15, 'max': 1.30, 'category': 'Tinggi', 'color': 'orange', 'description': 'Risiko ISPA tinggi'},
    {'min': 1.30, 'max': float('inf'), 'category': 'Sangat Tinggi', 'color': 'red', 'description': 'Risiko ISPA sangat tinggi'}
]

def get_pollution_rr(pollutant, concentration=None):
    """
    Mendapatkan Risk Ratio untuk polutan tertentu
    
    Args:
        pollutant: Nama polutan (PM2.5, PM10, NO2, SO2, O3)
        concentration: Konsentrasi (opsional, untuk scaling)
    
    Returns:
        float: Risk Ratio median
    """
    if pollutant in POLLUTION_RR:
        return POLLUTION_RR[pollutant]['median']
    return 1.0

def get_weather_rr(parameter, value):
    """
    Mendapatkan Risk Ratio untuk parameter cuaca
    
    Args:
        parameter: 'temperature', 'humidity', atau 'wind_speed'
        value: Nilai parameter
    
    Returns:
        tuple: (rr, category)
    """
    if parameter not in WEATHER_RR:
        return 1.0, 'Unknown'
    
    for rule in WEATHER_RR[parameter]:
        if rule['condition'](value):
            return rule['rr'], rule['category']
    
    return 1.0, 'Unknown'

def calculate_total_rr(pollution_data, weather_data):
    """
    Menghitung RR Total menggunakan model multiplikatif
    
    RR_total = RR_PM2.5 × RR_PM10 × RR_NO2 × RR_SO2 × RR_O3 × RR_suhu × RR_RH × RR_angin
    
    Args:
        pollution_data: Dict dengan konsentrasi polutan
        weather_data: Dict dengan parameter cuaca
    
    Returns:
        dict: {
            'rr_total': float,
            'category': str,
            'breakdown': dict dengan RR masing-masing faktor
        }
    """
    # Hitung RR Polusi
    rr_pm25 = get_pollution_rr('PM2.5')
    rr_pm10 = get_pollution_rr('PM10')
    rr_no2 = get_pollution_rr('NO2')
    rr_so2 = get_pollution_rr('SO2')
    rr_o3 = get_pollution_rr('O3')
    
    # Hitung RR Cuaca
    rr_temp, temp_cat = get_weather_rr('temperature', weather_data.get('temp', 25))
    rr_humid, humid_cat = get_weather_rr('humidity', weather_data.get('humidity', 50))
    rr_wind, wind_cat = get_weather_rr('wind_speed', weather_data.get('wind_speed', 2))
    
    # Model Multiplikatif
    rr_total = rr_pm25 * rr_pm10 * rr_no2 * rr_so2 * rr_o3 * rr_temp * rr_humid * rr_wind
    
    # Tentukan Kategori
    category = 'Unknown'
    for cat in RISK_CATEGORIES:
        if cat['min'] <= rr_total < cat['max']:
            category = cat['category']
            break
    
    return {
        'rr_total': round(rr_total, 4),
        'category': category,
        'breakdown': {
            'pollution': {
                'PM2.5': rr_pm25,
                'PM10': rr_pm10,
                'NO2': rr_no2,
                'SO2': rr_so2,
                'O3': rr_o3
            },
            'weather': {
                'temperature': {'rr': rr_temp, 'category': temp_cat},
                'humidity': {'rr': rr_humid, 'category': humid_cat},
                'wind_speed': {'rr': rr_wind, 'category': wind_cat}
            }
        }
    }
