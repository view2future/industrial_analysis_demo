#!/usr/bin/env python3
"""
Complete database inspection and verification
"""

import sys
import os
import sqlite3
from datetime import datetime
sys.path.append(os.getcwd())

from app import app, db, WeChatArticle, User

def inspect_and_verify_db():
    print("=== Database Verification ===")
    print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # Check the actual database file
    db_path = 'industrial_analysis.db'
    print(f"Database file exists: {os.path.exists(db_path)}")
    if os.path.exists(db_path):
        print(f"Database file size: {os.path.getsize(db_path)} bytes")
    
    # Use Flask application context to inspect tables
    with app.app_context():
        # Reflect the current state
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        # Print table info
        for table_name in tables:
            print(f"\nTable '{table_name}' columns:")
            columns = inspector.get_columns(table_name)
            for col in columns:
                print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")
        
        # Check wechat_articles content
        if 'we_chat_article' in tables:
            article_count = WeChatArticle.query.count()
            print(f"\nWeChat Articles in database: {article_count}")
            
            if article_count > 0:
                print("Sample articles:")
                for article in WeChatArticle.query.limit(3).all():
                    print(f"  - ID: {article.id}")
                    print(f"    Title: {article.title[:50]}...")
                    print(f"    Source: {article.source_account}")
                    print(f"    Date: {article.publish_date}")
                    print(f"    Keywords: {article.keywords}")
                    print()
        
        # Check if any data exists
        user_count = User.query.count()
        print(f"Users in database: {user_count}")
        
        from app import Report  # Import here to avoid circular import issues
        report_count = Report.query.count()
        print(f"Reports in database: {report_count}")
    
    # Direct SQLite inspection
    print("\n=== Direct SQLite Inspection ===")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables via direct SQLite: {[table[0] for table in tables]}")
        
        # Try to check if there are any records at all
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"Records in {table_name}: {count}")
            
        conn.close()
    except Exception as e:
        print(f"Error in direct SQLite inspection: {e}")

if __name__ == "__main__":
    inspect_and_verify_db()