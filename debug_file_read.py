#!/usr/bin/env python3
"""
Quick test to check the application and route
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# This is a debug approach that manually tests the function logic
def debug_route_logic():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'output', 'poi_upload', 'chengdu-ai-pois.json')
    
    print(f"Checking file path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
            print(f"File loaded successfully, keys: {list(data.keys())}")
            print(f"Number of POI entries: {len(data.get('poi_data', []))}")
            
            # Check the first entry
            if 'poi_data' in data and data['poi_data']:
                first_entry = data['poi_data'][0]
                print(f"First entry: {list(first_entry.keys()) if isinstance(first_entry, dict) else type(first_entry)}")
                
        except Exception as e:
            print(f"Error reading file: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("File does not exist!")

if __name__ == "__main__":
    debug_route_logic()