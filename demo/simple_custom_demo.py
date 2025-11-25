#!/usr/bin/env python3
"""
简化版自定义故事线演示系统
使用系统默认浏览器进行演示
"""

import os
import sys
import time
import logging
import subprocess
import webbrowser
import argparse
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_custom_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleCustomStoryDemo:
    def __init__(self):
        self.app_process = None
        self.project_root = Path(__file__).parent.parent.resolve()
        
    def start_flask_app(self):
        """启动Flask应用"""
        logger.info("启动Flask应用...")
        try:
            # 使用app.py启动应用
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
    
    def demo_homepage(self):
        """演示首页 - 打开浏览器展示首页"""
        logger.info("演示首页...")
        try:
            # 打开浏览器访问首页
            webbrowser.open("http://localhost:5000")
            
            # 等待页面加载
            time.sleep(3)
            
            logger.info("首页演示完成")
            return True
        except Exception as e:
            logger.error(f"首页演示失败: {e}")
            return False
    
    def demo_upload_page(self):
        """进入文件上传页面"""
        logger.info("演示上传页面...")
        try:
            # 打开浏览器访问上传页面
            webbrowser.open("http://localhost:5000/upload")
            
            # 停留展示
            time.sleep(3)
            
            logger.info("上传页面演示完成")
            return True
        except Exception as e:
            logger.error(f"上传页面演示失败: {e}")
            return False
    
    def run_custom_story_demo(self):
        """运行自定义故事线演示"""
        logger.info("开始简化版自定义故事线演示...")
        
        try:
            # 1. 启动Flask应用
            if not self.start_flask_app():
                return False
            
            # 2. 执行自定义故事线演示步骤
            logger.info("执行自定义故事线演示步骤...")
            
            # 步骤1: 演示首页
            if not self.demo_homepage():
                logger.warning("首页演示失败，继续下一步")
            
            # 等待用户查看首页
            time.sleep(2)
            
            # 步骤2: 演示上传页面
            if not self.demo_upload_page():
                logger.warning("上传页面演示失败，继续下一步")
            
            logger.info("简化版自定义故事线演示完成！")
            return True
            
        except Exception as e:
            logger.error(f"简化版自定义故事线演示出错: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理资源...")
        
        # 停止Flask应用
        if self.app_process:
            self.app_process.terminate()
            self.app_process.wait()
        
        logger.info("资源清理完成")

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="简化版自定义故事线演示系统")
    parser.add_argument("--test-mode", action="store_true", help="测试模式，不执行实际演示")
    args = parser.parse_args()
    
    # 测试模式
    if args.test_mode:
        logger.info("测试模式：系统可以正常导入和运行")
        return
    
    logger.info("启动简化版自定义故事线演示系统")
    
    # 创建演示系统
    demo_system = SimpleCustomStoryDemo()
    
    # 运行演示
    success = demo_system.run_custom_story_demo()
    
    if success:
        logger.info("🎉 简化版自定义故事线演示成功完成！")
    else:
        logger.error("❌ 演示失败，请检查日志")

if __name__ == "__main__":
    main()