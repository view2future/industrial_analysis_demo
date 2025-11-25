#!/usr/bin/env python3
"""
Fix the missing report by updating the database status
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app_enhanced import app, db, Report
from datetime import datetime

def fix_missing_report():
    """Fix the specific missing report"""
    with app.app_context():
        # Find our specific missing report
        report = Report.query.filter_by(report_id='llm_report_20251104_015136').first()
        
        if not report:
            print("❌ Report not found in database")
            return
            
        print(f"📋 Found report: {report.report_id}")
        print(f"  Current status: {report.status}")
        print(f"  File path: '{report.file_path}'")
        
        # Check if file exists
        expected_path = Path('data/output/llm_reports') / f"{report.report_id}.json"
        
        if expected_path.exists():
            print(f"✅ File actually exists: {expected_path}")
            print(f"  File size: {expected_path.stat().st_size} bytes")
            
            # Update database with correct file path
            if not report.file_path:
                report.file_path = str(expected_path)
                db.session.commit()
                print("✅ Updated database with correct file path")
        else:
            print(f"❌ File missing: {expected_path}")
            print("\n🔄 Setting report status to 'failed' so user can retry...")
            
            # Set report status back to failed so user can retry
            report.status = 'failed'
            report.completed_at = None
            db.session.commit()
            print("✅ Report status set to 'failed'")
            print("✅ User can now retry generating this report")

if __name__ == '__main__':
    fix_missing_report()