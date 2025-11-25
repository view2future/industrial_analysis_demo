#!/usr/bin/env python3
"""
自定义故事线演示系统测试脚本
用于验证自定义演示系统各组件是否正常工作
"""

import os
import sys
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_custom_demo_files():
    """测试自定义演示文件"""
    logger.info("测试自定义演示文件...")
    
    required_files = [
        "demo/custom_story_demo.py",
        "demo/start_custom_demo.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            file_size = Path(file_path).stat().st_size
            logger.info(f"✅ {file_path}: 存在 (大小: {file_size} bytes)")
        else:
            missing_files.append(file_path)
            logger.error(f"❌ {file_path}: 不存在")
    
    return len(missing_files) == 0

def test_custom_demo_imports():
    """测试自定义演示导入"""
    logger.info("测试自定义演示导入...")
    
    try:
        # 尝试导入自定义演示模块
        sys.path.append("demo")
        from custom_story_demo import CustomStoryDemo
        logger.info("✅ CustomStoryDemo: 导入成功")
        return True
    except Exception as e:
        logger.error(f"❌ CustomStoryDemo导入失败: {e}")
        return False

def test_custom_demo_methods():
    """测试自定义演示方法"""
    logger.info("测试自定义演示方法...")
    
    try:
        sys.path.append("demo")
        from custom_story_demo import CustomStoryDemo
        
        # 检查类是否有必要的方法
        demo = CustomStoryDemo()
        required_methods = [
            'start_flask_app',
            'setup_chrome_driver',
            'demo_homepage',
            'demo_upload_page',
            'run_custom_story_demo',
            'cleanup'
        ]
        
        missing_methods = []
        for method in required_methods:
            if hasattr(demo, method):
                logger.info(f"✅ {method}: 存在")
            else:
                missing_methods.append(method)
                logger.error(f"❌ {method}: 不存在")
        
        return len(missing_methods) == 0
        
    except Exception as e:
        logger.error(f"❌ 自定义演示方法测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    logger.info("=" * 50)
    logger.info("开始自定义故事线演示系统测试")
    logger.info("=" * 50)
    
    tests = [
        ("自定义演示文件测试", test_custom_demo_files),
        ("自定义演示导入测试", test_custom_demo_imports),
        ("自定义演示方法测试", test_custom_demo_methods)
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
        logger.info("🎉 所有测试通过！自定义故事线演示系统可以正常运行")
        return True
    else:
        logger.error("❌ 测试未通过，请解决上述问题后再运行自定义演示系统")
        return False

def main():
    """主函数"""
    try:
        success = run_all_tests()
        
        if success:
            logger.info("\n💡 使用方法:")
            logger.info("1. 运行 'python start_custom_demo.py' 启动自定义演示")
            logger.info("2. 或直接运行 'python demo/custom_story_demo.py'")
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