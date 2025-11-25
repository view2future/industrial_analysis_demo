#!/usr/bin/env python3
"""
Test script to verify the radar chart data access fix.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_radar_chart_data_access():
    """Test accessing radar chart data the correct way."""
    print("Testing radar chart data access patterns...")
    
    # Load the actual generated data
    with open('data/output/20251105_112200_analysis.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Test accessing radar chart data correctly
    try:
        # This is how the template should access the data
        if data['charts'] and data['charts'].get('ai_opportunities'):
            ai_data = data['charts']['ai_opportunities']
            print("AI Opportunities data structure:", ai_data)
            
            # Check if data[0] exists
            if 'data' in ai_data and len(ai_data['data']) > 0:
                first_data = ai_data['data'][0]
                print("First data item:", first_data)
                
                # Check if theta and r exist (correct fields for radar chart)
                if 'theta' in first_data:
                    print("theta data:", first_data['theta'])
                else:
                    print("theta field NOT found")
                    
                if 'r' in first_data:
                    print("r data:", first_data['r'])
                else:
                    print("r field NOT found")
                
                # Try to serialize with JSON (this is what the template does)
                try:
                    theta_json = json.dumps(first_data['theta'])
                    r_json = json.dumps(first_data['r'])
                    print("✅ theta and r data are JSON serializable")
                    print("theta JSON length:", len(theta_json))
                    print("r JSON length:", len(r_json))
                except Exception as e:
                    print(f"❌ Error serializing theta or r data: {e}")
                    return False
            else:
                print("❌ No data items found")
                return False
        else:
            print("❌ AI Opportunities chart not found or empty")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error accessing radar chart data: {e}")
        return False

def main():
    """Run the test."""
    print("🚀 Testing radar chart data access patterns...")
    print("=" * 60)
    
    if test_radar_chart_data_access():
        print("\n🎉 Radar chart data access test passed!")
        return 0
    else:
        print("\n⚠️  Radar chart data access test failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())