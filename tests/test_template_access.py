#!/usr/bin/env python3
"""
Test script to verify template data access patterns.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_template_data_access():
    """Test accessing chart data the same way the template does."""
    print("Testing template data access patterns...")
    
    # Load the actual generated data
    with open('data/output/20251105_112200_analysis.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("All chart keys:", list(data['charts'].keys()))
    
    # Test accessing data the same way the template does
    try:
        # This is how the template accesses the data
        if data['charts'] and data['charts'].get('ai_opportunities'):
            ai_data = data['charts']['ai_opportunities']
            print("AI Opportunities data structure:", ai_data)
            
            # Check if data[0] exists
            if 'data' in ai_data and len(ai_data['data']) > 0:
                first_data = ai_data['data'][0]
                print("First data item:", first_data)
                
                # Check if x and y exist
                if 'x' in first_data:
                    print("x data:", first_data['x'])
                else:
                    print("x field NOT found")
                    
                if 'y' in first_data:
                    print("y data:", first_data['y'])
                else:
                    print("y field NOT found")
                
                # Try to serialize with JSON (this is what the template does)
                try:
                    x_json = json.dumps(first_data['x'])
                    y_json = json.dumps(first_data['y'])
                    print("✅ x and y data are JSON serializable")
                    print("x JSON:", x_json)
                    print("y JSON:", y_json)
                except Exception as e:
                    print(f"❌ Error serializing x or y data: {e}")
                    return False
            else:
                print("❌ No data items found")
                return False
        else:
            print("❌ AI Opportunities chart not found or empty")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error accessing chart data: {e}")
        return False

def main():
    """Run the test."""
    print("🚀 Testing template data access patterns...")
    print("=" * 60)
    
    if test_template_data_access():
        print("\n🎉 Template data access test passed!")
        return 0
    else:
        print("\n⚠️  Template data access test failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())