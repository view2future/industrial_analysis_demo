#!/usr/bin/env python3
"""
测试Selenium是否能连接到Flask应用
"""

import time
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_selenium_connection():
    """测试Selenium连接"""
    print("启动Flask应用...")
    # 启动Flask应用
    app_process = subprocess.Popen(
        ["python3", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待应用启动
    time.sleep(5)
    
    try:
        print("设置Chrome浏览器...")
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 创建WebDriver实例
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome浏览器设置成功")
        
        print("访问Flask应用...")
        # 访问Flask应用
        driver.get("http://localhost:5000")
        print("✅ 成功连接到Flask应用")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    finally:
        # 停止Flask应用
        app_process.terminate()
        app_process.wait()

if __name__ == "__main__":
    success = test_selenium_connection()
    sys.exit(0 if success else 1)