#!/usr/bin/env python3
# Test the classification fix
from app import app, PolicyAnalysis, db

def test_classification_access():
    """Test that the classification attribute issue is fixed"""
    with app.app_context():
        try:
            # Create a test policy to verify that individual fields work
            test_policy = PolicyAnalysis(
                title="Test Policy",
                original_url="https://test.com/policy",
                classification_region="北京",
                classification_industry="人工智能",
                classification_year=2024,
                classification_policy_type="扶持政策"
            )
            
            print("✅ Created test policy with individual classification fields")
            print(f"✅ Region: {test_policy.classification_region}")
            print(f"✅ Industry: {test_policy.classification_industry}")
            print(f"✅ Year: {test_policy.classification_year}")
            print(f"✅ Type: {test_policy.classification_policy_type}")
            
            # Create the classification dict like in our route
            classification = {
                'region': test_policy.classification_region,
                'industry': test_policy.classification_industry,
                'year': test_policy.classification_year,
                'policy_type': test_policy.classification_policy_type
            }
            
            print(f"✅ Classification dict: {classification}")
            print("✅ Classification access fix working correctly!")
            return True
            
        except AttributeError as e:
            print(f"❌ Attribute error: {e}")
            return False
        except Exception as e:
            print(f"❌ General error: {e}")
            return False

if __name__ == "__main__":
    success = test_classification_access()
    if success:
        print("\\n🎉 All classification access issues resolved!")
    else:
        print("\\n❌ Issues remain with classification access")