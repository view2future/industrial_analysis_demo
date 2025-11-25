#!/usr/bin/env python3
"""
自动化演示系统
自动执行项目演示流程
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# 设置webdriver-manager环境变量以优化性能
# 延长缓存有效期至7天（604800秒）
os.environ['WDM_CACHE_VALID_RANGE'] = '7'
# 启用本地缓存
os.environ['WDM_LOCAL'] = '1'

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('demo_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoDemoSystem:
    def __init__(self):
        self.app_process = None
        self.driver = None
        self.demo_steps = []
        self.setup_paths()
        
    def check_and_switch_window(self):
        """
        Centralized function to check driver status and window handles.
        It switches to the latest window or attempts to recover by restarting the driver.
        Returns True if the driver is ready for use, False otherwise.
        """
        try:
            if self.driver and self.driver.window_handles:
                # If there are windows, switch to the last one.
                self.driver.switch_to.window(self.driver.window_handles[-1])
                return True
        except Exception as e:
            # This will catch errors like "no such window" if the handle is stale
            logger.warning(f"Error checking window handles: {e}. Will attempt to restart driver.")

        # If we're here, driver is None, has no windows, or threw an exception.
        logger.info("Attempting to recover WebDriver.")
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass # Ignore errors during quit

        self.driver = None
        if self.setup_chrome_driver():
            self.driver.get("http://localhost:5000/")
            logger.info("WebDriver recovered and navigated to homepage.")
            return True
        else:
            logger.error("Failed to recover WebDriver.")
            return False
        
    def setup_paths(self):
        """设置路径"""
        self.project_root = Path(__file__).parent.parent.resolve()
        self.demo_dir = self.project_root / "demo" / "output"
        self.demo_dir.mkdir(exist_ok=True)
        self.sample_file = self.project_root / "data" / "input" / "sample_ai_industry_analysis.md"
        
    def start_flask_app(self):
        """启动Flask应用"""
        logger.info("启动Flask应用...")
        try:
            # 使用app_enhanced.py启动应用
            self.app_process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # 等待应用启动
            time.sleep(5)
            logger.info("Flask应用启动成功")
            return True
        except Exception as e:
            logger.error(f"启动Flask应用失败: {e}")
            return False
    
    def setup_chrome_driver(self):
        """设置Chrome浏览器"""
        logger.info("设置Chrome浏览器...")
        try:
            # 使用优化的ChromeDriver管理器，跳过版本检查
            from demo.chromedriver_utils import get_chrome_driver
            
            self.driver = get_chrome_driver(headless=True, additional_options=[
                "--start-maximized"
            ], skip_version_check=True)
            logger.info("Chrome浏览器设置成功")
            return True
        except Exception as e:
            logger.error(f"设置Chrome浏览器失败: {e}")
            return False
    
    def demo_homepage(self):
        """演示首页"""
        logger.info("演示首页...")
        try:
            if not self.check_and_switch_window():
                logger.error("WebDriver not available, skipping step.")
                return False
            self.driver.get("http://localhost:5000")
            
            # 等待页面加载
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                logger.warning(f"首页可能未完全加载，继续演示: {e}")
            
            # 滚动页面展示
            self.driver.execute_script("window.scrollTo(0, 300)")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 0)")
            time.sleep(1)
            
            logger.info("首页演示完成")
            return True
        except Exception as e:
            logger.error(f"首页演示失败: {e}")
            # 即使首页演示失败，也继续执行后续步骤
            return True
    
    def demo_upload_page(self):
        """演示上传页面"""
        logger.info("演示上传页面...")
        try:
            if not self.check_and_switch_window():
                logger.error("WebDriver not available, skipping step.")
                return False
            
            # 点击开始分析按钮
            start_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '开始分析') or @class='btn btn-primary' or contains(@class, 'analyze-btn')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", start_btn)
            time.sleep(1) # Short pause for visibility
            start_btn.click()
            
            # 等待上传页面加载
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "fileInput"))
            )
            
            # 展示上传区域
            self.driver.execute_script("arguments[0].scrollIntoView(true);", file_input)
            time.sleep(2)
            
            logger.info("上传页面演示完成")
            return True
        except Exception as e:
            logger.error(f"上传页面演示失败: {e}")
            return False
    
    def demo_file_upload(self):
        """演示文件上传和分析"""
        logger.info("演示文件上传和分析...")
        try:
            if not self.check_and_switch_window():
                logger.error("WebDriver not available, skipping step.")
                return False

            upload_url = "http://localhost:5000/upload"
            if self.driver.current_url != upload_url:
                logger.info(f"Not on the upload page. Navigating to {upload_url}")
                self.driver.get(upload_url)
            
            # 找到并等待文件输入框
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "fileInput"))
            )
            
            if self.sample_file.exists():
                self.driver.execute_script("arguments[0].scrollIntoView(true);", file_input)
                time.sleep(1)
                
                file_input.send_keys(str(self.sample_file))

                # 点击分析按钮
                analyze_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(text(), '分析') or contains(text(), 'Analyze')]"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", analyze_btn)
                time.sleep(1)
                analyze_btn.click()
                
                # 等待分析完成
                WebDriverWait(self.driver, 90).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "analysis-results"))
                )
                
                logger.info("文件上传和分析演示完成")
                return True
            else:
                logger.error(f"示例文件不存在: {self.sample_file}")
                return False
                
        except Exception as e:
            logger.error(f"文件上传演示失败: {e}")
            return False
    
    def demo_analysis_results(self):
        """演示分析结果"""
        logger.info("演示分析结果...")
        try:
            if not self.check_and_switch_window():
                logger.error("WebDriver not available, skipping step.")
                return False
            # 滚动展示各个部分
            sections = [
                ("核心要点", 400),
                ("可视化图表", 800),
                ("分类分析详情", 1200),
                ("AI应用机会", 1600)
            ]
            
            for section, scroll_y in sections:
                logger.info(f"展示{section}...")
                self.driver.execute_script(f"window.scrollTo(0, {scroll_y})")
                time.sleep(3)
            
            # 回到顶部
            self.driver.execute_script("window.scrollTo(0, 0)")
            time.sleep(2)
            
            logger.info("分析结果演示完成")
            return True
        except Exception as e:
            logger.error(f"分析结果演示失败: {e}")
            return False
    
    def demo_visualizations(self):
        """演示可视化功能"""
        logger.info("演示可视化功能...")
        try:
            if not self.check_and_switch_window():
                logger.error("WebDriver not available, skipping step.")
                return False

            # 点击图表进行交互
            charts = self.driver.find_elements(By.CLASS_NAME, "plotly-graph-div")
            
            for i, chart in enumerate(charts[:3]):  # 演示前3个图表
                try:
                    # 点击图表
                    ActionChains(self.driver).move_to_element(chart).click().perform()
                    time.sleep(2)
                    
                    # 滚动展示图表详情
                    self.driver.execute_script(f"window.scrollTo(0, {chart.location['y'] - 100})")
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"图表{i+1}交互失败: {e}")
            
            logger.info("可视化功能演示完成")
            return True
        except Exception as e:
            logger.error(f"可视化功能演示失败: {e}")
            return False
    
    def demo_settings_page(self):
        """演示设置页面"""
        logger.info("演示设置页面...")
        try:
            if not self.check_and_switch_window():
                logger.error("WebDriver not available, skipping step.")
                return False

            # 导航到设置页面
            self.driver.get("http://localhost:5000/settings")
            
            # 检查页面是否加载成功
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 展示设置选项
            self.driver.execute_script("window.scrollTo(0, 300)")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 600)")
            time.sleep(2)
            
            logger.info("设置页面演示完成")
            return True
        except Exception as e:
            logger.error(f"设置页面演示失败: {e}")
            return False
    
    def demo_additional_features(self):
        """演示其他功能"""
        logger.info("演示其他功能...")
        try:
            if not self.check_and_switch_window():
                logger.error("WebDriver not available, skipping step.")
                return False
            # 演示地图可视化
            try:
                self.driver.get("http://localhost:5000/map_visualization")
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                logger.info("地图可视化演示完成")
            except:
                logger.warning("地图可视化不可用")
            
            # 演示知识图谱
            try:
                self.driver.get("http://localhost:5000/knowledge_graph")
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                logger.info("知识图谱演示完成")
            except:
                logger.warning("知识图谱不可用")
            
            return True
        except Exception as e:
            logger.error(f"其他功能演示失败: {e}")
            return False
    
    def run_demo(self):
        """运行完整演示"""
        logger.info("开始自动演示...")
        
        try:
            # 1. 启动Flask应用
            if not self.start_flask_app():
                return False
            
            # 2. 设置Chrome浏览器
            if not self.setup_chrome_driver():
                return False
            
            # 3. 执行演示步骤
            demo_steps = [
                ("首页演示", self.demo_homepage),
                ("上传页面演示", self.demo_upload_page),
                ("文件上传和分析演示", self.demo_file_upload),
                ("分析结果演示", self.demo_analysis_results),
                ("可视化功能演示", self.demo_visualizations),
                ("设置页面演示", self.demo_settings_page),
                ("其他功能演示", self.demo_additional_features)
            ]
            
            for step_name, step_func in demo_steps:
                logger.info(f"执行步骤: {step_name}")
                if not step_func():
                    logger.warning(f"步骤 {step_name} 执行失败，继续下一步")
                time.sleep(2)  # 步骤间暂停
            
            logger.info("自动演示完成！")
            return True
            
        except Exception as e:
            logger.error(f"自动演示出错: {e}")
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
    logger.info("启动区域产业分析小工作台自动演示系统")
    
    # 检查依赖
    try:
        import selenium
    except ImportError as e:
        logger.error(f"缺少依赖包: {e}")
        logger.info("请安装依赖: pip install selenium")
        return
    
    # 创建演示系统
    demo_system = AutoDemoSystem()
    
    # 运行演示
    success = demo_system.run_demo()
    
    if success:
        logger.info("演示成功完成！")
    else:
        logger.error("演示失败，请检查日志")

if __name__ == "__main__":
    main()
