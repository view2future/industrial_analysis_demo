#!/usr/bin/env python3
"""
Auto Demo System - Main Entry Point
Automated demonstration system for Regional Industrial Dashboard
"""

import asyncio
import argparse
import sys
import time
import socket
from pathlib import Path
import subprocess
import signal
import yaml

# Add auto_demo to path
sys.path.insert(0, str(Path(__file__).parent / 'auto_demo'))

from demo_engine import DemoEngine


def check_flask_server(host='localhost', port=5000, timeout=2) -> bool:
    """Check if Flask server is running and accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt user for yes/no input"""
    default_str = 'Y/n' if default else 'y/N'
    try:
        response = input(f"{question} [{default_str}]: ").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes', '是']
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*60)
    print("  🎬 区域产业分析小工作台 - 自动化演示系统")
    print("  Regional Industrial Dashboard - Auto Demo System")
    print("="*60 + "\n")


def print_progress(message: str):
    """Print progress message"""
    print(f"  ▶ {message}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='自动化演示系统 - 基于Playwright的浏览器自动化',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python start_demo.py                                    # 运行默认演示（headless模式）
  python start_demo.py --headed                           # 可视化浏览器模式
  python start_demo.py --record                           # 启用屏幕录制
  python start_demo.py --scenario auto_demo/scenarios/quick_demo.yaml
  python start_demo.py --headed --record                  # 可视化 + 录制
        """
    )
    
    parser.add_argument(
        '--scenario',
        default='auto_demo/scenarios/structured_showcase_8min.yaml',
        help='YAML scenario file path (default: structured_showcase_8min.yaml)'
    )
    
    parser.add_argument(
        '--headed',
        action='store_true',
        help='Run browser in headed mode (visible window)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (no window, default)'
    )
    
    parser.add_argument(
        '--record',
        action='store_true',
        help='Enable screen recording'
    )
    
    parser.add_argument(
        '--no-prompt',
        action='store_true',
        help='Skip interactive prompts'
    )

    parser.add_argument(
        '--ss',
        choices=['big', 'small'],
        required=True,
        help='set screen size (big=1920x1080, small=1280x720)'
    )
    parser.add_argument(
        '--speed',
        choices=['slow', 'normal', 'fast'],
        default='normal',
        help='demo speed profile'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Determine headless mode
    headless = not args.headed if args.headed else True
    
    # Prompt for recording if not specified
    record_video = args.record
    if not args.no_prompt and not args.record:
        record_video = prompt_yes_no("是否启用屏幕录制?", default=False)
    
    scenario_path = Path(args.scenario)
    if not scenario_path.exists():
        print(f"❌ 错误: 场景文件不存在: {scenario_path}")
        print(f"\n可用场景:")
        scenarios_dir = Path(__file__).parent / 'auto_demo' / 'scenarios'
        if scenarios_dir.exists():
            for yaml_file in scenarios_dir.glob('*.yaml'):
                print(f"  - {yaml_file.relative_to(Path.cwd())}")
        sys.exit(1)

    if args.speed != 'normal':
        try:
            with open(scenario_path, 'r', encoding='utf-8') as f:
                scenario_data = yaml.safe_load(f) or {}
            cfg = scenario_data.get('config', {})
            if args.speed == 'fast':
                cfg['action_delay'] = max(0.7, float(cfg.get('action_delay', 1.2)) * 0.7)
                cfg['slow_motion'] = int(float(cfg.get('slow_motion', 40)) * 0.5)
            elif args.speed == 'slow':
                cfg['action_delay'] = float(cfg.get('action_delay', 1.2)) * 1.5
                cfg['slow_motion'] = int(float(cfg.get('slow_motion', 40)) * 1.5)
            scenario_data['config'] = cfg
            tmp_path = Path(__file__).parent / 'auto_demo' / 'scenarios' / ('_runtime_' + scenario_path.name)
            with open(tmp_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(scenario_data, f, allow_unicode=True)
            scenario_path = tmp_path
        except Exception as e:
            print(f"⚠️ 速度参数处理失败: {e}")
    
    # Check Flask server
    print_progress("检查 Flask 服务器状态...")
    if not check_flask_server():
        print("  ⚠️  Flask 服务器未运行在 http://localhost:5000")
        print("  💡 请先在另一个终端运行: python app.py")
        
        if not args.no_prompt:
            continue_anyway = prompt_yes_no("是否继续（演示将失败）?", default=False)
            if not continue_anyway:
                sys.exit(1)
        else:
            sys.exit(1)
    else:
        print("  ✅ Flask 服务器运行正常")
    
    # Configuration summary
    print("\n" + "-"*60)
    print("配置信息:")
    print(f"  场景文件:  {scenario_path}")
    print(f"  浏览器模式: {'可视化 (Headed)' if not headless else '无头 (Headless)'}")
    print(f"  屏幕录制:  {'启用 ✅' if record_video else '禁用'}")
    print(f"  屏幕尺寸:  {'1920x1080' if args.ss=='big' else '1280x720'}")
    print(f"  演示速度:  {args.speed}")
    if record_video:
        recordings_dir = Path(__file__).parent / 'auto_demo' / 'recordings'
        print(f"  录制目录:  {recordings_dir}")
    print("-"*60 + "\n")
    
    if not args.no_prompt:
        input("按 Enter 键开始演示...")
        print()
    
    # Create and run demo engine
    try:
        print_progress("初始化演示引擎...")
        engine = DemoEngine(
            scenario_path=str(scenario_path),
            headless=headless,
            record_video=record_video,
            screen_size=args.ss
        )
        
        print_progress("开始执行演示场景...\n")
        success = await engine.run()
        
        if success:
            print("\n" + "="*60)
            print("  ✅ 演示执行成功！")
            if record_video:
                recordings_dir = Path(__file__).parent / 'auto_demo' / 'recordings'
                latest_video = max(recordings_dir.glob('*.webm'), key=lambda p: p.stat().st_mtime, default=None)
                if latest_video:
                    print(f"  📹 录制文件: {latest_video}")
            print("="*60 + "\n")
            return 0
        else:
            print("\n" + "="*60)
            print("  ❌ 演示执行失败")
            print("  请检查日志输出以获取详细错误信息")
            print("="*60 + "\n")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  演示被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 演示系统出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
