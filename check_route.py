#!/usr/bin/env python3
"""
Test the POI route by importing and checking for errors
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("App imported successfully")
    
    # Check if the file exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'output', 'poi_upload', 'chengdu-ai-pois.json')
    print(f"File path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} bytes")
    
    # Try to manually run the route function
    with app.app_context():
        result = app.view_functions['serve_local_poi_data']()
        print(f"Route function executed, result type: {type(result)}")
        print(f"Result: {result}")
        
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()