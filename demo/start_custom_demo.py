#!/usr/bin/env python3
"""
一键启动自定义故事线演示系统
"""

import os
import sys
import subprocess
import logging
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖包"""
    logger.info("检查依赖包...")
    required_packages = [
        'selenium',
        'webdriver-manager'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.info(f"安装缺失的依赖包: {missing_packages}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '-r', 'demo/demo_requirements.txt'
            ])
            logger.info("依赖包安装完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"安装依赖包失败: {e}")
            return False
    
    logger.info("所有依赖包已安装")
    return True

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="一键启动自定义故事线演示系统")
    parser.add_argument("--test-mode", action="store_true", help="测试模式，不执行实际演示")
    parser.add_argument("--simple", action="store_true", help="使用简化版演示（不依赖Selenium）")
    args = parser.parse_args()
    
    logger.info("启动自定义故事线演示系统")
    
    # 测试模式
    if args.test_mode:
        logger.info("测试模式：系统可以正常运行")
        return
    
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent.resolve()
    sys.path.insert(0, str(project_root))
    
    # 检查并安装依赖（除非使用简化版）
    if not args.simple and not check_dependencies():
        logger.error("依赖包检查失败")
        return
    
    # 等待用户确认
    logger.info("\n=== 自定义故事线演示系统准备就绪 ===")
    logger.info("请确保：")
    logger.info("1. 已关闭占用5000端口的其他应用")
    logger.info("2. 屏幕分辨率设置合适")
    logger.info("3. 关闭可能弹出的通知和窗口")
    logger.info("4. 保持网络连接稳定")
    
    try:
        input("\n按回车键开始自定义故事线演示...")
    except EOFError:
        logger.info("\n自动开始演示（无输入）...")
    
    # 运行演示
    try:
        if args.simple:
            from demo.simple_custom_demo import SimpleCustomStoryDemo
            demo_system = SimpleCustomStoryDemo()
            success = demo_system.run_custom_story_demo()
        else:
            from demo.custom_story_demo import CustomStoryDemo
            demo_system = CustomStoryDemo()
            success = demo_system.run_custom_story_demo()
        
        if success:
            logger.info(f"\n🎉 自定义故事线演示成功完成！")
        else:
            logger.error("\n演示失败，请查看日志获取详细信息")
            
    except KeyboardInterrupt:
        logger.info("\n演示被用户中断")
    except Exception as e:
        logger.error(f"\n演示出错: {e}")
        logger.error("请查看日志获取详细信息")

if __name__ == "__main__":
    main()