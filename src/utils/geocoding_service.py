"""
Geocoding Module for POI Data
Handles conversion of addresses to geographic coordinates using Google Maps API or Baidu Maps API
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import quote

logger = logging.getLogger(__name__)


class GoogleMapsGeocodingService:
    """Service for geocoding addresses to coordinates using Google Maps API."""
    
    def __init__(self, google_api_key: str):
        """
        Initialize geocoding service with Google Maps API key.
        
        Args:
            google_api_key: Google Maps API key
        """
        self.google_api_key = google_api_key
        self.geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.reverse_geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    def geocode_address(self, address: str, region: str = "") -> Optional[Dict[str, float]]:
        """
        Convert address to geographic coordinates using Google Maps API.
        
        Args:
            address: Address to geocode
            region: Region hint for more accurate results (ISO 3166-1 country code)
            
        Returns:
            Dictionary with 'longitude' and 'latitude' keys, or None if failed
        """
        if not self.google_api_key:
            logger.warning("Google API key not configured, skipping geocoding")
            return None
        
        try:
            params = {
                'address': address,
                'key': self.google_api_key
            }
            
            if region:
                params['region'] = region
            
            response = requests.get(self.geocode_url, params=params, timeout=10)
            result = response.json()
            
            if result.get('status') == 'OK' and result.get('results'):
                location = result['results'][0]['geometry']['location']
                return {
                    'longitude': location['lng'],
                    'latitude': location['lat']
                }
            else:
                status = result.get('status', 'UNKNOWN')
                error_message = result.get('error_message', 'No error message')
                logger.warning(f"Google Maps geocoding failed for '{address}': Status {status} - {error_message}")
                return None
                
        except Exception as e:
            logger.error(f"Error geocoding address '{address}' with Google Maps: {e}")
            return None
    
    def batch_geocode(self, addresses: List[str], region: str = "") -> List[Optional[Dict[str, float]]]:
        """
        Batch geocode multiple addresses using Google Maps API.
        
        Args:
            addresses: List of addresses to geocode
            region: Region hint for more accurate results (ISO 3166-1 country code)
            
        Returns:
            List of coordinate dictionaries or None for each address
        """
        results = []
        for address in addresses:
            coords = self.geocode_address(address, region)
            results.append(coords)
        return results
    
    def reverse_geocode(self, longitude: float, latitude: float) -> Optional[str]:
        """
        Convert coordinates to address (reverse geocoding) using Google Maps API.
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            
        Returns:
            Formatted address string or None if failed
        """
        if not self.google_api_key:
            logger.warning("Google API key not configured, skipping reverse geocoding")
            return None
        
        try:
            params = {
                'latlng': f"{latitude},{longitude}",
                'key': self.google_api_key
            }
            
            response = requests.get(self.reverse_geocode_url, params=params, timeout=10)
            result = response.json()
            
            if result.get('status') == 'OK' and result.get('results'):
                return result['results'][0]['formatted_address']
            else:
                status = result.get('status', 'UNKNOWN')
                error_message = result.get('error_message', 'No error message')
                logger.warning(f"Google Maps reverse geocoding failed for ({latitude}, {longitude}): Status {status} - {error_message}")
                return None
                
        except Exception as e:
            logger.error(f"Error reverse geocoding ({latitude}, {longitude}) with Google Maps: {e}")
            return None


class GeocodingService:
    """Service for geocoding addresses to coordinates using Baidu Maps API."""
    
    def __init__(self, baidu_ak: str):
        """
        Initialize geocoding service with Baidu Maps API key.
        
        Args:
            baidu_ak: Baidu Maps API key
        """
        self.baidu_ak = baidu_ak
        self.geocode_url = "http://api.map.baidu.com/geocoding/v3/"
        self.reverse_geocode_url = "http://api.map.baidu.com/reverse_geocoding/v3/"
    
    def geocode_address(self, address: str, region: str = "") -> Optional[Dict[str, float]]:
        """
        Convert address to geographic coordinates.
        
        Args:
            address: Address to geocode
            region: Region hint for more accurate results
            
        Returns:
            Dictionary with 'longitude' and 'latitude' keys, or None if failed
        """
        if not self.baidu_ak:
            logger.warning("Baidu AK not configured, skipping geocoding")
            return None
        
        try:
            params = {
                'address': address,
                'output': 'json',
                'ak': self.baidu_ak
            }
            
            if region:
                params['region'] = region
            
            response = requests.get(self.geocode_url, params=params, timeout=10)
            result = response.json()
            
            if result.get('status') == 0:  # Success
                location = result['result']['location']
                return {
                    'longitude': location['lng'],
                    'latitude': location['lat']
                }
            else:
                logger.warning(f"Geocoding failed for '{address}': Status {result.get('status')} - {result.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None
    
    def batch_geocode(self, addresses: List[str], region: str = "") -> List[Optional[Dict[str, float]]]:
        """
        Batch geocode multiple addresses.
        
        Args:
            addresses: List of addresses to geocode
            region: Region hint for more accurate results
            
        Returns:
            List of coordinate dictionaries or None for each address
        """
        results = []
        for address in addresses:
            coords = self.geocode_address(address, region)
            results.append(coords)
        return results
    
    def reverse_geocode(self, longitude: float, latitude: float) -> Optional[str]:
        """
        Convert coordinates to address (reverse geocoding).
        
        Args:
            longitude: Longitude coordinate
            latitude: Latitude coordinate
            
        Returns:
            Formatted address string or None if failed
        """
        if not self.baidu_ak:
            logger.warning("Baidu AK not configured, skipping reverse geocoding")
            return None
        
        try:
            params = {
                'location': f"{latitude},{longitude}",
                'output': 'json',
                'ak': self.baidu_ak
            }
            
            response = requests.get(self.reverse_geocode_url, params=params, timeout=10)
            result = response.json()
            
            if result.get('status') == 0:  # Success
                return result['result']['formatted_address']
            else:
                logger.warning(f"Reverse geocoding failed for ({latitude}, {longitude}): Status {result.get('status')} - {result.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error reverse geocoding ({latitude}, {longitude}): {e}")
            return None


class MockGeocodingService:
    """
    Mock geocoding service for testing purposes.
    Returns mock coordinates based on location names.
    """
    
    def __init__(self):
        # Mock coordinate database for common locations
        self.mock_coordinates = {
            '北京': (116.4074, 39.9042),
            '上海': (121.4737, 31.2304),
            '广州': (113.2644, 23.1291),
            '深圳': (114.0579, 22.5431),
            '成都': (104.0668, 30.5728),
            '杭州': (120.1551, 30.2741),
            '武汉': (114.3055, 30.5931),
            '西安': (108.9398, 34.3416),
            '重庆': (106.5516, 29.5630),
            '天津': (117.2010, 39.0842),
            '南京': (118.7969, 32.0603),
            '苏州': (120.5853, 31.2989),
            '青岛': (120.3842, 36.0671),
            '大连': (121.6147, 38.9140),
            '厦门': (118.0894, 24.4798),
            '长沙': (112.9762, 28.1977),
            '郑州': (113.6654, 34.7580),
            '济南': (117.0199, 36.6512),
            '福州': (119.3062, 26.0753),
            '乌鲁木齐': (87.6177, 43.7928),
            '昆明': (102.8329, 24.8801),
            '兰州': (103.8343, 36.0611),
            '呼和浩特': (111.6708, 40.8183),
            '长春': (125.3245, 43.8868),
            '太原': (112.5492, 37.8573),
            '石家庄': (114.5025, 38.0455),
            '西安': (108.9398, 34.3416)  # Duplicate - keeping original
        }
    
    def geocode_address(self, address: str, region: str = "") -> Optional[Dict[str, float]]:
        """Mock geocoding that looks for city names in addresses."""
        # Look for known city names in the address
        for city, (lng, lat) in self.mock_coordinates.items():
            if city in address:
                # Add some random offset to make locations more spread out
                import random
                offset_lng = random.uniform(-0.01, 0.01)
                offset_lat = random.uniform(-0.01, 0.01)
                
                return {
                    'longitude': lng + offset_lng,
                    'latitude': lat + offset_lat
                }
        
        # If no city found, return coordinates for a random location in China
        # China coordinates: roughly 73°E to 135°E, 18°N to 53°N
        import random
        return {
            'longitude': random.uniform(73, 135),
            'latitude': random.uniform(18, 53)
        }
    
    def batch_geocode(self, addresses: List[str], region: str = "") -> List[Optional[Dict[str, float]]]:
        """Mock batch geocoding."""
        results = []
        for address in addresses:
            coords = self.geocode_address(address, region)
            results.append(coords)
        return results
    
    def reverse_geocode(self, longitude: float, latitude: float) -> Optional[str]:
        """Mock reverse geocoding."""
        return f"模拟位置 ({latitude:.4f}, {longitude:.4f})"