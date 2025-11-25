import pytest
import json
import time

def test_streaming_endpoint(client):
    """Test the streaming endpoint directly"""
    print("Testing streaming endpoint...")
    
    url = "/streaming/api/stream/generate-report"
    payload = {
        "city": "北京",
        "industry": "人工智能",
        "llm_service": "kimi",
        "additional_context": ""
    }
    
    try:
        # Use client.post for Flask test client, remove stream=True and timeout
        r = client.post(url, json=payload)
        assert r.status_code == 200
        
        # For test client, response.data contains the full response
        response_data = r.data.decode('utf-8')
        print(response_data)
        
        # Check if the response contains expected SSE events
        assert 'event: generation_start' in response_data
        assert 'event: report_chunk' in response_data
        assert 'event: report_complete' in response_data
        
        print("\nAPI 流式传输成功。")
    except Exception as e:
        pytest.fail(f"API 流式传输失败: {e}")

def test_streaming_page_loads(client):
    """Test the streaming page loading"""
    print("\nTesting streaming page...")
    
    url = "/streaming-generate-report"
    params = {
        "city": "成都",
        "industry": "生物医药",
        "llm_service": "kimi"
    }
    
    try:
        # Use client.get for Flask test client, remove timeout
        response = client.get(url, query_string=params)
        assert response.status_code == 200
        content = response.text
        
        # Check for key elements
        checks = {
            "streaming container": "streaming-container" in content,
            "auto-start script": "Auto-starting streaming" in content,
            "retry button": "retry-streaming" in content,
            "city parameter": "成都" in content,
            "industry parameter": "生物医药" in content,
        }
        
        print("Page content checks:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}")
            assert result, f"Missing {check} in page content"
            
        # Check if JavaScript is properly structured
        if "Auto-starting streaming" in content:
            print("✅ Auto-start mechanism is present")
        else:
            print("❌ Auto-start mechanism missing")
            pytest.fail("Auto-start mechanism missing")
            
    except Exception as e:
        pytest.fail(f"Page load failed: {e}")