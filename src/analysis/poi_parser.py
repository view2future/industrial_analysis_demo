#!/usr/bin/env python3
"""
POI Document Parser - Handles parsing of various document formats for POI data
Supports JSON, Excel, and CSV formats for POI lists
"""

import json
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any
from io import StringIO

# Import coordinate conversion utilities
from src.utils.coordinate_converter import wgs84_to_gcj02

logger = logging.getLogger(__name__)


class PoiDocumentParser:
    """Parser for POI data from various document formats"""
    
    def __init__(self):
        pass
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a file and extract POI data
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            List of POI data dictionaries
        """
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.json':
            return self._parse_json(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return self._parse_excel(file_path)
        elif file_ext == '.csv':
            return self._parse_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _parse_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse JSON file containing POI data"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            pois = data
        elif isinstance(data, dict) and 'results' in data:
            pois = data['results']
        elif isinstance(data, dict) and 'poi_list' in data:
            pois = data['poi_list']
        else:
            raise ValueError("Invalid JSON format: expected array or object with 'results'/'poi_list' key")
        
        # Normalize the POI data to our standard format
        normalized_pois = []
        for poi in pois:
            normalized_poi = self._normalize_poi_data(poi)
            normalized_pois.append(normalized_poi)
        
        return normalized_pois
    
    def _parse_excel(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Excel file containing POI data"""
        df = pd.read_excel(file_path, dtype=str)  # Read as strings to handle mixed types
        
        # Convert to list of dictionaries
        pois = df.to_dict('records')
        
        # Normalize each record
        normalized_pois = []
        for poi in pois:
            normalized_poi = self._normalize_poi_data(poi)
            normalized_pois.append(normalized_poi)
        
        return normalized_pois
    
    def _parse_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse CSV file containing POI data"""
        df = pd.read_csv(file_path, dtype=str)  # Read as strings to handle mixed types
        
        # Convert to list of dictionaries
        pois = df.to_dict('records')
        
        # Normalize each record
        normalized_pois = []
        for poi in pois:
            normalized_poi = self._normalize_poi_data(poi)
            normalized_pois.append(normalized_poi)
        
        return normalized_pois
    
    def _normalize_poi_data(self, raw_poi: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize POI data to standard format"""
        # Handle different possible field names by mapping them to standard names
        poi = {}
        
        # Name field (could be 'name', '机构名称', 'title', etc.)
        name_fields = ['name', '机构名称', 'title', '名称', '机构名']
        for field in name_fields:
            if field in raw_poi and raw_poi[field]:
                poi['name'] = str(raw_poi[field]).strip()
                break
        else:
            poi['name'] = '未知机构'
        
        # Address field (could be 'address', '地址', 'location', 'full_address', etc.)
        address_fields = ['address', '地址', 'location', 'full_address', 'location_info']
        for field in address_fields:
            if field in raw_poi and raw_poi[field]:
                poi['address'] = str(raw_poi[field]).strip()
                break
        else:
            poi['address'] = '地址未知'
        
        # Type field (could be 'type', '类型', 'category', 'org_type', etc.)
        type_fields = ['type', '类型', 'category', 'org_type', '机构类型']
        for field in type_fields:
            if field in raw_poi and raw_poi[field]:
                poi['type'] = str(raw_poi[field]).strip()
                break
        else:
            poi['type'] = '其他'
        
        # Extract coordinates if available
        lng = None
        lat = None
        
        # 1) Try standard longitude/latitude fields
        lng_fields = ['lng', 'longitude', '经度', 'lng_value', 'x']
        for field in lng_fields:
            if field in raw_poi and raw_poi[field] and raw_poi[field] != '':
                try:
                    lng = float(str(raw_poi[field]))
                    break
                except (ValueError, TypeError):
                    continue
        
        lat_fields = ['lat', 'latitude', '纬度', 'lat_value', 'y']
        for field in lat_fields:
            if field in raw_poi and raw_poi[field] and raw_poi[field] != '':
                try:
                    lat = float(str(raw_poi[field]))
                    break
                except (ValueError, TypeError):
                    continue
        
        # 2) Try nested location structures
        if (lng is None or lat is None) and 'location' in raw_poi and raw_poi['location']:
            loc = raw_poi['location']
            # Dict with possible keys
            if isinstance(loc, dict):
                # direct keys
                for field in ['lng', 'longitude']:
                    if lng is None and field in loc and loc[field] not in (None, ''):
                        try:
                            lng = float(str(loc[field]))
                        except (ValueError, TypeError):
                            pass
                for field in ['lat', 'latitude']:
                    if lat is None and field in loc and loc[field] not in (None, ''):
                        try:
                            lat = float(str(loc[field]))
                        except (ValueError, TypeError):
                            pass
                # coordinates array
                if ('coordinates' in loc and isinstance(loc['coordinates'], (list, tuple)) and len(loc['coordinates']) >= 2):
                    try:
                        c0 = float(str(loc['coordinates'][0]))
                        c1 = float(str(loc['coordinates'][1]))
                        # Assume [lng, lat]
                        lng = c0 if lng is None else lng
                        lat = c1 if lat is None else lat
                    except (ValueError, TypeError):
                        pass
                # geometry with coordinates
                geom = loc.get('geometry') if isinstance(loc, dict) else None
                if isinstance(geom, dict) and 'coordinates' in geom and isinstance(geom['coordinates'], (list, tuple)) and len(geom['coordinates']) >= 2:
                    try:
                        c0 = float(str(geom['coordinates'][0]))
                        c1 = float(str(geom['coordinates'][1]))
                        lng = c0 if lng is None else lng
                        lat = c1 if lat is None else lat
                    except (ValueError, TypeError):
                        pass
            # String like "104.06,30.67" or "30.67,104.06"
            elif isinstance(loc, str):
                parts = [p.strip() for p in loc.replace('\u00a0', ' ').replace('\t', ' ').split(',')]
                if len(parts) >= 2:
                    try:
                        a = float(parts[0])
                        b = float(parts[1])
                        # Heuristic: prefer [lng, lat]
                        if -180 <= a <= 180 and -90 <= b <= 90:
                            lng = a if lng is None else lng
                            lat = b if lat is None else lat
                        elif -90 <= a <= 90 and -180 <= b <= 180:
                            # Looks like [lat, lng]
                            lng = b if lng is None else lng
                            lat = a if lat is None else lat
                    except (ValueError, TypeError):
                        pass
        
        # Set location with original/derived coordinates
        poi['location'] = {'lng': lng, 'lat': lat}

        # Convert coordinates from WGS-84 to GCJ-02 if available
        if lng is not None and lat is not None:
            gcj02_lng, gcj02_lat = wgs84_to_gcj02(lng, lat)
            poi['location'] = {'lng': gcj02_lng, 'lat': gcj02_lat}

        # Add other possible fields
        poi['distance'] = raw_poi.get('distance', 0)
        poi['tel'] = raw_poi.get('tel', raw_poi.get('电话', ''))
        poi['rating'] = raw_poi.get('rating', raw_poi.get('评分', 0))
        poi['region'] = raw_poi.get('region', raw_poi.get('区域', raw_poi.get('地区', '')))

        # Set tag to type if not provided
        poi['tag'] = raw_poi.get('tag', poi['type'])

        return poi


# Example usage and test function
def test_parser():
    """Test function for the parser"""
    import tempfile
    import os

    # Create test JSON file
    test_data = [
        {
            "name": "测试机构1",
            "address": "成都市高新区天府大道",
            "type": "高校",
            "lng": 104.06,
            "lat": 30.67
        },
        {
            "机构名称": "测试机构2",
            "地址": "成都市武侯区科华北路",
            "类型": "科研院所",
            "经度": 104.08,
            "纬度": 30.65
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, ensure_ascii=False)
        temp_path = f.name

    try:
        parser = PoiDocumentParser()
        result = parser.parse_file(temp_path)
        print(f"Parsed {len(result)} POIs from JSON file")
        for poi in result:
            print(f"  - {poi['name']}: {poi['address']} ({poi['type']}) - Location: {poi['location']}")
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    test_parser()