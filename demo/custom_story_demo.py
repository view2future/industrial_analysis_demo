#!/usr/bin/env python3
"""
自定义故事线演示系统
根据用户指定的故事线执行自动化演示
"""

import os
import sys
import time
import logging
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('custom_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CustomStoryDemo:
    def __init__(self):
        self.app_process = None
        self.driver = None
        self.project_root = Path(__file__).parent.parent.resolve()
        
    def start_flask_app(self):
        """启动Flask应用"""
        logger.info("启动Flask应用...")
        try:
            # 使用app.py启动应用，指定端口为5000
            env = dict(os.environ, PORT="5000")
            self.app_process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            # 等待应用启动
            time.sleep(8)
            logger.info("Flask应用启动成功")
            return True
        except Exception as e:
            logger.error(f"启动Flask应用失败: {e}")
            return False
    
    def setup_chrome_driver(self):
        """设置Chrome浏览器"""
        logger.info("设置Chrome浏览器...")
        try:
            # 首先尝试使用系统已安装的ChromeDriver
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome浏览器设置成功")
            return True
        except Exception as e:
            logger.warning(f"使用系统ChromeDriver失败: {e}")
            try:
                # 如果系统ChromeDriver失败，尝试使用webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # 自动下载并使用兼容的ChromeDriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Chrome浏览器设置成功")
                return True
            except Exception as e2:
                logger.error(f"设置Chrome浏览器失败: {e2}")
                return False
    
    def demo_homepage(self):
        """演示首页 - 从上到下滑动鼠标，完整展示首页，用两秒钟时间"""
        logger.info("演示首页...")
        try:
            self.driver.get("http://localhost:5000")
            
            # 等待页面加载
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                logger.warning(f"首页可能未完全加载，继续演示: {e}")
            
            # 从上到下滑动页面，完整展示首页
            # 获取页面总高度
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 分步骤滚动，模拟鼠标滑动效果
            scroll_steps = 10
            step_height = total_height // scroll_steps
            
            for i in range(scroll_steps + 1):
                scroll_position = i * step_height
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position})")
                time.sleep(0.2)  # 每步间隔0.2秒，总共2秒
            
            # 停留展示
            time.sleep(2)
            
            logger.info("首页演示完成")
            return True
        except Exception as e:
            logger.error(f"首页演示失败: {e}")
            # 尝试获取页面源码以帮助调试
            try:
                page_source = self.driver.page_source
                logger.debug(f"页面源码前1000字符: {page_source[:1000]}")
            except:
                pass
            return False
    
    def demo_upload_page(self):
        """进入文件上传页面，停留3秒钟"""
        logger.info("演示上传页面...")
        try:
            # 导航到上传页面
            self.driver.get("http://localhost:5000/upload")
            
            # 等待页面加载
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                logger.warning(f"上传页面可能未完全加载，继续演示: {e}")
            
            # 停留3秒钟展示上传页面
            time.sleep(3)
            
            logger.info("上传页面演示完成")
            return True
        except Exception as e:
            logger.error(f"上传页面演示失败: {e}")
            # 尝试获取当前URL以帮助调试
            try:
                current_url = self.driver.current_url
                logger.debug(f"当前页面URL: {current_url}")
            except:
                pass
            return False
    
    def run_custom_story_demo(self):
        """运行自定义故事线演示"""
        logger.info("开始自定义故事线演示...")
        
        try:
            # 1. 启动Flask应用
            if not self.start_flask_app():
                return False
            
            # 2. 设置Chrome浏览器
            if not self.setup_chrome_driver():
                return False
            
            # 3. 执行自定义故事线演示步骤
            logger.info("执行自定义故事线演示步骤...")
            
            # 步骤1: 演示首页
            if not self.demo_homepage():
                logger.warning("首页演示失败，继续下一步")
            
            # 步骤2: 演示上传页面
            if not self.demo_upload_page():
                logger.warning("上传页面演示失败，继续下一步")
            
            logger.info("自定义故事线演示完成！")
            return True
            
        except Exception as e:
            logger.error(f"自定义故事线演示出错: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理资源...")
        
        # 关闭浏览器
        if self.driver:
            self.driver.quit()
        
        # 停止Flask应用
        if self.app_process:
            self.app_process.terminate()
            self.app_process.wait()
        
        logger.info("资源清理完成")

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="自定义故事线演示系统")
    parser.add_argument("--no-app", action="store_true", help="不启动Flask应用")
    parser.add_argument("--no-browser", action="store_true", help="不启动浏览器")
    parser.add_argument("--test-mode", action="store_true", help="测试模式，不执行实际演示")
    
    args = parser.parse_args()
    
    logger.info("启动自定义故事线演示系统")
    
    # 测试模式下直接返回
    if args.test_mode:
        logger.info("测试模式：系统可以正常导入和运行")
        return
    
    # 创建演示系统
    demo_system = CustomStoryDemo()
    
    # 运行演示
    success = demo_system.run_custom_story_demo()
    
    if success:
        logger.info("🎉 自定义故事线演示成功完成！")
    else:
        logger.error("❌ 演示失败，请检查日志")

if __name__ == "__main__":
    main()