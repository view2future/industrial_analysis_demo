#!/usr/bin/env python3
"""Debug the fallback mechanism"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.api_error_handler import api_error_handler, APIService

def debug_fallback():
    print("🔍 调试服务回退机制")
    print("="*50)
    
    # Test the exact scenario from the test
    available_services = [APIService.KIMI, APIService.GEMINI, APIService.DOUBAO]
    
    print(f"可用服务: {[s.value for s in available_services]}")
    print(f"服务回退顺序: {[s.value for s in api_error_handler.service_fallback_order]}")
    
    # Test 1: Fallback from Kimi
    print(f"\n1️⃣ 测试 Kimi 回退:")
    fallback_service = api_error_handler.get_fallback_service(APIService.KIMI, available_services)
    print(f"   失败服务: {APIService.KIMI.value}")
    print(f"   回退服务: {fallback_service.value if fallback_service else 'None'}")
    print(f"   期望服务: gemini")
    
    # Show the logic
    fallback_order = [s for s in api_error_handler.service_fallback_order if s != APIService.KIMI]
    print(f"   回退顺序 (排除Kimi): {[s.value for s in fallback_order]}")
    for service in fallback_order:
        if service in available_services:
            print(f"   ✅ 找到可用服务: {service.value}")
            break
    
    # Test 2: Fallback from Gemini
    print(f"\n2️⃣ 测试 Gemini 回退:")
    fallback_service = api_error_handler.get_fallback_service(APIService.GEMINI, available_services)
    print(f"   失败服务: {APIService.GEMINI.value}")
    print(f"   回退服务: {fallback_service.value if fallback_service else 'None'}")
    print(f"   期望服务: doubao")
    
    # Show the logic
    fallback_order = [s for s in api_error_handler.service_fallback_order if s != APIService.GEMINI]
    print(f"   回退顺序 (排除Gemini): {[s.value for s in fallback_order]}")
    for service in fallback_order:
        if service in available_services:
            print(f"   ✅ 找到可用服务: {service.value}")
            break
    
    # Test 3: Limited services
    print(f"\n3️⃣ 测试有限服务回退:")
    limited_services = [APIService.KIMI, APIService.GEMINI]
    fallback_service = api_error_handler.get_fallback_service(APIService.KIMI, limited_services)
    print(f"   可用服务: {[s.value for s in limited_services]}")
    print(f"   失败服务: {APIService.KIMI.value}")
    print(f"   回退服务: {fallback_service.value if fallback_service else 'None'}")
    print(f"   期望服务: gemini")
    
    # Test 4: No available fallback
    print(f"\n4️⃣ 测试无可用回退:")
    no_fallback_services = [APIService.KIMI]  # Only the failed service
    fallback_service = api_error_handler.get_fallback_service(APIService.KIMI, no_fallback_services)
    print(f"   可用服务: {[s.value for s in no_fallback_services]}")
    print(f"   失败服务: {APIService.KIMI.value}")
    print(f"   回退服务: {fallback_service}")
    print(f"   期望结果: None")

if __name__ == '__main__':
    debug_fallback()