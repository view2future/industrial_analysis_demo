#!/usr/bin/env python3
"""Debug the pattern matching for '配额已用完'"""

import re

def test_pattern():
    error_message = "配额已用完"
    pattern = r'配额.*不足'
    
    print(f"错误消息: '{error_message}'")
    print(f"正则表达式: '{pattern}'")
    
    match = re.search(pattern, error_message, re.IGNORECASE)
    print(f"匹配结果: {match}")
    
    if match:
        print(f"匹配到的文本: '{match.group()}'")
    else:
        print("❌ 没有匹配")
        
    # Test alternative patterns
    alternative_patterns = [
        r'配额.*已用完',
        r'配额已用完',
        r'配额.*不足|配额.*已用完',
        r'配额.*(不足|已用完)'
    ]
    
    print(f"\n🧪 测试替代模式:")
    for alt_pattern in alternative_patterns:
        alt_match = re.search(alt_pattern, error_message, re.IGNORECASE)
        print(f"模式 '{alt_pattern}': {'✅ 匹配' if alt_match else '❌ 不匹配'}")

if __name__ == '__main__':
    test_pattern()