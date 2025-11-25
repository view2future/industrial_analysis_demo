#!/usr/bin/env python3
"""
一键启动演示系统
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖包"""
    logger.info("检查依赖包...")
    required_packages = [
        'selenium',
        'pyautogui', 
        'cv2',
        'numpy',
        'webdriver_manager'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.info(f"安装缺失的依赖包: {missing_packages}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '-r', 'demo_requirements.txt'
            ])
            logger.info("依赖包安装完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"安装依赖包失败: {e}")
            return False
    
    logger.info("所有依赖包已安装")
    return True

def setup_chrome_driver():
    """设置Chrome浏览器驱动"""
    logger.info("设置Chrome浏览器驱动...")
    try:
        # 检查系统中是否已安装ChromeDriver
        import shutil
        system_chromedriver = shutil.which("chromedriver")
        
        if system_chromedriver:
            logger.info(f"使用系统已安装的ChromeDriver: {system_chromedriver}")
            return True
        else:
            # 使用优化的ChromeDriver管理器，跳过版本检查
            from demo.chromedriver_utils import get_chrome_driver
            # 测试驱动是否可用
            driver = get_chrome_driver(headless=True, skip_version_check=True)
            driver.quit()
            logger.info("ChromeDriver安装完成")
            return True
    except Exception as e:
        logger.error(f"设置Chrome驱动失败: {e}")
        logger.info("请确保已安装Chrome浏览器")
        return False

def main():
    """主函数"""
    logger.info("启动区域产业分析小工作台自动演示系统")
    
    # 检查并安装依赖
    if not check_dependencies():
        logger.error("依赖包检查失败")
        return
    
    # 设置Chrome驱动
    if not setup_chrome_driver():
        logger.error("Chrome驱动设置失败")
        return
    
    # 等待用户确认
    logger.info("\n=== 演示系统准备就绪 ===")
    logger.info("请确保：")
    logger.info("1. 已关闭占用5000端口的其他应用")
    logger.info("2. 屏幕分辨率设置合适（推荐1920x1080）")
    logger.info("3. 关闭可能弹出的通知和窗口")
    logger.info("4. 保持网络连接稳定")
    
    try:
        input("\n按回车键开始自动演示...")
    except EOFError:
        logger.info("\n自动开始演示（无输入）...")
    
    # 运行演示
    try:
        # 询问用户选择演示类型
        print("\n请选择演示类型:")
        print("1. 完整功能演示（默认）")
        print("2. 自动滚动演示（新需求）")
        
        try:
            choice = input("请输入选择 (1 或 2，默认为 1): ").strip()
        except EOFError:
            choice = "1"
        
        if choice == "2":
            from auto_scroll_demo import ScrollDemoSystem
            demo_system = ScrollDemoSystem()
            success = demo_system.run_demo()
        else:
            from demo_system import AutoDemoSystem
            demo_system = AutoDemoSystem()
            success = demo_system.run_demo()
        
        if success:
            logger.info(f"\n🎉 演示成功完成！")
            logger.info(f"视频文件保存在: {demo_system.video_path}")
            logger.info(f"文件大小: {os.path.getsize(demo_system.video_path) / 1024 / 1024:.1f} MB")
        else:
            logger.error("\n演示失败，请查看demo_system.log获取详细信息")
            
    except KeyboardInterrupt:
        logger.info("\n演示被用户中断")
    except Exception as e:
        logger.error(f"\n演示出错: {e}")
        logger.error("请查看demo_system.log获取详细信息")

if __name__ == "__main__":
    main()