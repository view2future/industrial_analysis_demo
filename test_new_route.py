#!/usr/bin/env python3
"""
Test the new POI route using Flask test client
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_new_route():
    """Test the new POI route using Flask's test client"""
    with app.test_client() as client:
        response = client.get('/api/poi-data/chengdu-ai-pois.json')
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.content_type}")
        print(f"Response Length: {len(response.data)}")
        
        if response.status_code == 200:
            print("✓ Route is working correctly!")
            print(f"Response starts with: {response.data[:100]}")
        else:
            print(f"✗ Route returned {response.status_code}: {response.data[:200]}")

if __name__ == "__main__":
    test_new_route()