#!/usr/bin/env python3
"""
简化版自动演示系统
使用macOS内置录屏功能
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleDemoSystem:
    def __init__(self):
        self.app_process = None
        self.recording_process = None
        self.demo_dir = Path("demo_output")
        self.demo_dir.mkdir(exist_ok=True)
        self.video_path = self.demo_dir / f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mov"
        self.sample_file = Path("data/input/sample_ai_industry_analysis.md")
        
    def start_flask_app(self):
        """启动Flask应用"""
        logger.info("启动Flask应用...")
        try:
            self.app_process = subprocess.Popen(
                [sys.executable, "app_enhanced.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(5)  # 等待应用启动
            logger.info("Flask应用启动成功")
            return True
        except Exception as e:
            logger.error(f"启动Flask应用失败: {e}")
            return False
    
    def start_screen_recording(self):
        """开始录屏（macOS）"""
        logger.info("开始录屏...")
        try:
            # 使用macOS的screencapture命令
            cmd = [
                "screencapture", "-v",  # 视频模式
                "-T", "0",  # 不显示倒计时
                str(self.video_path)
            ]
            
            self.recording_process = subprocess.Popen(cmd)
            time.sleep(2)  # 给录屏一些启动时间
            logger.info(f"录屏开始，保存到: {self.video_path}")
            return True
        except Exception as e:
            logger.error(f"开始录屏失败: {e}")
            return False
    
    def stop_screen_recording(self):
        """停止录屏"""
        logger.info("停止录屏...")
        if self.recording_process:
            # 发送SIGTERM信号停止录屏
            self.recording_process.terminate()
            self.recording_process.wait()
            logger.info("录屏停止")
    
    def automate_browser_actions(self):
        """使用系统命令自动操作浏览器"""
        logger.info("开始浏览器自动化操作...")
        
        try:
            # 打开浏览器
            subprocess.run(["open", "http://localhost:5000"])
            time.sleep(5)
            
            # 演示步骤
            steps = [
                ("等待首页加载", 3),
                ("滚动页面展示", 2),
                ("等待用户查看", 5),
                ("滚动到上传区域", 2),
                ("等待上传演示", 8),
                ("滚动展示结果", 10),
                ("最终展示", 5)
            ]
            
            for step_name, duration in steps:
                logger.info(f"步骤: {step_name}")
                
                # 使用AppleScript进行页面交互
                if "滚动" in step_name:
                    script = '''
                    tell application "System Events"
                        key code 125 using {shift down}  -- 向下滚动
                    end tell
                    '''
                    subprocess.run(["osascript", "-e", script])
                
                time.sleep(duration)
            
            logger.info("浏览器自动化完成")
            return True
            
        except Exception as e:
            logger.error(f"浏览器自动化失败: {e}")
            return False
    
    def run_demo(self):
        """运行简化演示"""
        logger.info("开始简化版自动演示...")
        
        try:
            # 启动应用
            if not self.start_flask_app():
                return False
            
            # 开始录屏
            if not self.start_screen_recording():
                return False
            
            # 执行浏览器自动化
            self.automate_browser_actions()
            
            # 停止录屏
            self.stop_screen_recording()
            
            logger.info("简化演示完成！")
            return True
            
        except Exception as e:
            logger.error(f"简化演示出错: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理资源...")
        
        # 停止录屏
        self.stop_screen_recording()
        
        # 停止Flask应用
        if self.app_process:
            self.app_process.terminate()
            self.app_process.wait()
        
        # 关闭浏览器
        try:
            subprocess.run(["pkill", "-f", "Chrome"], capture_output=True)
        except:
            pass

def main():
    """主函数"""
    logger.info("启动简化版区域产业分析小工作台自动演示系统")
    logger.info("适用于macOS系统")
    
    # 检查系统
    if sys.platform != "darwin":
        logger.warning("此简化版适用于macOS系统")
        logger.info("对于其他系统，请使用完整的demo_system.py")
    
    # 创建演示系统
    demo_system = SimpleDemoSystem()
    
    # 运行演示
    try:
        success = demo_system.run_demo()
        
        if success:
            logger.info(f"\n🎉 简化演示完成！")
            logger.info(f"视频文件保存在: {demo_system.video_path}")
        else:
            logger.error("\n简化演示失败")
            
    except KeyboardInterrupt:
        logger.info("\n演示被用户中断")
    except Exception as e:
        logger.error(f"\n演示出错: {e}")

if __name__ == "__main__":
    main()