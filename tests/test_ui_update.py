#!/usr/bin/env python3
"""
完整测试脚本 - 测试UI实时更新
"""

import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app, db, Report, User
from src.tasks.report_tasks import generate_llm_report_task
from celery.result import AsyncResult

def test_ui_update():
    """测试UI实时更新功能"""
    
    print("="*80)
    print("🧪 测试报告生成UI实时更新")
    print("="*80)
    
    with app.app_context():
        # 1. 创建测试用户（如果不存在）
        user = User.query.filter_by(username='admin').first()
        if not user:
            print("\n❌ 请先启动Flask应用创建admin用户")
            return False
        
        # 2. 提交任务
        print("\n📤 提交报告生成任务...")
        task = generate_llm_report_task.delay(
            city="测试市",
            industry="测试行业",
            additional_context="这是一个UI测试，请生成300字以内的简短报告",
            user_id=user.id,
            initial_report_id="ui_test_report"
        )
        
        print(f"✓ 任务ID: {task.id}")
        print(f"✓ 报告ID: ui_test_report")
        
        # 3. 模拟前端轮询，监控状态变化
        print(f"\n📊 监控任务状态变化 (模拟前端每2秒轮询)...\n")
        
        stages_seen = set()
        last_stage = None
        start_time = time.time()
        
        for i in range(60):  # 最多60秒
            result = AsyncResult(task.id)
            
            if result.state == 'PENDING':
                if i % 5 == 0:  # 每10秒打印一次
                    print(f"[{i:2d}s] ⏳ PENDING - 等待处理...")
                    
            elif result.state == 'PROGRESS':
                info = result.info
                stage = info.get('stage', 'unknown')
                message = info.get('message', '')
                status = info.get('status', '')
                current = info.get('current', 0)
                total = info.get('total', 100)
                
                if stage != last_stage:
                    stages_seen.add(stage)
                    elapsed = time.time() - start_time
                    
                    print(f"\n[{elapsed:5.1f}s] 🔄 阶段变化: {last_stage or '开始'} → {stage}")
                    print(f"         进度: {current}/{total}")
                    print(f"         状态: {status}")
                    print(f"         消息: {message}")
                    
                    last_stage = stage
                    
            elif result.state == 'SUCCESS':
                elapsed = time.time() - start_time
                info = result.info
                
                print(f"\n[{elapsed:5.1f}s] ✅ SUCCESS - 任务完成!")
                print(f"\n📄 最终结果:")
                print(f"   Report ID: {info.get('report_id')}")
                print(f"   File Path: {info.get('file_path')}")
                print(f"   File Size: {info.get('file_size')}")
                print(f"   City: {info.get('city')}")
                print(f"   Industry: {info.get('industry')}")
                
                print(f"\n📈 阶段统计:")
                print(f"   总耗时: {elapsed:.1f} 秒")
                print(f"   经历阶段: {len(stages_seen)} 个")
                print(f"   阶段列表: {', '.join(stages_seen)}")
                
                break
                
            elif result.state == 'FAILURE':
                elapsed = time.time() - start_time
                print(f"\n[{elapsed:5.1f}s] ❌ FAILURE - 任务失败")
                print(f"   错误: {result.info}")
                return False
            
            time.sleep(2)
        
        # 4. 验证预期的阶段都出现了
        expected_stages = {'init', 'generating', 'summary_zh', 'summary_en', 'swot', 'saving', 'completed'}
        
        print(f"\n✅ 阶段验证:")
        for stage in expected_stages:
            if stage in stages_seen:
                print(f"   ✓ {stage}")
            else:
                print(f"   ✗ {stage} (未检测到)")
        
        missing = expected_stages - stages_seen
        if missing:
            print(f"\n⚠️  警告: 缺少阶段 {missing}")
        else:
            print(f"\n✅ 所有预期阶段都已正确更新!")
        
        print("\n" + "="*80)
        print("🎉 测试完成")
        print("="*80)
        
        return True

if __name__ == '__main__':
    success = test_ui_update()
    sys.exit(0 if success else 1)
