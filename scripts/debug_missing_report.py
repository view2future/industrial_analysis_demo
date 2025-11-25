#!/usr/bin/env python3
"""
Debug script to investigate the missing report issue
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app_enhanced import app, db, Report
from datetime import datetime
import json

def debug_missing_report():
    """Debug the specific missing report"""
    with app.app_context():
        # Find our specific missing report
        report = Report.query.filter_by(report_id='llm_report_20251104_015136').first()
        
        if not report:
            print("❌ Report not found in database")
            return
            
        print(f"📋 Report Details:")
        print(f"  Report ID: {report.report_id}")
        print(f"  Status: {report.status}")
        print(f"  Type: {report.report_type}")
        print(f"  User ID: {report.user_id}")
        print(f"  Created: {report.created_at}")
        print(f"  Completed: {report.completed_at}")
        print(f"  File Path: {report.file_path}")
        print()
        
        # Check if file path is set in database
        if report.file_path:
            file_path = Path(report.file_path)
            print(f"📁 Expected file path from database: {file_path}")
            print(f"  File exists: {file_path.exists()}")
            if file_path.exists():
                print(f"  File size: {file_path.stat().st_size} bytes")
        else:
            print("⚠️  No file path set in database")
        
        # Check the default expected path
        expected_path = Path('data/output/llm_reports') / f"{report.report_id}.json"
        print(f"\n📁 Default expected path: {expected_path}")
        print(f"  File exists: {expected_path.exists()}")
        if expected_path.exists():
            print(f"  File size: {expected_path.stat().st_size} bytes")
            
        # Check if there are any similar files (maybe with slightly different names)
        output_dir = Path('data/output/llm_reports')
        if output_dir.exists():
            print(f"\n🔍 Checking for similar files in {output_dir}:")
            similar_files = []
            for json_file in output_dir.glob('llm_report_*.json'):
                if report.report_id[:20] in json_file.name:  # Check first 20 chars for similarity
                    similar_files.append(json_file)
            
            if similar_files:
                for similar in similar_files:
                    print(f"  - {similar.name} (size: {similar.stat().st_size} bytes)")
            else:
                print("  No similar files found")
        
        # Check for any files created around the same time
        report_time = report.created_at
        print(f"\n⏰ Looking for files created around {report_time}:")
        if output_dir.exists():
            time_matches = []
            for json_file in output_dir.glob('llm_report_*.json'):
                file_time = datetime.fromtimestamp(json_file.stat().st_mtime)
                time_diff = abs((file_time - report_time).total_seconds())
                if time_diff < 600:  # Within 10 minutes
                    time_matches.append((json_file, time_diff))
            
            if time_matches:
                for json_file, time_diff in sorted(time_matches, key=lambda x: x[1]):
                    print(f"  - {json_file.name} (time diff: {time_diff:.0f} seconds)")
            else:
                print("  No time-matching files found")

if __name__ == '__main__':
    debug_missing_report()