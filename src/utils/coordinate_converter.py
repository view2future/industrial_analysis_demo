#!/usr/bin/env python3
"""
Coordinate Conversion Utility
Converts between WGS-84 (standard GPS coordinates) and GCJ-02 (Mars coordinates used in China)
"""

import math

# Constants for coordinate conversion
PI = math.pi
EE = 0.00669342162296594323  # First eccentricity squared, e^2
A = 6378245.0  # Semi-major axis of the ellipsoid


def wgs84_to_gcj02(lon, lat):
    """
    Convert WGS-84 coordinates to GCJ-02 coordinates (Mars coordinates)
    
    Args:
        lon (float): Longitude in WGS-84
        lat (float): Latitude in WGS-84
    
    Returns:
        tuple: (longitude, latitude) in GCJ-02
    """
    if out_of_china(lon, lat):
        return lon, lat

    dlat = transform_lat(lon - 105.0, lat - 35.0)
    dlon = transform_lon(lon - 105.0, lat - 35.0)

    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)

    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlon = (dlon * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)

    return lon + dlon, lat + dlat


def gcj02_to_wgs84(lon, lat):
    """
    Convert GCJ-02 coordinates to WGS-84 coordinates
    
    Args:
        lon (float): Longitude in GCJ-02
        lat (float): Latitude in GCJ-02
    
    Returns:
        tuple: (longitude, latitude) in WGS-84
    """
    if out_of_china(lon, lat):
        return lon, lat

    dlat = transform_lat(lon - 105.0, lat - 35.0)
    dlon = transform_lon(lon - 105.0, lat - 35.0)

    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)

    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlon = (dlon * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)

    return lon - dlon, lat - dlat


def transform_lat(x, y):
    """
    Transform latitude for coordinate conversion
    """
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * PI) + 40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * PI) + 320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret


def transform_lon(x, y):
    """
    Transform longitude for coordinate conversion
    """
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * PI) + 40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * PI) + 300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0
    return ret


def out_of_china(lon, lat):
    """
    Check if coordinates are outside China (for which the GCJ-02 conversion should not be applied)
    
    Args:
        lon (float): Longitude
        lat (float): Latitude
    
    Returns:
        bool: True if coordinates are outside China
    """
    if lon < 72.004 or lon > 137.8347 or lat < 0.8293 or lat > 55.8271:
        return True
    return False


def convert_poi_coordinates(poi_list, source_system='WGS84', target_system='GCJ02'):
    """
    Convert coordinates for a list of POI objects
    
    Args:
        poi_list (list): List of POI objects with location coordinates
        source_system (str): Source coordinate system ('WGS84' or 'GCJ02')
        target_system (str): Target coordinate system ('WGS84' or 'GCJ02')
    
    Returns:
        list: List of POI objects with converted coordinates
    """
    if source_system == target_system:
        return poi_list
    
    converted_poi_list = []
    
    for poi in poi_list:
        # Make a copy of the POI to avoid modifying the original
        converted_poi = poi.copy()
        
        # Check if the POI has location coordinates
        if 'location' in converted_poi and 'lng' in converted_poi['location'] and 'lat' in converted_poi['location']:
            original_lng = converted_poi['location']['lng']
            original_lat = converted_poi['location']['lat']
            
            # Only convert if coordinates are present and not None
            if original_lng is not None and original_lat is not None:
                if source_system == 'WGS84' and target_system == 'GCJ02':
                    new_lng, new_lat = wgs84_to_gcj02(original_lng, original_lat)
                elif source_system == 'GCJ02' and target_system == 'WGS84':
                    new_lng, new_lat = gcj02_to_wgs84(original_lng, original_lat)
                else:
                    # Conversion not needed or unsupported
                    new_lng, new_lat = original_lng, original_lat
                
                # Update the coordinates
                converted_poi['location']['lng'] = new_lng
                converted_poi['location']['lat'] = new_lat
        
        converted_poi_list.append(converted_poi)
    
    return converted_poi_list


if __name__ == '__main__':
    # Example usage
    print("Coordinate Conversion Utility")
    print("WGS84 to GCJ02 example:")
    
    # Example coordinates (Beijing)
    wgs84_lon, wgs84_lat = 116.3974, 39.9092
    print(f"WGS84: ({wgs84_lon}, {wgs84_lat})")
    
    gcj02_lon, gcj02_lat = wgs84_to_gcj02(wgs84_lon, wgs84_lat)
    print(f"GCJ02: ({gcj02_lon}, {gcj02_lat})")
    
    # Convert back to verify
    back_lon, back_lat = gcj02_to_wgs84(gcj02_lon, gcj02_lat)
    print(f"Back to WGS84: ({back_lon}, {back_lat})")