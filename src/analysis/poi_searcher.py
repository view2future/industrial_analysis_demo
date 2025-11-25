#!/usr/bin/env python3
"""
POI (Points of Interest) Search and Processing Module
Handles POI data search, processing, and visualization for regional industry analysis
"""

import os
import json
import logging
import pandas as pd
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlencode

# Import coordinate conversion utilities
from src.utils.coordinate_converter import wgs84_to_gcj02

logger = logging.getLogger(__name__)


class BaiduPoiSearcher:
    """Class to handle Baidu Map POI search operations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.map.baidu.com/place/v2/search"
    
    def search_poi_by_region_and_keywords(self, region: str, keywords: List[str], 
                                        page_size: int = 20, page_num: int = 0) -> List[Dict]:
        """
        Search POIs by region and keywords using Baidu Map API
        
        Args:
            region: Target region (province/city/district)
            keywords: List of keywords to search for
            page_size: Number of results per page (max 20)
            page_num: Page number (0-based)
        
        Returns:
            List of POI data
        """
        all_results = []
        
        for keyword in keywords:
            try:
                params = {
                    'query': keyword,
                    'region': region,
                    'output': 'json',
                    'ak': self.api_key,
                    'page_size': min(page_size, 20),  # Baidu API max is 20
                    'page_num': page_num
                }
                
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 0:  # Success
                    pois = data.get('results', [])
                    for poi in pois:
                        # Extract relevant information
                        poi_data = {
                            'name': poi.get('name', ''),
                            'address': poi.get('address', ''),
                            'type': poi.get('detail_info', {}).get('type', ''),
                            'location': {
                                'lng': poi.get('location', {}).get('lng'),
                                'lat': poi.get('location', {}).get('lat')
                            },
                            'distance': poi.get('detail_info', {}).get('distance', 0),
                            'tag': keyword,
                            'tel': poi.get('telephone', ''),
                            'detail_url': poi.get('detail_info', {}).get('detail_url', ''),
                            'price': poi.get('detail_info', {}).get('price', ''),
                            'overall_rating': poi.get('detail_info', {}).get('overall_rating', 0)
                        }
                        all_results.append(poi_data)
                else:
                    logger.error(f"Baidu API error for keyword '{keyword}': {data.get('message', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Error searching POI for keyword '{keyword}': {str(e)}")
                continue
        
        return all_results
    
    def batch_search_poi(self, region: str, keywords: List[str], 
                        max_results: int = 100) -> List[Dict]:
        """
        Perform batch search to get more results
        
        Args:
            region: Target region
            keywords: List of keywords
            max_results: Maximum number of results to return
        
        Returns:
            List of POI data
        """
        all_results = []
        page_num = 0
        page_size = 20
        
        while len(all_results) < max_results:
            batch_results = self.search_poi_by_region_and_keywords(
                region, keywords, page_size, page_num
            )
            
            if not batch_results:
                break  # No more results
                
            all_results.extend(batch_results)
            page_num += 1
            
            # Limit the total number of results
            if len(all_results) >= max_results:
                all_results = all_results[:max_results]
                break
        
        return all_results


class GooglePlacesSearcher:
    """Class to handle Google Places API search operations"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    def _get_region_bounds(self, region: str) -> Optional[Dict]:
        """
        Get precise bounds for a region using Google Geocoding API
        """
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': region,
            'key': self.api_key
        }

        try:
            response = requests.get(geocode_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'OK' and data.get('results'):
                # Find the result that best matches the requested region
                for result in data['results']:
                    # Check if the result matches the requested region type
                    address_components = result.get('address_components', [])
                    formatted_address = result.get('formatted_address', '')

                    # Verify this is the correct administrative level by checking address components
                    if region in formatted_address:
                        geometry = result.get('geometry', {})
                        bounds = geometry.get('bounds', {})

                        if bounds:
                            return {
                                'northeast': bounds.get('northeast', {}),
                                'southwest': bounds.get('southwest', {}),
                                'center': geometry.get('location', {}),
                                'place_id': result.get('place_id', ''),
                                'formatted_address': formatted_address
                            }

        except Exception as e:
            logger.error(f"Error getting region bounds for {region}: {str(e)}")

        return None

    def _point_in_bounds(self, point: Dict, bounds: Dict) -> bool:
        """
        Check if a point is within the specified bounds
        """
        if not point or not bounds:
            return False

        lat = point.get('lat')
        lng = point.get('lng')

        if lat is None or lng is None:
            return False

        # Get bounds coordinates
        ne_lat = bounds['northeast'].get('lat')
        ne_lng = bounds['northeast'].get('lng')
        sw_lat = bounds['southwest'].get('lat')
        sw_lng = bounds['southwest'].get('lng')

        if None in [ne_lat, ne_lng, sw_lat, sw_lng]:
            return False

        # Check if point is within bounds (for rectangular bounds)
        # Note: This is an approximation for complex administrative boundaries
        return (sw_lat <= lat <= ne_lat) and (sw_lng <= lng <= ne_lng)

    def _expand_keywords(self, keyword: str) -> List[str]:
        """
        Expand keywords to include related terms for more comprehensive search
        """
        keyword_expansions = {
            '人工智能': ['AI', 'artificial intelligence', 'machine learning', '智能科技', '算法', '大数据'],
            '文旅': ['tourism', 'culture', 'tourist', 'cultural', 'heritage', 'museum', 'attraction', 'recreation'],
            '制造': ['manufacturing', 'production', 'factory', 'industrial', 'industries', 'manufacturer', 'industry'],
            '高校': ['university', 'college', 'school', 'education', 'institute', 'academic'],
            '科研院所': ['research', 'institute', 'laboratory', 'academy', 'R&D', 'science', 'scientific']
        }

        expanded = [keyword]  # Include original keyword
        if keyword in keyword_expansions:
            expanded.extend(keyword_expansions[keyword])

        return expanded

    def search_poi_by_region_and_keywords(self, region: str, keywords: List[str],
                                        page_size: int = 20, page_num: int = 0) -> List[Dict]:
        """
        Search POIs by region and keywords using Google Places API with precise bounds

        Args:
            region: Target region (province/city/district)
            keywords: List of keywords to search for
            page_size: Number of results per page
            page_num: Page number (for pagination handling)

        Returns:
            List of POI data
        """
        all_results = []

        # Get precise bounds for the region
        region_bounds = self._get_region_bounds(region)
        bounds_available = region_bounds is not None

        for keyword in keywords:
            # Expand the keyword to include related terms for comprehensive search
            expanded_keywords = self._expand_keywords(keyword)

            for expanded_keyword in expanded_keywords:
                if len(all_results) >= page_size:
                    break

                try:
                    # Create search query
                    query = f"{expanded_keyword} {region}"

                    params = {
                        'query': query,
                        'key': self.api_key
                    }

                    # Add location bias using the region bounds if available
                    if bounds_available:
                        northeast = region_bounds['northeast']
                        southwest = region_bounds['southwest']

                        # Calculate center and radius from bounds
                        center_lat = (northeast['lat'] + southwest['lat']) / 2
                        center_lng = (northeast['lng'] + southwest['lng']) / 2

                        # Calculate approximate radius based on bounds
                        lat_diff = abs(northeast['lat'] - southwest['lat'])
                        lng_diff = abs(northeast['lng'] - southwest['lng'])
                        # Convert to meters (approximation)
                        radius = int(max(lat_diff, lng_diff) * 111000)  # Rough conversion: 1 degree ≈ 111 km
                        radius = max(radius, 5000)  # Minimum 5km radius
                        radius = min(radius, 50000)  # Maximum 50km radius

                        params['locationbias'] = f"circle:{radius}@{center_lat},{center_lng}"

                    response = requests.get(self.base_url, params=params)
                    response.raise_for_status()

                    data = response.json()

                    if data.get('status') == 'OK':
                        results = data.get('results', [])
                        for place in results:
                            if len(all_results) >= page_size:
                                break

                            # Get the location of the place
                            location = place.get('geometry', {}).get('location', {})
                            poi_lat = location.get('lat')
                            poi_lng = location.get('lng')

                            # If bounds are available, filter results to only include those within the bounds
                            if bounds_available and poi_lat is not None and poi_lng is not None:
                                point = {'lat': poi_lat, 'lng': poi_lng}
                                if not self._point_in_bounds(point, region_bounds):
                                    continue  # Skip this result if it's outside the bounds

                            # Convert coordinates from WGS-84 to GCJ-02 for displaying on Chinese maps
                            gcj02_lng, gcj02_lat = wgs84_to_gcj02(poi_lng, poi_lat) if poi_lng and poi_lat else (poi_lng, poi_lat)

                            # Extract relevant information similar to Baidu format
                            poi_data = {
                                'name': place.get('name', ''),
                                'address': place.get('formatted_address', ''),
                                'type': place.get('types', ['unknown'])[0] if place.get('types') else 'unknown',
                                'location': {
                                    'lng': gcj02_lng,
                                    'lat': gcj02_lat
                                },
                                'distance': 0,  # Google Places doesn't directly provide distance like Baidu
                                'tag': keyword,  # Use original keyword as tag
                                'tel': place.get('formatted_phone_number', ''),
                                'detail_url': f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id', '')}",
                                'price': place.get('price_level', ''),
                                'overall_rating': place.get('rating', 0),
                                'place_id': place.get('place_id', ''),
                                'expanded_keyword': expanded_keyword  # Track which expanded term found this result
                            }
                            all_results.append(poi_data)
                    else:
                        logger.info(f"Google Places API returned no results for query '{query}': {data.get('error_message', data.get('status'))}")

                except Exception as e:
                    logger.error(f"Error searching POI for keyword '{expanded_keyword}' with Google Places: {str(e)}")
                    continue

            if len(all_results) >= page_size:
                break

        return all_results

    def batch_search_poi(self, region: str, keywords: List[str],
                        max_results: int = 100) -> List[Dict]:
        """
        Perform batch search to get more results using Google Places API with precise bounds
        and comprehensive keyword expansion

        Args:
            region: Target region
            keywords: List of keywords
            max_results: Maximum number of results to return

        Returns:
            List of POI data
        """
        all_results = []

        # Get precise bounds for the region
        region_bounds = self._get_region_bounds(region)
        bounds_available = region_bounds is not None

        for keyword in keywords:
            if len(all_results) >= max_results:
                break

            # Expand the keyword to include related terms for comprehensive search
            expanded_keywords = self._expand_keywords(keyword)

            for expanded_keyword in expanded_keywords:
                if len(all_results) >= max_results:
                    break

                try:
                    # Create search query
                    query = f"{expanded_keyword} {region}"

                    params = {
                        'query': query,
                        'key': self.api_key
                    }

                    # Add location bias using the region bounds if available
                    if bounds_available:
                        northeast = region_bounds['northeast']
                        southwest = region_bounds['southwest']

                        # Calculate center and radius from bounds
                        center_lat = (northeast['lat'] + southwest['lat']) / 2
                        center_lng = (northeast['lng'] + southwest['lng']) / 2

                        # Calculate approximate radius based on bounds
                        lat_diff = abs(northeast['lat'] - southwest['lat'])
                        lng_diff = abs(northeast['lng'] - southwest['lng'])
                        # Convert to meters (approximation)
                        radius = int(max(lat_diff, lng_diff) * 111000)  # Rough conversion: 1 degree ≈ 111 km
                        radius = max(radius, 5000)  # Minimum 5km radius
                        radius = min(radius, 50000)  # Maximum 50km radius

                        params['locationbias'] = f"circle:{radius}@{center_lat},{center_lng}"

                    response = requests.get(self.base_url, params=params)
                    response.raise_for_status()

                    data = response.json()

                    if data.get('status') == 'OK':
                        results = data.get('results', [])
                        for place in results:
                            if len(all_results) >= max_results:
                                break

                            # Get the location of the place
                            location = place.get('geometry', {}).get('location', {})
                            poi_lat = location.get('lat')
                            poi_lng = location.get('lng')

                            # If bounds are available, filter results to only include those within the bounds
                            if bounds_available and poi_lat is not None and poi_lng is not None:
                                point = {'lat': poi_lat, 'lng': poi_lng}
                                if not self._point_in_bounds(point, region_bounds):
                                    continue  # Skip this result if it's outside the bounds

                            # Convert coordinates from WGS-84 to GCJ-02 for displaying on Chinese maps
                            gcj02_lng, gcj02_lat = wgs84_to_gcj02(poi_lng, poi_lat) if poi_lng and poi_lat else (poi_lng, poi_lat)

                            # Extract relevant information similar to Baidu format
                            poi_data = {
                                'name': place.get('name', ''),
                                'address': place.get('formatted_address', ''),
                                'type': place.get('types', ['unknown'])[0] if place.get('types') else 'unknown',
                                'location': {
                                    'lng': gcj02_lng,
                                    'lat': gcj02_lat
                                },
                                'distance': 0,  # Google Places doesn't directly provide distance like Baidu
                                'tag': keyword,  # Use original keyword as tag
                                'tel': place.get('formatted_phone_number', ''),
                                'detail_url': f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id', '')}",
                                'price': place.get('price_level', ''),
                                'overall_rating': place.get('rating', 0),
                                'place_id': place.get('place_id', ''),
                                'expanded_keyword': expanded_keyword  # Track which expanded term found this result
                            }
                            all_results.append(poi_data)
                    else:
                        logger.info(f"Google Places API returned no results for query '{query}': {data.get('error_message', data.get('status'))}")

                except Exception as e:
                    logger.error(f"Error searching POI for keyword '{expanded_keyword}' with Google Places: {str(e)}")
                    continue

        return all_results[:max_results]


class PoiDataProcessor:
    """Class to process and manipulate POI data"""
    
    @staticmethod
    def calculate_statistics(poi_data: List[Dict]) -> Dict:
        """Calculate statistics for POI data"""
        if not poi_data:
            return {}
        
        # Count by type
        type_counts = {}
        for poi in poi_data:
            poi_type = poi.get('type', '未知类型')
            type_counts[poi_type] = type_counts.get(poi_type, 0) + 1
        
        # Calculate geographic bounds
        lats = [poi['location']['lat'] for poi in poi_data if poi['location'].get('lat')]
        lngs = [poi['location']['lng'] for poi in poi_data if poi['location'].get('lng')]
        
        bounds = {}
        if lats and lngs:
            bounds = {
                'min_lat': min(lats),
                'max_lat': max(lats),
                'min_lng': min(lngs),
                'max_lng': max(lngs)
            }
        
        return {
            'total_count': len(poi_data),
            'type_distribution': type_counts,
            'geographic_bounds': bounds,
            'region_coverage': len(set([poi.get('region', '') for poi in poi_data if poi.get('region')]))
        }
    
    @staticmethod
    def generate_heatmap_data(poi_data: List[Dict]) -> List[Dict]:
        """Generate data for heatmap visualization"""
        heatmap_data = []
        
        for poi in poi_data:
            if poi['location'].get('lng') and poi['location'].get('lat'):
                heatmap_data.append({
                    'lng': poi['location']['lng'],
                    'lat': poi['location']['lat'],
                    'count': 1  # Could be weighted based on importance
                })
        
        return heatmap_data
    
    @staticmethod
    def generate_cluster_data(poi_data: List[Dict]) -> List[Dict]:
        """Generate data for cluster visualization"""
        # For clustering, we'll group nearby POIs
        clusters = []
        
        # This is a simple implementation - in a real scenario, 
        # you'd use clustering algorithms like K-means
        for i, poi in enumerate(poi_data):
            if poi['location'].get('lng') and poi['location'].get('lat'):
                clusters.append({
                    'id': i,
                    'lng': poi['location']['lng'],
                    'lat': poi['location']['lat'],
                    'name': poi['name'],
                    'type': poi['type'],
                    'size': 1
                })
        
        return clusters


class PoiExporter:
    """Class to handle POI data export"""
    
    @staticmethod
    def export_to_json(poi_data: List[Dict], export_path: str) -> str:
        """Export POI data to JSON file"""
        export_dir = Path(export_path).parent
        export_dir.mkdir(parents=True, exist_ok=True)
        
        data = {
            'export_time': pd.Timestamp.now().isoformat(),
            'total_count': len(poi_data),
            'poi_data': poi_data
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return export_path
    
    @staticmethod
    def export_to_excel(poi_data: List[Dict], export_path: str) -> str:
        """Export POI data to Excel file"""
        export_dir = Path(export_path).parent
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to DataFrame
        df_data = []
        for poi in poi_data:
            row = {
                '机构名称': poi.get('name', ''),
                '地址': poi.get('address', ''),
                '类型': poi.get('type', ''),
                '标签': poi.get('tag', ''),
                '经度': poi['location'].get('lng', ''),
                '纬度': poi['location'].get('lat', ''),
                '距离(米)': poi.get('distance', ''),
                '电话': poi.get('tel', ''),
                '评分': poi.get('overall_rating', ''),
                '详情链接': poi.get('detail_url', '')
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='POI数据', index=False)
            
            # Also create a summary sheet
            summary_data = {
                '项目': ['总机构数', '数据导出时间'],
                '数值': [len(poi_data), pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
        
        return export_path