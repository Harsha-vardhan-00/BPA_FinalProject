import requests  # For making HTTP requests to fetch data from the API
import pandas as pd  # For handling and analyzing tabular data
from datetime import datetime  # For working with date and time
import streamlit as st  # For building interactive web apps
from typing import Dict, Optional  # For type hinting to improve code readability

class WeatherAPI:
    def __init__(self, api_key: str):
        """
        Initialize the WeatherAPI class with an API key from OpenWeatherMap.

        Args:
            api_key (str): Your OpenWeatherMap API key.
        """
        self.api_key = api_key  # Store the API key
        self.base_url = "https://api.openweathermap.org/data/2.5"  # Base URL for the API endpoints
        
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """
        Make an API request to the specified endpoint with the given parameters.
        
        Args:
            endpoint (str): The specific API endpoint to hit (e.g., "weather").
            params (Dict): Query parameters for the API request.

        Returns:
            Optional[Dict]: JSON response from the API or None in case of an error.
        """
        try:
            # Construct the full URL and add essential parameters
            url = f"{self.base_url}/{endpoint}"
            params["appid"] = self.api_key  # Include API key in the parameters
            params["units"] = "metric"  # Use metric units (e.g., Celsius)

            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Return the JSON response
        except requests.exceptions.HTTPError as http_err:
            # Handle specific HTTP errors
            if response.status_code == 401:
                st.error("API key error: Please check if your API key is valid and activated.")
            elif response.status_code == 429:
                st.error("Too many requests: Please wait before trying again.")
            else:
                st.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            # Handle any other errors
            st.error(f"Error occurred: {err}")
        return None  # Return None in case of an error

    @st.cache_data(ttl=1800)
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch current weather data for specific coordinates.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.

        Returns:
            Optional[Dict]: Parsed weather data or None if the request fails.
        """
        params = {"lat": lat, "lon": lon}  # Define parameters for the API call
        data = self._make_request("weather", params)  # Make the API call
        
        if data:
            # Parse and return the relevant weather information
            return {
                "temperature": round(data["main"]["temp"], 1),  # Current temperature
                "feels_like": round(data["main"]["feels_like"], 1),  # Feels-like temperature
                "humidity": data["main"]["humidity"],  # Humidity percentage
                "pressure": data["main"]["pressure"],  # Atmospheric pressure in hPa
                "wind_speed": round(data["wind"]["speed"] * 3.6, 1),  # Wind speed in km/h
                "description": data["weather"][0]["description"].capitalize(),  # Weather description
                "icon": data["weather"][0]["icon"],  # Weather icon code
                "city": data.get("name", "Unknown Location"),  # City name (fallback: Unknown)
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp
            }
        return None  # Return None if no data is available

    @st.cache_data(ttl=1800)
    def get_forecast_by_coordinates(self, lat: float, lon: float) -> Optional[pd.DataFrame]:
        """
        Fetch a 5-day weather forecast for specific coordinates.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.

        Returns:
            Optional[pd.DataFrame]: DataFrame with forecast data or None if the request fails.
        """
        params = {"lat": lat, "lon": lon}  # Define parameters for the API call
        data = self._make_request("forecast", params)  # Make the API call
        
        if data:
            # Extract and organize the forecast data
            forecast_data = []
            for item in data["list"]:
                forecast_data.append({
                    "timestamp": datetime.fromtimestamp(item["dt"]),  # Forecast timestamp
                    "temperature": round(item["main"]["temp"], 1),  # Forecast temperature
                    "humidity": item["main"]["humidity"],  # Forecast humidity
                    "wind_speed": round(item["wind"]["speed"] * 3.6, 1),  # Forecast wind speed in km/h
                    "description": item["weather"][0]["description"].capitalize(),  # Forecast description
                })
            return pd.DataFrame(forecast_data)  # Convert to a DataFrame for analysis
        return None  # Return None if no data is available

    def calculate_weather_kpis(self, current_data: Dict, forecast_data: pd.DataFrame) -> Dict:
        """
        Calculate Key Performance Indicators (KPIs) from weather data.

        Args:
            current_data (Dict): Current weather data.
            forecast_data (pd.DataFrame): DataFrame with forecast data.

        Returns:
            Dict: Calculated KPIs including temperature trends and weather stability.
        """
        if not current_data or forecast_data is None:
            # Return default KPIs if data is missing
            return {
                "current_temp": None,
                "temp_trend": 0,
                "avg_humidity": 0,
                "max_wind_speed": 0,
                "weather_stability": 0
            }
            
        # Calculate and return the KPIs
        kpis = {
            "current_temp": current_data["temperature"],  # Current temperature
            "temp_trend": self._calculate_temperature_trend(forecast_data),  # Temperature trend over 5 days
            "avg_humidity": round(forecast_data["humidity"].mean(), 1),  # Average humidity
            "max_wind_speed": round(forecast_data["wind_speed"].max(), 1),  # Maximum wind speed
            "weather_stability": self._calculate_weather_stability(forecast_data)  # Weather stability score
        }
        return kpis

    def _calculate_temperature_trend(self, forecast_data: pd.DataFrame) -> float:
        """
        Calculate the temperature trend over the forecast period.

        Args:
            forecast_data (pd.DataFrame): DataFrame with forecast data.

        Returns:
            float: Difference in average temperature between the first and last day.
        """
        if len(forecast_data) < 2:
            return 0  # Return 0 if not enough data points
        first_day = forecast_data.head(8)["temperature"].mean()  # Average temp for the first day
        last_day = forecast_data.tail(8)["temperature"].mean()  # Average temp for the last day
        return round(last_day - first_day, 1)  # Return the trend

    def _calculate_weather_stability(self, forecast_data: pd.DataFrame) -> float:
        """
        Calculate a weather stability score based on temperature and humidity variance.

        Args:
            forecast_data (pd.DataFrame): DataFrame with forecast data.

        Returns:
            float: Weather stability score (0-100).
        """
        temp_variance = forecast_data["temperature"].var()  # Temperature variance
        humidity_variance = forecast_data["humidity"].var()  # Humidity variance
        temp_stability = 100 * (1 / (1 + temp_variance / 10))  # Stability score for temperature
        humidity_stability = 100 * (1 / (1 + humidity_variance / 100))  # Stability score for humidity
        return round((temp_stability + humidity_stability) / 2, 1)  # Average stability score
