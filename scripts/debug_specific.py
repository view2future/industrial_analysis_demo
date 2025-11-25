#!/usr/bin/env python3
"""Debug the specific pattern matching issue"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.api_error_handler import api_error_handler, APIErrorType, APIService

def debug_specific():
    print("🔍 调试特定模式匹配问题")
    print("="*50)
    
    # Test the specific error that's failing
    error = Exception("配额已用完")
    service = APIService.KIMI
    
    print(f"测试错误: '{error}'")
    print(f"服务: {service.value}")
    
    # Check what patterns are available for this service
    service_patterns = api_error_handler.ERROR_PATTERNS.get(service, {})
    quota_patterns = service_patterns.get(APIErrorType.QUOTA_EXCEEDED, [])
    
    print(f"\nKimi 配额超限模式:")
    for pattern in quota_patterns:
        print(f"  - {pattern}")
    
    # Test each pattern individually
    error_message = str(error).lower()
    print(f"\n错误消息 (小写): '{error_message}'")
    
    for pattern in quota_patterns:
        match = re.search(pattern, error_message, re.IGNORECASE)
        print(f"模式 '{pattern}': {'✅ 匹配' if match else '❌ 不匹配'}")
        if match:
            print(f"   匹配到的文本: '{match.group()}'")
    
    # Test the full detection
    api_error = api_error_handler.detect_error_type(error, service)
    print(f"\n检测结果: {api_error.error_type.value}")
    print(f"期望结果: quota_exceeded")

if __name__ == '__main__':
    import re
    debug_specific()