#!/usr/bin/env python3
"""
Simple test to check the POI route functionality
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from app import app

def test_route_directly():
    """Test the route directly within the Flask app context"""
    with app.test_client() as client:
        response = client.get('/data/output/poi_upload/chengdu-ai-pois.json')
        print(f"Status Code: {response.status_code}")
        print(f"Response Data (first 200 chars): {response.data[:200]}")
        print(f"Content Type: {response.content_type}")
        
        # Check the raw response for any error details
        if response.status_code == 404:
            print("Route not found - possible issues:")
            print("1. Route is being overridden by another route")
            print("2. There's an error in the route function")
            print("3. The function name conflicts with another function")

if __name__ == "__main__":
    test_route_directly()