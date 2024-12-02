# Weather Analytics Dashboard

A real-time weather analytics dashboard built with Python and Streamlit. This project was developed as part of the MGS 627 course.

## Features

- Real-time weather data visualization
- Interactive map for location selection
- Location search functionality
- 5-day weather forecast
- Temperature trend analysis
- Weather condition distribution
- Detailed weather metrics

## Technologies Used

- Python 3.8+
- Streamlit
- Folium
- Plotly
- OpenWeatherMap API

## Setup and Installation

1. Clone the repository:
git clone https://github.com/your-username/weather-dashboard.git
cd weather-dashboard


2. Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


3. Install required packages:

pip install -r requirements.txt


4. Create a `.streamlit/secrets.toml` file and add your OpenWeatherMap API key:

OPENWEATHER_API_KEY = "your-api-key-here"


5. Run the application:

streamlit run main.py


## Project Structure


weather_dashboard/
├── .streamlit/
│   └── secrets.toml
├── api/
│   └── weather_api.py
├── main.py
├── config.py
├── requirements.txt
└── README.md


## Contributors

- HarshavardhanReddy Nadedi
- Sputhnik Gundu

## License

This project is licensed under the MIT License - see the LICENSE file for details.