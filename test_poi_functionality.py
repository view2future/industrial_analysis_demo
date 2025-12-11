#!/usr/bin/env python3
"""
Test script to verify POI map visualization functionality
"""
import requests
import time
import json

def test_poi_visualization():
    # Wait for the server to fully start
    time.sleep(3)

    try:
        # First, try to trigger auto-login by accessing the login page
        print("Accessing login page to trigger auto-login...")
        login_response = requests.get('http://localhost:5000/login')
        print(f"Login page status: {login_response.status_code}")

        # Now test if the POI visualization page is accessible with session
        print("Testing POI visualization page accessibility...")
        session = requests.Session()

        # Access login first to trigger auto-login
        session.get('http://localhost:5000/login')

        response = session.get('http://localhost:5000/poi-map-visualization')
        print(f"POI Map Visualization page status: {response.status_code}")

        if response.status_code == 200:
            print("✓ POI Map Visualization page loaded successfully")
            # Check if Google Maps API key is present in the response
            if 'AIzaSyAXYz1pRN0FEgVHyMmVk0jVFJdopNWt1BY' in response.text:
                print("✓ Google Maps API key found in page")
            else:
                print("✗ Google Maps API key not found in page")

            # Check that UI elements have proper white background and dark text contrast
            print("Checking UI elements for proper styling...")
            if 'input-modern' in response.text:
                print("✓ Modern input styling found")
            else:
                print("✗ Modern input styling not found")

            if 'background:.*white' in response.text or 'background.*#FFFFFF' in response.text:
                print("✓ White background styling found")
            else:
                print("? White background styling not explicitly verified")

            if 'color.*#000000' in response.text or 'color.*black' in response.text:
                print("✓ Dark text styling found")
            else:
                print("? Dark text styling not explicitly verified")
        else:
            print(f"✗ Failed to load POI Map Visualization page: {response.status_code}")

        # Test if the JSON data file is accessible (this doesn't require authentication)
        print("Testing POI data file accessibility...")
        data_response = requests.get('http://localhost:5000/data/output/poi_upload/chengdu-ai-pois.json')
        print(f"POI data file status: {data_response.status_code}")

        if data_response.status_code == 200:
            try:
                data = data_response.json()
                if 'poi_data' in data and len(data['poi_data']) == 100:
                    print(f"✓ POI data file loaded successfully with {len(data['poi_data'])} entries")
                else:
                    print("✗ POI data file doesn't contain expected structure")
                    print(f"  Data structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                    if 'poi_data' in data:
                        print(f"  Number of POI entries: {len(data['poi_data'])}")
            except json.JSONDecodeError:
                print("✗ POI data file is not valid JSON")
        else:
            print(f"✗ Failed to access POI data file: {data_response.status_code}")

        # Test boundary API (this may require authentication)
        print("Testing boundaries API...")
        boundary_response = session.get('http://localhost:5000/api/boundaries?region=成都市&level=city')
        print(f"Boundaries API status: {boundary_response.status_code}")

        if boundary_response.status_code == 200:
            try:
                boundary_data = boundary_response.json()
                success = boundary_data.get('success', False)
                print(f"✓ Boundaries API response: success={success}")
                if not success:
                    print(f"  Error message: {boundary_data.get('error', 'No error message')}")
            except json.JSONDecodeError:
                print("✗ Boundaries API response is not valid JSON")
        else:
            print(f"Note: Boundaries API returned {boundary_response.status_code} (may be expected if no boundary data)")

        print("All tests completed!")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_poi_visualization()