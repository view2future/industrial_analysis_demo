#!/usr/bin/env python3
"""
修复数据库中处于 processing 状态的报告记录
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app_enhanced import app, db, Report
from datetime import datetime

def fix_processing_reports():
    """修复所有 processing 状态的报告"""
    with app.app_context():
        # 查找所有 processing 状态的报告
        processing_reports = Report.query.filter_by(status='processing').all()
        
        print(f"找到 {len(processing_reports)} 个 processing 状态的报告\n")
        
        # 获取所有已存在的报告文件
        output_dir = Path('data/output/llm_reports')
        if not output_dir.exists():
            print("报告目录不存在")
            return
        
        json_files = {f.stem: f for f in output_dir.glob('llm_report_*.json')}
        print(f"找到 {len(json_files)} 个报告文件:")
        for fname in sorted(json_files.keys()):
            print(f"  - {fname}")
        print()
        
        updated = 0
        for report in processing_reports:
            print(f"检查报告: {report.report_id}")
            
            # 1. 检查精确匹配的文件
            if report.report_id in json_files:
                file_path = json_files[report.report_id]
                print(f"  ✓ 找到匹配文件: {file_path.name}")
                report.status = 'completed'
                report.completed_at = datetime.utcnow()
                report.file_path = str(file_path)
                updated += 1
                continue
            
            # 2. 尝试时间戳匹配 (前后5分钟)
            report_time = report.created_at
            best_match = None
            min_diff = float('inf')
            
            for file_id, file_path in json_files.items():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                time_diff = abs((file_time - report_time).total_seconds())
                
                if time_diff < min_diff and time_diff < 300:  # 5分钟内
                    min_diff = time_diff
                    best_match = (file_id, file_path)
            
            if best_match:
                file_id, file_path = best_match
                print(f"  ✓ 找到时间匹配文件: {file_path.name} (时差 {min_diff:.0f}秒)")
                report.report_id = file_id
                report.status = 'completed'
                report.completed_at = datetime.utcnow()
                report.file_path = str(file_path)
                updated += 1
            else:
                print(f"  ✗ 未找到匹配文件，保持 processing 状态")
        
        db.session.commit()
        print(f"\n✅ 更新了 {updated} 个报告状态")
        
        # 显示当前状态
        print(f"\n当前报告状态统计:")
        completed = Report.query.filter_by(status='completed').count()
        processing = Report.query.filter_by(status='processing').count()
        failed = Report.query.filter_by(status='failed').count()
        
        print(f"  Completed: {completed}")
        print(f"  Processing: {processing}")
        print(f"  Failed: {failed}")

if __name__ == '__main__':
    fix_processing_reports()
