# src/api/weather_api.py
import requests
import pandas as pd
from datetime import datetime
import streamlit as st
from typing import Dict, Optional

class WeatherAPI:
    def __init__(self, api_key: str):
        """Initialize WeatherAPI with your OpenWeatherMap API key."""
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with error handling."""
        try:
            url = f"{self.base_url}/{endpoint}"
            params["appid"] = self.api_key
            params["units"] = "metric"
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                st.error("API key error: Please check if your API key is valid and activated")
            elif response.status_code == 429:
                st.error("Too many requests: Please wait before trying again")
            else:
                st.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            st.error(f"Error occurred: {err}")
        return None

    @st.cache_data(ttl=1800)
    def get_weather_by_coordinates(_self, lat: float, lon: float) -> Optional[Dict]:
        """Get current weather data for specific coordinates."""
        params = {"lat": lat, "lon": lon}
        data = _self._make_request("weather", params)
        
        if data:
            return {
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": round(data["wind"]["speed"] * 3.6, 1),
                "description": data["weather"][0]["description"].capitalize(),
                "icon": data["weather"][0]["icon"],
                "city": data.get("name", "Unknown Location"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        return None

    @st.cache_data(ttl=1800)
    def get_forecast_by_coordinates(_self, lat: float, lon: float) -> Optional[pd.DataFrame]:
        """Get 5-day weather forecast for specific coordinates."""
        params = {"lat": lat, "lon": lon}
        data = _self._make_request("forecast", params)
        
        if data:
            forecast_data = []
            for item in data["list"]:
                forecast_data.append({
                    "timestamp": datetime.fromtimestamp(item["dt"]),
                    "temperature": round(item["main"]["temp"], 1),
                    "humidity": item["main"]["humidity"],
                    "wind_speed": round(item["wind"]["speed"] * 3.6, 1),
                    "description": item["weather"][0]["description"].capitalize(),
                })
            return pd.DataFrame(forecast_data)
        return None

    def calculate_weather_kpis(self, current_data: Dict, forecast_data: pd.DataFrame) -> Dict:
        """Calculate Key Performance Indicators from weather data."""
        if not current_data or forecast_data is None:
            return {
                "current_temp": None,
                "temp_trend": 0,
                "avg_humidity": 0,
                "max_wind_speed": 0,
                "weather_stability": 0
            }
            
        kpis = {
            "current_temp": current_data["temperature"],
            "temp_trend": self._calculate_temperature_trend(forecast_data),
            "avg_humidity": round(forecast_data["humidity"].mean(), 1),
            "max_wind_speed": round(forecast_data["wind_speed"].max(), 1),
            "weather_stability": self._calculate_weather_stability(forecast_data)
        }
        return kpis

    def _calculate_temperature_trend(self, forecast_data: pd.DataFrame) -> float:
        """Calculate temperature trend from forecast data."""
        if len(forecast_data) < 2:
            return 0
        first_day = forecast_data.head(8)["temperature"].mean()
        last_day = forecast_data.tail(8)["temperature"].mean()
        return round(last_day - first_day, 1)

    def _calculate_weather_stability(self, forecast_data: pd.DataFrame) -> float:
        """Calculate weather stability score (0-100)."""
        temp_variance = forecast_data["temperature"].var()
        humidity_variance = forecast_data["humidity"].var()
        temp_stability = 100 * (1 / (1 + temp_variance/10))
        humidity_stability = 100 * (1 / (1 + humidity_variance/100))
        return round((temp_stability + humidity_stability) / 2, 1)