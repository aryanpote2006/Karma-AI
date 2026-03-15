"""
Weather Module for KARMA AI
Enhanced weather and environment data

Features:
- Current weather conditions
- Weather forecast
- AQI (Air Quality Index) data
- Humidity, wind, UV index
- Location-based weather
"""

import os
import requests
import logging
from datetime import datetime


class Weather:
    """
    Weather and environment data provider for KARMA AI
    Uses OpenWeatherMap API and wttr.in for weather data
    """
    
    def __init__(self, api_key=None):
        """Initialize weather module"""
        self.logger = logging.getLogger('KARMA-Weather')
        
        # API keys (use free wttr.in as primary)
        self.openweathermap_key = api_key or os.environ.get('OPENWEATHERMAP_API_KEY', '')
        
        # Cache
        self.cache = {}
        self.cache_timeout = 1800  # 30 minutes
        
        self.logger.info("Weather module initialized")
    
    def get_current_weather(self, location=None):
        """
        Get current weather for location
        
        Args:
            location: City name or coordinates (lat,lon)
            
        Returns:
            Weather information dictionary
        """
        try:
            # Use wttr.in (free, no API key needed)
            if location:
                url = f"https://wttr.in/{location}?format=j1"
            else:
                url = "https://wttr.in/?format=j1"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                weather = {
                    'location': data.get('nearest_area', [{}])[0].get('areaName', [{}])[0].get('value', 'Unknown'),
                    'temperature': current['temp_C'][0],
                    'temperature_f': current['temp_F'][0],
                    'condition': current['weatherDesc'][0]['value'],
                    'humidity': current['humidity'][0],
                    'wind_speed': current['windspeedKmph'][0],
                    'wind_direction': current['winddir16Point'][0],
                    'pressure': current['pressure'][0],
                    'visibility': current['visibility'][0],
                    'uv_index': current.get('uvIndex', ['0'])[0],
                    'feels_like': current['FeelsLikeC'][0],
                    'precipitation': current['precipMM'][0],
                    'last_updated': current['localObsDateTime'][0]
                }
                
                self.cache['current'] = {
                    'data': weather,
                    'timestamp': datetime.now().timestamp()
                }
                
                return weather
            
        except Exception as e:
            self.logger.error(f"Weather error: {e}")
        
        return None
    
    def get_weather_description(self, location=None):
        """
        Get simple weather description for TTS output
        
        Args:
            location: City name
            
        Returns:
            Weather description string
        """
        weather = self.get_current_weather(location)
        
        if weather:
            return (
                f"Currently in {weather['location']}, it's {weather['temperature']} degrees Celsius "
                f"with {weather['condition']}. "
                f"Humidity is {weather['humidity']} percent. "
                f"Feels like {weather['feels_like']} degrees."
            )
        
        return "Sorry, I couldn't get the weather information."
    
    def get_aqi(self, location=None):
        """
        Get Air Quality Index data
        
        Args:
            location: City name (works best with OpenWeatherMap)
            
        Returns:
            AQI information dictionary
        """
        try:
            # For now, use wttr.in for basic air quality indication
            # In production, use OpenWeatherMap Air Pollution API
            
            if location:
                url = f"https://wttr.in/{location}?format=j1"
            else:
                url = "https://wttr.in/?format=j1"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                # Parse air quality from available data
                # Note: wttr.in has limited AQI data
                aqi_value = current.get('pollutionindex', {}).get('value', 'NA')
                
                if aqi_value == 'NA':
                    # Estimate based on other factors
                    pm25 = current.get('pm25', ['0'])[0]
                    if int(pm25) > 75:
                        aqi_value = "Unhealthy"
                    elif int(pm25) > 35:
                        aqi_value = "Moderate"
                    else:
                        aqi_value = "Good"
                
                aqi = {
                    'location': data.get('nearest_area', [{}])[0].get('areaName', [{}])[0].get('value', 'Unknown'),
                    'aqi': aqi_value,
                    'pm25': current.get('pm25', ['NA'])[0],
                    'pm10': current.get('pm10', ['NA'])[0],
                    'ozone': current.get('ozone', ['NA'])[0],
                    'co': current.get('co', ['NA'])[0],
                    'no2': current.get('no2', ['NA'])[0],
                    'so2': current.get('so2', ['NA'])[0],
                }
                
                return aqi
            
        except Exception as e:
            self.logger.error(f"AQI error: {e}")
        
        return None
    
    def get_aqi_description(self, location=None):
        """
        Get simple AQI description for TTS output
        
        Args:
            location: City name
            
        Returns:
            AQI description string
        """
        aqi = self.get_aqi(location)
        
        if aqi:
            if aqi['aqi'] == 'Good':
                quality = "good"
                advice = "Air quality is satisfactory. Enjoy outdoor activities!"
            elif aqi['aqi'] == 'Moderate':
                quality = "moderate"
                advice = "Air quality is acceptable. Sensitive individuals should limit prolonged outdoor exertion."
            elif aqi['aqi'] == 'Unhealthy':
                quality = "unhealthy"
                advice = "Everyone may begin to experience health effects. Limit outdoor activities."
            elif aqi['aqi'] == 'Very Unhealthy':
                quality = "very unhealthy"
                advice = "Health alert. Avoid outdoor exercises."
            elif aqi['aqi'] == 'Hazardous':
                quality = "hazardous"
                advice = "Health warnings of emergency conditions. Stay indoors."
            else:
                return f"Air quality data is not available for {aqi['location']}."
            
            return f"Air quality in {aqi['location']} is {quality}. {advice}"
        
        return "Sorry, I couldn't get air quality information."
    
    def get_forecast(self, location=None, days=3):
        """
        Get weather forecast
        
        Args:
            location: City name
            days: Number of days (1-3)
            
        Returns:
            Forecast list
        """
        try:
            if location:
                url = f"https://wttr.in/{location}?format=j1"
            else:
                url = "https://wttr.in/?format=j1"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather = data['weather'][:days]
                
                forecast = []
                for day in weather:
                    forecast.append({
                        'date': day['date'],
                        'max_temp': day['maxtempC'][0],
                        'min_temp': day['mintempC'][0],
                        'condition': day['hourly'][4]['weatherDesc'][0]['value'],  # Noon condition
                        'chance_of_rain': day['hourly'][4]['chanceofrain'][0],
                        'sunrise': day['astronomy'][0]['sunrise'][0],
                        'sunset': day['astronomy'][0]['sunset'][0]
                    })
                
                return forecast
            
        except Exception as e:
            self.logger.error(f"Forecast error: {e}")
        
        return None
    
    def get_forecast_description(self, location=None, days=2):
        """
        Get simple forecast description for TTS output
        
        Args:
            location: City name
            days: Number of days
            
        Returns:
            Forecast description string
        """
        forecast = self.get_forecast(location, days)
        
        if forecast:
            desc = f"Weather forecast for {forecast[0].get('location', 'your area')}: "
            
            for day in forecast:
                date = day['date']
                max_temp = day['max_temp']
                min_temp = day['min_temp']
                condition = day['condition']
                
                desc += f"On {date}, expect {condition} with temperatures between {min_temp} and {max_temp} degrees. "
            
            return desc
        
        return "Sorry, I couldn't get the forecast."
    
    def get_weather_and_aqi(self, location=None):
        """
        Get combined weather and AQI information
        
        Args:
            location: City name
            
        Returns:
            Combined description string
        """
        weather = self.get_current_weather(location)
        aqi = self.get_aqi(location)
        
        if weather:
            desc = self.get_weather_description(location)
            
            if aqi and aqi['aqi'] != 'NA':
                desc += " " + self.get_aqi_description(location).split('.')[0] + "."
            
            return desc
        
        return "Sorry, I couldn't get the weather information."


# Import os for environment variables
import os
