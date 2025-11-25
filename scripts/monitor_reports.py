#!/usr/bin/env python3
"""
Monitor and fix report inconsistencies between database and filesystem
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app_enhanced import app, db, Report
from datetime import datetime
import json

def analyze_reports():
    """Analyze all reports and identify inconsistencies"""
    with app.app_context():
        print("🔍 开始分析报告状态...")
        
        # Get all reports
        all_reports = Report.query.all()
        print(f"📊 数据库中共有 {len(all_reports)} 个报告")
        
        # Categorize by status
        completed_reports = [r for r in all_reports if r.status == 'completed']
        processing_reports = [r for r in all_reports if r.status == 'processing']
        failed_reports = [r for r in all_reports if r.status == 'failed']
        
        print(f"  ✅ Completed: {len(completed_reports)}")
        print(f"  ⏳ Processing: {len(processing_reports)}")
        print(f"  ❌ Failed: {len(failed_reports)}")
        print()
        
        # Check filesystem
        output_dir = Path('data/output/llm_reports')
        if output_dir.exists():
            json_files = {f.stem: f for f in output_dir.glob('llm_report_*.json')}
            print(f"📁 文件系统中共有 {len(json_files)} 个报告文件")
        else:
            print("❌ 报告目录不存在")
            json_files = {}
        
        print()
        
        # Analyze completed reports
        print("🔍 分析已完成的报告...")
        missing_files = []
        empty_file_paths = []
        invalid_file_paths = []
        valid_completed = []
        
        for report in completed_reports:
            if not report.file_path:
                empty_file_paths.append(report)
                continue
                
            file_path = Path(report.file_path)
            if not file_path.exists():
                missing_files.append(report)
            else:
                # Verify it's a valid JSON file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    valid_completed.append(report)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    invalid_file_paths.append(report)
        
        print(f"  ✅ 有效的已完成报告: {len(valid_completed)}")
        print(f"  ⚠️  空文件路径: {len(empty_file_paths)}")
        print(f"  ❌ 缺失文件: {len(missing_files)}")
        print(f"  🔥 无效JSON文件: {len(invalid_file_paths)}")
        
        if empty_file_paths:
            print("\\n📋 空文件路径的报告:")
            for report in empty_file_paths[:5]:  # Show first 5
                print(f"  - {report.report_id} (created: {report.created_at})")
            if len(empty_file_paths) > 5:
                print(f"  ... and {len(empty_file_paths) - 5} more")
        
        if missing_files:
            print("\\n📋 缺失文件的报告:")
            for report in missing_files[:5]:  # Show first 5
                print(f"  - {report.report_id} (expected: {report.file_path})")
            if len(missing_files) > 5:
                print(f"  ... and {len(missing_files) - 5} more")
        
        if invalid_file_paths:
            print("\\n📋 无效JSON文件的报告:")
            for report in invalid_file_paths[:5]:  # Show first 5
                print(f"  - {report.report_id} (file: {report.file_path})")
            if len(invalid_file_paths) > 5:
                print(f"  ... and {len(invalid_file_paths) - 5} more")
        
        # Analyze processing reports
        print(f"\\n🔍 分析处理中的报告...")
        stale_processing = []
        recent_processing = []
        
        for report in processing_reports:
            age_hours = (datetime.now() - report.created_at).total_seconds() / 3600
            if age_hours > 2:  # Older than 2 hours
                stale_processing.append((report, age_hours))
            else:
                recent_processing.append((report, age_hours))
        
        print(f"  ⏰ 最近的处理中报告 (<2小时): {len(recent_processing)}")
        print(f"  🕰️  陈旧的处理中报告 (>2小时): {len(stale_processing)}")
        
        if stale_processing:
            print("\\n📋 陈旧的 processing 报告 (可能需要修复):")
            for report, age_hours in stale_processing[:5]:
                print(f"  - {report.report_id} (年龄: {age_hours:.1f} 小时)")
        
        # Find orphaned files (files without database records)
        print(f"\\n🔍 检查孤立文件...")
        db_report_ids = {r.report_id for r in all_reports}
        orphaned_files = []
        
        for file_id, file_path in json_files.items():
            if file_id not in db_report_ids:
                orphaned_files.append(file_path)
        
        print(f"  🗂️  孤立文件 (无数据库记录): {len(orphaned_files)}")
        if orphaned_files:
            print("📋 孤立文件:")
            for file_path in orphaned_files[:5]:
                print(f"  - {file_path.name}")
            if len(orphaned_files) > 5:
                print(f"  ... and {len(orphaned_files) - 5} more")
        
        return {
            'total_reports': len(all_reports),
            'completed': len(completed_reports),
            'processing': len(processing_reports),
            'failed': len(failed_reports),
            'valid_completed': len(valid_completed),
            'empty_file_paths': empty_file_paths,
            'missing_files': missing_files,
            'invalid_file_paths': invalid_file_paths,
            'stale_processing': stale_processing,
            'recent_processing': recent_processing,
            'orphaned_files': orphaned_files,
            'filesystem_files': len(json_files)
        }

def fix_issues(analysis_results):
    """Fix identified issues"""
    with app.app_context():
        print("\\n🔧 开始修复问题...")
        
        fixed_count = 0
        
        # Fix empty file paths in completed reports
        if analysis_results['empty_file_paths']:
            print(f"\\n🛠️ 修复空文件路径的报告 ({len(analysis_results['empty_file_paths'])} 个)...")
            for report in analysis_results['empty_file_paths']:
                expected_path = Path('data/output/llm_reports') / f"{report.report_id}.json"
                if expected_path.exists():
                    report.file_path = str(expected_path)
                    print(f"  ✅ 修复: {report.report_id}")
                    fixed_count += 1
                else:
                    print(f"  ⚠️  文件缺失，设为failed: {report.report_id}")
                    report.status = 'failed'
                    report.completed_at = None
                    fixed_count += 1
        
        # Fix stale processing reports
        if analysis_results['stale_processing']:
            print(f"\\n🛠️ 修复陈旧的 processing 报告 ({len(analysis_results['stale_processing'])} 个)...")
            for report, age_hours in analysis_results['stale_processing']:
                expected_path = Path('data/output/llm_reports') / f"{report.report_id}.json"
                if expected_path.exists():
                    # File exists, mark as completed
                    report.status = 'completed'
                    report.file_path = str(expected_path)
                    print(f"  ✅ 完成: {report.report_id} (找到文件)")
                else:
                    # File doesn't exist, mark as failed
                    report.status = 'failed'
                    report.completed_at = None
                    print(f"  ❌ 失败: {report.report_id} (文件缺失)")
                fixed_count += 1
        
        # Commit all changes
        if fixed_count > 0:
            db.session.commit()
            print(f"\\n✅ 共修复了 {fixed_count} 个问题")
        else:
            print("\\n✅ 没有发现需要修复的问题")

def main():
    """Main function"""
    print("🚀 启动报告监控系统...")
    
    # Analyze reports
    results = analyze_reports()
    
    # Ask if user wants to fix issues
    total_issues = len(results['empty_file_paths']) + len(results['stale_processing'])
    
    if total_issues > 0:
        print(f"\\n❓ 发现 {total_issues} 个问题，是否修复？ (yes/no): ", end="")
        try:
            response = input().strip().lower()
            if response == 'yes':
                fix_issues(results)
            else:
                print("\\n⏭️  跳过修复")
        except (EOFError, KeyboardInterrupt):
            print("\\n⏭️  跳过修复 (无输入)")
    else:
        print("\\n✅ 没有发现需要修复的问题")
    
    print("\\n🎉 报告监控完成！")

if __name__ == '__main__':
    main()