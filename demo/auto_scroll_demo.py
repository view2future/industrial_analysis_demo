#!/usr/bin/env python3
"""
自动化滚动演示系统
根据新需求实现的演示程序
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

# 设置webdriver-manager环境变量以优化性能
# 延长缓存有效期至7天
os.environ['WDM_CACHE_VALID_RANGE'] = '7'
# 启用本地缓存
os.environ['WDM_LOCAL'] = '1'
# 设置缓存路径到项目目录
os.environ['WDM_CACHE_PATH'] = str(os.path.join(os.path.dirname(__file__), '.wdm'))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkipVersionCheckCacheManager(DriverCacheManager):
    """跳过版本检查的缓存管理器"""
    
    def __init__(self, root_dir=None, valid_range=1, file_manager=None):
        # 设置一个非常大的有效范围，实际上总是认为缓存有效
        super().__init__(root_dir, 365*100, file_manager)  # 100年有效期
    
    def __is_valid(self, driver_info):
        """重写验证方法，总是返回True"""
        return True  # 总是认为缓存有效

class ScrollDemoSystem:
    def __init__(self):
        self.driver = None
        
    def setup_chrome_driver(self):
        """设置Chrome浏览器"""
        logger.info("设置Chrome浏览器...")
        try:
            # 直接使用已缓存的ChromeDriver，跳过版本检查
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--start-maximized")
            
            # 直接使用已缓存的ChromeDriver路径
            chromedriver_path = os.path.expanduser("~/.wdm/drivers/chromedriver/mac64/141.0.7390.122/chromedriver-mac-arm64/chromedriver")
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome浏览器设置成功")
            return True
        except Exception as e:
            logger.error(f"设置Chrome浏览器失败: {e}")
            return False
    
    def scroll_page(self, duration):
        """滚动页面指定时间（秒）"""
        logger.info(f"开始滚动页面 {duration} 秒...")
        start_time = time.time()
        current_scroll = 0
        
        while time.time() - start_time < duration:
            # 每次向下滚动100像素
            self.driver.execute_script(f"window.scrollTo(0, {current_scroll});")
            current_scroll += 100
            time.sleep(0.1)  # 控制滚动速度
            
        logger.info(f"页面滚动 {duration} 秒完成")
    
    def run_demo(self):
        """运行滚动演示"""
        logger.info("开始自动滚动演示...")
        
        try:
            # 1. 设置Chrome浏览器
            if not self.setup_chrome_driver():
                return False
            
            # 2. 访问首页并滚动3秒
            logger.info("访问首页...")
            self.driver.get("http://localhost:5000")
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 滚动3秒
            self.scroll_page(3)
            
            # 3. 进入v3_roadmap页面并滚动5秒
            logger.info("进入v3_roadmap页面...")
            self.driver.get("http://localhost:5000/v3_roadmap")
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 滚动5秒
            self.scroll_page(5)
            
            # 4. 进入upload页面并滚动5秒
            logger.info("进入upload页面...")
            self.driver.get("http://localhost:5000/upload")
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 滚动5秒
            self.scroll_page(5)
            
            logger.info("自动滚动演示完成！")
            return True
            
        except Exception as e:
            logger.error(f"自动滚动演示出错: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理资源...")
        
        # 关闭浏览器
        if self.driver:
            self.driver.quit()
        
        logger.info("资源清理完成")

def main():
    """主函数"""
    logger.info("启动自动化滚动演示系统")
    
    # 创建演示系统
    demo_system = ScrollDemoSystem()
    
    # 运行演示
    success = demo_system.run_demo()
    
    if success:
        logger.info("演示成功完成！")
    else:
        logger.error("演示失败")

if __name__ == "__main__":
    main()