#!/usr/bin/env python3
"""
演示系统测试脚本
用于验证演示系统各组件是否正常工作
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dependencies():
    """测试依赖包"""
    logger.info("测试依赖包...")
    
    required_packages = {
        'selenium': 'Selenium WebDriver',
        'pyautogui': 'PyAutoGUI',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'webdriver_manager': 'WebDriver Manager'
    }
    
    missing_packages = []
    for package, name in required_packages.items():
        try:
            if package == 'cv2':
                import cv2
                logger.info(f"✅ {name}: 已安装 (版本: {cv2.__version__})")
            elif package == 'numpy':
                import numpy
                logger.info(f"✅ {name}: 已安装 (版本: {numpy.__version__})")
            else:
                __import__(package)
                logger.info(f"✅ {name}: 已安装")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {name}: 未安装")
    
    return len(missing_packages) == 0

def test_chrome_browser():
    """测试Chrome浏览器"""
    logger.info("测试Chrome浏览器...")
    
    try:
        # 检查Chrome是否安装
        if sys.platform == "darwin":  # macOS
            result = subprocess.run(["osascript", "-e", "tell application \"System Events\" to get name of every application process"], 
                                  capture_output=True, text=True)
            has_chrome = "Google Chrome" in result.stdout
        elif sys.platform == "linux":
            result = subprocess.run(["which", "google-chrome"], capture_output=True)
            has_chrome = result.returncode == 0
        else:  # Windows
            result = subprocess.run(["where", "chrome.exe"], capture_output=True)
            has_chrome = result.returncode == 0
        
        if has_chrome:
            logger.info("✅ Chrome浏览器: 已安装")
            return True
        else:
            logger.error("❌ Chrome浏览器: 未安装")
            return False
            
    except Exception as e:
        logger.error(f"❌ Chrome浏览器测试失败: {e}")
        return False

def test_webdriver():
    """测试WebDriver"""
    logger.info("测试WebDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 尝试创建WebDriver实例
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        
        logger.info("✅ WebDriver: 正常工作")
        return True
        
    except Exception as e:
        logger.error(f"❌ WebDriver测试失败: {e}")
        return False

def test_sample_file():
    """测试示例文件"""
    logger.info("测试示例文件...")
    
    sample_files = [
        Path("data/input/sample_ai_industry_analysis.md"),
        Path("data/input/chengdu_ai_industry_report.md"),
        Path("data/input/wuhan_smart_manufacturing_report.md")
    ]
    
    available_files = []
    for file_path in sample_files:
        if file_path.exists():
            file_size = file_path.stat().st_size
            logger.info(f"✅ {file_path.name}: 存在 (大小: {file_size} bytes)")
            available_files.append(file_path)
        else:
            logger.warning(f"⚠️  {file_path.name}: 不存在")
    
    if available_files:
        logger.info(f"找到 {len(available_files)} 个可用的示例文件")
        return True
    else:
        logger.error("❌ 没有找到可用的示例文件")
        return False

def test_flask_app():
    """测试Flask应用"""
    logger.info("测试Flask应用...")
    
    try:
        # 检查必要的文件
        required_files = [
            "app_enhanced.py",
            "requirements.txt",
            "config.json",
            "templates/index.html"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"❌ 缺少必要文件: {missing_files}")
            return False
        
        logger.info("✅ Flask应用文件: 完整")
        return True
        
    except Exception as e:
        logger.error(f"❌ Flask应用测试失败: {e}")
        return False

def test_port_availability():
    """测试端口可用性"""
    logger.info("测试端口5000可用性...")
    
    try:
        import socket
        
        # 尝试绑定端口5000
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        try:
            sock.bind(('localhost', 5000))
            logger.info("✅ 端口5000: 可用")
            return True
        except OSError:
            logger.error("❌ 端口5000: 被占用")
            return False
        finally:
            sock.close()
            
    except Exception as e:
        logger.error(f"❌ 端口测试失败: {e}")
        return False

def test_disk_space():
    """测试磁盘空间"""
    logger.info("测试磁盘空间...")
    
    try:
        import shutil
        
        # 获取当前磁盘使用情况
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024**3)
        
        if free_gb > 2:  # 需要至少2GB可用空间
            logger.info(f"✅ 磁盘空间: {free_gb:.1f}GB 可用")
            return True
        else:
            logger.warning(f"⚠️  磁盘空间: {free_gb:.1f}GB 可用 (建议至少2GB)")
            return False
            
    except Exception as e:
        logger.error(f"❌ 磁盘空间测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    logger.info("=" * 50)
    logger.info("开始演示系统测试")
    logger.info("=" * 50)
    
    tests = [
        ("依赖包测试", test_dependencies),
        ("Chrome浏览器测试", test_chrome_browser),
        ("WebDriver测试", test_webdriver),
        ("示例文件测试", test_sample_file),
        ("Flask应用测试", test_flask_app),
        ("端口可用性测试", test_port_availability),
        ("磁盘空间测试", test_disk_space)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
            time.sleep(1)  # 测试间暂停
        except Exception as e:
            logger.error(f"测试出错: {e}")
    
    # 总结
    logger.info("\n" + "=" * 50)
    logger.info(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！演示系统可以正常运行")
        return True
    elif passed >= total * 0.8:  # 80%通过
        logger.info("⚠️  大部分测试通过，演示系统应该可以运行，但建议解决警告项")
        return True
    else:
        logger.error("❌ 测试未通过，请解决上述问题后再运行演示系统")
        return False

def main():
    """主函数"""
    try:
        success = run_all_tests()
        
        if success:
            logger.info("\n💡 建议:")
            logger.info("1. 运行 'python start_demo.py' 开始自动演示")
            logger.info("2. 或运行 'python demo_simple.py' 使用简化版（macOS）")
            logger.info("3. 详细使用说明请查看 'demo_guide.md'")
        
        return success
        
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
        return False
    except Exception as e:
        logger.error(f"\n测试出错: {e}")
        return False

if __name__ == "__main__":
    main()