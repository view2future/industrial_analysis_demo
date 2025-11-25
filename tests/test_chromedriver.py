#!/usr/bin/env python3
"""
测试ChromeDriver是否可用
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_chromedriver():
    """测试ChromeDriver"""
    print("测试ChromeDriver...")
    try:
        # 使用优化的ChromeDriver管理器，跳过版本检查
        from demo.chromedriver_utils import get_chrome_driver
        
        # 尝试创建WebDriver实例，跳过版本检查
        driver = get_chrome_driver(headless=True, skip_version_check=True)
        print("✅ ChromeDriver正常工作")
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chromedriver()
    sys.exit(0 if success else 1)