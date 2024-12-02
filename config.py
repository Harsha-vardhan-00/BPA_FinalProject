import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY:
    raise ValueError("Please set the OPENWEATHER_API_KEY environment variable")

# Default locations
DEFAULT_LOCATIONS = {
    "Hyderabad":{"lat":17.0725, "lon":78.5777},
    "Buffalo":{"lat":42.8867, "lon": -78.8784},
    "Niagara Falls":{"lat":43.0844, "lon": -79.0615},    
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Sydney": {"lat": -33.8688, "lon": 151.2093}
    
}



# Cache settings
CACHE_TTL = 1800  # 30 minutes

# Display settings
TEMPERATURE_UNIT = "°C"
WIND_SPEED_UNIT = "km/h"
PRESSURE_UNIT = "hPa"

# Map settings
DEFAULT_MAP_CENTER = [20.0, 0.0]
DEFAULT_MAP_ZOOM = 2

# Chart settings
CHART_THEME = "streamlit"
CHART_HEIGHT = 400


