#!/usr/bin/env python3
"""
Test the POI data route directly using Flask's debugging
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    # Enable debug mode to see more errors
    app.debug = True
    
    # Check if the file exists at runtime
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'output', 'poi_upload', 'chengdu-ai-pois.json')
    
    print(f"Checking file path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"Base dir: {base_dir}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Run the app on a different port to avoid conflicts
    app.run(host='0.0.0.0', port=5001, debug=True)