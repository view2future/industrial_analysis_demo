#!/usr/bin/env python3
"""
测试缓存查找功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from demo.chromedriver_utils import ChromeDriverManagerOptimized

def test_cache_lookup():
    """测试缓存查找功能"""
    print("测试缓存查找功能...")
    
    # 创建ChromeDriverManagerOptimized实例
    manager = ChromeDriverManagerOptimized()
    
    # 测试直接从缓存中获取ChromeDriver路径
    driver_path = manager._get_cached_driver_path()
    
    if driver_path:
        print(f"✅ 找到缓存的ChromeDriver: {driver_path}")
        return True
    else:
        print("❌ 未找到缓存的ChromeDriver")
        
        # 调试信息
        import platform
        print(f"系统: {platform.system()}")
        print(f"机器架构: {platform.machine()}")
        
        # 检查缓存目录
        cache_paths = [
            os.path.join(os.getcwd(), '.wdm'),  # 项目目录缓存
            os.path.expanduser('~/.wdm'),       # 用户目录缓存
        ]
        
        for cache_path in cache_paths:
            print(f"检查缓存目录: {cache_path}")
            if os.path.exists(cache_path):
                print(f"  缓存目录存在")
                drivers_json_path = os.path.join(cache_path, 'drivers.json')
                print(f"  drivers.json路径: {drivers_json_path}")
                if os.path.exists(drivers_json_path):
                    print(f"  drivers.json存在")
                    import json
                    with open(drivers_json_path, 'r') as f:
                        metadata = json.load(f)
                    print(f"  metadata内容: {metadata}")
                else:
                    print(f"  drivers.json不存在")
            else:
                print(f"  缓存目录不存在")
        
        return False

if __name__ == "__main__":
    success = test_cache_lookup()
    sys.exit(0 if success else 1)