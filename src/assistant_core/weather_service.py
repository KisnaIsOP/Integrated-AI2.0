import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def get_weather(self, city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        """Get current weather for a city"""
        try:
            location = f"{city}"
            if country_code:
                location = f"{city},{country_code}"

            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'  # Use metric units
            }

            response = requests.get(f"{self.base_url}/weather", params=params)
            response.raise_for_status()
            data = response.json()

            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'city': data['name'],
                'country': data['sys']['country']
            }
        except requests.RequestException as e:
            return {'error': f"Weather API Error: {str(e)}"}

    def get_forecast(self, city: str, country_code: Optional[str] = None, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a city"""
        try:
            location = f"{city}"
            if country_code:
                location = f"{city},{country_code}"

            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days
            }

            response = requests.get(f"{self.base_url}/forecast", params=params)
            response.raise_for_status()
            data = response.json()

            forecast = []
            for item in data['list']:
                forecast.append({
                    'datetime': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description'],
                    'wind_speed': item['wind']['speed']
                })

            return {
                'city': data['city']['name'],
                'country': data['city']['country'],
                'forecast': forecast
            }
        except requests.RequestException as e:
            return {'error': f"Weather API Error: {str(e)}"}
