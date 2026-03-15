"""
Location Tracker Module for KARMA ULTRA PRO
Handles location detection and tracking for personalized services
"""

import logging
import requests
import json
from datetime import datetime
from pathlib import Path


class LocationTracker:
    """
    Location Tracking for KARMA AI
    Features:
    - Auto-detect location using IP
    - Manual location setting
    - Location history
    - Weather-based location
    """
    
    def __init__(self, logger=None):
        """Initialize location tracker"""
        self.logger = logger or logging.getLogger('KARMA-Location')
        
        # Current location
        self.current_location = None
        self.location_history = []
        
        # Cache file
        self.cache_file = Path(__file__).parent / 'data' / 'location_cache.json'
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load cached location
        self._load_cache()
        
        self.logger.info("Location Tracker initialized")
    
    def _load_cache(self):
        """Load cached location"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.current_location = data.get('current')
                    self.location_history = data.get('history', [])
        except Exception as e:
            self.logger.error(f"Cache load error: {e}")
    
    def _save_cache(self):
        """Save location to cache"""
        try:
            data = {
                'current': self.current_location,
                'history': self.location_history[-10:],  # Keep last 10
                'last_updated': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Cache save error: {e}")
    
    def detect_location(self):
        """
        Auto-detect location using IP address
        
        Returns:
            Location dictionary with city, region, country, lat, lon
        """
        try:
            # Use ipapi service (free, no API key needed)
            response = requests.get('https://ipapi.co/json/', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                location = {
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'country': data.get('country_name', 'Unknown'),
                    'country_code': data.get('country_code', ''),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'timezone': data.get('timezone', 'UTC'),
                    'isp': data.get('org', ''),
                    'ip': data.get('ip', ''),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.current_location = location
                self.location_history.append(location)
                self._save_cache()
                
                self.logger.info(f"Location detected: {location['city']}, {location['country']}")
                return location
            
        except Exception as e:
            self.logger.error(f"Location detection error: {e}")
        
        # Fallback to ipinfo
        try:
            response = requests.get('https://ipinfo.io/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                coords = data.get('loc', '0,0').split(',')
                
                location = {
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'latitude': float(coords[0]) if len(coords) > 0 else None,
                    'longitude': float(coords[1]) if len(coords) > 1 else None,
                    'ip': data.get('ip', ''),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.current_location = location
                self.location_history.append(location)
                self._save_cache()
                
                return location
                
        except Exception as e:
            self.logger.error(f"Fallback location error: {e}")
        
        return None
    
    def set_location(self, city=None, region=None, country=None, latitude=None, longitude=None):
        """
        Manually set location
        
        Args:
            city: City name
            region: Region/state
            country: Country name
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            Location dictionary
        """
        location = {
            'city': city or 'Unknown',
            'region': region or 'Unknown',
            'country': country or 'Unknown',
            'latitude': latitude,
            'longitude': longitude,
            'manual': True,
            'timestamp': datetime.now().isoformat()
        }
        
        self.current_location = location
        self.location_history.append(location)
        self._save_cache()
        
        self.logger.info(f"Location set manually: {city}, {country}")
        return location
    
    def get_current_location(self):
        """
        Get current location (cached or detect)
        
        Returns:
            Location dictionary
        """
        if self.current_location:
            return self.current_location
        
        return self.detect_location()
    
    def get_location_string(self):
        """
        Get location as a string for weather APIs
        
        Returns:
            Location string (city or coordinates)
        """
        location = self.get_current_location()
        
        if location:
            # Prefer coordinates for accuracy
            if location.get('latitude') and location.get('longitude'):
                return f"{location['latitude']},{location['longitude']}"
            
            # Fall back to city name
            city = location.get('city', '')
            if city and city != 'Unknown':
                return city
        
        return None
    
    def get_location_name(self):
        """
        Get human-readable location name
        
        Returns:
            Location string (e.g., "Mumbai, Maharashtra, India")
        """
        location = self.get_current_location()
        
        if location:
            parts = []
            if location.get('city') and location['city'] != 'Unknown':
                parts.append(location['city'])
            if location.get('region') and location['region'] != 'Unknown':
                parts.append(location['region'])
            if location.get('country'):
                parts.append(location['country'])
            
            if parts:
                return ', '.join(parts)
        
        return "Unknown Location"
    
    def get_history(self):
        """
        Get location history
        
        Returns:
            List of location records
        """
        return self.location_history
    
    def get_timezone(self):
        """
        Get current timezone
        
        Returns:
            Timezone string
        """
        location = self.get_current_location()
        
        if location:
            return location.get('timezone', 'UTC')
        
        return 'UTC'
    
    def get_local_time(self):
        """
        Get current local time
        
        Returns:
            datetime object in local timezone
        """
        from datetime import timezone
        import pytz
        
        tz_name = self.get_timezone()
        
        try:
            tz = pytz.timezone(tz_name)
            return datetime.now(tz)
        except:
            return datetime.now()
    
    def get_greeting_by_time(self):
        """
        Get greeting based on local time
        
        Returns:
            Greeting string (morning/afternoon/evening/night)
        """
        local_time = self.get_local_time()
        hour = local_time.hour
        
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "Good night"
    
    def refresh_location(self):
        """
        Force refresh location detection
        
        Returns:
            New location dictionary
        """
        return self.detect_location()


# Singleton instance
_location_tracker = None

def get_location_tracker(logger=None):
    """Get or create location tracker singleton"""
    global _location_tracker
    if _location_tracker is None:
        _location_tracker = LocationTracker(logger)
    return _location_tracker
