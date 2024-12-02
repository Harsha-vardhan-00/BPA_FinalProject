# main.py
import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium
from api.weather_api import WeatherAPI
from config import *
import plotly.express as px
from datetime import datetime
import requests

def geocode_location(location_name, api_key):
    """Convert location name to coordinates using OpenWeatherMap Geocoding API."""
    try:
        url = f"http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": location_name,
            "limit": 5,
            "appid": api_key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        locations = response.json()
        
        if locations:
            # Return list of locations with their details
            return [(loc['name'], loc['lat'], loc['lon'], 
                    f"{loc.get('state', '')}, {loc.get('country', '')}") 
                   for loc in locations]
        return []
    except Exception as e:
        st.error(f"Error in geocoding: {str(e)}")
        return []

# Page configuration
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# Initialize API if not already in session state
if 'weather_api' not in st.session_state:
    st.session_state.weather_api = WeatherAPI(OPENWEATHER_API_KEY)

def initialize_session_state():
    """Initialize session state variables."""
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = DEFAULT_MAP_CENTER
    if 'location_name' not in st.session_state:
        st.session_state.location_name = "Select a location"
    if 'map_center' not in st.session_state:
        st.session_state.map_center = DEFAULT_MAP_CENTER

def update_weather_data(lat, lon):
    """Update weather data based on selected location."""
    try:
        with st.spinner('Fetching weather data...'):
            current_weather = st.session_state.weather_api.get_weather_by_coordinates(lat, lon)
            forecast_data = st.session_state.weather_api.get_forecast_by_coordinates(lat, lon)
            
            if current_weather and forecast_data is not None:
                kpis = st.session_state.weather_api.calculate_weather_kpis(current_weather, forecast_data)
                
                # Update session state
                st.session_state.current_weather = current_weather
                st.session_state.forecast_data = forecast_data
                st.session_state.kpis = kpis
                st.session_state.location_name = current_weather.get('city', 'Unknown Location')
    except Exception as e:
        st.error(f"Error updating weather data: {str(e)}")

def create_map():
    """Create and display interactive map."""
    # Create the base map
    m = folium.Map(
        location=st.session_state.map_center,
        zoom_start=DEFAULT_MAP_ZOOM,
        tiles="OpenStreetMap"
    )
    
    # Add marker for selected location
    if st.session_state.selected_location != DEFAULT_MAP_CENTER:
        folium.Marker(
            st.session_state.selected_location,
            #popup="",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # Add click event handler
    m.add_child(folium.LatLngPopup())
    
    # Display the map and get the last clicked location
    map_data = st_folium(m, width=800, height=400)
    
    # Update selected location if map is clicked
    if map_data['last_clicked']:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        st.session_state.selected_location = [clicked_lat, clicked_lng]
        update_weather_data(clicked_lat, clicked_lng)

def main():
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🌤️ Weather Analytics")
        
        # Location search box
        st.subheader("🔍 Search Location")
        search_query = st.text_input("Enter city name", key="search_box")
        
        if search_query:
            locations = geocode_location(search_query, OPENWEATHER_API_KEY)
            if locations:
                location_options = [f"{loc[0]}, {loc[3]}" for loc in locations]
                selected_index = st.selectbox(
                    "Select location:",
                    range(len(location_options)),
                    format_func=lambda x: location_options[x]
                )
                
                if st.button("Use Selected Location"):
                    selected_loc = locations[selected_index]
                    st.session_state.selected_location = [selected_loc[1], selected_loc[2]]
                    st.session_state.map_center = [selected_loc[1], selected_loc[2]]
                    update_weather_data(selected_loc[1], selected_loc[2])
        
        st.markdown("---")
        
        # Quick select locations
        st.subheader("⚡ Quick Select Location")
        selected_default = st.selectbox(
            "Choose a city",
            options=list(DEFAULT_LOCATIONS.keys()),
            key="default_location"
        )
        
        if st.button("Use Selected City"):
            location = DEFAULT_LOCATIONS[selected_default]
            st.session_state.selected_location = [location['lat'], location['lon']]
            st.session_state.map_center = [location['lat'], location['lon']]
            update_weather_data(location['lat'], location['lon'])
        
        st.markdown("---")
        st.markdown("### 📍 Selected Location")
        st.write(f"**{st.session_state.location_name}**")
        st.write(f"Lat: {st.session_state.selected_location[0]:.4f}")
        st.write(f"Lon: {st.session_state.selected_location[1]:.4f}")
        
        st.markdown("---")
        st.markdown("### 🗺️ Map Instructions")
        st.markdown("1. Click anywhere on the map to select location")
        st.markdown("2. Use the search box to find specific places")
        st.markdown("3. Or use quick select for major cities")

    # Main content
    st.title("📊 Weather Analytics Dashboard")
    st.markdown(f"### 📍 {st.session_state.location_name}")

    # Display map
    st.subheader("🗺️ Interactive Map")
    create_map()

    # Rest of your dashboard code remains the same...
    # Display weather information if available
    if 'current_weather' in st.session_state:
        # Display KPIs
        st.markdown("### 📈 Key Weather Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Temperature",
                f"{st.session_state.current_weather['temperature']}°C",
                f"{st.session_state.kpis['temp_trend']}°C"
            )
        
        with col2:
            st.metric(
                "Humidity",
                f"{st.session_state.current_weather['humidity']}%",
                None
            )
        
        with col3:
            st.metric(
                "Wind Speed",
                f"{st.session_state.current_weather['wind_speed']} km/h",
                None
            )

        # Create two columns for charts
        col_temp, col_cond = st.columns(2)
        
        with col_temp:
            st.markdown("### 🌡️ Temperature Forecast")
            fig_temp = px.line(
                st.session_state.forecast_data,
                x='timestamp',
                y='temperature',
                title='Temperature Over Time'
            )
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col_cond:
            st.markdown("### ⛅ Weather Conditions")
            conditions = st.session_state.forecast_data['description'].value_counts()
            fig_cond = px.pie(
                values=conditions.values,
                names=conditions.index,
                title='Weather Conditions Distribution'
            )
            st.plotly_chart(fig_cond, use_container_width=True)

        # Detailed Data Table
        st.markdown("### 📋 Detailed Weather Data")
        st.dataframe(
            st.session_state.forecast_data,
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    main()